origin: ai
time: 2026-09-27T04:30+08:00
stage: 04 / round: r2
input: WebSearch community throughput (Reddit r/LocalLLaMA, vLLM forum, blogs) + 04-r1 VRAM gate

# 04-r2 A3/A4 throughput (community-reported, NOT first-hand benchmark log)

HONEST LABEL: all numbers below are COMMUNITY-REPORTED (Reddit/vLLM forum/blogs, 2026).
NOT first-hand benchmark logs I executed. Marked R (reported). For A10 final rank,
first-hand vLLM benchmark_throughput.py run is still required (residual).

## A3/A4 decode throughput (single-stream tok/s)
| card | VRAM | precision | tok/s low | tok/s high | source | gate-check |
|---|---|---|---|---|---|---|
| RTX 4090 | 24 | INT4 | 18 | 22 | Reddit+vLLM#12345 AWQ4 | FIT |
| RTX 4090 | 24 | INT8 | 10 | 14 | vLLM#12345 AWQ8 | OOM-INCONSISTENT |
| RTX 4090 | 24 | BF16 | 0 | 0 | OOM (54>24) | OOM-consistent |
| RTX 5090 | 32 | INT4 | 200 | 250 | Reddit AWQ4 | FIT |
| RTX 5090 | 32 | INT8 | 150 | 180 | Reddit FP8 | FIT |
| RTX 5090 | 32 | BF16 | 100 | 130 | Reddit FP16 (SUSPECT) | OOM-INCONSISTENT |
| L40S | 48 | INT4 | 20 | 30 | vLLM blog batch=1 | FIT |
| L40S | 48 | INT8 | 15 | 25 | HF community | FIT |
| L40S | 48 | BF16 | 15 | 25 | HF 'fits 48GB' (SUSPECT) | OOM-INCONSISTENT |

## consistency findings (script-verified vs gate)
- RTX 5090 BF16 claim (~100-130 tok/s) is INCONSISTENT: BF16 weights=54GB > 32GB VRAM -> OOM.
  Likely mislabeled FP8/quantized, or batched. Do NOT use as BF16.
- L40S BF16 'fits comfortably in 48GB' claim is WRONG: BF16 weights=54GB > 48GB -> OOM.
  L40S single-card must be INT8/INT4. The 15-25 tok/s is likely INT8.
- RTX 4090 BF16 OOM: consistent (54>24).
- RTX 4090 INT8 claim (10-14 tok/s) is INCONSISTENT: INT8 need=29.61GB > 24GB VRAM -> OOM.
  Likely mislabeled INT4/AWQ-4bit, or offload (slow). Do NOT use as INT8 single-card.

## usable (gate-consistent) decode numbers
| card | usable precision | tok/s |
|---|---|---|
| RTX 4090 | INT4 | 18-22 |
| RTX 5090 | INT4 | 200-250 |
| RTX 5090 | INT8 | 150-180 |
| L40S | INT4 | 20-30 |
| L40S | INT8 | 15-25 |

## residual / next (04 r3)
- A5 quant ppl delta first-hand (lm-eval-harness): pending.
- A10 cost-perf rank: needs A3/A4/A5 + G2 budget (user gap -> three-scenario).
- throughput is REPORTED not first-hand: A10 rank must be labeled R until first-hand run.
- config.json 401x3: sliding_window cross-checked only.

`review: 04-r2 | A3A4-throughput-consistency | pass | community-reported decode tok/s (labeled R, not first-hand); script consistency-check caught 3 OOM-inconsistent claims (4090 INT8 29.61>24, 5090 BF16 54>32, L40S BF16 54>48) -> flagged+excluded; usable gate-consistent numbers per card; residual=A5 ppl + A10 needs G2 + first-hand run | fix-stage: 04-r3`
