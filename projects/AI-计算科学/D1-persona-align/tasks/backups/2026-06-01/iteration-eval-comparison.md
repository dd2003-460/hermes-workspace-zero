# Iteration: Eval Strategy Comparison — Prompt vs LoRA

**Date:** 2026-05-22  
**Origin:** ai  
**Purpose:** Analyze eval results comparing persona alignment strategies

## Key Finding

**Pure prompt injection outperforms prompt + LoRA combination.**

| Strategy | Avg Score | Score Breakdown |
|----------|-----------|-----------------|
| method_only (pure prompt injection) | **0.747** | Best overall |
| chenglu_persona | 0.705 | Second |
| chenglu_persona_plus_lora | 0.669 | Third — worse than either alone |
| baseline (no injection) | 0.653 | Worst |

## Interpretation

The LoRA adapter appears to **degrade** persona alignment when combined with prompt injection. This suggests:

1. **LoRA fine-tuning may have memorized non-persona patterns** from training data
2. **Prompt injection is sufficient** — the base model already has the needed capabilities
3. **Combining both introduces conflict** — prompt-based and weight-based persona signals may compete

## Recommendation

**Skip LoRA for persona alignment.** Focus on:
1. Improving prompt injection (the current best approach)
2. Better synthetic data quality (currently only 66.67% avg fidelity)
3. Larger eval set (only 5 questions tested)

---

*Note: This analysis is autonomous — no author confirmation needed.*
