# Iteration 353: DIMENSION_KEYWORDS 分层 — 核心 vs 通用关键词

## 背景

迭代 352 发现 gap_filler_v2 的关键词注入导致评估过拟合 — 36 个关键词命中率 100%，std 被压缩到 0.0176。本迭代修改 DIMENSION_KEYWORDS 添加核心关键词子集。

## 变更

### persona_keywords.py

添加 `CORE_KEYWORDS` — 命中率 < 50% 的关键词，难以被模板注入伪造:

| 维度 | 原始关键词数 | 核心关键词数 |
|------|-----------|-----------|
| 自适应感知 | 14 | 5 |
| 自适应探索 | 9 | 4 |
| 自适应精度 | 8 | 3 |
| 自适应自我 | 9 | 3 |
| 自适应投影 | 8 | 1 |
| 自适应先验 | 7 | 1 |

新增 `compute_core_scores()` 函数。

### 筛选策略分析

不同关键词筛选阈值:

| 阈值 | mean | std | std 倍数 |
|------|------|-----|---------|
| 100% (原始) | 0.7288 | 0.0176 | 1.0x |
| < 50% (核心) | 0.0637 | **0.0735** | **4.2x** |

核心关键词标准差提升 4.2 倍，但 mean 也大幅降低 (0.73 → 0.06)。

## 策略: 互补评估，不替代

不替换 DIMENSION_KEYWORDS，而是保留两套评估:

1. **标准评估** (`compute_dimension_scores`): 继续用于 "minimum viable alignment" 指标
2. **核心评估** (`compute_core_scores`): 用于 "true semantic alignment" 指标

两套评估互补:
- 标准评估检测到关键词注入 (gap_filler 效果)
- 核心评估检测到真实语义对齐
- 两者的差异揭示评估质量

## 下一步

1. 更新 unified_eval.py 支持核心关键词评估
2. 修改 gap_filler_v2 减少通用关键词注入
3. 记录 persona-v3 基线 — 使用两套指标
