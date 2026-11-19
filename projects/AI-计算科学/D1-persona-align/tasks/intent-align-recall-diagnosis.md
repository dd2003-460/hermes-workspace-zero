# intent-align-recall 现状诊断 (r1)

> origin: ai | 2026-11-20 | 01-diagnose 产出 | 所有断言带出处

## 注入链路盘点（A）

### A1 inject-rules.py 便签注入 — 生效中
- 出处：config.yaml pre_llm_call 第 1 条（`agent-hooks/inject-rules.py`）
- 机制：常驻 4 条小便签（执行纪律索引/自问/安全/人话，515 chars）+ 随机轮询命中全文（autonomy 4-6 轮、source-trace 5-8 轮、fixed-round-check 5-8 轮）
- 生效方式：pre_llm_call 返回 context → 框架注入（本轮消息头可见 `[规则注入 · 常驻 + 本轮命中: ...]`）
- 已知问题：随机轮询 = 命中间隔内规则缺席（C3）

### A2 stop_hook 两条路径 — 一条生效一条死链
- **continue message（生效）**：pre_verify 返回值 `{"action":"continue","message":...}`，框架以 user-role nudge 注入当前回合（turn_stop_gates.py:53-80 `_pre_verify_nudge`）。已加来源标注（commit a8db8d1）。
- **INBOX（死链）**：stop_hook `_write_inbox` 写 `~/.hermes/.stage-gate/INBOX.md`，设计上是 auto_continue_hook.py 在 pre_llm_call 消费。
  - **发现（T1）**：auto_continue_hook.py 存在于 `stage_gate/adapters/`，但 **config.yaml 的 pre_llm_call 里没有注册它**（只有 inject-rules.py + hook.py 两条）。
  - 后果：INBOX 写入后无人消费，文件残留（当前 INBOX.md 内容停在 11-19 21:17）。stop_hook 注释里"auto_continue_hook 下一轮以模拟用户消息注入"是**设计意图，不是现状**。
  - 出处：config.yaml pre_llm_call 段（04:20 读取）；auto_continue_hook.py:13-14 自述。

### A3 proxy.mjs ZH tail — 已停用（本次乌龙真凶）
- 出处：`~/.claude-vllm-proxy/proxy.mjs:410-411`（ZH_THINK_TAIL 常量）+ `:610-628`（appendZhThinkingTail，11-20 起 `return false` 停用）
- 机制：作为**最后一条 user 消息**追加到 messages 尾部（注释：system 前/尾都无效，user 轮 3/3 稳定）
- **归因修正**：本会话反复出现的"（内部思考 thinking 必须全程用中文书写…）"user message，文本与 ZH_THINK_TAIL **逐字一致**——来源是 proxy，不是 stop hook（stop_hook 全文 grep 无此文本）。D 之前归因为 stop hook 不准确，实际是 proxy 层。
- 停用后残留风险：[残留] 中文思考原需求未解决（见缺口 6）

### A4 USER.md/MEMORY.md system 层 — 最稳定
- 出处：agent_init.py:1300-1339（persistent memory 从磁盘加载进 system prompt）
- 机制：每轮无条件加载，权重最高。中文规则曾在此层（11-16 加，11-20 03:56 移除，bak-remove-cn2-20261120）
- 已知问题：字符预算 95% 满（USER.md 1314/1375，MEMORY.md 2092/2200）——加新规则要挤旧规则

### A5 重复投递（D 报告的"发一次看到两次"）— 机制已定位，具体事件无法复现归因
- 出处：`plugins/platforms/weixin/adapter.py:747`（`MessageDeduplicator(ttl=300s)`）+ `:916-930`（`_process_message` 两层去重）
- 机制：① message_id 去重 ② 内容指纹去重（`content:{sender}:{md5(text)}`）。代码注释明说 iLink 上游会"用新 message_id 重发相同文本"，所以加了第二层。
- **实测（gateway.log）**：`Content-dedup` 命中 **0 次**。即内容去重从未拦截过任何一条。
- 推断（中置信）：若 D 观察到的重复真发生了，它绕过两层去重的唯一路径 = 上游重发时**文本内容有细微差异**（md5 不同，如带时间戳/格式/引用块），或那两条本就是 D 客户端发的两条不同消息（微信重发按钮/网络抖动）。
- 证据边界：04:18:26 与 04:18:33 有两条 7 秒间隔的 inbound（from=o9cq808x），但 gateway.log 只记 from/type 不记文本，无法确认是否同一条。要 100% 归因需开 weixin adapter 的 DEBUG 日志（`Content-dedup: skipping` 是 debug 级）复现一次。
- 处置：不改框架代码（红线：框架源码改动需 D 明令）。若 D 仍频繁遇到，最小动作 = 把 weixin adapter 日志级别调到 DEBUG 观察一次是否命中 content-dedup。

## 对齐提醒有效性（B）

### B1 审计日志 — 只有送达证据
- 出处：inject-rules.py:451-474（每轮 pre_llm_call 落 JSONL：注入规则/正文长度/sha1 + 模型上轮输出）
- 缺口：能证明"注入了"，不能证明"模型执行了"。B 类问题（注入后不跟）没有量化手段。

### B2 效力层级实证（本会话观察）
- system 层（USER.md）中文规则：稳定遵循（D 确认"唯一稳定"）
- 便签层：执行纪律 8 条索引每轮可见，但"值不值得走"这类软约束遵循率未知
- 尾部 user 轮（proxy ZH tail）：3/3 遵循（proxy 注释 10-24 实测），但身份伪装导致被当用户指令回"收到"
- 结论：效力 system > 便签 ≈ user 轮，但 user 轮有身份反噬副作用

### B4 bench 基线（T2 实测）
- 出处：`pfb/experiments/rule-injection-bench/results/`（8 runs，2026-11-20 03:00）
- A0（无注入）：T1 人话 mean=4.0/10, T2 安全 mean=7.0/10, T3 执行纪律 mean=10.0/10（n=2）
- A1（便签）/A2（全文）臂：**0 runs**——便签 vs 全文的效力差没有数据
- bench 可跑通（8787 连接正常，runner 纯 stdlib）

## 规则 recall（C）

### C1-C2 现象与机制假设
- 现象（D 报告）：召回不稳定，唯一稳定的是 USER.md 层规则
- 机制假设：system 层每轮加载 → 稳定；便签层条件/随机注入 → 命中间隔 = 规则缺席；索引层按需 read_file → 依赖模型主动想起
- [待核验] 三位置 A/B 实验未跑（C2），当前是假设不是结论

### C3 随机轮询的结构性缺口
- 出处：inject-rules.py:312（per-session 计数器，random 2-5 轮）+ routing.json 各规则 interval
- autonomy 4-6 轮、source-trace 5-8 轮 = 连续多轮无该规则。若任务恰好需要该规则，缺席 = 召回失败
- 这是"召回不稳定"的结构性根因之一（高置信：机制直接可推）

## 意图对齐（D）

### D1-D2 现有机制
- 出处：USER.md（偏好 13 条）+ qanda-ledger.md（问题台账）+ autonomy.md（自主决策）+ 自问便签（每轮）
- 机制：偏好靠 system 层常驻；"做对的事"靠 goal-template 优先级 + 自主决策两问标准
- 缺口（D3）：没有"主动做 D 会惊喜的事"的机制——D 原话（本会话）："做我想要的事情，或者会觉得惊喜的事情"

### D4 便签换位思考（D 提议）
- D 原话：便签改成"你知道我想要什么吗/做到哪了/接下来还有什么"，让便签驱动自主对齐
- [待核验] 可行性未实验。与 C3 的结构性缺口相关：把"随机轮询全文"换成"常驻换位思考便签"可能是更优解（待 A/B 验证）

## 缺口清单（更新）

1. ~~A5 INBOX 消费端~~ → **已定位**：auto_continue_hook.py 存在但未注册，INBOX 是死链（本诊断解决）
2. [待核验] A5' gateway 重复投递机制（D 报告的发一次看到两次）
3. [待核验] C2 三位置 A/B 遵循率基线（bench 只有 A0，A1/A2 未跑）
4. [待核验] D4 便签换位思考可行性
5. [残留] proxy ZH tail 停用后中文思考是否保持（原需求未解决）
6. [新] INBOX 死链处置：注册 auto_continue_hook（恢复设计意图）还是删掉 INBOX 写入路径（承认现状）？需 D 定夺或 02 设计时给推荐

## 改动候选（给 02-design 的输入）

| # | 问题 | 候选改动 | 回滚 | 验证 |
|---|------|---------|------|------|
| K1 | INBOX 死链 | 方案a: 注册 auto_continue_hook 到 pre_llm_call；方案b: 删 INBOX 写入（只留 continue message 一条路） | config.yaml 备份 / git | INBOX 文件是否被消费（mtime 变化）|
| K2 | 召回不稳定（C3） | 高频规则从随机轮询改常驻便签（autonomy/source-trace 便签化） | routing.json 备份 | bench A1 臂 vs A0 基线 |
| K3 | 便签效力未知（B4） | 跑 A1/A2 臂补齐对照数据 | 无（只加数据） | results/ 新增 run + score |
| K4 | 换位思考便签（D4） | 设计新便签文案 + 灰度（先替换一条随机规则观察） | routing.json 备份 | 观察 + bench |
| K5 | 中文思考残留 | 重新设计：不走 user 轮伪装，改 system 层短指令或接受现状 | proxy.mjs 注释里有恢复法 | 8787 直测思考语言 |
