origin: ai
time: 2026-09-27T04:10+08:00
stage: 03
round: r5
status: PASS (re-ground A1/A6/A8 on first-hand G1)

# 3-r5 status (ASCII, clean)

## cursor advance
- 02.5/r3 PASS (G1 first-hand anchored) -> advance to 03.
- 03 had r1-r4 (r4 pass on old 02.5 estimate) -> this is r5 (next free round, honest collision).

## done (first-hand)
- A1 weights: BF16 54GB / INT8 27GB / INT4 13.5GB (dtype BF16 first-hand).
- A6 KV: 0.484 MB/token (GQA kv_heads=16, head_dim=128, L=62 first-hand).
- A8 card-count vs gate F3.1.3 (BF16>=60 / INT8>=33 / INT4>=17.5 GB).

## residual
- sliding_window unanchored (config.json 401) -> A6 KV upper bound; TODO 04.
- G1-G6 user decisions -> three-scenario.

## next
- 04: sliding_window anchor + first-hand price/throughput -> A10 rank.
