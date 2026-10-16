origin: ai
time: 2026-09-27T04:55+08:00
stage: 04 / round: r4 / status: START

# cursor: 04/r3 DONE -> 04/r4 START

## 04/r3 done (pass)
- A5 quant ppl delta (INT4 +0.7 / INT8 +0.1, labeled R).
- A10 cost-perf rank three-scenario (5090 wins INT4/INT8).
- provisional H* = RTX 5090 (labeled R).

## 04/r4 scope
- convert R -> first-hand: vLLM benchmark_throughput.py + lm-eval-harness run (if GPU available).
- fill A100-40 throughput gap (better search or first-hand).
- finalize H* recommendation (three-scenario -> single if G1/G2 given).

## precise blocking
- no local GPU to run first-hand benchmark (environment gap).
- G2 budget + G3 form factor: user gaps -> scenarios not single answer.
- A100-40 throughput: not found in searches.

## next concrete action (04/r4)
- WebSearch A100-40 Gemma-3-27B throughput (fill gap) OR accept gap + finalize three-scenario H* report.
