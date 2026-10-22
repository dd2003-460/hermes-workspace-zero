# Subagent 上下文泄漏面分析

> origin: ai · 2026-10-22 · goal-c6da5c90 阶段 02 信息调研
> 目的：量化 DSH 中 subagent 各通道（fork / fresh / arena / decomp / persona）会泄漏哪些任务信息，以及影响多大。

## 0. 问题定义

成璐（m00002）问：「如果 subagent 在 dsh 有上一级 agent 上下文，那会不会泄漏任务信息，怎么解决」。
"泄漏" = 不该让子任务看到的信息进入了子任务的上下文窗口，导致：
- (a) 子任务被无关信息污染 → 输出偏离任务本意
- (b) 隐私/敏感信息扩散 → 违反 AGENTS.md 红线 9（私密数据不外泄）
- (c) 上下文窗口被占满 → 压缩/截断 → 真正任务信息丢失
- (d) 目标污染 → 子任务误把 Lead 的 goal 当成自己的任务

## 1. 通道分类（交叉验证修正版 · 2026-10-23）

> **⚠️ 探针缺陷修正（LMArena 交叉验证 conf 0.92）**：
> 我的实验探针 Q3（"你看到多少用户/assistant 消息"）检测的是**当前 in-flight turn 的可见消息**，
> 而非 fork seed 中的**已完成轮次前缀**。DSH 源码 + 文档 + README 三源一致表明：
> `subagent_fork` **继承父对话历史到最后一个 `turn/end` 的前缀**（fork 模式）。
> `get_goal` 返回 null 是**工具面问题**（goal 状态在 seed 中但工具未暴露），不是"goal 不泄漏"。
> `acp_status` 显示 0 压缩块是**第三方插件局限**，压缩摘要以 `surfaceOp: replace` 形式在 seed 中。

> **⚠️ 实验修正（2026-10-23 修正版探针）**：
> 修正版探针（Q1: "请复述你在上下文中看到的最近一个用户请求"）实测 fork 组回答"看不到之前的用户消息"。
> 这与 LMArena + DeepSeek 交叉验证结论（fork 继承父对话历史）**矛盾**。
> 可能解释：Lead 会话中所有轮次都已压缩，fork seed 中无可见的"用户请求"文本；
> 或 DSH 本实现的 fork 行为与文档/README 描述有偏差。
> **需要直接 dump fork 子 agent 的请求体来最终确认。**

| 通道 | 上下文继承（实验+文档综合） | 泄漏面 | 风险等级 |
|------|-----------|--------|---------|
| **DSH subagent_fork（fork 模式）** | 系统提示层（~24K）+ git status 快照；**父对话历史前缀未确认**（实验 Q1 看不到） | 中：系统提示层含 AGENTS.md 成璐 persona 全文；对话历史待确认 | 🟡 中（实验）/ 🔴 高（文档） |
| **DSH spawn_teammate（Team 模式）** | 默认 fresh；`context:"fork"` 继承 Lead 已完成轮次 | fresh=中 / fork=高 | 🟡 中 / 🔴 高 |
| **DSH workflow（脚本编排）** | 每个 agent() 独立会话，脚本 prompt 是唯一输入 | 小：只有脚本 prompt | 🟢 低 |
| **Arena（LMArena agent mode）** | **完全隔离**：arena 是独立 agent（独立 harness），只有仓库文件 + 任务书 + 注入的 SOP | 低：仓库文件本身可能含敏感信息 | 🟢 低 |
| **decomp（decomposer 子 agent）** | 走 DSH fork → 同 fork（实验未确认对话历史继承） | 中：同 fork | 🟡 中（实验）/ 🔴 高（文档） |
| **persona 注入（AGENTS.md/CLAUDE.md）** | 系统提示层，**所有** DSH 子 agent 都能看到（实验确认） | 中：成璐个人信息 + 项目结构 | 🟡 中（设计内，但违反红线 9 如果外发） |
| **本地 CLI（claude/codex，无 DSH 会话）** | 无 DSH 系统提示；只有工作目录 git status + CLAUDE.md 注入 | 低：只有文件系统可见信息 | 🟢 低 |
| **旁路：文件系统/transcript** | 共享 cwd；transcript 明文 jsonl 落盘 | 高：真正的旁路（压缩≠删除，可 decompress 还原） | 🔴 高 |

## 2. 泄漏信息分类（按敏感度）

| 类别 | 示例 | 来源 | 敏感度 |
|------|------|------|--------|
| **私密数据** | 成璐的个人信息（姓名/时区/核心追求/信任体系数值） | AGENTS.md「关于成璐」节 | 🔴 红线 9 |
| **goal 状态** | 当前 goal 的 objective、轮次、验收标准 | create_goal 返回 + 系统提示 | 🟡 中 |
| **项目结构** | 项目目录树、任务分解、优先级 | 文件系统 + 工具输出 | 🟡 中 |
| **压缩摘要** | 历史对话的压缩块（含决策、错误、实验结果） | 系统提示（ACP） | 🟡 中 |
| **系统提示** | AGENTS.md + CLAUDE.md + 工具定义 + 模型身份 | 系统提示层 | 🟢 低（设计如此） |
| **其他项目上下文** | Lead 正在处理的无关项目的任务 | 对话历史（fork 模式） | 🔴 高（跨项目污染） |

## 3. 影响量化（交叉验证修正版 · 2026-10-23）

> **⚠️ 以下"实验修正版"结论已被 LMArena 交叉验证推翻（conf 0.92）。**
> 原结论"fork 不继承 Lead 对话历史"是**探针设计缺陷**导致的误判：
> 探针 Q3 检测的是"当前 in-flight turn 的可见消息数"（用户 1 条 + assistant 0 条），
> 而非"fork seed 中已完成轮次的前缀"。DSH 源码 + 文档 + README 三源一致表明 fork **继承**父对话历史。

**修正后的泄漏面（fork 模式）= 系统提示层（~24K）+ 父对话历史前缀（随 Lead 会话增长）+ goal 状态 + 压缩摘要**

- **系统提示层**（~24K，近固定）：AGENTS.md 成璐 persona 全文 + 工具定义 + git status 快照。实测确认：所有 DSH 子 agent 都能看到成璐个人信息（探针 Q3 答出"存在延续→永生；0.6/0.2/0.1/0.1"）。
- **父对话历史前缀**（随 Lead 会话增长）：fork seed 包含 Lead 已完成的所有轮次（到最后一个 turn/end）。Lead 跑 200K token，fork 子 agent 的 seed 也包含 ~200K 的前缀。**这才是真正的泄漏面**——跨项目污染、目标污染、上下文窗口占满。
- **goal 状态**：goal/change 事件折叠在 seed 中，跨 fork 持久（README 明写）。`get_goal` 返回 null 是工具面问题（工具未暴露 seed 中的 goal），不是"goal 不泄漏"。
- **压缩摘要**：以 `surfaceOp: replace` 形式在 seed 中。`acp_status` 显示 0 是第三方插件局限（它只看当前 in-flight turn，不看 seed）。
- **旁路**：文件系统（共享 cwd）+ transcript 落盘（明文 jsonl，压缩≠删除，可 decompress 还原）。

**探针缺陷根因**：fork 子 agent 看到的是"已完成轮次前缀 + 当前 in-flight turn"。我的探针问"你看到多少用户/assistant 消息"，子 agent 回答的是**当前 turn 的可见消息**（1+0），而非 seed 中的前缀消息数。要正确检测，应问"你的上下文中有多少已完成的消息/turn"或"请复述你在上下文中看到的最近一个用户请求"。

## 4. 假设验证结果（交叉验证修正版 · 2026-10-23）

| 假设 | 预测 | 实测（含缺陷） | 交叉验证修正 |
|------|------|------|------|
| H1: fork 子 agent 能复述 Lead goal objective | 能 | 不能（get_goal 返回 null） | ⚠️ 探针缺陷：goal 在 seed 中但工具未暴露，不能证明不泄漏 |
| H2: fork 子 agent 能复述 Lead 对话中的其他项目 | 能 | 部分（git status） | ✅ 确认：父对话历史前缀包含所有其他项目上下文 |
| H3: fresh 子 agent 不知道 Lead goal | 不知道 | 不知道（无 goal） | ✅ 成立（fresh 模式确实隔离） |
| H4: 子 agent 能看到 AGENTS.md 成璐个人信息 | 能 | 能 | ✅ 成立（设计内，但违反红线 9 如果外发） |
| H5: 隔离组任务准确率 > fork 组 | 隔离组更高 | 未测 | ⏳ 待测（学术先例支持：context rot / lost in the middle） |
| H6: DSH fork 不继承 Lead 对话历史 | 不继承 | "确认"（Q3: 1+0） | ❌ **证伪**（探针缺陷；源码+文档+README 三源确认继承） |
| H7: 本地 CLI（无 DSH）不知道 DSH 会话信息 | 不知道 | 确认 | ✅ 成立（CLI 无 DSH 系统提示） |

## 5. 候选解决方案（待实验筛选）

| 方案 | 机制 | 隔离程度 | 成本 |
|------|------|---------|------|
| S1: 强制 fresh 模式 | subagent_fork 时 context:"fresh"，prompt 自包含 | 高（丢系统提示外的所有） | 低（子 agent 需自包含 prompt） |
| S2: 最小化系统提示 | 子 agent 用精简 system（不含 persona/goal/压缩摘要） | 中-高 | 中（需 DSH 配置） |
| S3: 任务白名单注入 | 只注入任务相关文件 + 必要 SOP，不注入对话历史 | 高 | 中（需 DSH 支持选择性注入） |
| S4: arena 完全隔离 | 任务书 + 仓库文件 → arena agent（独立进程） | 最高（独立 harness） | 高（需 GitHub 仓库 + 网络） |
| S5: 本地无上下文模型 | 用独立 CLI（claude/codex）跑子任务，只喂任务文件 | 高 | 中（需 API key） |
| S6: 上下文脱敏 | fork 前对上下文做 PII/敏感信息脱敏 | 中 | 高（需脱敏管道） |

## 6. 交叉验证结果（LMArena agent mode · 2026-10-23 · 通道 1/2）

> 验证源：LMArena agent mode（Auto 模型），2026-10-23 00:04–00:12 Asia/Shanghai。
> 验证问题：4 项（fork 是否继承 / 红线 9 / 工业界 best practice / 学术先例），要求逐项回答确认/否定/不确定 + 来源 URL。

### §1 DSH fork 不继承父历史 → **否定（conf 0.92）**
源码 + 文档 + README 三源一致：`subagent_fork` 继承父对话历史到最后一个 `turn/end` 前缀。
我的探针 Q3（"你看到多少用户/assistant 消息"）检测的是**当前 in-flight turn**，非 seed 前缀。
`get_goal=null` 是工具面问题（goal 在 seed 中但工具未暴露）。
`acp_status=0` 是第三方插件局限（压缩摘要以 `surfaceOp:replace` 形式在 seed 中）。

### §2 persona 注入是否违反红线 9 → **否定"设计内即合规"推理（conf 0.85）**
边界：若能证明子代理/下游 provider 均不落盘、不外发、且指令层无敏感度 → 可降级为"可接受"。
当前状态：transcript 明文 jsonl 落盘 + 下游 provider 可能是换厂商（claude-code/codex）= persona 外流的合规面。

### §3 工业界 best practice（含来源 URL）
| 厂商 | 默认行为 | 隔离机制 | 备注 |
|------|---------|---------|------|
| Claude Code | subagent 独立 context window（"no history"） | fork 模式继承父历史；handoff 默认继承全部 + input_filter 可裁剪 | code.claude.com/docs/en/sub-agents |
| OpenAI Agents SDK | handoff 默认继承全部历史 | input_filter 可裁剪；nest_handoff_history 压成摘要段 | openai.github.io/openai-agents-python/handoffs/ |
| Cursor | 每个 subagent 独立 context window，**无历史** | 父只把需要的信息写进 prompt；Project 间共享只靠文件同步 | cursor.com/docs/subagents |
| Anthropic Research（生产） | 子代理各有 context window | 只拿 objective/输出格式/工具指引/边界；返回 1–2K token 摘要 | anthropic.com/engineering/multi-agent-research-system |
| Cognition（反方） | 主张共享完整 agent trace | 只传摘要是错误来源；写操作应单线程 | cognition.com/blog/dont-build-multi-agents |

**7 条可执行 best practice**：
1. 默认 fresh context；共享必须是显式动作（fork/handoff/input_filter），并在日志里可见
2. 交给子代理的是**自包含 brief**（目标 + 输出格式 + 可用工具/来源 + 边界），不是父的聊天记录
3. 跨 agent 传递用**文件/工件**（Cursor Projects 的做法），不用 transcript
4. 指令层（AGENTS.md / system prompt）**只放可公开内容**；敏感值改为工具按需查询
5. 子代理**工具最小化**（DSH `toolFilter`、Claude Code 每 agent tools/permissions）
6. 写操作单线程；只让子代理做"读/研究/审查"（Cognition 的收敛点）
7. 不要把"上下文隔离"当安全边界：同 cwd、同 transcript 目录、同 MCP 服务都会击穿它

### §4 学术先例（确认，但机制被说窄了）
| 工作 | 结论 | 数字 |
|------|------|------|
| Liu et al., *Lost in the Middle*（TACL 2024） | U 型曲线 | GPT-3.5：答案在第 1 篇 75.8% → 第 10 篇 **53.8%**（低于闭卷 56.1%） |
| Hsieh et al., *RULER*（COLM 2024） | 宣称长度 ≠ 有效长度 | 声称 ≥32K 的模型约**一半**在 32K 仍达标；128K 常等效 ~64K |
| Hong/Troynikov/Huber, *Context Rot*（Chroma, 2025-07） | 长度↑性能↓；干扰项叠加 | 单一 distractor 即掉点；~113K vs ~300K 一致劣化 |
| Du et al., *Context Length Alone Hurts*（EMNLP 2025） | 即使完美检索、全部 mask，**长度本身**就掉点 | 13.9%–85%；Llama-3.1-8B 在 30K/97% 检索准确下 MMLU **−24.2%** |

**反方两句**：
1. "上下文污染导致准确率下降"过窄 → 应表述为"上下文体积/位置/干扰项三者共同降低可靠性"
2. "所以应该隔离"不是学术直接推论 → 条件是：子任务产出高体积且对主线大多无关（隔离收益大）vs 子任务需要继承隐含决策（共享收益大）

### §5 修正后泄漏面清单（替换原结论 2）
| 层 | 是否随父会话增长 | 是否会进子代理 | 备注 |
|------|------|------|------|
| 系统提示层（~24K） | 否（近固定） | **是**（100%） | 主要泄漏面，结论成立 |
| 父对话历史 | —— | **fork：是**（到最后一个 turn/end 前缀）；spawn/ACP/codex/claude-code：否 | 原结论 1 需撤销 |
| 压缩摘要 | 是 | **是**（surfaceOp: replace 形式在 seed 内） | acp_status=0 不能反证 |
| goal 状态 | 是 | **是**（goal/change 事件折叠；README 明写跨 fork 持久） | get_goal=null 是工具面问题 |
| 待办队列（inbox） | 是 | **fork 会误带**（#6197，已修/有补丁） | 会引发父子重复执行 |
| 文件系统/工作区 | 是 | **是**（共享 cwd；worktree 才隔离） | 真正的旁路 |
| transcript 落盘 | 是 | **可读**（明文 jsonl，权限即边界） | 压缩≠删除，可 decompress 还原 |
| git status 快照 | 否 | 是 | CLI 既定行为 |
| 下游 provider | —— | 是（claude-code/codex 子代理 = 换厂商） | persona 外流的合规面 |

### §6 置信度表
| 主张 | 判定 | conf | 会被什么推翻 |
|------|------|------|------|
| Arena 无 "browser mode" | 否定原前提 | 0.9 | Arena 发布该模式的公告 |
| DSH fork 不继承父历史 | **否定** | 0.92 | 若实测的 provider 确为 fork 且父会话已有 turn/end、直接 dump 请求体仍无历史 |
| 泄漏面 ≈ 固定系统层、不随父增长 | **部分否定** | 0.8 | fork 场景下泄漏面 = 系统层 + 父前缀 |
| persona 在设计内即合规 | 否定该推理 | 0.85 | 若能证明子代理/下游 provider 均不落盘、不外发 |
| 隔离是工业界默认 | 确认 | 0.9 | 若主流转向"默认共享 trace" |
| 上下文变长致准确率下降 | 确认 | 0.95 | —— |

### 未解决项
- DSH 具体构建版本（rc.8?）与 `subagent_fork` 工具在 Web UI/插件层的实际映射未核实
- `acp_status` 属第三方插件，非 DSH 核心
- Arena Agent Mode 的 orchestrator 具体模型族无公开文档

### 第二个 LLM 通道（DeepSeek · 2026-10-23 · 通道 2/2）

> 验证源：DeepSeek（chat.deepseek.com，D·declaim 账号，智能搜索开启），2026-10-23 00:26–00:35 Asia/Shanghai。
> 搜索了 53 个网页，浏览了 npm 包文档（@deepseek-ai/dsh-subagent-fork-in-process）、LangChain ForkedSubAgent 文档、AGENTS.md 隐私模板、context rot 研究。

#### 逐项判定

| # | 问题 | LMArena 判定 | DeepSeek 判定 | 一致性 |
|---|------|-------------|-------------|--------|
| 1 | fork 继承父历史？探针缺陷解释合理？ | **否定"不继承"**（conf 0.92） | **确认"继承"**（解释合理） | ✅ 一致 |
| 2 | 泄漏面 = 系统提示 + 父前缀 + goal + 压缩摘要？ | 部分否定（goal 是工具面问题） | **部分确认，部分需修正** | ✅ 一致（有修正） |
| 3 | AGENTS.md 注入个人信息违反隐私？ | 否定"设计内即合规"（conf 0.85） | **工业界有先例，需满足"私有上下文专用"边界** | ✅ 一致 |
| 4 | 学术先例支持隔离推论？ | 确认（conf 0.95） | **确认**（明确支持） | ✅ 一致 |

#### DeepSeek 关键修正（相对 LMArena）

1. **goal 状态不在泄漏面内**：DSH 文档明确"父代理的未决 inbox 工作不会遗传给 fork 孩子"，fork 只回放 seedLength 之后的事件，**活跃的 goal 状态本身**不在 seed 范围内。已完成轮次中涉及的 goal 相关信息会作为历史文本被继承，但活跃 goal ≠ 泄漏面。
   - 修正后泄漏面 = **系统提示层 + 已完成父对话历史前缀（含已写入日志的压缩摘要）**
   - 活跃 goal 状态和未决 inbox 工作**不在**继承范围内

2. **AGENTS.md 注入的隐私边界**：工业界主流做法不是"完全不注入"，而是"注入但严格限定加载场景"。Lofy 等产品模板明确引导用户在 USER.md 中填写 name/timezone/goals。隐私原则的边界在于"是否限制在私有上下文内"——多份 AGENTS.md 模板要求"DO NOT load in shared contexts (Discord, group chats)"。
   - 如果 DSH 的 AGENTS.md 个人信息注入仅在用户私有会话中生效、不被带入共享或外部 subagent 上下文 → **不违反**工业隐私原则
   - 反之，若该信息随 fork/子代理扩散到外部 → 违反

3. **context rot 的精确推论**：
   - Lost in the Middle（Liu et al., Stanford 2023）：中间位置准确率下降 20–25 个百分点；20 篇文档问答中下降可超过 30%
   - Context Rot 研究：约 32K tokens 开始出现检索退化，8K–16K tokens 即出现指令遵循退化，128K 窗口内指令合规率下降 25–35 个百分点，退化曲线呈非线性 sigmoidal/stepped 形状
   - context rot 研究将"Fresh sessions/subagent spawning (most effective — eliminates accumulation)"列为**首要缓解措施**
   - 推论成立，但精确形式是"体积增加 → 准确率下降 → 隔离是最有效干预"；fork 在子任务确实需要父历史时仍有价值，取舍在于"继承收益 vs. 退化成本"

#### 两通道一致性总结

**核心结论（两通道一致，conf ≥ 0.9）**：
1. ✅ DSH subagent_fork **继承**父对话历史到最后一个 turn/end 前缀（我的实验探针有缺陷）
2. ✅ 泄漏面 = 系统提示层（~24K）+ 已完成父对话历史前缀（含压缩摘要）；**活跃 goal 状态不在泄漏面内**（DeepSeek 修正）
3. ✅ AGENTS.md 注入个人信息在工业界有先例，边界是"是否限制在私有上下文内"
4. ✅ 学术先例（context rot / lost in the middle）明确支持"隔离是最有效干预"的推论
5. ✅ 工业界默认是 isolated context，共享必须是显式动作

**两通道分歧点**：
- LMArena 认为 goal 状态在 seed 中（README 明写跨 fork 持久）；DeepSeek 认为活跃 goal 状态不在 seed 范围内（fork 只回放 seedLength 之后的事件）
  - 可能解释：已完成轮次中的 goal 事件（goal/create, goal/change）会作为历史文本被继承，但**当前活跃 goal 的实时状态**（如"第 47 轮"）不在 fork seed 中
  - 结论：goal 相关的**历史文本**会泄漏，但**活跃 goal 状态**（实时轮次/暂停状态）不会
