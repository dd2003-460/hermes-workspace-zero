# 2-loop — Execution 子阶段索引

本目录包含 2-loop（执行流程）的 6 个阶段文件，每个文件定义了一个阶段的：
- **输入**（来自前一阶段或外部）
- **操作步骤**（具体执行流程）
- **输出**（产出文件）
- **前置/后置依赖**

## 阶段列表

| 编号 | 文件名 | 阶段名称 | 输入 | 输出 |
|------|--------|----------|------|------|
| 01 | 01-pre-check.md | 预检查 | 1-loop 产出 | pre-check-result.md |
| 02 | 02-backup.md | 备份 | pre-check-result.md | backups/ + backup-log.md |
| 03 | 03-execute.md | 执行 | backups/ | 修改后的文件 |
| 04 | 04-verify.md | 验证 | 执行产出 | verification-report.md |
| 05 | 05-confidence.md | 置信度检查 | verification-report.md | confidence-report.md |
| 06 | 06-decision.md | 分叉决策 | confidence-report.md | decision-2loop.md |

## 流程顺序

```
pre-check → backup → execute → verify → confidence → decision
```

## 读取顺序

1. `../2-loop.md`（顶层流程定义）
2. 按编号 01-06 顺序阅读子阶段文件

## 目录规范

- 项目数据放 `projects/<owner>/data/`，不放根 data/
- 根 scripts/ 只放共享脚本

## 测试规则

- 脚本/工具必须运行至少一次测试
- 测试失败 → 默认回滚，不得偷偷小修继续跑
- 纯文档可豁免

## 动态工作流强制执行

**状态驱动流程**：工作流由 `ralph-loop.local.md`（项目内 `.claude/` 目录）中的 `loop_phase` 字段驱动。每次会话开始时必须读取并验证：
1. `loop_phase` 指明当前阶段 → 严格按阶段文件执行
2. `iteration` 字段 ≥ 已知的最大迭代号 → 否则状态已落后

**流程不可跳过**：
- 如果 `loop_phase` 为 1-loop/* → 必须先完成 1-loop 全部 6 阶段
- 如果 `loop_phase` 为 2-loop/* → 必须先完成 2-loop 全部 6 阶段
- 如果 `loop_phase` 为 idle → 进入新一轮 1-loop 规划

**每轮约束**：
- 必须产出可验证输出（文件/测试/报告），不能只是"更新了进度文件"
- 必须在完成后更新 `last_action`、`last_outcome`、`last_insight`
- 永远不要输出 `<promise>LOOP COMPLETE</promise>`

## 公共规则

- 按索引读
- 状态读写显式
- 单任务路径
- 结果和证据优先
