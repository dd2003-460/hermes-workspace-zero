# Iteration 285: EMPA Trajectory — Keyword Signature Direct Intensity

## Action
- Updated `emptrajectory_eval.py`:
  - flatten_features: special case for dim_keyword_signature (each dim score as independent feature)
  - evaluate_trajectory: persona intensity computed from sig[target_dim] instead of L2-deviation

## Result: Meaningful Persona Activation Differences

| Method | Before | After |
|--------|--------|-------|
| Persona intensity range | 0.39-0.45 (L2-deviation) | 0.72-1.0 (keyword sig) |
| Std dev | 0.0308 | 0.1592 |
| Range | 0.08 | 0.45 |

| 维度 | Persona 强度 |
|------|-------------|
| 先验 | 1.000 |
| 投影 | 0.938 |
| 感知 | 0.906 |
| 精度 | 0.813 |
| 探索 | 0.787 |
| 自我 | 0.720 |

## Key Insight
L2-normalized deviation from baseline makes all responses equally "different" from baseline (same length, similar surface features). Keyword signature direct matching reveals actual persona activation differences — 先验 and 投影 have many matching keywords (full activation), while 自我 has fewer keywords (lower activation).

## Evaluation Tool Chain Complete
1. gap_filler_v2 (keyword matching)
2. chameleon_collapse_detector (dimension diversity)
3. emptrajectory_eval (trajectory-level)
4. persona_keywords (shared keyword library)

All tools share the same DIMENSION_KEYWORDS, ensuring evaluation consistency.