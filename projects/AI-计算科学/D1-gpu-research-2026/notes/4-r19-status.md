origin: ai
time: 2026-09-27T21:05+08:00
stage: 04 / round: r19 / status: DONE (roofline ceiling proven a VALID UPPER BOUND incl previously-UNACCOUNTED KV-cache read traffic; quantified tightness 2.2%@8K / 11.6%@128K; teeth-proven)

# cursor: 04/r19 = roofline ceiling is honest (never exceeded) -- KV-cache traffic was silently ignored; now bounded

## ground-truth (re-confirm, honest-first)
- stop-hook "持久状态" (stage 02 / Ego Lite / partition-cover / well-founded μ) = GLOBAL formal-methods cursor, NOT this project.
- real cursor = notes/4-r18-status.md -> advanced to r19 here. Stayed GPU thread, did not restart.

## done this round (验证, not analysis — per "上一多为验证/分析 -> 本轮验证")
r18 proved the roofline MODEL applies (memory-bound). But the ceiling formula bw/weights_bytes silently assumed each
token reads ONLY the weights. Decode ALSO moves the KV cache every step (attention re-reads all prior K/V). That
traffic was UNACCOUNTED in every roofline number. inv11 (NEW) bounds it:
- true bytes/token = weights + KV_read_per_step ; roofline_true = bw/(weights+KV) <= bw/weights = my_ceiling.
  => my roofline is a VALID UPPER BOUND (never exceeded), which is exactly what a "ceiling" must satisfy.
- KV_read uses the SAME hybrid structure as the VRAM gate (full layers over full ctx, sliding over the 4096 window):
  kv_elems = 2*kv_heads(8)*head_dim(128)*(FULL_LAYERS*ctx + SLIDING_LAYERS*min(ctx,window)).
- quantified tightness: 8K -> KV=0.60GB vs weights=27GB -> 2.2% overhead (ceiling tight, realistic);
  128K -> KV=3.12GB -> 11.6% (ceiling ~12% looser at long context). Honest: the ceiling is a SHORT-context bound.

## why this matters (advance, not restate)
- Before r19: the ceiling ignored KV traffic -> it was an OPTIMISTIC bound of unknown looseness. A reviewer could
  ask "is 66 tok/s real or inflated by ignoring KV?" -> now answered: at 8K it's within 2.2% of the true bound,
  so the H* cost-perf numbers are not materially inflated. At 128K they'd be ~12% high -> flagged honestly.
- This is the SECOND-deepest assumption (after r18's regime): the ceiling's tightness. Both now machine-checked.

## honest boundary (unchanged, NOT loosened)
- KV overhead is computed from 一手✓ hybrid structure (configuration_gemma3.py) + 一手✓ ctx assumption (8K).
- throughput still roofline ceiling / community R; first-hand vLLM ENV-BLOCKED (Apple Silicon no CUDA).
- A100-40 bw 一手✓ BLOCKED (not fabricated); 5090/4090 branches 一手✓ grounded (inv8).

## precise blocking (deliverable advances ONLY on these; this round bounded the ceiling's honesty, not the answer)
1. form-factor = USER (Q1). 2. refurb A100-40 quote vs $1735 = USER/market (Q2). 3. refurb RTX 4090 quote vs
$1124 = USER/market (Q3). 4. first-hand single-stream vLLM = ENV (no CUDA).

## next concrete action
- autonomous 一手✓ + logic/regime/ceiling-tightness verification exhausted. Roofline now: inputs pinned (3/4),
  tree runs+tested (r17), regime proven (r18), ceiling proven valid-upper-bound + tightness quantified (r19).
- resting state: deliverable = self-resolving tree whose ceiling is now a PROVEN, quantified-tight upper bound.