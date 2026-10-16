origin: ai
time: 2026-09-27T23:20+08:00
stage: 04 / round: r25 / status: DONE (inv17 sparsity-invariance: the roofline's premise "each token reads ALL 27B params" silently assumes the model is DENSE; if MoE-sparse, bytes/token = active params only and bw/bytes would OVERESTIMATE throughput; no local config/transformers -> cannot confirm dense 一手✓ (ENV-BLOCKED); proved EXACTNESS IS UNNECESSARY -- the H* DECISION is SPARSITY-INVARIANT (active fraction cancels in the break-even ratio, same model on both cards) AND the VRAM gate is UNAFFECTED (all experts stay resident regardless of activation))

# cursor: 04/r25 = the dense-vs-MoE premise is bounded -- the decision is invariant to it, the VRAM gate ignores it

## ground-truth (re-confirm, honest-first)
- stop-hook "持久状态" (stage 02 / Ego Lite / partition-cover / well-founded μ) = GLOBAL formal-methods cursor, NOT this project.
- real cursor = notes/4-r24-status.md -> advanced to r25 here. Stayed GPU thread, did not restart.

## done this round (验证, not analysis — per "上一多为分析结论 -> 本轮验证")
The roofline bw/bytes premise "each token reads ALL 27B params" silently assumes the model is DENSE (every token
activates every parameter). If it were a sparse MoE, bytes/token = ACTIVE params only, and bw/bytes would OVERESTIMATE
throughput by 1/active-fraction. No local Gemma-3-27B config and no transformers installed -> cannot confirm dense
一手✓ (ENV-BLOCKED). But, exactly as inv14 did for PARAMS, prove EXACTNESS IS UNNECESSARY:
- (1) SPARSITY-INVARIANCE of the H* DECISION: roofline ~ 1/(P*fr) for EVERY card (same model -> same active fraction
  fr on both), so the break-even RATIO p_be = price_5090*(bw_A/(P*fr*bp))/(bw_5090/(P*fr*bp)) cancels fr -> p_be is
  INVARIANT to the active fraction. Proved: be=$1735 at fr=1.0 (dense) AND fr=0.111 (MoE-A3B-like), identical. The
  H* choice does not depend on whether the model is dense or sparse.
- (2) VRAM gate UNAFFECTED: a MoE must keep ALL experts RESIDENT in VRAM (you need every expert loaded even though
  only some run per token), so VRAM bytes = FULL PARAMS, not active. Proved: full-resident INT8=27GB > 4090 24GB ->
  4090 correctly OUT at INT8; the WRONG sparse-resident physics (active-only=3GB) would falsely pass 4090 -> the
  full-resident requirement is REAL and sparsity does NOT loosen the gate.

## teeth-proven (caught a no-op canary, then re-proved with a real injection)
- FIRST canary was a NO-OP: sed'd vram_int8_full to use ACTIVE_FRAC but ACTIVE_FRAC=1.0 by default -> multiply-by-1
  -> value unchanged (27GB) -> EXIT stayed 0 -> the canary did NOT bite (a canary that can't fail is decorative).
  Caught it (printed 27GB despite the edit), re-injected the WRONG physics directly (hardcode 0.111).
- [A] normal: green exit0, be $1735 at fr=1.0 & 0.111, teeth(a) leaky be=$15627 moves, teeth(b) full=27>24.
- [B] canary: sed vram_int8_full -> PARAMS*0.111*bp (sparse-resident, wrong) -> INT8 27->3GB <= 24GB -> inv17
  teeth(b) RED exit1 ✓ (proves the full-resident check bites against the real threat: a sparse-resident VRAM error).
- [C] full gate: run_all.py 3 suites ALL GREEN exit0.

## why this matters (advance, not restate)
- Completes the premise chain one layer deeper: inv16 proved the weights can't be cache-absorbed (so they stream from
  VRAM); inv17 proves that even if the model were MoE-sparse, the deliverable's H* DECISION is unchanged (the active
  fraction cancels in the ratio) and the VRAM gate is unchanged (experts must be resident). So the only thing sparsity
  could change is the ABSOLUTE roofline tok/s -- which is already community-R / ENV-BLOCKED anyway. The choice of
  hardware does not hinge on dense-vs-MoE. Honest-first: I do NOT claim Gemma-3-27B is dense (cannot confirm, no
  config); I prove the decision does not depend on it.

## honest boundary (NOT loosened)
- dense-vs-MoE not 一手✓ (no local config, no transformers, ENV-BLOCKED); the INVARIANCE proof makes it unnecessary.
  If the model turned out MoE, absolute tok/s would rise (fewer bytes/token) but every card rises proportionally -> the
  ranking and break-even are untouched; only the (already community-R) absolute numbers shift.
- throughput still roofline ceiling / community R; first-hand vLLM single-stream BLOCKED (Apple Silicon no CUDA).
- A100-40 bw 一手✓ BLOCKED (not fabricated); 5090/4090 branches 一手✓ grounded (inv8).

## precise blocking (deliverable advances ONLY on these; this round bounded the dense-vs-MoE premise)
1. form-factor = USER (Q1). 2. refurb A100-40 quote vs $1735 = USER/market (Q2). 3. refurb RTX 4090 quote vs $1124
= USER/market (Q3). 4. first-hand single-stream vLLM = ENV (no CUDA) -- also answers the eta question (inv13).

## next concrete action
- premise chain now complete through sparsity: regime (inv10) + traffic terms (inv11/inv15) + cache-cannot-absorb
  (inv16) + dense-vs-MoE-invariance (inv17) + eta (inv13) + constants (inv8/inv14) + cross-file (inv12) + tree
  (r17/inv9). Every remaining unknown is ENV/USER-gated. Offline advance genuinely exhausted.