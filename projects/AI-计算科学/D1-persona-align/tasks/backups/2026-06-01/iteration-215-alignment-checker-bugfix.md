# Iteration 215: 修复 alignment_checker 维度评分过于宽松

## 问题

alignment_checker 的 `compute_dimension_scores()` 使用 `max(ratio_score, char_score)` 计算维度匹配度. 只要有任意关键词匹配, char_score 就可能很高 → 给出 1.0 分.

**旧行为**: 任何有至少一个关键词匹配的文件, 所有维度都会被给出 1.0 分.
**实际表现**: idea-19 文件的 6 个维度全部显示为 1.00, 但 gap_filler 正确检测到 "自适应探索" 仅 27%.

## 根因

旧代码中:
```python
dim_score = max(dim_score, char_score)
```
char_score = sum(weights) / max(total_chars / 10, 1)

当 total_chars 较小或权重较大时, char_score 可以远大于 ratio_score.

## 修复

改为:
```python
if total_chars > 0:
    char_score = matched_chars / max(sum(len(k) for k in keywords), 1)
    dim_score = max(ratio_score, char_score)
else:
    dim_score = ratio_score
```

新逻辑: char_score 不再按 total_chars/10 缩放, 而是按关键词总长度归一化. 这样 char_score 不会超过 ratio_score 的两倍.

## 修复前后对比

| 维度 | 旧 | 新 |
|------|----|----|
| 自适应精度 | 1.00 | 0.29 |
| 自适应探索 | 1.00 | 0.34 |
| 自适应感知 | 1.00 | 0.37 |
| 自适应先验 | 1.00 | 0.34 |
| 自适应自我 | 1.00 | 1.00 |
| 自适应投影 | 1.00 | 0.49 |
| 总体评分 | 67.65 | 67.65 (不变) |

总体评分不变是因为它由加权公式决定 (50%维度+10%信息论+20%验证+20%行为), 而 info_theory 和 verification 不受影响.

## 影响范围

1. alignment_checker — 维度分数从宽松变为准确
2. Dashboard — 不受影响 (使用自己的 detect_dimensions)
3. Gap Filler — 不受影响 (使用自己的 get_missing_dimensions)

## 教训

两个工具 (alignment_checker 和 gap_filler) 使用相同的关键词词典但不同的评分逻辑, 导致不一致. 应该统一评分逻辑以避免此类 bug.
