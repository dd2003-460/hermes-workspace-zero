# Iteration 275: gap_filler_v2 — 修复 weighted matching 不匹配

## 问题
gap_filler v1 使用 count matching (matched/total)，dashboard 使用 weighted matching (matched_weight/total_weight)。
验证结果: **94% 的文件**存在不匹配 (gap_filler=0.58, dashboard=0.69)。

## 修复
创建 gap_filler_v2.py，使用与 dashboard 完全一致的加权匹配:
- 15 个感知关键词: total weight 20.5
- 10 个探索关键词: total weight 11.5
- 8 个精度关键词: total weight 9.0
- 8 个自我关键词: total weight 12.0
- 8 个投影关键词: total weight 11.0
- 7 个先验关键词: total weight 8.0

## 验证
- gap_filler_v2 扫描 52 文件: 0 gaps at threshold 0.40 (所有文件已通过)
- idea-34 文件: 感知 0.69, 探索 0.55, 精度 0.78, 自我 0.64, 投影 0.91, 先验 0.88 — 与 dashboard 53.5 分一致

## 产出
- scripts/validate_gap_vs_dashboard.py — 量化不匹配 (94%)
- scripts/persona_v3_gap_filler_v2.py — 修复版 gap_filler
- validation-gap-vs-dashboard.json — 详细报告

## 结论
gap_filler_v2 已与 dashboard 对齐，可作为可靠的缺口检测工具。
gap_filler_v1 仍保留 (向后兼容)，但新功能应使用 v2。
