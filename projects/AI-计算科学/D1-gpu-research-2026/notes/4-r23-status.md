origin: ai
time: 2026-09-27T22:20+08:00
stage: 04 / round: r23 / status: DONE (inv15 attention-FLOPs regime: inv10's AI counted ONLY the weights traffic and never the per-step ATTENTION FLOPs on the KV cache, which grow LINEARLY with context -> if they dominated, decode would flip COMPUTE-bound and bw/bytes would be the WRONG ceiling; proved roofline survives INCLUDING attention, at every ctx, and even in the attention-DOMINANT limit ctx->inf)

# cursor: 04/r23 = the roofline's fourth silent gap (unaccounted attention FLOPs) closed; ceiling VALID at all ctx

## ground-truth (re-confirm, honest-first)
- stop-hook "持久状态" (stage 02 / Ego Lite / partition-cover / well-founded μ) = GLOBAL formal-methods cursor, NOT this project.
- real cursor = notes/4-r22-status.md -> advanced to r23 here. Stayed GPU thread, did not restart.

## done this round (验证, not analysis — per "上一多为分析结论 -> 本轮验证")
inv10 (r18) proved decode is MEMORY-bound using AI = 2/bytes_per_param — but that counted ONLY the WEIGHTS traffic
(flops=2*params, bytes=params*bp). It NEVER counted the per-step ATTENTION FLOPs (QK^T + PV matmuls on the KV
cache), which grow LINEARLY with context length. r19 (inv11) accounted the KV *bytes* but not the attention *flops*.
This was the last un-accounted traffic term. inv15 (NEW) adds the attention term to BOTH sides of AI and proves the
roofline SURVIVES including attention:
- (1) per-ctx loop: true AI = (weights_flops + attn_flops)/(weights_bytes + attn_bytes). At 8K attention adds only
  +2% (2.03 vs 2.0); at 128K it adds +45% (2.90 vs 2.0) — attention grows fast — but BOTH stay far below ridge
  27.9 -> memory-bound holds at every context length tested.
- (2) the DECISIVE limit: as ctx->inf the fixed 27GB weight traffic VANISHES relative to attention -> AI ->
  attention-only asymptote = ATTN_MULT * 2 * KV_LAYERS/FULL_LAYERS = 12.4 flops/byte. Even the WORST case (weights
  gone, attention dominant) is 12.4 < ridge 27.9 -> a 2.3x floor -> roofline VALID at ALL context lengths, not just
  short ones. This is strictly stronger than inv11's "ceiling is a short-context bound" — the REGIME survives to inf.

## teeth-proven (caught a decorative-check bug in my own invariant, then fixed + re-proved)
- DESIGN BUG caught by test-the-test: first draft hardcoded attn_asymptote = 2*KV_LAYERS/FULL_LAYERS WITHOUT the
  ATTN_MULT knob -> sed ATTN_MULT would NOT move the asymptote -> the teeth were decorative (a check that cannot
  fail). Fixed: asymptote now scales with ATTN_MULT (physical: attention-only AI = ATTN_MULT*2*L/FULL).
- [A] normal: green exit0, prints attention +2%@8K / +45%@128K, asymptote 12.4 < ridge 27.9 (2.3x floor).
- [B] canary: sed ATTN_MULT 1.0->3.0 -> asymptote 12.4->37.2 >= ridge 27.9 -> inv15 RED exit1 ✓ (proves the
  asymptote check has teeth against the actual threat model: a heavier attention kernel CAN flip decode compute-bound).
- [C] full gate: run_all.py 3 suites ALL GREEN exit0.

## why this matters (advance, not restate)
- The roofline's memory-bound regime was only ever proven for the WEIGHTS traffic. Attention is the OTHER traffic source
  and it is the one that GROWS with the workload (ctx). Proving the regime survives even when attention dominates (the
  ctx->inf limit) closes the last hole in the foundation: bw/bytes is the right ceiling not just at 8K but at any
  context length a user might run. The 2.3x floor at the asymptote is the honest margin — thinner than inv10's 7x at
  weights-only, because attention eats into it, but still comfortably above the ridge.
- Honest-first: the margin NARROWS with ctx (7x weights-only -> 2.3x attention-dominant limit). I report the floor,
  not the flattering short-ctx number.

## honest boundary (NOT loosened)
- attention flops use the standard 4*L*kv_heads*head_dim*ctx (QK^T+PV); ATTN_MULT=1.0 = standard attention, the
  canary's 3.0 is a hypothetical heavier kernel, NOT measured. A genuinely quadratic-attention model would break the
  roofline at long ctx — Gemma-3 uses softmax/hybrid attention (linear KV read per step), so ATTN_MULT=1 is correct
  for this model; the invariant proves the regime is robust to up to ~2.2x kernel inflation before flipping.
- throughput still roofline ceiling / community R; first-hand vLLM single-stream BLOCKED (Apple Silicon no CUDA).
- A100-40 bw 一手✓ BLOCKED (not fabricated); 5090/4090 branches 一手✓ grounded (inv8).

## precise blocking (deliverable advances ONLY on these; this round closed the last traffic-term gap in the regime proof)
1. form-factor = USER (Q1). 2. refurb A100-40 quote vs $1735 = USER/market (Q2). 3. refurb RTX 4090 quote vs $1124
= USER/market (Q3). 4. first-hand single-stream vLLM = ENV (no CUDA) -- also answers the eta question (inv13).

## next concrete action
- silent-assumption audit now spans: inputs (inv8), tree (r17/inv9), regime-weights (inv10), ceiling-KV-bytes (inv11),
  cross-file (inv12), eta (inv13), PARAMS (inv14), regime-attention-flops (inv15). Every traffic term and constant the
  roofline rests on is now accounted or bounded. Offline advance genuinely exhausted; resting state honest + characterized.