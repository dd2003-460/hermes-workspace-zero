# Agent 团队索引 — RALPH Loop

## 架构

全局 `.claude/agents/` 目录包含所有 Agent 定义。
Claude Code 在主 prompt 加载这些文件作为 context。

## Agent 映射表

### 1-loop（规划阶段）— 指挥官不执行，只派发

| Agent | 阶段 | 职责 |
|-------|------|------|
| `clarifier` | 1-loop/01-任务澄清 | 读取项目状态、memory、现有产出，澄清当前任务目标 |
| `decomposer` | 1-loop/02-目标澄清 → 03-任务分解 | 分解任务为 DAG，列出子任务，预估耗时 |
| `gatherer` | 1-loop/04-信息搜集 | 搜索文献、检查工具/代码/现有脚本，搜集信息 |
| `verifier` | 1-loop/05-完备核验 | 执行 gap analysis，检查置信度，记录风险 |
| `decision-maker` | 1-loop/06-决策 | 根据所有输入做 enter_2loop / needs_replan 决策 |

### 2-loop（执行阶段）

| Agent | 阶段 | 职责 |
|-------|------|------|
| `prechecker` | 2-loop/01-pre-check | 环境检查：Python、依赖、磁盘、已有备份 |
| `backup-agent` | 2-loop/02-backup | 创建时间戳备份，记录备份清单 |
| `executor` | 2-loop/03-execute | **实际执行者** — 写代码、计算、跑脚本、画图 |
| `quality-checker` | 2-loop/04-verify | 编写并运行验证脚本，逐项 PASS/FAIL |
| `confidence-judge` | 2-loop/05-confidence | 综合评估置信度，记录不确定性 |
| `fork-decider` | 2-loop/06-decision | 判定 completed / needs_replan / completed_with_branches |

## 通用副脑

| Agent | 职责 |
|-------|------|
| `brain-sub` | 每轮派发，质疑主脑判断，找盲区，提醒不停止 |

## 使用方式

Claude Code 主会话作为 **指挥官（leader）**：
1. 读取 `.claude/ralph-loop.local.md` 获知当前阶段
2. 按本索引派发给对应 Agent
3. 收到 Agent 产出后验收
4. 推进到下一阶段

**规则7铁律：指挥官只调度、不执行。写代码和计算必须由 executor Agent 完成。**

## 规格文件

全局阶段规格文件在 `/Users/a1-6/Desktop/workspace/loop/` 目录下：
- 1-loop: `1-loop/01-任务澄清.md` ~ `1-loop/06-决策.md`
- 2-loop: `2-loop/01-pre-check.md` ~ `2-loop/06-decision.md`

每个项目必须在 `loop/` 下镜像对应结构作为实例文件。
