# loop/ 目录概览

> 项目：D1-loop-spec-decomposition

## plan.md
1-loop 产出的任务计划（9 个任务 DAG + 并行组标注）。

## 1-loop/
- [01-信息搜集.md](1-loop/01-信息搜集.md) — R1-D1 目标澄清 + 约束确认 + 技术背景搜集
- [02-任务分解-old-v1.md](1-loop/02-任务分解-old-v1.md) — ❌ 旧版（10任务单文件，已废弃）
- [03-execute-子任务验证.md](1-loop/tasks/) — 子任务 DAG 生成 + 分解完整性验证（独立文档）
- [tasks/](1-loop/tasks/) — 9 个独立任务文档，供 subagent 独立执行

## 2-loop/
- [03-execute-子任务验证.md](2-loop/03-execute-子任务验证.md) — 子任务验证（5/5 通过）
- [04-verify-decomposition.md](2-loop/04-verify-decomposition.md) — 分解完整性验证（置信度 1.0）
- [04-verify-integrity.md](2-loop/04-verify-integrity.md) — 整体验证（置信度 1.0）
- [04-verify-decision.md](2-loop/04-verify-decision.md) — 决策（置信度 1.0 → 进入 2-loop）
