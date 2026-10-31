# 04 阶段字段快照

> 由 `ralph render` 自动从 `loop-artifacts/stages/04/r1/tasks/04-r1-field-verification_report.json` 生成，请勿手改。

> 生成时间：2026-10-31 22:54

## 概览

- 字段总数：**3**
- 待办（pending / research_required）：**0**
- 分组：coverage_proof×1、task_graph×1、verification_report×1

## 字段明细

### coverage_proof

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| coverage_proof | T08节点完成后填写:节点→产物映射+gap列表+结论 | confirmed | 0.90 |  |  |

### task_graph

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| task_graph | T08节点完成后填写:节点→产物映射+gap列表+结论 | confirmed | 0.90 |  |  |

### verification_report

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| verification_report | S1 BTC 回测验证报告: PIT 自检 + 45 格矩阵 + F1-F8 判据 + 负结果结论 | confirmed | 0.95 |  |  |

## 证据与备注

### coverage_proof

T08 coverage_proof join 节点已完成 (plan.completed 含 T01-T08): 7 个 declared artifact 全部在盘且字节核验通过@2026-10-17, 0 缺失; 跨 artifact 一致性 6 项核验 5✅+1❌(已记录于 T08 output). gap: 无未覆盖 declared artifact.

证据：
- loop-artifacts/stages/03/r1/artifacts/t01-arxiv-260827734-verify.md
- loop-state.json#plan.task_results.T08
- loop-artifacts/stages/03/r1/fields.md

### task_graph

03 阶段 task graph 已分解为 8 个最小执行单元 (T01-T08) 且全部完成 (plan.completed=T01..T08, joins T04/T08 收敛); 下游 04/05 阶段产物证明该分解被执行完毕; gap: 无未覆盖 declared artifact.

证据：
- loop-state.json#plan.task_results
- loop-artifacts/stages/04/r1/backtest_results.json
- loop-artifacts/stages/05/r2/f6_backtest_results.json

### verification_report

S1 BTC 资金费率信号回测完成并全链路验证: (1) PIT B6 8/8 PASS (pit_selfcheck.json); (2) 45 格检验矩阵(3 regime × 3 threshold × 5 window 2021-2025) BH-FDR 0/45 通过; (3) DSR z=-4.87, pooled Sharpe T1=-1.031; (4) F1-F8 判据全灭 → final_verdict=FAIL. 预注册冻结于 run 前, 无 in-sample 调参. 产物: backtest_results.json + backtest_trades.parquet(6576行) + pit_selfcheck.json + t06-signal-backtest-report.md.

证据：
- loop-artifacts/stages/04/r1/backtest_results.json
- loop-artifacts/stages/04/r1/pit_selfcheck.json
- loop-artifacts/stages/04/r1/t06-signal-backtest-report.md
- loop-artifacts/stages/04/r1/backtest_trades.parquet
