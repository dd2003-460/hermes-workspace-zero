origin: ai
time: 2026-09-27T04:35+08:00
stage: 04 / round: r3 / status: START

# cursor: 04/r2 DONE -> 04/r3 START

## 04/r2 done (pass)
- A3/A4 decode throughput (community-reported, labeled R).
- gate consistency check: 3 OOM-inconsistent claims caught + excluded.
- usable gate-consistent decode numbers per card.

## 04/r3 scope
- A5 quant ppl delta (INT8/INT4 vs BF16) first-hand or reported.
- A10 cost-perf rank three-scenario (conservative FP16 / baseline INT8 / aggressive INT4).

## precise blocking
- G2 budget not given -> A10 three-scenario (user gap).
- throughput/ppl REPORTED not first-hand -> A10 labeled R.
- config.json 401x3 -> sliding_window cross-checked only.

## next concrete action (04/r3)
- WebSearch Gemma-3-27B quantization perplexity delta (AWQ/GPTQ/INT8 vs BF16, lm-eval-harness).
