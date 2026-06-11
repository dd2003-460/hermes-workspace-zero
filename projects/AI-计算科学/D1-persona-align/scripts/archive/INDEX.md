# Scripts Archive

Obsolete persona-v3 scripts archived from `scripts/` (iteration 309). 30 files moved here to reduce active scripts from 50 to 20.

## Archival Criteria

- Superseded by newer versions (v1 → v2)
- Single-purpose scripts replaced by unified_eval.py
- From early persona-v1/v2 iterations (T7-T16 era)
- Abandoned experiments (TF-IDF scoring)
- LORA pipeline scripts (no longer used after prompt-based approach)

## Archived Scripts

| Script | Reason | Replacement |
|--------|--------|-------------|
| `persona_v3_gap_filler.py` | v1 (superseded by v2) | `persona_v3_gap_filler_v2.py` |
| `eval_baseline.py` | Early evaluation (T7) | `unified_eval.py` |
| `eval_complex_reasoning.py` | Early evaluation (T13) | `unified_eval.py` |
| `eval_hermes_personality.py` | Early evaluation | `unified_eval.py` |
| `eval_lora_direct.py` | LORA evaluation | No longer needed |
| `eval_personas_responses.py` | Early evaluation (T7) | `unified_eval.py` |
| `eval_prompt_baseline.py` | Early evaluation (T9) | `unified_eval.py` |
| `eval_prompt_v2.py` | Early evaluation (T10) | `unified_eval.py` |
| `eval_strategies.py` | Early evaluation (T13) | `unified_eval.py` |
| `eval_thinking_engine.py` | Early evaluation | `unified_eval.py` |
| `eval_thinking_v2.py` | Early evaluation | `unified_eval.py` |
| `enhance_all_dimensions_v3.py` | Single-purpose | `persona_v3_batch_enhance.py` |
| `enhance_bottom5.py` | Single-purpose | `persona_v3_batch_enhance.py` |
| `enhance_exploration.py` | Single-purpose | `persona_v3_batch_enhance.py` |
| `enhance_highest_weight.py` | Single-purpose | `persona_v3_batch_enhance.py` |
| `enhance_perception_v2.py` | Single-purpose | `persona_v3_batch_enhance.py` |
| `enhance_perception.py` | Single-purpose | `persona_v3_batch_enhance.py` |
| `enhance_remaining_dimensions_v2.py` | Single-purpose | `persona_v3_batch_enhance.py` |
| `enhance_remaining_dimensions.py` | Single-purpose | `persona_v3_batch_enhance.py` |
| `enhance_weak_dimensions.py` | Single-purpose | `persona_v3_batch_enhance.py` |
| `generate_persona_prompt.py` | Early generation | `generate_analyses.py` |
| `quick_baseline.py` | Single-purpose | `unified_eval.py` |
| `realtime_alignment_monitor.py` | Replaced by unified_eval | `unified_eval.py` |
| `test_quick.py` | Single-purpose | `integration_test.py` |
| `tfidf_scoring.py` | Abandoned (scores too low) | N/A |
| `train_lora.py` | LORA pipeline (unused) | N/A |
| `validate_gap_vs_dashboard.py` | Single-purpose | `unified_eval.py` |
| `validate_persona_in_context.py` | Single-purpose | `unified_eval.py` |
| `verify_prompt.py` | Single-purpose | `unified_eval.py` |
| `classify_raw_ideas.py` | Early classification | N/A |

## Active Scripts (20)

See `scripts/INDEX.md` for the current active script list.
