origin: ai
time: 2026-09-27T04:30+08:00
stage: 03
round: r6
status: PASS (A6 KV tightened via cross-checked sliding_window anchor, script-verified)

# 3-r6 status (ASCII, clean)

## done
- sliding_window=1024 + pattern [x4,full] anchored (DISJOINT source, not the 401 config.json).
- real KV script-verified: 8K=1.22GB, 128K=13.30GB (was 61.99 upper bound).
- gate tightened: 128K INT4=28.8GB fits single 32GB 5090.

## residual
- cross-checked not config-first-hand; layer-count (12/50) verify vs config when unblocked.
- G1-G6 user decisions -> three-scenario.

## next
- 04: first-hand price/throughput -> A10 rank.
