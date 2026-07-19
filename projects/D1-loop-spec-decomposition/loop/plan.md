# plan.md — 综述分解任务计划

> 所属项目：D1-loop-spec-decomposition
> 分解轮次：R1
> 生成时间：2026-07-15

## 目标

将 1-loop/00-综述.md 中的流程规范分解为可执行、可验证的具体任务步骤。

## 约束

- 每个任务写入**独立文档**（`tasks/R-D-S-{名称}.md`）
- 单个 subagent 的 `prompt + 执行产出` 不超过 **8K token**
- 去掉模板匹配（非必须）
- 从正交维度并行分解

## 任务 DAG

```
并行组1:  R1-D1-S1(目标澄清) → R1-D1-S2(约束确认) → R1-D1-S3(技术背景)
                                              ↗            ↘
                                             ↙              ↘
                                         R1-D2-S1(DAG生成) → R1-D2-S2(验证分解)
                                                               |
                                                          R1-D3-S1(执行)
                                                               |
                                                          R1-D3-S2(子任务验证)
                                                               |
                                                          R1-D4-S1(整体验证)
                                                               |
                                                          R1-D4-S2(决策)
```

## 任务列表

| ID | 名称 | 状态 | 文件 | 并行 |
|----|------|------|------|------|
| R1-D1-S1 | 目标澄清 | completed | [tasks/R1-D1-S1-目标澄清.md](tasks/R1-D1-S1-目标澄清.md) | 组1 |
| R1-D1-S2 | 约束确认 | completed | [tasks/R1-D1-S2-约束确认.md](tasks/R1-D1-S2-约束确认.md) | 组1 |
| R1-D1-S3 | 技术背景搜集 | completed | [tasks/R1-D1-S3-技术背景搜集.md](tasks/R1-D1-S3-技术背景搜集.md) | 组1 |
| R1-D2-S1 | 生成任务 DAG | completed | [tasks/R1-D2-S1-生成任务DAG.md](tasks/R1-D2-S1-生成任务DAG.md) | — |
| R1-D2-S2 | 验证分解完整性 | completed | [tasks/R1-D2-S2-验证分解完整性.md](tasks/R1-D2-S2-验证分解完整性.md) | — |
| R1-D3-S1 | 按 plan 执行 | completed | [tasks/R1-D3-S1-按计划执行子任务.md](tasks/R1-D3-S1-按计划执行子任务.md) | R1-D1/S2 已产出 |
| R1-D3-S2 | 子任务验证 | completed | [tasks/R1-D3-S2-子任务验证.md](tasks/R1-D3-S2-子任务验证.md) | verify-subtasks.md |
| R1-D4-S1 | 整体验证 | completed | [tasks/R1-D4-S1-整体验证.md](tasks/R1-D4-S1-整体验证.md) | integrity-verify.md |
| R1-D4-S2 | 决策 | completed | [decision.md](1-loop/decision.md) | — |

## 置信度

- 当前置信度: 1.0（1-loop 全部完成，进入 2-loop）
- 决策：置信度 1.0 ≥ 0.8 → 进入 2-loop 阶段
- 最终产出：分解规范（9 个独立任务文档 + 3 份验证报告 + 1 份决策报告）
