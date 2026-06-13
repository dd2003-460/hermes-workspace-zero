# 1-loop — Planning 子阶段索引

本目录包含 1-loop（规划流程）的 6 个阶段文件，每个文件定义了一个阶段的：
- **输入**（来自前一阶段或外部）
- **操作步骤**（具体执行流程）
- **输出**（产出文件）
- **前置/后置依赖**

## 阶段列表

| 编号 | 文件名 | 阶段名称 | 输入 | 输出 |
|------|--------|----------|------|------|
| 01 | 01-任务澄清.md | 任务澄清 | task-spec.md | task-definition.md |
| 02 | 02-目标澄清.md | 目标澄清 | task-definition.md | acceptance-criteria.md |
| 03 | 03-任务分解.md | 任务分解 | acceptance-criteria.md | task-decomposition.md |
| 04 | 04-信息搜集.md | 信息搜集 | task-decomposition.md | tool-inventory.md |
| 05 | 05-完备核验.md | 完备核验 | tool-inventory + task-decomposition | gap-analysis.json |
| 06 | 06-决策.md | 决策 | gap-analysis.json | decision.md + task-state.json |

## 读取顺序

1. `../1-loop.md`（顶层流程定义）
2. 按编号 01-06 顺序阅读子阶段文件

## 双脑原则

- **主脑**：说清任务、目标、状态路径。接收副脑质疑。
- **副脑**：质疑主脑、找缺口、提醒不停止。每轮必出现。
- **不做什么**：不直接改文件、不替代 2-loop、不把一次回复当成结束

## 转移标准（进入 2-loop）

所有硬条件满足时，进入 2-loop：
- task-definition 存在且不超过 3 行
- acceptance-criteria 存在，所有维度可验证
- task-decomposition 存在，DAG 无环
- tool-inventory 存在，无阻塞项
- gap-analysis 存在，所有高影响项 = complete
- decision.md 存在，`enter_2loop: true`
- 副脑无未解决的质疑
