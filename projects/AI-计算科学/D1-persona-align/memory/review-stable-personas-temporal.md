# Review: Stable Personas — Temporal Stability in LLM Human Simulation

**Paper**: Stable Personas: Dual-Assessment of Temporal Stability in LLM-Based Human Simulation
**Authors**: Jana Gonnermann-Müller, Jennifer Haase, et al. (Germany)
**Finding**: Self-reports remain stable but persona expressions decline during extended conversations.

## Key Insights

1. **Dual assessment approach**: Uses both self-reports and observer ratings to measure stability.

2. **Key finding**: "Self-reports remain stable, but persona expressions decline during extended conversations." This is exactly the Chameleon's Limit problem — personas fade over time in actual use.

3. **Temporal stability dimensions**:
   - Immediate stability (same conversation, different turns)
   - Delayed stability (across sessions)
   - Context stability (different topics)

4. **Relevance to persona-v3**: Our Chameleon collapse detector measures dimensional diversity but NOT temporal stability. The persona-v3 prompt might score 0.9278 but fail in extended Hermse sessions.

## Connection to persona-v3

1. **Chameleon collapse detector** → Add temporal stability sub-test: split conversation into 5-turn blocks, evaluate each block's persona consistency
2. **Section alignment test** → Could be extended to test if DPA (dynamic priority adjustment) section actually maintains persona over time
3. **Trajectory eval** → `stability` metric is already measured but not tested with extended conversations

## Recommendations

1. Create a "temporal stability test" in chameleon_collapse_detector: evaluate persona consistency across conversation turns
2. Add a "persona drift detection" metric: how fast does persona quality decay over conversation length?
3. Update DPA section to explicitly address temporal stability (not just single-turn optimization)
