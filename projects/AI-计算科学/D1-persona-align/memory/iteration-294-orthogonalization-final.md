# Iteration 294: Cross-Dimensional Keyword Orthogonalization — Final

## Action
- Identified that only 1 keyword ("信噪比") was truly cross-dimensional (in both 感知 and 精度)
- Experimented with full TF-IDF approach (3 iterations) which over-corrected
- Implemented surgical fix: removed "信噪比" from 自适应感知, kept in 自适应精度

## Results

### Cross-dimensional keywords: 0 (was 1)
- Before: 信噪比 → 自适应感知 + 自适应精度
- After: 信噪比 → 自适应精度 only

### Prompt score (unchanged)
- Before: 0.9292
- After: 0.9278 (Δ=-0.0014, negligible)

### Idea file scores (preserved)
- Avg file score: 0.7318 → 0.7263 (Δ=-0.0056)
- Min file score: 0.4118 (unchanged)
- All dims >= 0.40: True

### Orthogonalization experiments
1. **Full orthogonalization (v2)**: Added many specific keywords → hotspot 0.74→0.825 but idea score 0.73→0.59
2. **TF-IDF raw IDF**: Scores collapsed to 0.19 (IDF too aggressive)
3. **TF-IDF bounded factor (0,1)**: Scores 0.54 (still too low, uniform scores)
4. **TF-IDF mild factor (0.7-1.0)**: Scores 0.76 but all identical (0.757) — penalized too many keywords
5. **Surgical (1 keyword)**: Score 0.7263 (Δ=-0.006) — ideal balance

## Decision
Keep v1 keywords with single "信噪比" removal from 感知. This achieves true 0 cross-dimensional overlap with negligible score impact.

## Status
Keyword orthogonalization experiment complete. Final v1+ version in place.
