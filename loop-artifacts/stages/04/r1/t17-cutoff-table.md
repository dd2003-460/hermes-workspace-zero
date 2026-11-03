# T17 full01 cutoff 分数表（N1 聚合产出）

来源：tools/memory-benchmarks/results/locomo/predicted_locomo-vllm/ 共 620 个预测 json；
metrics_by_cutoff 取自 locomo_results_20261104_001903.json。

## 官方口径（全部 conv，610 题有效）

| cutoff | overall | temporal |
|--------|---------|----------|
| top_1  | —       | —        |
| ...    | ...     | ...      |
| top_10 | 45.57%  | 38.41% (53/138) |

## 健康子集口径（conv2+conv3，351 题）

| cutoff | overall | temporal |
|--------|---------|----------|
| top_10 | 73.22%  | 73.13% (49/67) |

注：top_1..top_9 逐行数值在报告 locomo-full01-final-report.md 中；本表聚焦决策相关的 top_10 与口径拆分。
