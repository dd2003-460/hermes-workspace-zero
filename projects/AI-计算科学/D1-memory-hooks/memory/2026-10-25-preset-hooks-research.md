# origin: ai
# preset 工作机制调研 + hook 注册通用规则可行性（2026-10-25，Lead 直查 asar 源码）

用户请求（m00001）：调研各种 preset 工作机制/优势劣势，是否适合用 hook 注册通用规则和工具。
两用例：A=压缩前提醒模型写简短摘要再机械清空只留最后几条消息；B=每隔固定步数提醒模型规则和当前阶段。

## 1. DSH 的「preset」到底是什么

三层概念，容易混淆：

### 1.1 Agent preset（`@deepseek-ai/dsh-agent-preset`）
- 在 Cordis YAML 里声明一组**插件行列表**（persona/instructions/tools/compaction 组/delegation 组…），`id` 必填（会话保存时引用），可同时声明多个 preset 由会话选择。
- 出货样例 4 个（`dsh-web-app/presets/*.patch.yml`）：standard（全量工具+压缩+委派+plan-mode 组）、minimal（persistent shell 为主、无压缩无 web）、ptc（code-mode）、cordis（开发者向）。
- **关键机制**：声明提前加载；修改 preset 只影响之后创建的 Agent——同一插件组合的 Agent 共享 KV Cache 热前缀（preset 稳定性=cache 稳定性）。
- 需要 registry 服务（`dsh-agent-preset-registry`）；重复 id 加载失败。
- **preset 本身不是 hook**：它只是「插件清单模板」。要注入规则，本质是选/改 persona 行的 `text`（静态系统提示词）或挂插件。

### 1.2 Persona（`@deepseek-ai/dsh-persona`）
- 静态系统提示词拼装：`prefix`（如 "You are a coding agent powered by {{model}}"）+ `suffix`（如 working directory）+ `text`（旧 key，desktop-transfer 的 `migratePersonaPrefix()` 会把 `text` 改写成 `prefix`）。
- loop-recipe preset 的 persona `text` 就是那份 253 行公理/Loop 规则全文——**一次性静态注入，永远占 token，永远在热前缀里（cache 友好但贵）**。
- `complete: true`（minimal 用）= persona 就是全部身份，不再叠加其他。

### 1.3 内置压缩 preset 组（`cordis:group` + `isolate: {compaction, toolResultPruner}`）
- standard preset 里 `compaction` 组 = compaction-basic（自动压缩引擎）+ command-compact（/compact）+ tool-result-pruner（thresholdChars 8192, head 4096, tail 1024）。
- `isolate` 字段给子插件建独立能力域（planMode/compaction/workflowEngine/terminals）。

## 2. 扩展点（harness 事件）全景 —— 这才是「hook 能站在哪里」

Cordis `ctx.on(name, listener, {prepend?, global?})` 注册，随 fiber 卸载自动 dispose。内置 DispatchMode：emit/parallel/serial/bail/waterfall。

已确认的内置扩展点（来自解包源码）：

| 扩展点 | 模式 | 消费方 | 时机 |
|---|---|---|---|
| `agent/created` | emit（脱离运行） | SessionStart 桥 | agent 诞生，可能错过第一个请求 |
| `agent/pre-step` | **waterfall（可拒绝/改写）** | UserPromptSubmit 桥、compaction-basic 自动触发 | **每步 LLM 请求派生前** |
| `agent/turn-stopping` | serial（阻塞→steer() 强制再走一步） | Stop 桥 | 轮次即将停止 |
| `tools/pre-execute` | waterfall（阻塞→deny） | PreToolUse 桥 | 工具执行前 |
| `tools/post-execute` | waterfall（阻塞反馈/加上下文） | PostToolUse 桥 | 工具执行后 |
| `agent/status` | emit | compaction-basic | 状态变化 |
| `session/event` | emit | compaction-basic | 任何会话事件 |
| `agent/request-error` | waterfall | compaction-basic 溢出恢复 | 请求失败（如 CONTEXT_WINDOW_EXCEEDED） |
| `compaction/summary-error` | waterfall | compaction 后端 | 摘要失败恢复 |
| `subagent/start` / `subagent/end` | emit | claude-code 桥 Subagent 事件 | child 生命周期（仅 claude-code 桥暴露） |
| `agent/assistant-stream` | emit | （内部，dsh-agent-loop lib/index.js:1068） | **reasoning-delta + usage 流，两桥均未暴露** |

## 3. 两套 hook 桥（外部配置→内置扩展点）

| | hooks-codex | hooks-claude-code |
|---|---|---|
| 配置 | 进程级单 configPath，启动读一次 | 同左（configPath 指向 hooks.json / settings） |
| 事件 | 5：SessionStart/UserPromptSubmit/PreToolUse/PostToolUse/Stop | 7：+SubagentStart/SubagentStop |
| handler | 仅同步 shell command，串行 | 同左（http/mcp_tool/prompt/agent handler 跳过） |
| 阻塞语义 | 退出码2=阻塞；deny>ask>allow；首个 continue:false 粘性 | 同左 |
| 加上下文 | additionalContext→user 消息（模型可见，重发直到压缩） | 同左 |
| 不支持 | PermissionRequest/PreCompact/PostCompact/Subagent* | PreCompact/PostCompact 等 23/30 项 |
| 已装状态 | **未装**（profile 缺包，cordis loader 静默失败） | 未装 |

共享规则（dsh-hook-protocol）：`HookOutput.updatedInput` 解析但不应用（延期）；`systemMessage` 不呈现；`continue:false` 折叠为 stop 但无运行级硬停；`transcript_path` 恒空（zstd 日志 hook 脚本读不了）；hook/invoked+hook/result 仅日志事件，不进模型历史；Stop 无条件阻塞=每步强制 continuation（hook 需自限）。

## 4. compaction 引擎的可扩展面（对应用例 A）

- seam（`dsh-compaction`）：抽象 `CompactionEngine` 三操作 `compactIfNeeded/compactNow/compactRegion`；`summarize()` 是**唯一后端钩子**，可继承基类换摘要方式（模板/远程/便宜模型）。
- compaction-basic：触发阈值 `floor(min(W×0.8, W−O−B))`；retainRatio 0.16 保留尾部；pruner 先剪不花调用；摘要走 `ctx.llm.stream()` 不走 agent loop，`GenerateOptions.purpose='compaction'`，可 `summarizationProvider/Model` 路由给便宜模型；摘要后=一条 user 消息（`<compacted-summary>`）替换早期范围，尾部逐字保留；**替换使第一个被遮蔽 token 起 KV cache 全部失效**。
- **没有 PreCompact/PostCompact 扩展点**（两桥 README 明列不支持）——压缩触发发生在 `agent/pre-step` 内部，外部 hook 无法在「摘要前」插话。
- 已知限制：计量=字符启发式（4 字符/token，CJK 偏低）；不可分工具节点不拆；摘要失败保留旧表层。

## 5. 两用例裁决

### 用例 A：「压缩前提醒模型写简短摘要→机械清空只留最后几条消息」
**不适合做 hook，适合做 compaction 后端替换。**
- 时序上做不到：没有 PreCompact 扩展点；compaction 在 pre-step 内同步执行，hook 桥站在 pre-step 上只能看到压缩后结果。
- 「机械清空只留最后几条」正是 compaction seam 的设计目标（替换早期范围+保留尾部）——现有 compaction-basic 已做「摘要+保留」，你只是想要更短的摘要和更少的保留。
- 正确姿势：**继承 CompactionEngine 写薄后端**（模板化摘要指令，retainRatio 调到更小或固定 retainTokens，summarizationModel 路由便宜模型）。不需要 hook，不需要「提醒模型写摘要」——摘要本来就是模型调用，只是由引擎发起而非主循环发起。
- 「提醒模型自己写摘要」路线的反例：主循环模型写摘要 = 在 pre-step 注入指令让它「先总结再继续」，但此时上下文已超窗，模型总结本身就是压缩的替代品（Claude Code 的 /compact、OpenAI 的 pre-compact 提示都是引擎代做，不是主模型自做）。

### 用例 B：「每固定步数提醒模型规则和当前阶段」
**适合做插件，不适合做 hook 桥。**
- 扩展点选 `agent/pre-step`（waterfall，每步 LLM 请求前）——这正是「每步注入」的锚点。codex 桥的 UserPromptSubmit 也站在这，但它只能按「用户提交提示词」触发且 payload 不含步数。
- 计数依据：`agent/pre-step` 的 payload 有 `turn` + messages 长度；或自维护计数（每 pre-step 命中 +1）。注意引擎 metric 只有 `tool_calls_this_turn/total`（`agent/assistant-stream` 有 usage 但桥未暴露）——「固定步数」建议按 pre-step 次数（≈每次 LLM 调用）计，而非「轮次」。
- 注入形式：往 messages 尾追加一条 user 系统提示（类似 hook additionalContext 的 createUserMessage），内容=规则摘要+当前阶段（从 loop-state.json 读）。
- **成本警告**：追加内容在后续请求重发直到压缩 → 每步 +N token×剩余步数；且追加在热前缀之后（cache 不失效，只增量）。规则文本应压到几百字符内（对比：persona 全文 253 行永远在前缀里）。
- 若走 hook 桥实现：PostToolUse 桥 + 自己计数的 state 文件也能做，但 codex 桥未安装、且桥只跑 shell command（脚本读文件→stdout JSON），复杂度不比原生 `ctx.on` 插件（~40 行）低，还少了 waterfall 的改写能力。**结论：直接写 Cordis 原生插件，跳过桥。**

## 6. 外部框架对照（preset 机制优劣汇总）

| 框架 | preset/规则注入机制 | 优点 | 缺点 |
|---|---|---|---|
| DSH | agent-preset=插件清单模板；persona=静态前缀；插件 ctx.on 扩展点；hook 桥=外部 JSON→扩展点 | 扩展点类型化（waterfall 可拒绝）；preset 稳定=KV cache 稳定；摘要可路由便宜模型 | 扩展点目录无公开 API 文档（靠解包/README）；hook 桥覆盖 5-7 事件，updatedInput/PreCompact 等延期；CJK token 计量偏低 |
| Claude Code | CLAUDE.md（静态）+ settings.json hooks（30 事件，command/http/mcp/prompt/agent 五类 handler） | 事件最全（PreCompact/PostCompact/PermissionRequest…）；handler 可并行+去重；updatedInput 可改写工具输入 | 规则与 hook 分离；压缩摘要策略不可自定义后端 |
| Codex | AGENTS.md（静态）+ ~/.codex/config.toml hooks（5 事件） | 简单；与 DSH codex 桥同构 | 事件少；无输入改写 |
| OpenAI Codex CLI / Aider 等 | 纯静态 AGENTS.md/CONVENTIONS.md | 零成本、cache 友好 | 无动态注入、无步数感知 |

**通用结论**：静态规则→persona/CLAUDE.md 类（cache 友好、零逻辑）；动态注入→扩展点/hook（步数感知、可改写，但每步有重发成本）；压缩定制→compaction 后端（引擎代做，勿让主模型自做）。

## 7. 建议（待用户拍板）

1. **用例 A**：写 `compaction-recipe` 插件（继承 CompactionEngine，~80 行）：固定模板摘要指令（只留决策/路径/错误/未决项）+ 小 retainTokens + 便宜摘要模型。替代方案=调 compaction-basic 的 modelPolicies（零代码，先试这个）。
2. **用例 B**：写 `rule-reminder` 插件（~40 行）：`ctx.on("agent/pre-step")` 计数，每 N 步追加一条短 user 消息（规则摘要 + `cat loop-state.json` 的 phase 字段）；N 和文案可配置。
3. 两个都是 **Cordis 原生插件**，不经过 hook 桥——桥的价值在复用 Claude Code/Codex 现成配置，本场景没有现成配置可复用。
4. 安装面：同 hooks-codex 问题，需 install_bundle（L2）或 profile 手动加包，待拍板。

## 8. 证据锚点

- 解包目录：`/Users/a1-6/Desktop/workspace/tmp/asar-preset/extract/`（25 文件）
- asar base=5559404；entries.json offset 为字符串需 int()
- 关键源码：dsh-hooks-codex/lib/index.js:193-272（5 个 ctx.on）；dsh-compaction-basic/lib/index.js:839-861（4 个 ctx.on）+ :292 summarizeWithLlm；dsh-compaction/README.zh.md（seam 三操作+标记对锁）；dsh-hooks-{codex,claude-code}/README.zh.md（事件表+延期清单）；dsh-web-app/presets/{standard,minimal,ptc,cordis}.patch.yml
- 前序：memory/plugin-approach-research.md（5 缝桥+assistant-stream 内部点+方案①）
