# fields 字段快照

> 由 `ralph render` 自动从 `loop-artifacts/stages/04.5/r1/fields.json` 生成，请勿手改。

> 生成时间：2026-07-25 05:56

## 概览

- 字段总数：**1**
- 待办（pending / research_required）：**0**
- 分组：cross_validation_out×1

## 字段明细

### cross_validation_out

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| cross_validation_out | 关键机械 claim 已由实现代码、定向测试和现场事件三路核验；未完成的真实 Agent 写入能力明确保留为开放风险 | confirmed | 0.90 | material | 是 |

## 证据与备注

### cross_validation_out

交叉核验没有把‘模型成功’和‘状态机可恢复’混为一谈；矛盾项已记录为后续实验风险。

证据：
- loop/ralph_runtime/ralph_runtime/cli.py
- loop/ralph_runtime/tests/test_field_workflow.py
- loop-events.md#auto_field_worker_stall_reaped
