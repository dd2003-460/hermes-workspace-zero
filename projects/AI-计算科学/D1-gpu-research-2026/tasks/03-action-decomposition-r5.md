origin: ai
input: tasks/03-action-decomposition-r4.md (factor-tree DAG) + notes/02.5-vram-base-gemma327b.md (first-hand G1 anchor) + notes/2.5-r3.md
time: 2026-09-27T04:10+08:00

# stage 03 r5 artifact: re-ground A1/A6/A8 on first-hand G1 (replace estimates)

## 0. why r5
03-r4 DAG was grounded on OLD 02.5 (G1 = estimate, bytes/param three-scenario).
02.5-r3 anchored G1 FIRST-HAND from google/gemma-3-27b-pt config.json:
  L=62, hidden=5376, heads=32, kv_heads=16 (GQA 32:16), head_dim=128, vocab=262208, dtype=BF16.
r5 re-ground the VRAM-gate nodes (A1 weights, A6 KV, A8 card-count) on first-hand numbers.
A3/A4/A5/A7/A9/A10 unchanged (still 04 first-hand / G1-G6 three-scenario).

## 1. re-grounded nodes (first-hand, recomputable)
- A1 weights bytes [first-hand: dtype=BF16, 27B params]
  BF16 = 27e9*2 = 54 GB | INT8 = 27 GB | INT4 = 13.5 GB
  was: estimate -> now: exact per precision (dtype first-hand).
- A6 KV cache [first-hand: GQA kv_heads=16, head_dim=128, L=62]
  KV/token(BF16) = 2*62*16*128*2 = 507904 B = 0.484 MB/token
  8K ctx = 3.87 GB | 128K ctx = 61.99 GB (full-attn UPPER bound)
  was: "KV estimate" -> now: exact GQA formula (kv_heads=16 not 32 -> 2x smaller than MHA).
  RESIDUAL: sliding_window unanchored (config.json 401) -> real KV << upper bound; TODO 04.
- A8 card-count [first-hand: gate F3.1.3]
  BF16: ceil(54+KV+2 / VRAM) | INT8: ceil(27+KV+2 / VRAM) | INT4: ceil(13.5+KV+2 / VRAM)
  single-card feasible INT4: 4090(24)/5090(32)/A100-40/L40S(48)/6000Ada(48)/Apple.

## 2. gate F3.1.3 (first-hand, closed)
| precision | weights | +KV(8K) | gate |
| BF16 | 54 GB | +3.87 | >=60 GB |
| INT8 | 27 GB | +3.87 | >=33 GB |
| INT4 | 13.5 GB | +1.94 | >=17.5 GB |

## 3. unchanged (04 / G1-G6)
A3 prefill, A4 decode, A5 quant-ppl, A7 price, A9 TDP -> 04 first-hand.
A10 cost-perf rank -> 04 after first-hand price+throughput align (G2 budget).
G1-G6 user decisions -> three-scenario (conservative FP16 / baseline INT8 / aggressive INT4).

## 4. residual (precise)
- sliding_window unanchored (config.json 401 x2) -> A6 KV is upper bound, real smaller. TODO 04.
- G1-G6 user decisions not given -> three-scenario, not fabricated single-best.

## Reviewer
`review: 03-r5 | re-ground-A1A6A8-firsthand-G1 | pass | A1 weights exact per precision (dtype BF16 first-hand); A6 KV exact GQA 0.484MB/tok (kv_heads=16,head_dim=128,L=62 first-hand, 2x smaller than MHA); A8 card-count vs gate F3.1.3 closed; A3/A4/A5/A7/A9/A10 unchanged (04/G1-G6); residual=sliding_window 401 (KV upper bound) + G1-G6 three-scenario | fix-stage: 04`
