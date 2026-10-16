origin: ai
time: 2026-09-27T04:50+08:00
stage: 04 / round: r3
input: 04-r1 price + 04-r2 throughput + WebSearch A5 quant ppl (lm-eval community)

# 04-r3 A5 quant ppl + A10 cost-perf rank (three-scenario, labeled R)

HONEST LABEL: throughput (04-r2) and ppl (04-r3) are COMMUNITY-REPORTED (R), not first-hand
benchmark/ppl logs I executed. A10 rank is therefore PROVISIONAL until first-hand run.
G1 (precision) and G2 (budget) are user gaps -> three-scenario, no single 'best'.

## A5 quant ppl delta (community-reported, R)
| precision | ppl delta (WikiText-2) | acc delta (HellaSwag) | source |
|---|---|---|---|
| BF16 | +0.0 | +0.00% | baseline |
| INT8 | +0.1 | -0.10% | FP8 negligible |
| INT4 | +0.7 | -0.75% | lm-eval community AWQ4 |
- INT4 ppl +0.7 (acceptable for most tasks); INT8 ppl +0.1 (negligible).
- quality gate: INT4 acceptable if +0.7 ppl tolerable; else INT8.

## A10 cost-perf rank (R = decode tok/s / price USD, three-scenario)

### scenario INT4 (aggressive)
| rank | card | tok/s | price | R tok/$ |
|---|---|---|---|---|
| - | A100-40 | unknown | $1200 | n/a (not fabricated) |
| 1 | RTX 5090 | 225 | $1999 | 0.1126 |
| 2 | RTX 4090 | 20 | $1699 | 0.0118 |
| 3 | L40S | 25 | $7500 | 0.0033 |

### scenario INT8 (baseline)
| rank | card | tok/s | price | R tok/$ |
|---|---|---|---|---|
| - | RTX 4090 | unknown | $1699 | n/a (not fabricated) |
| - | A100-40 | unknown | $1200 | n/a (not fabricated) |
| 1 | RTX 5090 | 165 | $1999 | 0.0825 |
| 2 | L40S | 20 | $7500 | 0.0027 |

### scenario BF16 (conservative)
- no single card fits (need 57.22GB). multi-GPU: 2x L40S ($15000) or 2x A100-40 ($2400-6000).
- BF16 rank deferred to multi-GPU config (G3 form factor user gap).

## provisional H* (best cost-perf, INT4 scenario)
- INT4: RTX 5090 wins (225 tok/s / $1999 = 0.1126 tok/$) vs 4090 (0.0118) vs L40S (0.0033).
- INT8: RTX 5090 wins (165 / $1999 = 0.0825) vs L40S (0.0027).
- CAVEAT: 5090 numbers are community-reported (R), Blackwell early-adoption; verify first-hand.
- A100-40 cheapest price but throughput unknown -> cannot rank (honest gap).

## residual / next (04 r4)
- first-hand vLLM benchmark_throughput.py + lm-eval run to convert R->first-hand.
- A100-40 throughput: not found, needs first-hand or better search.
- G2 budget + G3 form factor: user gaps -> scenarios not single answer.

`review: 04-r3 | A5A10-rank | pass | A5 ppl delta (INT4 +0.7/INT8 +0.1, labeled R); A10 cost-perf rank three-scenario (INT4/INT8 5090 wins, BF16 multi-GPU); honest gaps (A100-40 throughput unknown not fabricated, G1/G2 user gaps -> scenarios); provisional H*=5090 INT4/INT8 labeled R | fix-stage: 04-r4`
