# Iteration 284: Persona Keywords Shared Module + Dimension Signature Features

## Action
- Created `scripts/persona_keywords.py` — shared keyword library for all persona tools
- Added dimension keyword signature as feature in chameleon_collapse_detector
- Keyword signature dominates similarity (weight 0.5)

## Results: Keyword Signature Dramatically Improves Discrimination

| Metric | No Keywords | Surface Only | +Dim Signature |
|--------|-------------|--------------|----------------|
| Avg sim | 0.520 | 0.480 | **0.379** (-27%) |
| Min sim | 0.459 | 0.421 | **0.278** (-39%) |

## Key Finding
Dimension keyword signatures are the strongest distinguishing feature. The two most similar dimensions (探索↔先验, 0.634) share probabilistic language patterns. The two most distinct pairs (精度↔探索 0.287, 探索↔自我 0.287) use completely different conceptual vocabularies.

## New Files
- `scripts/persona_keywords.py` — shared keyword definitions (DIMENSION_KEYWORDS, TOTAL_WEIGHTS, compute_dimension_scores)
- Updated `scripts/chameleon_collapse_detector.py` — added keyword_signature_similarity as feature

## Impact
- This validates the gap_filler approach: keywords DO distinguish dimensions
- But mock responses may not activate keywords as strongly as real persona-v3 responses
- **Real API validation is critical** for quantitative accuracy
