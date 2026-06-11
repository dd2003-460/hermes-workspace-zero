# Iteration 309: Scripts Directory Cleanup

## Action
- Archived 30 obsolete scripts to `scripts/archive/`
- Reduced scripts/ from 50 to 20 active scripts
- Verified integration test still passes (11/11)

## Archived Scripts (30)
- `persona_v3_gap_filler.py` — v1 (superseded by v2)
- `eval_baseline.py` — early evaluation
- `eval_complex_reasoning.py` — early evaluation
- `eval_hermes_personality.py` — early evaluation
- `eval_lora_direct.py` — early evaluation
- `eval_personas_responses.py` — early evaluation
- `eval_prompt_baseline.py` — early evaluation
- `eval_prompt_v2.py` — early evaluation
- `eval_strategies.py` — early evaluation
- `eval_thinking_engine.py` — early evaluation
- `eval_thinking_v2.py` — early evaluation
- `enhance_all_dimensions_v3.py` — single-purpose
- `enhance_bottom5.py` — single-purpose
- `enhance_exploration.py` — single-purpose
- `enhance_highest_weight.py` — single-purpose
- `enhance_perception_v2.py` — single-purpose
- `enhance_perception.py` — single-purpose
- `enhance_remaining_dimensions_v2.py` — single-purpose
- `enhance_remaining_dimensions.py` — single-purpose
- `enhance_weak_dimensions.py` — single-purpose
- `generate_persona_prompt.py` — early generation
- `quick_baseline.py` — single-purpose
- `realtime_alignment_monitor.py` — replaced by unified_eval
- `test_quick.py` — single-purpose
- `tfidf_scoring.py` — abandoned iteration
- `train_lora.py` — LORA pipeline (no longer used)
- `validate_gap_vs_dashboard.py` — single-purpose
- `validate_persona_in_context.py` — single-purpose
- `verify_prompt.py` — single-purpose
- `classify_raw_ideas.py` — early classification

## Active Scripts (20)
- `persona_keywords.py` — shared keyword library (core)
- `unified_eval.py` — unified pipeline (core)
- `integration_test.py` — integration test
- `regression_test.py` — regression test
- `chameleon_collapse_detector.py` — dimension collapse detector
- `emptrajectory_eval.py` — trajectory evaluation
- `persona_v3_gap_filler_v2.py` — gap filler v2
- `persona_v3_alignment_checker.py` — alignment checker
- `persona_v3_alignment_checker_en.py` — alignment checker EN
- `persona_v3_dashboard.py` — alignment dashboard
- `persona_v3_batch_enhance.py` — batch enhance
- `sync_personality.py` — sync to Hermse
- `section_alignment_test.py` — section alignment
- `temporal_stability_test.py` — temporal stability
- `test_time_optimize.py` — test-time optimization
- `cross_dim_ortho.py` — cross-dim orthogonalization
- `textbo_prompt_optimizer.py` — TextBO optimizer
- `generate_analyses.py` — batch analysis
- `quality_check.py` — quality check
- `integrate_persona.py` — cross-project integration

## Status
scripts/ cleaned up. Integration test passes. Archive preserved for reference.
