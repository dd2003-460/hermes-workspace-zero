# fields 字段快照

> 由 `ralph render` 自动从 `loop-artifacts/stages/02.5/r1/fields.json` 生成，请勿手改。

> 生成时间：2026-07-25 05:53

## 概览

- 字段总数：**1**
- 待办（pending / research_required）：**0**
- 分组：cross_validation×1

## 字段明细

### cross_validation

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| cross_validation | 运行时字段门禁、Hook 恢复、动态任务数量、DAG 并行与 Join 的交叉验证结果 | confirmed | 0.90 | material | 是 |

## 证据与备注

### cross_validation

独立测试覆盖字段增量提交、非法输入不变更状态、动态字段任务、DAG 环检测/写冲突/Join；现场事件覆盖 Agent 停滞回收。真实本地 Agent 字段写入仍是未验证项。

证据：
- loop/ralph_runtime/tests/test_field_workflow.py
- loop/ralph_runtime/tests/test_dag.py
- loop/ralph_runtime/tests/test_cli_run.py
- loop-events.md#auto_field_worker_stall_reaped
