# Iteration 304: Chameleon Collapse Bug Fix

## Action
- Fixed `compute_chameleon_metrics()` in `unified_eval.py`
- Bug: `vec_i` and `vec_j` were identical copies of `avg_sigs`, so cosine similarity was always exactly 1.0
- Fix: use `dim_aggregate[dim_i]` and `dim_aggregate[dim_j]` (per-dimension score vectors across files)

## Results
- Before: Chameleon Collapse similarity = 1.0 (bug)
- After: Chameleon Collapse similarity = 0.995 avg / 0.9986 max (real)
- Core baselines unchanged: avg 0.7288 ≥ 0.70 ✅, min 0.6592 ≥ 0.65 ✅, dim_min 0.5514 ≥ 0.40 ✅
- Integration test: 11/11 PASS

## Analysis
- 0.995 similarity is still above collapse threshold (0.70), meaning dimensions are genuinely highly correlated
- Root cause: all 6 dimensions use the same academic/mathematical keyword register
- Core evaluation (gap_filler scores) is unaffected — Chameleon is a secondary metric
- The fix makes the metric meaningful (differentiates between dimension pairs)

## Status
Chameleon collapse metric fixed. All baselines pass. Integration test passes.
