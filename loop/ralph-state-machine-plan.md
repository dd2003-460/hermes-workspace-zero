# RALPH 状态机实施计划

> origin: ai
> human intent: 先让 Prompt 动作可稳定复现，再逐层接入状态、日志、DAG 和 Hook。
> status: implementation

## 目标

分四层验证 RALPH：

```text
Prompt 动作复现 → loop-state.json 状态转换 → Hook 工具控制 → Claude Code 并行实验
```

本计划保留 `loop/1-loop/00-综述.md`、现有 `R1-D*` 详细模板和 `loop/1-loop/templates/`。不修改 `AGENTS.md`，不删除旧探索过程。

## 当前实现顺序

1. 最小 `python-statemachine` 节点机：固定顺序节点 `01`～`06`、探索任务接续、阻塞跳过和显式完成兼容。
2. 结构化 Prompt 动作协议：`advance`、`rollback`、`blocked_human`、`skip_blocked`、`candidate`、`explore`、`dispatch`、`join`、`repair_prompt`。
3. 固定 fixture 重放，验证同一状态和同一输出得到同一状态分支。
4. `loop-state.json` 持久化适配层。
5. Markdown 事件日志、DAG、候选任务、PreToolUse/Stop Hook 和真实 Claude 实验。

## Prompt 动作协议

Agent 必须输出可解析的结构化结果：

```json
{
  "action": "advance",
  "status": "passed",
  "stage_id": "02",
  "revision": "r1",
  "next_stage": "03",
  "rollback_to": null,
  "evidence": [],
  "artifact_refs": [],
  "message": ""
}
```

自然语言不要求逐字一致；状态机只接受经过协议验证的动作。

## 状态与编号

- 项目唯一运行状态：`<project-root>/loop-state.json`。
- 普通 Prompt 阶段只使用 `01`、`02`、`03` 等顺序编号。
- `r1`、`r2`、`r3` 表示同一阶段重新进入，不限制计划修订次数。
- `T1.1`、`T1.2` 表示任务图节点；`J1` 表示 Join 节点。
- 人类阻塞任务标记 `blocked_human` 后跳过，不阻塞其他任务。
- 探索是额外控制阶段：先扫描当前项目 `tasks/TASKS.md` 和 ready 队列，有可执行任务时优先接取已有任务并从 01 重新开始。
- 没有可执行任务时，探索输出 `preference_brief` 和带有 `candidate` 标记的候选任务；候选不得被静默执行，只有明确批准后才能作为新任务进入 01。
- `ralph task-next <project>` 是只读扫描命令；结构化探索动作通过校验后才会 claim 任务板，并写入 `task_intake`、`task_intake_history` 和事件日志。

## 后续层

### 事件日志

使用 `loop-events.md`。每个事件包含严格的 `RALPH_EVENT` JSON 区块、Agent 输出摘录、验证结果和 artifact 引用。隐藏思维过程不记录。

### DAG 与并行

同一并行层级必须正交、输出不冲突、可独立验证；不同层级必须声明输入、输出、前置条件、后置条件和 Join 规则。

### Hook

PreToolUse 依次判断角色权限、当前阶段策略、具体工具和路径；Stop Hook 读取 `last_assistant_message`，自动解析并 apply 合法的 `RALPH_STAGE_RESULT`，非法结果返回修复 Prompt。受控会话只允许一个 Stop 循环拥有者。

## 实验记录

每次实验记录 Prompt 版本、状态文件、原始 Agent 输出、期望动作、实际动作、状态差异和失败原因。真实项目接入前必须通过 fixture 重放、非法动作保护、状态恢复和 Shadow Hook 实验。

## 决策变更

| 日期 | 决策 | 原因 |
|---|---|---|
| 2026-07-15 | 先实现最小状态机节点和 Prompt fixture，不先铺完整 Hook/DAG | 优先验证 Agent 是否能稳定复现动作 |
| 2026-07-15 | `ralph run` 对已完成项目开启新运行时从 `01` 重置，并保留 `run_history` 摘要 | 旧项目可能是状态机接入前的跳步产物，继续把输入交给终态会造成 Hook 空转 |
| 2026-07-15 | Prompt 的 `next_stage` 必须来自节点 `on_success`，并禁止只回复 `READY` | 真实本地 Claude 实验暴露了硬编码 `03` 和非结构化终止输出 |
| 2026-07-15 | 不按字面无限拆词；按决策语义拆到“确认/追问/假设/研究”叶节点 | 既要求主动发现隐藏属性，又避免 Prompt 陷入无穷语言分析 |
| 2026-07-15 | 01/02/04 强制派发边界化审计子代理；03 只允许批准任务卡派发 | 防止 Commander 跳过澄清/DAG 直接启动 deep-research |
| 2026-07-15 | `deep-research` 只作为广覆盖候选事实发现，04 引入 claim ledger 核验 | 深搜覆盖面有价值，但其自然语言报告不能自动成为事实或最终推荐 |
| 2026-07-15 | Hook 授权使用阶段、工具、任务卡 ID、生命周期和字段契约，不用 Agent 名称或语义关键词猜测 | 关键词匹配无法可靠判断任务边界或语义正确性 |
| 2026-07-15 | 每个 01～06 阶段均须有有界上下文的独立门禁；03 在全部 DAG 节点完成后再生成 Join 门禁 | 避免主 Agent 自我确认，同时避免“完全无输入”导致无法判断输入输出关系 |
| 2026-07-15 | 每阶段生成固定 `submission-template.json`，通过时必须填写 `payload.stage_review` | 让结构化协议成为可复制填写的接口，而不是要求模型从自然语言记住字段 |
| 2026-07-15 | 任务卡只在 `SubagentStop` 收到带 `<RALPH_GATE_REVIEW>` 的合法回执后完成 | foreground Agent 的自然语言结果不能证明独立门禁通过，曾造成错误 completed |
| 2026-07-15 | 为 `blocked_human` 提供完整专用模板，最终 Prompt 不再展示精简 JSON | 本地模型会优先复制最后的短模板，导致漏掉 01 所需的 `payload.questions` |
| 2026-07-15 | `recover-card` 只能恢复没有有效 gate receipt 的错误终态 | 中断或旧 Hook 缺陷不能静默满足阶段 Guard，同时保留旧 agent ID 作为证据 |
| 2026-07-15 | 事件重放恢复会话输入和任务卡生命周期 | 仅重放阶段动作不能在中断后恢复完整当前上下文 |
| 2026-07-15 | 聚合脚本即使本身无可执行位也由 `ralph-sync.sh` 通过 Bash 调用 | `-x` 检查会静默跳过 ACTIVE 面板更新，破坏中断后的状态可见性 |

| 2026-07-16 | 06 后固定进入探索尾节点，优先扫描并接取项目 `tasks/TASKS.md` 中的 ready/pending 任务 | 让完成一个任务后可以自动接续已有任务；没有 ready 任务时才输出偏好简报和 candidate，避免流程终止或静默创造任务 |
| 2026-07-16 | oMLX 运行时错误不再进入普通字段修复循环；Stop Hook 记录 `runtime_interrupted` 并允许安全停止 | 实际日志显示 71,805-token prefill 触发 memory guard；完整恢复 Prompt 会增加原会话上下文，必须从持久化状态开短上下文恢复 |
| 2026-07-16 | 保留 oMLX tiered/SSD cache，不把 `aggressive` 作为默认修复 | 日志确认 32 个缓存 block、65,536 tokens 已成功恢复；失败点是活跃请求的 prefill 峰值和 `No idle model evicted`，不是 SSD cache 被关闭 |
| 2026-07-16 | RALPH 受控会话记录 `PreCompact`/`PostCompact`，并把当前设备的默认主动压缩目标下调到约 32k | 自定义模型可能按默认 200k 窗口计算；最新日志显示 41,472-token prefill 已超过 balanced 安全上限，64k 作为默认目标偏晚；压缩 Hook 只观察，不阻止恢复路径 |
| 2026-07-16 | 01 阶段增加“需求分流闸门”和 `inferred` disposition；只有四条件同时满足才向人类提问 | 旧提示虽然允许假设，但没有阻止模型把未单独命名的字段都变成选择题；GPU/硬件、云服务角色和模型档位应优先从输入、环境、研究或场景推导 |
| 2026-07-16 | `dispatched` 明确为内部等待状态；禁止重复派发、用 Agent/Write 生成运行时契约，并禁止 Commander 全量读取 `loop-events.md` | 真实运行中重复派发被正确拒绝后，模型尝试绕过 Write 并反复读取事件日志；这会造成工具循环和上下文/KV cache 膨胀 |
| 2026-07-16 | `recover-card` 默认不触碰 `dispatched`；只有确认旧进程退出且没有 `SubagentStop`/有效 gate receipt 时，才允许显式 `--force-dispatched` 恢复为 `pending` | 防止把仍在运行的子代理误判为 stale，同时为旧会话残留 agent_id 提供可审计的恢复路径 |
| 2026-07-16 | 新 `ralph resume` 在状态快照已列出 pending 卡时，下一次工具调用直接派发指定 Agent；不再同时要求先 Read 状态文件 | 实验显示“先 Read”与“立即 Agent”会形成提示冲突，模型会回到读取/规划循环 |
| 2026-07-16 | 用“我需要跑本地 AI，帮我调研性价比最高的 GPU”作为最小完整分解基准；同时验收语义覆盖、结构化协议和独立审计生命周期 | 简单输入仍应展开背景、目标、约束、比较维度、交付物和不确定性；不能用自然语言看起来完整替代可验证 task_spec |
| 2026-07-16 | 真实实验的第一动作闸门改为 pending auditor 时必须先派发指定 Agent | 第一次实验先调用 `deep-research`/AskUserQuestion，未形成结构化 task_spec；反馈后第二次实验成功派发 auditor，并由独立审计返回 `rollback`，证明空结构不会被误判为通过 |
| 2026-07-16 | 阶段 01 的 auditor 返回 rollback 后增加受控 `clarify` 动作；它只写回完整 task_spec、递增阶段 revision 并重新生成 auditor，不直接进入 02 | 真实 GPU 项目停在 `01-r1` 的根因是 rollback 之后没有合法的结构化写回路径，Commander 于是尝试 Write、AskUserQuestion 和重复读日志 |
| 2026-07-16 | 任务卡生命周期改为终态单向；迟到的 PostToolUse 不得把 `completed`/ `failed` 改回 `dispatched` | 真实事件中 gate 已收到合法 rollback 回执，随后 PostToolUse 又写入 dispatched，造成状态与事件矛盾和等待死锁 |
| 2026-07-16 | 新增 `ralph loop` 外层监督器；每轮 Claude 退出后从持久化状态开新上下文，并自动回收本轮残留 dispatched 卡 | Stop Hook 能保护当前进程，但无法复活 API reset、memory guard、终端关闭或无响应后已经退出的 Claude；持续性必须由外层进程承担 |
| 2026-07-16 | 同一 Claude 上下文连续 3 次阶段协议失败后释放上下文；重复 Stop Hook 也计入失败预算 | 仅看文件活动会把“持续写 rejection 事件”的格式循环误判为进展，必须交给外层监督器换新上下文 |
| 2026-07-16 | 当前阶段有必派 pending 卡时，Commander 的第一工作工具只能是指定 Agent；允许 `ralph ...` 控制命令作为诊断例外 | 实验中 Prompt 已要求立即派发，但 Hook 仍允许先 Read，导致模型重新规划和读取循环 |
| 2026-07-16 | dispatched 子代理遇到重复 Stop Hook 时保留卡状态，不解析 Commander 的旧结果；阶段输出按 `loop-artifacts/stages/<stage>/<revision>/` 归档，并提供 `ralph validate --result [--apply]` | 把进程存活、子代理生命周期、阶段结果校验和状态写回分开，避免旧消息触发假修复，同时为文件化提交提供机械校验入口 |
## 实施记录

- 已实现 `scripts/ralph_runtime/` 最小 Python 运行时。
- 已使用 `python-statemachine` 3.2.0 实现固定节点机和合法转换。
- 已实现结构化 Prompt 动作协议、Prompt 哈希、修复 Prompt 和 fixture 重放。
- 已实现 `loop-state.json` 初始化、迁移、原子写入和动作应用。
- 已实现 `loop-events.md` 事件追加、Agent 输出摘录、完整输出 artifact 和事件重放。
- 已增加一条命令启动入口：`ralph run "任务描述"` 自动从 workspace 匹配或创建项目；`ralph run <project> "任务描述"` 保留显式路径模式。
- 已支持旧版 `.claude/ralph-loop.local.md` 迁移到项目 `loop-state.json`，并让启动命令加载 `user,project,local`，保留用户本地模型配置。
- 已实现 DAG 环检测、依赖检查、并行组正交键和写入冲突检查。
- 已实现 Hook Shadow/Enforce 纯函数和项目级 settings 安装。
- 已实现 Stop Hook 自动 apply、字段/状态失败修复提示和重复输出幂等保护。
- 已实现已完成项目的新运行重开：旧完成运行摘要写入 `run_history`，新运行从阶段 `01` 开始；`ralph start` 仍保持原阶段。
- 已修正 Prompt 的动态 `next_stage`，并增加 `--effort` 选项以控制本地 Claude 的推理开销。
- 已完成独立虚拟环境部署和 42 个本地测试。
- 已完成真实本地 Claude 终端实验：PTY 交互可用，非法 `READY` 被记录并触发修复提示；随后合法 `advance(01→02)` 被 Stop Hook 自动应用，`loop-state.json` 更新为阶段 `02`，事件日志和 artifact 均生成。
- 已实现 `contracts.py`：阶段契约、规范 `task_spec`、项目内 task card 文档和指定 Agent prompt 标记。
- 已实现 01 的语义属性矩阵与一次性问题包字段校验；一个属性达到确认、追问、假设或可验证研究任务时停止继续拆分。
- 已实现 02 的 DAG/任务卡字段校验；通过后自动为 ready 节点生成 03 任务卡。
- 已实现 04 的 claim ledger 字段校验：关键事实必须带来源、来源类型、复核者和核验状态。
- 已实现 PreToolUse 拒绝裸 Agent、PostToolUse/SubagentStop 更新子代理卡生命周期、UserPromptSubmit 将人类补充写回规范任务输入。
- 新受控会话默认使用 `enforce`；可显式使用 `--mode shadow` 做诊断。
- 已新增阶段契约回归测试；运行时测试总数为 49。
- 已将阶段门禁扩展到 `01`～`06`：审计代理只获得 `stage-input-package.json`、阶段契约与提交模板；主对话与隐藏推理不进入其上下文。
- 已新增 `submission-template.json`，并要求每个 advance 填写独立 `stage_review`；03 的全部 DAG 节点完成后会自动生成 `execution-join-auditor`。
- 已将运行时回归测试扩展至 52 项。
- 已接入 `SubagentStart`：批准任务卡在子代理启动时绑定 `agent_id` 并注入边界；已绑定 worker 的工具调用按任务卡白名单和可读文件再次拦截。
- 已改为只有 `SubagentStop` 的合法 `<RALPH_GATE_REVIEW>` 回执才能完成阶段门禁；无标记、缺字段或不合格回执保持 `dispatched` 并返回修复提示。
- 已新增 `ralph recover-card <project> <card-id> --reason ...`，用于恢复没有有效门禁回执却被错误标为 `completed`/`failed` 的卡；已在金融项目的旧错误终态上实际使用。
- 已将完整 `submission-template.json` 与 `blocked_human` 专用 JSON 模板同时放入最终 Prompt，防止模型只复制省略 `payload` 的短结构。
- 已扩展事件重放：会话任务、人类补充、任务卡派发、绑定、完成、失败和恢复都会重建；已用金融项目真实日志对比当前阶段、任务输入、卡状态、旧 agent ID 与恢复次数，结果一致。
- 已修复 `ralph-sync.sh` 对非可执行 `aggregate-active.sh` 的错误 `-x` 判断；ACTIVE 面板现已显示金融、人格提取和 LaTex 项目。
- 已完成金融项目真实 Claude Code Hook 试验：旧子代理未返回门禁 JSON，控制器发现并安全回退；后续 9B 与 3B 本地模型在 Claude Code 工具上下文中长时间未开始新的工具调用，因此主动中断，不把无响应误当作阶段完成。三个项目均保持 `01-r1`、门禁卡 `pending`。
- 当前运行时回归测试共 63 项，全部通过；Python 模块编译、任务板扫描和探索接续 Smoke Test 均通过。
- 已加入 Markdown 任务板接续：金融任务 F1-F5、LaTeX 任务 L1-L4；`ralph task-next .` 只读选择最高优先级且依赖满足的任务，结构化探索通过后才 claim。
- 已将 Stop Hook 的正常继续和协议修复改为有界短恢复 Prompt；完整阶段 Prompt 不再在 Stop 响应中重复注入。
- 已识别 API/连接/超时/oMLX prefill memory guard/OOM，事件只保存有限错误摘要；状态不推进、不回滚，允许会话安全退出。
- 已新增 `ralph resume <project>`：不使用 Claude `--continue`，从 `loop-state.json` 开启新上下文，避免重复提交超大 transcript。
- 已加入运行时中断、短恢复 Prompt 和 Stop Hook 回归测试；当前运行时回归测试共 77 项，全部通过；模块编译和 CLI `resume` 帮助检查通过。
- 已为 `ralph run`、`ralph start --launch` 和 `ralph resume` 注入项目级自动压缩预算：当前默认 `40000 × 80% ≈ 32000` token，可通过 CLI 或 `RALPH_*` 环境变量调整，不修改全局 Claude 配置；有足够内存时可显式调回约 64k。
- 已安装项目级 `PreCompact`/`PostCompact` Hook；它们把压缩开始、完成、触发类型和有限摘要写入 `loop-events.md`，并保持压缩永不被 RALPH 阻塞。
- 已更新 01 阶段 Prompt、requirements-auditor 任务卡和协议：支持 `inferred`，并要求按证据优先级、影响程度和场景覆盖能力筛选问题，避免把可推断信息重复问给人类。
- 已加入有界事件诊断：`ralph events <project> --tail N` 只返回有限摘要；Commander 全量 Read `loop-events.md` 会被 enforce Hook 拒绝；PostToolUse 工具响应在写入日志前截断。
- 已把任务卡生命周期和运行时物化边界写入阶段 Prompt、项目模板和阶段契约：`dispatched` 只能等待 `SubagentStop`，不能伪装成 `blocked_human` 或通过 Agent 绕过 Write 限制。
- 已实现 stale `dispatched` 卡的显式 `--force-dispatched` 恢复保护；真实 GPU 项目已确认旧进程退出、无有效 gate receipt 后恢复为 `pending`，并用新上下文成功重新派发 auditor。
- 已将新上下文的 pending-card 首动作、Commander Bash 拒绝提示和只读 Worker gate 输出做成明确反馈；真实本地实验已验证 `pending → Agent allow → dispatched`、Stop 等待和 Worker 工具边界。
- 已修复 Stop Hook 的终态分支：`blocked_human` 自动 apply 后允许当前会话结束，不再返回 `decision=block` 触发无意义的 ToolSearch/事件读取循环；新增回归测试覆盖该行为。
- GPU 项目真实实验已完成 `requirements-auditor` 门禁：合法 `blocked_human` 结果被 Stop Hook 自动写入 `loop-state.json`，问题包进入 `queue.blocked_human`；实验暴露了旧逻辑的 `stop_intercepted_after_apply`/后续工具尝试，现已改为 `stop_allowed_after_apply`，并由回归测试锁定。
- 已根据真实错误增加统一 `RALPH_FEEDBACK[错误码]`：覆盖事件日志循环、重复派发、任务卡生命周期、Commander 越权写入、AskUserQuestion、Worker 范围、门禁回执、阶段协议、Stop 无动作和 oMLX/连接中断；每条反馈都包含检测、修正、唯一下一步和禁止事项。
- 协议修复提示现在保留原输出中可识别的 action；有 pending/dispatched 卡时优先反馈派发/等待，不再展示会诱导模型提前推进的 `blocked_human` 或 `advance` 模板。
- 当前运行时回归测试共 90 项，全部通过；Python 模块编译和 `git diff --check` 均通过。
- 新增简单任务分解 benchmark：用“我需要跑本地 AI，帮我调研性价比最高的 GPU”检查七个语义角色、attribute_matrix 叶节点、隐藏属性、处置方式、场景、成功标准和问题闸门；真实项目模式还必须核对 `requirements-auditor` 的 completed 独立门禁生命周期。
- `ralph benchmark-decomposition` 只读评估项目状态或保存的 action/task-spec JSON；它与状态机分工明确，协议负责字段合法性，benchmark 负责语义完整性，Hook/门禁负责实际派发是否发生。
- 简单任务基准的固定 fixture 已通过（score=1.0），运行时回归测试 90 项全部通过。
- 已实现 stage-01 rollback→clarify→新 revision auditor 链路；clarify 会把 task_spec 标记为 `structured_pending_audit`，不会绕过独立门禁。
- 已实现终态任务卡单向保护、gate receipt 驱动的 stale-card reconciliation、`subagent_card_reconciled` 事件以及监督循环的启动/结束事件。
- 已实现 `ralph loop`：新项目输入一次任务即可自动创建/匹配项目；旧会话退出后使用新 Claude 上下文继续，默认自动跳过 `blocked_human`，`--wait-human` 可改为等待。
- `ralph loop` 默认启用 1800 秒无事件/状态活动看门狗；超时只终止卡住的 Claude 上下文，不删除状态，并在下一轮使用新上下文恢复。
- 本轮新增回归覆盖 clarify 状态转换、迟到 Hook 不回退、有效 gate receipt 回收和 supervisor cycle；运行时测试共 95 项，全部通过。
- 已增加同上下文协议修复预算、pending 卡首动作强制、重复 Stop 等待保护，以及阶段范围结果工件和 `ralph validate <project> --result <artifact> [--apply]`；新增回归后测试继续全部通过。
