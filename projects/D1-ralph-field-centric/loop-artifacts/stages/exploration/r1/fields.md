# fields 字段快照

> 由 `ralph render` 自动从 `loop-artifacts/stages/exploration/r1/fields.json` 生成，请勿手改。

> 生成时间：2026-07-25 05:56

## 概览

- 字段总数：**2**
- 待办（pending / research_required）：**0**
- 分组：preference_brief×1、candidate_tasks×1

## 字段明细

### preference_brief

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| preference_brief | 继续优先验证本地 Agent 的实际字段写入；其次验证真实网页调研；保持小任务、可回滚、证据优先，不因人类确认阻塞其他 ready 任务 | confirmed | 0.90 | material | 是 |

### candidate_tasks

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| candidate_tasks | 候选任务：用更短的字段 worker prompt 重测 goal/known/unknown；候选任务：在可用网页工具下完成一个独立 GPU 因素调研 | confirmed | 0.85 | material | 是 |

## 证据与备注

### preference_brief

根据现场失败模式和用户持续推进偏好生成下一轮探索偏好。

证据：
- loop-events.md

### candidate_tasks

探索阶段只进入候选队列，不静默执行；下一轮由主 Agent 分解并选择。

证据：
- loop-events.md
