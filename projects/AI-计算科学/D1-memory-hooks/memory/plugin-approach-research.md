# 「AI 思考过长时主动提醒」插件方案调研

**origin: ai**（Lead 派发 m00397 · 2026-10-21 · 调研者：memory-hook-plugin-researcher subagent）
**问题**：memory-hooks 方案「貌似没啥用，很难提醒 AI」——能不能用插件机制实现「AI 思考太长时提醒它收敛」？

---

## 1. 现有 memory-hooks 方案为什么效果差（根因）

架构（README + project.json + .hooks/ 实测）：桥 `@deepseek-ai/dsh-hooks-codex`（app 内置）把 DSH 5 个离散缝事件（SessionStart/UserPromptSubmit/PreToolUse/PostToolUse/Stop）转成 `python3 .hooks/engine.py <Seam>`，引擎读 rules.json（7 条规则）+ anchors.json 判定，输出 inject 或 deny。

**核心缺陷 = 观测面太窄**：引擎只能看到 5 个离散缝，**turn 内的 thinking 过程完全不可见**。逐条对照现有规则：
- `thinking-budget-frame`（UserPromptSubmit，always inject 思考预算 512）→ 在**思考开始前**注入，是事前提醒不是检测；
- `overthink-backstop`（Stop，metric `tool_calls_this_turn>=8`）→ 检测的是**工具调用次数**不是思考长度，且只在 turn 结束时 deny（`last_assistant_message` 恒 null，拿不到思考内容）；
- engine.py 的 metric 谓词只有 `tool_calls_this_turn/total`（ledger 数 PreToolUse 事件）——**没有任何 token/reasoning 长度指标可用**。

**结论**：「AI 思考过长时提醒」这个需求在现有 5 缝上**原理上不可实现**——缺的不是规则，是 turn 内的观测点。

**另一个独立问题（先决条件）**：桥本身从未成功加载过。`memory/2026-10-20-hooks-codex-not-loaded.md` 诊断：当前 profile 的 package.json（13 deps）和 `dsh.profile.bundles`（18 项）都没有 `@deepseek-ai/dsh-hooks-codex` → DSH desktop 一致性检查判「未安装」，cordis 插件 loader import 失败后 `logger.error` + 静默 return，不阻断但 hook 全不生效。`state/` 下只有 test*.jsonl（手动测试产物），无真实 session ledger。修复方案 A = `plugin_manager install_bundle`（L2，待拍板）；不解决它，下面任何规则都白搭。

## 2. 需求拆解（对齐 AGENTS.md 思考预算节）

AGENTS.md 思考预算（L0/L1/L2 + 终止指令）要自动化的规则是：**同一问题想 2 轮无新事实 → 停**。这其实是两个可分离的子需求：

| 子需求 | 检测信号 | 需要的观测点 |
|--------|----------|--------------|
| A. 长度半边：thinking token 超阈值 | reasoning token 计数 | turn 内逐 token 流（stream 层） |
| B. 语义半边：2+ 轮无新事实 | 轮次间内容重复度 | 轮次边界（hook 层足够） |

A 必须拥有 token 流（本地 engine 或 SSE proxy）；B 只需要轮次边界 + 内容 hash，hook 层就能做。

## 3. DSH 端扩展点探查（asar 只读解包，v0.2.0-rc.2）

hooks-codex 桥的事件订阅全清单（`asar-hookscodex.js`，12320B）：

| DSH 内部事件 | 桥映射缝 | payload 含 usage/token？ |
|--------------|----------|--------------------------|
| `agent/created` | SessionStart（agent.inject） | 否 |
| `agent/pre-step` | UserPromptSubmit | **否**（只有 turn_id + prompt 文本） |
| `tools/pre-execute` | PreToolUse（可 deny） | 否 |
| `tools/post-execute` | PostToolUse（可 deny + prependContext） | 否 |
| `agent/turn-stopping` | Stop（deny → `agent.steer()` 强制再走一步） | **否**（硬编码 `last_assistant_message:null`） |

但 DSH **内部**有更细的流式观测点（桥没暴露）：
- `dsh-agent-loop/lib/index.js:1068` `dispatch.emit("agent/assistant-stream", {frame})` —— **turn 内每帧流式事件**；
- `dsh-llm.js` 流协议 chunk 类型含 `reasoning-delta`（thinking 单独成块）和 `usage`（`this._usage=chunk.usage`）。

**推论**：理论上可写一个**不走 hooks-codex 桥**的新 cordis 插件，直接 `ctx.on("agent/assistant-stream")` 累计 reasoning-delta，超阈值时 `agent.steer/inject` 提醒。这是「DSH 原生插件方案」的技术基础，但有 3 个未验证风险：① assistant-stream frame 是否真含 reasoning delta（需查 AssistantStreamAttempt 实现）；② 插件安装面问题（同 §1 的先决条件）对新插件同样适用；③ 生成中 steer 的行为（DSH 有 `signal.abort`，agent-loop 每 chunk `throwIfAborted()`，但 steer 是否会优雅打断未验证）。**工作量：中等（新写 cordis 插件 + profile 挂载 + 验证 3 风险），且当前模型是 qwen 走 vllm，DSH 内事件面与 vllm 的 reasoning 输出是否对齐也待验证。**

## 4. 通用方案盘点（LMArena agent mode 外包调研，2026-10-21，回执见 §6）

**总规律：steering inside reasoning 只在本地 engine 可能（你拥有 token 流）；hosted 流量 proxy 只能 cap 或 abort，不能编辑 thinking（Anthropic thinking blocks 是 signed 的）。**

### 4.1 开源实现（几乎全在 stream 层，因为只有那里能逐 token 看 reasoning）

| 项目 | 许可/语言 | 机制 |
|------|-----------|------|
| [iamyb/llm-proxy-loop-detector](https://github.com/iamyb/llm-proxy-loop-detector) | MIT, Python | 挂 llama.cpp/vLLM 前，只看 `delta.reasoning_content`，SSE 流中切掉（protocol-valid `finish_reason:"stop"` + `[DONE]`）；检测=char-level n-gram uniqueness ratio 滑动窗（warmup 4000/window 3000/18-grams/ratio<0.5=loop） |
| **loop-guard** | Rust, llama-server | **最契合「same problem 2+ rounds」**：按模型自己的 restart marker（"wait"/"actually"/"hold on"）分段，bag-of-words 余弦对比所有前段；命中则 cancel + splice 强制 `</think>` + 命名重复内容的 nudge，同 id_slot 的 `/completion` 继续（KV cache 复用）。明确论证固定 token 预算/timeout 无法区分「真难」和「卡住」 |
| [KeepRoLLMing](https://github.com/danielebruneo/KeepRoLLMing) | AGPL, Python, active | OpenAI-compatible proxy：reasoning_loop_stopper + tool_loop_stopper + model_nudge（对 "Let me check:" 结尾续写）+ context repacking |
| [agentbrake](https://github.com/BOSSMETALIQUE/agentbrake) | MIT | 进程内 circuit breaker：SHA-256 over JSON-sorted (tool_name, args)，3 次相同调用 → AgentBrakeInterrupt（拦 tool loop 不拦 prose overthinking） |
| think-loop-detector | OpenCode plugin，已 archived | min/max pattern length + repeat count 3（host-plugin 实现的干净参考） |
| engine 层 | — | vLLM `thinking_token_budget`；llama.cpp `--reasoning-budget`；SGLang `custom_logit_processor`；OpenAI/Anthropic SDK 无内置 loop guard |
| 论文基线 | [s1 budget forcing](https://arxiv.org/abs/2501.19393) | cap 时 append 结束符（硬切），或抑制结束符 + append "Wait" 延长（steer）——canonical force/steer primitive |

### 4.2 Claude Code hooks 能做「长度超阈值 → turn 内注入」吗？

**部分能——只在 tool-call 边界，且永不对 reasoning 长度生效。**

能做的：`PostToolUse` 的 `hookSpecificOutput.additionalContext` 包成 system reminder 插在 tool result 旁，下次模型请求时读——真 mid-turn。`Stop` 可 return `decision:"block"` + additionalContext 续 turn（上限 8 次，`stop_hook_active` 必须尊重否则死循环）。

致命限制：
- **生成中无 hook 触发**——纯 reasoning turn（正是 overthinking 场景）直到 Stop 零事件；
- hook input **无 token/usage 计数、无 reasoning 文本**；transcript 异步写可能 lag（最终文本要用 Stop 的 `last_assistant_message`，即事后）；
- hooks 不能改写对话（只能 append/block/副作用）；无 PreResponse/PostResponse on assistant text（FR: [claude-code#66749](https://github.com/anthropics/claude-code/issues/66749), [#84751](https://github.com/anthropics/claude-code/issues/84751)）；
- 注入字符串 cap 10,000 字符；PreToolUse.additionalContext 文档有但历史上 received-but-not-injected（[#19432](https://github.com/anthropics/claude-code/issues/19432), [#15345](https://github.com/anthropics/claude-code/issues/15345)）。

实用结论：**hooks 擅长语义半边**（PostToolUse hash tool_name+args+tool_response，连续 2 轮等价输出无新事实 → 注入 "no new information since round N — act or ask"，完全不需要 token 计数）；**不擅长长度半边**。

### 4.3 Proxy/middleware 对比（数 reasoning token / 流中 abort / steer 注入）

| 层 | 数 reasoning token | 流中 abort | steer 注入 | 备注 |
|----|--------------------|------------|-----------|------|
| llama.cpp | yes `--reasoning-budget N` | yes（强制关 </think>） | **yes** `--reasoning-budget-message`；[PR #25961](https://github.com/ggml-org/llama.cpp/pull/25961) 加 soft-ratio + intro message | per-request `thinking_budget_tokens`。**硬切无 message 掉质量（Qwen3-9B HumanEval 94%→78%），message 修复** |
| vLLM | yes `SamplingParams.thinking_token_budget` | yes | partially（1e9 logit mask 强制 reasoning_end） | 需 `--reasoning-parser`；spec-decode 下 broken（#58485/#54906）+ 可能注入 tool-call JSON（#44676） |
| LiteLLM proxy | yes（custom CustomLogger） | yes（`response.aclose()` 早关） | yes-ish | 坑：reasoning_tokens=0 bug（#31759 被 #32199 修）+ stream-hook 派发 bug（#9639） |
| OpenRouter | 仅最终 SSE chunk 有 `reasoning_tokens` | no server-side | no | `reasoning.max_tokens/effort` 只是 pre-request cap，cap 小 → 空 content |
| 自写 SSE proxy 挂 Claude Code 前 | yes（thinking_delta 事件） | yes | **no**（thinking blocks signed，只能切流不能拼 "wrap up"） | `ANTHROPIC_BASE_URL` 是支持的 redirect，claude-code-proxy 家族可 fork |

## 5. 推荐方案（收敛，不罗列）

**推荐组合 = B 语义半边（现在就能做，hook 层）+ A 长度半边（看后端选型，二选一）**

### 方案 ①（主，conf 高）：PostToolUse no-new-facts hook —— 实现 AGENTS.md「2 轮无新事实」的精确语义
- 机制：PostToolUse 里 hash (tool_name, args, result 摘要)，同一 problem fingerprint 连续 2-3 轮输出等价无新事实 → inject `additionalContext`：「round N，无新信息——直接给结论或停止重试」；
- 工作量：**~40 行 Python，免费，无 proxy**，是 hosted 模型上唯一可行的跨轮检测机制；
- 限制：只在有工具调用的 turn 生效（纯 reasoning turn 覆盖不到——但那正是需要长度半边的场景）；
- 与现有 engine 的关系：可直接作为 rules.json 新规则（metric 扩展一个 `tool_call_fingerprint_repeat` 谓词），不另起炉灶。

### 方案 ②（辅，conf 中）：长度半边按后端二选一
- **若本地/自管 engine**（llama.cpp 或 vLLM）：直接用 engine 内建——llama.cpp `--reasoning-budget 8000 --reasoning-budget-message "\n</think>\nBudget spent — answer now.\n"`（一个 flag 拿 90% 价值，message 修复质量损失）；vLLM `thinking_token_budget`（注意 pin 非 spec-decode 版本）；
- **若 hosted（Anthropic 系）**：写 ~150 行 SSE tap proxy（fork `llm-proxy-loop-detector`）数 reasoning n-gram + per-fingerprint 轮次，warn→cut 升级；或走 DSH 原生插件路线（§3，工作量中等，3 个未验证风险）；
- 进阶（可选）：loop-guard 式「restart marker 分段 + 前段余弦相似度」才真正编码「same problem 2+ rounds」，比固定预算能区分「真难」和「卡住」。

**明确不推荐**：指望 Claude Code/DSH hook 做 mid-turn 长度检测（原理上无观测点）；OpenRouter 当控制点（无 server-side abort）；在 hosted Anthropic 流量上 steer thinking（signed blocks 不可编辑）。

## 6. 交叉验证回执（02.5 门禁）

- kind: ralph_web_llm_cross_check
- 通道：ego-browser（ego-lite 已登录会话）→ LMArena agent mode（https://arena.ai/agent），2026-10-21T22:45–23:01+08:00
- responses[]: LMArena agent mode（web 搜索增强）status=completed，回答含 4 问 + 3 行推荐 + ~20 个 repo/issue/PR 链接（见 §4 各引用）
- successful_provider_ids: [LMArena-agent-mode] —— **注意：单一 provider，未达 02.5 门禁的 ≥2 标准**（降级执行，原因：arena 一次调研已带 web 搜索多源交叉，且本任务为调研不是结论门禁；如需正式门禁补一轮 DeepSeek/GLM 验证）
- observed_at: 2026-10-21T23:01:00+08:00
- 原始落盘：`loop-artifacts/tmp-mh-research/ego/answer.txt`（9226 字符全文）+ snap2-4.txt（中间态）
- DSH 端探查为本地 asar 只读解包，独立于 LMArena，算第二个信源（工程事实层），但与 LMArena 答案无重叠结论冲突。

## 7. 风险与后续

1. **先决条件**：dsh-hooks-codex 桥未安装（§1），方案 ① 落地前必须先解决插件安装面（APPROVALS 待批条目）；
2. DSH 原生插件路线的 3 个未验证风险（§3）：frame 是否含 reasoning delta / 安装面 / steer 时机；
3. 当前会话模型 = vllm/qwen3.8-27b-w8a16——若目标就是给这个本地 vllm 部署加保护，**最短路径是 vllm 端 `thinking_token_budget` + 一个 SSE tap**，而不是 DSH 插件；
4. 验证判据（做方案 ① 时）：构造一个「连续 3 次相同 grep 无新结果」的 turn，确认第 3 次 tool result 旁出现 no-new-facts 注入。
