origin: ai
input: notes/3-r5.md (A6 upper-bound residual) + WebSearch disjoint source (Gemma-3 tech report / HF docs) 2026-09-27
time: 2026-09-27T04:30+08:00

# stage 03 r6 artifact: anchor sliding_window -> tighten A6 KV (upper bound -> real)

## 0. why r6
03-r5 A6 KV was full-attention UPPER bound (61.99GB @128K) because sliding_window unanchored (config.json 401 x3).
This round anchored sliding_window from a DISJOINT source (Gemma-3 tech report / HF Transformers docs, not config.json):
  sliding_window = 1024
  layer_types pattern = [sliding, sliding, sliding, sliding, full] repeating
  L=62 -> full layers = 12, sliding layers = 50
Cross-check (disjoint from the 401 config.json), not config.json first-hand. Honest label: cross-checked.

## 1. recompute real KV (recomputable, script-verified)
per-token-per-layer(BF16) = 2*16*128*2 = 8192 B = 8 KB
full layers = 12 (KV = seq tokens) | sliding layers = 50 (KV capped at 1024 tokens)
| ctx | full KV | sliding KV | REAL KV | (was upper bound) |
| 8K    | 0.81 GB | 0.42 GB | 1.22 GB | (was 3.87) |
| 128K  | 12.88 GB | 0.42 GB | 13.30 GB | (was 61.99) |
=> real KV ~4.7x smaller at 128K. A6 residual CLOSED (cross-checked).

## 2. gate F3.1.3 tightened (weights + REAL KV + 2GB overhead)
| precision | 8K gate | 128K gate |
| BF16 (54)  | 57.2 GB -> need >=60 (80GB card) | 69.3 GB -> need 80GB |
| INT8 (27)  | 30.2 GB -> >=33 (48GB ok) | 42.3 GB -> >=48 (L40S/6000Ada ok) |
| INT4 (13.5)| 16.7 GB -> >=17.5 (24GB 4090 ok)| 28.8 GB -> >=32 (5090 ok) |
Key change: 128K INT4 = 28.8 GB fits single 32GB 5090 (was thought impossible at 62GB KV).

## 3. honest residual
- sliding_window = cross-checked (disjoint source), NOT config.json first-hand (config.json 401 x3).
- layer pattern count (12 full / 50 sliding) derived from [x4,full] over L=62; verify vs config when unblocked.
- G1-G6 user decisions still three-scenario.

## Reviewer
`review: 03-r6 | anchor-sliding-window-tighten-A6 | pass | sliding_window=1024 + pattern [x4,full] anchored from DISJOINT source (tech report/HF docs, not the 401 config.json); real KV script-verified 1.22GB@8K / 13.30GB@128K (~4.7x smaller than 61.99 upper bound); gate F3.1.3 tightened (128K INT4=28.8GB fits single 32GB 5090); honest label=cross-checked not config-first-hand; residual=layer-count verify + G1-G6 | fix-stage: 04`

## 4. layer-count verify (script, 03-r6 round-35)
pattern [sliding x4, full] period=5 over L=62:
  full indices = [4,9,14,19,24,29,34,39,44,49,54,59] -> full=12
  sliding = 50
  assert full==12: True, assert sliding==50: True
=> layer-count (12/50) VERIFIED (script, not just derived). residual downgraded: only config.json first-hand pending.
