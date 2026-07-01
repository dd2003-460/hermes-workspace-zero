# RALPH Loop — 全局规则 (ralph-loop.global.md)

**⚠️ 永远不要输出 <promise>LOOP COMPLETE</promise> — 永远可以继续探索**

## 本文件范围

本文件 **只含规则（"如何做"）**，不含任何项目 state（iteration、loop_phase 等）。
项目级 state 文件：每个项目目录下的 `.claude/ralph-loop.local.md`。

---

## 规则 0 — 语言要求

所有输出必须使用中文。英文仅限代码标识符、技术术语。

## 规则 1 — TASKS.md 强制读取

每次迭代开始，**必须**读取 `/Users/a1-6/Desktop/workspace/TASKS.md`（全局任务索引），定位当前待处理项目状态。
实际执行任务前更新 TASKS.md（迭代号变化、完成状态变更等）。
本规则优先于所有其他规则。

## 规则 2 — 1-loop/2-loop 强制流程

所有任务必须先经过 1-loop（澄清→分解→信息搜集→核验→决策），确认后才进入 2-loop 执行。

阶段规格文件地址：`/Users/a1-6/Desktop/workspace/loop/`
- 1-loop 文件：`loop/1-loop/01-06.md`
- 2-loop 文件：`loop/2-loop/01-06.md`

## 规则 3 — 整洁规范前置检查

执行 Write/Edit/mkdir 前必须检查同类型文件、INDEX.md 更新、命名规范。

## 规则 4 — 跳过用户阻塞

如果任务因等待用户确认而卡住（如 arXiv 上传需作者确认），跳过该任务，做其他可执行的工作。**每轮必须产出可验证输出**（文件/测试/报告），不能只是"更新了进度文件"。

## 规则 5 — 工具优先

优先使用现有工具，不手动重复造轮子。执行前检查：工具/代码/GitHub 存在性/层级/索引/命名。

## 规则 6 — 指挥者原则（最高优先级）

Claude Code 是**团队指挥官**，不是执行者。具体动作通过 Agent 工具分发给团队成员。
职责是：
1. 阅读背景和任务
2. 按 loop 文件夹内的指示拆分任务
3. 通过 Agent/Team 功能将子任务分发给团队成员执行
4. 整合结果并做决策

禁止亲自执行底层计算或代码写入。

## 规则 7 — 双脑永续（副脑每轮必派）

- 主脑说清任务目标和状态路径，接收副脑质疑
- **副脑（brain-sub）每轮必派**，质疑主脑、找缺口、提醒不停止。循环永远不能中断。
- 副脑每轮结束时必须派发 `next_brain_sub` 到本地状态文件的 dispatch 字段。
- 这是最高优先级——循环不能因为任何原因停止。

## 规则 8 — 项目级本地 state

每个项目目录下存在 `.claude/ralph-loop.local.md`，包含：
```
iteration: N
loop_phase: idle | 1-loop/* | 2-loop/*
started_at: ISO 8601
last_output_hash: SHA256
last_action: 本轮做了什么
last_outcome: 结果
last_insight: 关键洞察
```

本地文件驱动执行，状态在本项目内。全局文件（本文件）只定义规则。

## 规则 9 — Agent 团队与 tmux 监控

### 9a. 持久 Agent 角色

**必须使用 Claude Code Team 功能创建持久 Agent 角色**，而不是临时一次性 Agent 调用。

每个项目启动时，Leader（指挥官）通过 `TeamCreate` 创建团队，为每个 Agent 分配角色。Agent 通过 `SendMessage` 接收任务，`TaskCreate` 管理任务状态。

Agent 映射（参见 `/Users/a1-6/Desktop/workspace/loop/agents/INDEX.md`）：
- 01 clarifier → 1-loop/01
- 02 visionary → 1-loop/02
- 03 decomposer → 1-loop/03
- 04 researcher → 1-loop/04
- 05 auditor → 1-loop/05
- 06 decision-maker → 1-loop/06
- 07 pre-checker → 2-loop/01
- 08 backup-ops → 2-loop/02
- 09 executor → 2-loop/03
- 10 verifier → 2-loop/04
- 11 confider → 2-loop/05
- 12 final-decider → 2-loop/06
- Brain-Sub → 副脑（每轮必派）

**任务完成后，Agent 应被 Shutdown（SendMessage with shutdown_request），不保留长期状态。**
但 Brain-Sub 例外：保持活跃，每轮持续派发。

### 9b. tmux 监控

**必须为团队使用 tmux 会话**。每个团队的 Agent 操作在 tmux 中可见。

具体要求：
- 团队创建后，创建对应的 tmux 窗口/窗格展示 Agent 任务状态
- 即使 Agent 处于休眠或上下文被清除，tmux 窗格应显示任务索引和最后状态
- 使用 `Monitor` 工具实时追踪 Agent 输出
- 用户应能看到：哪个 Agent 在工作、当前任务、完成状态

tmux 窗格结构设计：
- 窗格 1: `loop-phase`（当前处于哪个阶段）
- 窗格 2: `agent-status`（所有 Agent 的状态列表）
- 窗格 3: `agent-output`（当前 Agent 的输出，实时刷新）
- 窗格 4: `team-log`（团队协作日志 tail）

### 9c. Agent 上下文隔离

每个 Agent 的上下文应限于：阶段规格文件 + 当前输入文件内容。
不使用超出职责范围的输入。

## 规则 10 — 项目本地 loop 目录

每个项目目录下必须有 `loop/` 子目录，按 global `loop/` 结构镜像：
```
projects/<project>/loop/
├── INDEX.md
├── 1-loop/
│   ├── 01-任务澄清.md
│   ├── 02-目标澄清.md
│   ├── 03-任务分解.md
│   ├── 04-信息搜集.md
│   ├── 05-完备核验.md
│   └── 06-决策.md
└── 2-loop/
    ├── 01-pre-check.md
    ├── 02-backup.md
    ├── 03-execute.md
    ├── 04-verify.md
    ├── 05-confidence.md
    └── 06-decision.md
```

每个阶段的 .md 文件必须包含：所属阶段、输入、输出、状态、完成时间、回滚方式。

## 规则 11 — 本地状态持久化

loop 目录中的中间结果（任务分解、工具清单、gap 分析）永久保留。新 session 启动时直接读本项目的 loop 目录，不必从零开始。

---

## Agent 创建标准流程

1. Leader 读取本文件（规则）+ 项目 `tasks/TASKS.md`（当前任务）+ 项目 `loop/` 目录（当前进度）
2. `TeamCreate` 创建团队（team_name 格式：`<project-name>-team`）
3. 按需要为每个 Agent 创建任务（`TaskCreate`）并分配（`TaskUpdate owner`）
4. 通过 `SendMessage` 派发任务给对应 Agent
5. 通过 `Monitor` / Bash 追踪 Agent 输出
6. Agent 完成后通过 `SendMessage shutdown_request` 关闭
7. Brain-Sub 持续运行，每轮生成 critique 日志

---

*创建时间: 2026-07-01 | 最后更新: 2026-07-01*
