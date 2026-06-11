# Iteration 293: DIMENSION_KEYWORDS Orthogonalization Experiment

## Action
- Identified cross-dimensional keyword overlap: 信噪比 (感知+精度), 信息密度 (感知，但也是精度概念), 认知结构 (先验/自我交叉), 结构 (投影，太通用)
- Attempted full orthogonalization: removed shared keywords, added dimension-specific keywords
- Evaluated impact on both prompt alignment and idea file scores

## Results: Section Alignment

| Metric | Before (v1) | After (v2 orthogonalized) |
|--------|-------------|---------------------------|
| Avg hotspot ratio | 0.740 | **0.825** |
| 自适应精度 | 0.941 | 1.000 |
| 自适应感知 | 0.797 | 0.878 |
| 自适应先验 | 0.838 | 0.932 |
| 自适应自我 | 0.815 | 0.941 |
| 自适应探索 | 0.594 | 0.679 |
| 自适应投影 | 0.453 | 0.519 |

## Results: Idea File Scores (Top-5 + Top-5 strongest, 10 files)

| Metric | Original (v1) | Orthogonalized (v2) |
|--------|---------------|---------------------|
| Avg file score | 0.7247 | **0.5903** |
| Min file score | 0.6627 | **0.52** |
| Min dim score | 0.5153 | **0.4302** |
| All dims >= 0.40 | True | **False** |

## Analysis

The orthogonalization improved prompt section hotspot (0.740→0.825) but decreased idea file scores (0.725→0.590).

**Root cause**: Keyword expansion increased TOTAL_WEIGHTS significantly.
- 自适应精度: 8 keywords → 22 keywords (total_weight ×2.5)
- 自适应探索: 9 keywords → 14 keywords (total_weight ×1.7)
- 自适应投影: 8 keywords → 18 keywords (total_weight ×1.6)

The score formula `matched_weight / total_weight` means added keywords inflate the denominator without increasing matched_weight (idea files don't contain the new specific keywords).

The new keywords ARE better for dimension discrimination (higher hotspot), but the weighted matching formula penalizes texts that don't match the expanded set. This is a fundamental tension between **evaluation purity** (no shared keywords) and **real-world coverage** (lenient scoring for texts that reference the framework indirectly).

## Decision

Revert to original keyword set. The improvement in hotspot (0.740→0.825) is meaningful but not worth the 13-point drop in idea file scores. The original keyword set achieved a better balance:
- avg hotspot 0.740 (acceptable dimension discrimination)
- avg file score 0.73 (good coverage)
- all dims >= 0.40 (baseline passing)

The dimension overlap can be addressed separately by improving the evaluation metric (e.g., normalization, TF-IDF weighting) rather than keyword purging.

## Status
Experiments documented. Reverted to v1 keywords to maintain baseline compatibility.
