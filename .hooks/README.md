# memory-hooks — 模型外置记忆/提醒引擎

# origin: ai（设计对齐 m00002 成璐提问：hook 防遗忘 + 触发点设计）

## 一句话
固定引擎（engine.py 不改）+ 模型可写数据（rules.json / anchors.json）；模型"写数据"而非"写代码"，触发逻辑由引擎解释。hook 只负责**提醒，不判断**——判断仍由模型做。

## 触发点（5 个拦截缝，来自 DSH 原生 seam，经 @deepseek-ai/dsh-hooks-codex 桥接）

| seam | 时机 | 能看到的 payload 字段 | 能做的事 | 适合什么触发 |
|------|------|----------------------|----------|--------------|
| SessionStart | 会话开始 | 基础字段（detach 执行，可能错过首请求） | 加上下文 | always（会话定向） |
| UserPromptSubmit | 每条新用户消息进入前 | **prompt 全文** + 基础 | 注入提醒 / 拒绝 prompt | 语义/关键词/向量（主战场） |
| PreToolUse | 工具执行前 | tool_name + **tool_input（command/file_path/path）** | **只能 deny 阻塞**（此缝忽略 additionalContext） | 不可逆命令保护 |
| PostToolUse | 工具执行后 | 同上 + **tool_response** | 阻塞结果+反馈 / 注入提醒 | 结果异常检测 |
| Stop | 模型想停止时 | turn_id 等（**last_assistant_message 恒 null**） | deny = steer 强制再走一步（付一次完整请求） | 代理指标兜底 |

基础字段：session_id / transcript_path（**恒 null**，两桥皆然）/ cwd / hook_event_name / model / permission_mode；turn 级事件加 turn_id。

## 触发谓词（trigger 是数组，OR 级联短路，便宜的放前面）

| type | 字段 | 说明 |
|------|------|------|
| always | — | 恒真 |
| keyword | any / all / regex / case_insensitive / max_len / min_len | 文本匹配。匹配文本按缝自动选：UserPromptSubmit=prompt；Pre/PostToolUse=tool_name+tool_input+response |
| metric | field / op / value | 状态账本指标：tool_calls_this_turn / tool_calls_total（跨事件累积，见 state/ 账本） |
| lexicon | min_hits / domain? | anchors.json 锚关键词 distinct 命中数 >= min_hits（best domain 取胜）；短中文比 vector 可分（D4 实测：256 维 char 3-gram 哈希余弦噪声 0.22 > 信号 0.14，不可用；vector 槽位保留给将来真实 embedder） |
| vector | threshold / domain? | 离线特征哈希余弦（char n-gram→256 维，anchors.json 定义）；免费、无网络；阈值需按 stderr 调试值校准 |
| judge | judge_cmd / expect / timeout | 外部 LLM 裁判（stdin 给文本，stdout 以 expect 开头=触发）；默认不启用，要烧 token 时才上 |

三级级联（便宜→贵）：metric/keyword → vector → judge。这就是"不同领域任务怎么判断和触发"的答案：硬指标用 metric，模式用 keyword，语义用 vector/judge，hook 永远只提醒。

## 诚实约束（v0 边界）
1. **command hook 测不到 thinking token 数**（无 usage 字段、transcript_path 恒 null）→"思考>1k"只能实现为：①UserPromptSubmit 主动式 L0 分类（省在思考开始前）②Stop 用 tool_calls_this_turn 代理指标兜底。精确测量需写**原生 DSH 插件**（完整 harness API，未验证，低 conf）。
2. PreToolUse 的 tool_input 桥接只提取部分参数（command/file_path/path）；非 shell 工具的结构化参数可能为空。
3. 规则文件每次事件实时读（子进程启动读）→ 改规则无需重启；hooks.json 的 seam 接线才是进程级（改它要重启会话/插件）。
4. 每次 inject 都是追加式上下文（付 token，不破坏 KV 前缀）→ 必须配 cooldown_turns 防成本失控。Stop 的 deny = 强制 continuation = 一次完整模型请求，最贵，阈值调高。
5. 硬阻塞会跟弱模型死锁（事故先例：loop/ralph_runtime/DECOMPOSITION-REDESIGN.md:6，8+ invalid-agent-output 死循环）→ 提醒类一律 soft（inject），只有不可逆操作保护用 deny；出现死循环就把 deny 降级为 inject。

## config（全局数字配置，数字单点维护）
rules.json 顶层 `config`；inject/deny 文本用 `{key}` 引用配置键（缺键原样保留）。
例：`config.thinking_budget_tokens: 512` → `thinking-budget-frame` 规则注入"本会话思考预算 512 tokens"。改预算 = 改这一个数字，改完即生效。

## 文件
- engine.py — 固定解释器（勿改逻辑；扩展谓词类型才动它）
- rules.json — 规则 + 顶层 config（模型直接编辑）
- anchors.json — 领域锚库（模型直接编辑；加新领域 = 加一个 domain）
- state/ — 每会话账本（A4 观察：hook 触发记录/工具调用计数，可审计）
- ../.codex/hooks.json — 5 缝接线（DSH codex 桥 configPath 指向它）

## 调试
`HOOK_DEBUG=1 python3 .hooks/engine.py <Seam> < payload.json` → stderr 看每条谓词评估；触发记录在 state/<session>.jsonl。
