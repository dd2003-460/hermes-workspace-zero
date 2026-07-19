---
iteration: 1
iteration: 2
loop_phase: 2-loop
started_at: 2026-07-15T00:00+0800
last_action: iter6 - loop目录规范化整理（完成）
last_outcome: INDEX.md 创建、验证文件移至 2-loop/、旧版标记过期
last_updated: 2026-07-15T02:42+0800
last_insight: 1-loop产出验证文件命名不符合CLAUDE.md规范，需统一为03/04前缀
---

# D1-loop-spec-decomposition — 综述分解项目

本项目的任务是：**将 1-loop/00-综述.md 中的流程规范分解为可执行、可验证的具体任务步骤**，并用 Gold Case / Bad Case / Chain of Thought 校准。

## 约束

- 每个任务写入**独立文档**，供 subagent 独立执行
- 单个 subagent 的 `prompt + 执行产出` 不超过 **8K token** 上下文
- 不去除综述中的分支设计、置信度阈值、轮次机制
- 去掉模板匹配（非必须）
- GPU 调研正交并行分解作为示范写入综述

## 任务列表

参考 `loop/1-loop/tasks/` 目录下的独立任务文档。

## 计划

参考 `loop/plan.md`
