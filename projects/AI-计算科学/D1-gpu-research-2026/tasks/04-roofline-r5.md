origin: ai
time: 2026-09-27T05:50+08:00
stage: 04 / round: r5
input: memory-bandwidth roofline test (adversarial self-check on R throughput) + spec bw (WebSearch R)

# 04-r5 roofline adversarial check on community single-stream throughput

METHOD: single-stream decode (batch=1) is memory-bandwidth-bound. Roofline tok/s = bw / weights_bytes.
Any community 'single-stream' number ABOVE roofline is mislabeled (batched/aggregate).
Any number FAR BELOW roofline = non-optimized path (llama.cpp/offload) or different config.

## bandwidth (R, NVIDIA spec, anchored 2026-09-27)
| card | bw GB/s | mem type |
|---|---|---|
| RTX 5090 | 1792 | GDDR7 |
| RTX 4090 | 1008 | GDDR6X |
| L40S | 864 | GDDR6 |
| A100-40 | 1555 | HBM2e |

## roofline vs community (script-verified)
| card | prec | roofline | community | verdict |
|---|---|---|---|---|
| A100-40 | INT4 | 115 | 25-35 | FAR-BELOW-ROOFLINE |
| A100-40 | INT8 | 58 | 20-40 | PLAUSIBLE |
| L40S | INT4 | 64 | 20-30 | PLAUSIBLE |
| L40S | INT8 | 32 | 15-25 | PLAUSIBLE |
| RTX 4090 | INT4 | 75 | 18-22 | FAR-BELOW-ROOFLINE |
| RTX 5090 | INT4 | 133 | 200-250 | ABOVE-ROOFLINE |
| RTX 5090 | INT8 | 66 | 150-180 | ABOVE-ROOFLINE |

## findings
- 5090 INT4 comm 200-250 EXCEEDS roofline 133 -> almost certainly BATCHED/aggregate, not single-stream.
- 5090 INT8 comm 150-180 EXCEEDS roofline 66 -> batched.
- 4090 INT4 comm 18-22 FAR BELOW roofline 75 -> non-optimized (llama.cpp) or offload.
- A100-40 INT4 comm 25-35 FAR BELOW roofline 115 -> non-optimized path.
- L40S numbers WITHIN roofline -> plausible single-stream.
- CAVEAT: ABOVE-roofline = batched OR speculative-decoding OR mislabeled. Spec-decoding legitimately exceeds the single-model roofline (reads small draft + verifies >1 token/pass), so 'exceeds' != 'wrong', but != a clean batch=1 dense figure.

## roofline-based rank (theoretical ceiling)
### INT4
- #1 A100-40: 115 tok/s, R@low=0.0960 (@$1200)
- #2 RTX 5090: 133 tok/s, R@low=0.0664 (@$1999)
- #3 RTX 4090: 75 tok/s, R@low=0.0439 (@$1699)
- #4 L40S: 64 tok/s, R@low=0.0085 (@$7500)
### INT8
- #1 A100-40: 58 tok/s, R@low=0.0480 (@$1200)
- #2 RTX 5090: 66 tok/s, R@low=0.0332 (@$1999)
- #3 RTX 4090: 37 tok/s, R@low=0.0220 (@$1699)
- #4 L40S: 32 tok/s, R@low=0.0043 (@$7500)

## KEY: rank is NOT robust to roofline
- roofline INT4 R: 5090@1999=0.0664, A100-40@1200=0.0960
- at roofline, A100-40 refurb @ $1200 BEATS 5090 -> community rank (5090 #1) is fragile.
- community put 5090 #1 because its number exceeds roofline (batched) while A100-40's is far below (non-opt).
- => H*=5090 confidence DROPS: rank depends on (a) single-stream vs batched, (b) optimization, (c) refurb price.

## honest conclusion
- community R throughput is NOT internally consistent with physics roofline -> rank provisional, first-hand needed.
- H*=5090 still plausible (5090 bw 1.8x 4090 at 1.7x price) but margin far thinner than community 11x claim.
- first-hand vLLM single-stream benchmark is now LOAD-BEARING, not optional.

`review: 04-r5 | roofline-adversarial | pass | roofline=bw/weights script-verified; caught 5090 INT4/INT8 comm ABOVE roofline (batched/mislabeled) + 4090/A100 FAR-BELOW (non-opt); roofline rank flips cheapest-refurb (A100-40@1200 beats 5090); H*=5090 confidence drops, rank fragile to single-stream-vs-batched + refurb price; first-hand now load-bearing | fix-stage: 04-r6 (first-hand) or await GPU`
