origin: ai
time: 2026-09-27T05:20+08:00
stage: 04.5 / round: r5 / status: START

# cursor: 04/r4 DONE -> 04.5/r5 START

## 04/r4 done (pass)
- A100-40 throughput gap filled (INT4 25-35 / INT8 20-40, R; BF16 OOM consistent).
- A10 rank recomputed price-sensitive; 5090 still #1 cost-perf.
- budget-binding H* alt = A100-40 refurb INT8 ($1200, cheapest feasible INT8).

## 04 atoms status
- A7 price OK | A3A4 throughput OK(R) | A5 ppl OK(R) | A10 rank OK(R) | A100-fill OK(R).
- first-hand benchmark BLOCKED (no local GPU, environment gap).
- G1-G6 user decisions: user gaps -> three-scenario stands.

## 04.5/r5 scope
- revise final review to fold A100-40: gap now filled, budget-binding H* alt added, H*=5090 unchanged.
- update traceability table + weakest-points (A100-40 gap CLOSED; first-hand still open).

## precise blocking
- no local GPU -> first-hand vLLM/lm-eval blocked (environment, not content).
- G2 budget + G3 form factor: user gaps -> scenarios not single answer.

## next concrete action (04.5/r5)
- write tasks/04.5-final-review-r5.md folding A100-40 + budget-binding alternative into final review.
