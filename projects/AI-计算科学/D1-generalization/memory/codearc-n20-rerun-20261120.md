# CodeARC n=20 重跑结果（2026-11-20）
# origin: ai
# 来源①：/tmp/codearc-probe 本地跑，proc_f1d50177bcf5，run20.log + output/。

## 设置
- qwen3.8-27b-mtp @ 8787，reasoning_guided，mi=30, mdr=1（= 论文默认 = o3-mini 参考配置）
- total_idx=20，num_processes=1，timeout=5m/批
- P4 为 skip 复用（n=5 旧产物），P19 超时被 kill

## 结果（可靠口径 = evaluation_results 的 is_correct）
- **5/7 = 71%**（P0✓ P1✓ P11✓ P12✓ P16✓ / P4✗ P15✗）
- 7 题：P0/P1/P4/P11/P12/P15/P16 落了 evaluation_results；其余 12 题（P2/P3/P5-P10/P13/P14/P17/P18/P19）没写
- **对照 o3-mini 52.7%（论文，1114 题全量）**：27b 71% 反而更高，但 n=7 太小 + 选择偏差，不能直接引用

## 三个 caveat（为什么 71% 不能引用）
1. n=7 太小（20 题只落盘 7 题）
2. 选择偏差：落盘的 7 题是"正常跑完的"，慢题/难题可能没落盘，71% 偏高
3. "judge 分歧"模式（pynguin True/mokav False）来自 n=5 旧 json，本轮 combined_result 是 csv 且只 pynguin 行 0/0，未复现

## 关键发现：单轮方差极大
- n=5 跑 = 0%（0/5）
- n=20 跑 = 71%（5/7）
- 同一模型同一配置，两轮差 71 个百分点 → **CodeARC 对本地 27b 单次评测噪声 > 模型间差异**
- 这对任何"用 CodeARC 比 27b vs o3-mini"的实验都是硬约束：必须多轮 + 大 n，单轮数字无意义

## 待办
- [ ] 干净全量重跑：清 temp + evaluation_results，timeout 提到 10m/批，n=20 完整落盘
- [ ] 多轮（≥3）拿均值 + 方差，才能和 52.7% 比
- [ ] 失败分类（语法/逻辑/judge 分歧）在干净数据上重做
