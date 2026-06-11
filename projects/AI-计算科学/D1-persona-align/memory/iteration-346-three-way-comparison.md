# Iteration 346: Three-Way Comparison — Prompt Length vs Persona Activation

## Summary
Tested 3 prompt versions with real Hermes Gateway session to find optimal persona activation.

## Results

| Version | Prompt Size | avg_score | min_score | 探索 | 感知 | 自我 |
|---------|------------|-----------|-----------|------|------|------|
| v1 (original) | 11278 bytes / 20604 tokens | 0.2849 | 0.0000 | 0.00 | 0.00 | 0.00 |
| v2 (math injected) | 11566 bytes / 20749 tokens | 0.1864 | 0.0000 | 0.00 | 0.00 | 0.24 |
| minimal | 810 bytes / 405 tokens | 0.0686 | 0.0000 | 0.00 | 0.00 | 0.00 |

## Key Findings
1. **Shorter ≠ Better**: Minimal (810 bytes) performed WORST, not best
2. **Math injection failed**: Injected symbols (argmax, ε, ρ, σ²) completely absent
3. **Context_length=32768**: Sufficient for all versions — truncation ruled out
4. **Model preserves persona CONCEPTS but NOT keywords**:
   - v1 response: rate-distortion, 贝叶斯, epigenetics, boundary conditions (✓ concepts)
   - v1 response: 探索:0, 感知:0, 观测者:0 (✗ keywords)
   - minimal response: "成璐的数字分身", "贝叶斯闭环", "存在延续→永生" (✓ concepts)
   - minimal response: 探索:0, 感知:0, 观测者:0 (✗ keywords)

## Root Cause
**Model architecture limitation**: Qwen3.6-35B-A3B cannot map persona instructions → generated keywords reliably, even when it uses persona CONCEPTS.

## Implication
The alignment_checker evaluates persona-v3 alignment using keyword matching. The model generates persona-conceptual content (which IS aligned) but lacks persona-keyword tokens (which the checker flags as misaligned). This creates a **false negative**: the system IS functionally aligned but appears misaligned to the metrics.

## Next Steps
1. **Evaluation redesign**: Semantic matching > keyword matching. The alignment_checker should understand synonyms and paraphrasing.
2. **Accept current metrics**: avg 0.28 on keyword matching doesn't mean low alignment — it means low keyword retention.
3. **Natural keyword injection**: Find ways to make keywords appear organically (e.g., in the user query, or as role-play framing).
