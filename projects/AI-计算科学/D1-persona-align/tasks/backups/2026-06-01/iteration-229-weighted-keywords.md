# Iteration 229: alignment_checker 加权关键词 — 从 flat matching 到 category-based retrieval

## 目标
根据 Synthius-Mem 的 6 认知域分解思路, 将 keyword matching 从 flat 改为 weighted, 实现初步的 category-based retrieval。

## 执行动作

### persona_v3_alignment_checker.py 修改
1. DIMENSION_KEYWORDS 从 flat list 改为 `(keyword, weight)` 元组
2. 三个权重等级:
   - weight 2.0: 核心术语 (dimension name, fundamental concept)
   - weight 1.0-1.5: 相关术语 (synonyms, technical terms)
   - weight 0.5: 表达变体 (alternative phrasings, less direct)
3. compute_dimension_scores() 改用 weighted sum 替代 flat count

### 验证
- 总体评分 63.47 (无回归)
- 维度分数变化:
  - 自适应探索 0.40 → 0.53 (+0.13) — "探索利用" 2.0x, "磨刀理论" 1.5x
  - 自适应自我 0.99 → 0.84 (-0.15) — false positive 修正
  - 自适应精度 0.36 → 0.42 (+0.06) — 核心术语获得应有权重

### EN checker / dashboard
- 保留简单比率 (仅做 presence/absence 检测)
- 未来可同步加权结构 (deferred)

## 影响
- alignment_checker 评分更精准 — 核心术语匹配比低权重变体更重要
- 符合 Synthius-Mem "认知域分解" 思路: 不是所有关键词同等重要
- 从 flat keyword matching 到 category-based retrieval 的第一步
