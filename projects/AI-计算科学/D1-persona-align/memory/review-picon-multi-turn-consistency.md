# Review: PICon — Multi-Turn Persona Agent Consistency

**Paper**: PICon: A Multi-Turn Interrogation Framework for Evaluating Persona Agent Consistency
**Authors**: Minseo Kim, Sujeong Im, et al. (Korea)
**Finding**: Persona agents often fail human baselines on internal and external consistency under sustained interrogation.

## Key Insights

1. **PICon framework**: Logically chained questioning to verify persona consistency. Agents appear consistent in single-turn but break under multi-turn logical pressure.

2. **Two consistency types**:
   - Internal consistency: Agent maintains self-consistent narrative
   - External consistency: Agent's claims align with known facts

3. **Relevance to persona-v3**: Our evaluation (gap_filler, unified_eval) only tests single-file static alignment. PICon would test whether persona-v3 prompt actually maintains consistency across multi-turn conversation.

## Connection to persona-v3

- EMPA trajectory eval already tests "directional alignment" but doesn't test logical consistency under interrogation
- PICon could be integrated as a new test: `python3 scripts/persona_v3_alignment_checker.py --picon-test`
- Our keyword signature approach might be robust to PICon if keywords are distributed across all responses (not just prompt)

## Action Items

1. Research PICon methodology more deeply
2. Consider adding PICon-style logical pressure test to unified_eval pipeline
3. Test persona-v3 prompt against PICon interrogation patterns
