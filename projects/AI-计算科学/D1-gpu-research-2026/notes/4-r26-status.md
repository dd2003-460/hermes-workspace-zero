origin: ai
time: 2026-09-27T23:55+08:00
stage: 04 / round: r26 / status: DONE (inv18 quant-metadata overhead: GATE bytes_per_param = prec_bits/8 treats each weight as EXACTLY that many bytes, IGNORING the per-group scale/zero-point every real groupwise quant stores alongside the weights -> true bytes/token > PARAMS*bp -> roofline OVERESTIMATES throughput AND UNDERSTATES VRAM by (1+meta); no local safetensors header / no transformers -> cannot confirm exact overhead 一手✓ (ENV-BLOCKED); proved EXACTNESS IS UNNECESSARY -- ceiling still valid (3rd optimism layer, same direction as inv11 KV), H* DECISION metadata-invariant ((1+meta) cancels in the break-even ratio), VRAM gate survives (worst-case overhead < tightest tolerance))

# cursor: 04/r26 = the roofline's bytes/param is a floor, not the whole story — quant metadata overhead is bounded and the decision is invariant to it

## ground-truth (re-confirm, honest-first)
- stop-hook "持久状态" (stage 02 / Ego Lite / partition-cover / well-founded μ) = GLOBAL formal-methods cursor, NOT this project.
- real cursor = notes/4-r25-status.md -> advanced to r26 here. Stayed GPU thread, did not restart.

## done this round (验证, not analysis — per "上一多为分析结论 -> 本轮验证")
GATE bytes_per_param = {INT4:0.5, INT8:1.0, BF16:2.0} = prec_bits/8 treats every weight as EXACTLY that many bytes. But
every REAL groupwise quantization format (GPTQ/AWQ INT4/INT8) stores ALONGSIDE the weights a per-group fp16 SCALE +
zero-point. That metadata ADDS bytes/param -> true bytes/token = PARAMS*bp*(1+meta) > PARAMS*bp -> the roofline
OVERESTIMATES throughput AND UNDERSTATES VRAM by (1+meta). No local safetensors header / no transformers -> cannot
confirm the exact overhead 一手✓ (ENV-BLOCKED). Prove EXACTNESS IS UNNECESSARY (same pattern as inv14/inv17):
- (1) ceiling STILL VALID (3rd optimism layer, SAME direction as inv11 KV): more bytes/token -> roofline_true =
  bw/(weights*(1+meta)+KV) is STRICTLY LOWER than bw/weights = ceiling. INT4 +6.2% -> 122.4<=132.7; INT8 +3.1% ->
  63.0<=66.4. The ceiling is now known to be even looser, never exceeded.
- (2) H* DECISION METADATA-INVARIANT: (1+meta) scales BOTH cards' bytes/token (same model + same quant on both) ->
  cancels in the break-even RATIO -> be=$1735 unchanged. The hardware choice does not depend on the metadata overhead.
- (3) VRAM gate SURVIVES: worst-case metadata overhead (+6.2% INT4, +3.1% INT8) < the tightest fit tolerance (INT8/5090
  recomputed WITH metadata = ~5.6% > band 2%) -> no fit verdict flips.

## teeth-proven
- teeth(a): leaky break-even (metadata applied to the A100 numerator only, dense denominator) = $1682 != $1735 -> MOVES
  -> the invariance test DETECTS a future formula that lets metadata leak into the decision.
- teeth(b): inflate metadata past the INT8/5090 tolerance -> OOM -> the gate check BITES against the real threat.
- [A] normal: green exit0, prints +6.2%/+3.1% overhead, be=$1735 invariant, teeth(a)=$1682 moves.
- [B] canary: sed META_BYTES_PER_PARAM 4.0/128(=0.03125)->0.085 -> INT8/5090 total=31.90GB<32 but tolerance collapses
  to 0.3%<band 2% -> inv18(3) RED exit1 ✓ (proves the tolerance check bites against a real metadata inflation, not a
  strawman). Restored -> green exit0.
- [C] full gate: run_all.py 3 suites ALL GREEN exit0.
- honest bug caught: first draft referenced inv14's BAND which is defined LATER in the file -> NameError (same forward-ref
  class as inv17's BE_A100_BE); fixed with a local META_BAND=0.02 re-declaration.

## why this matters (advance, not restate)
- This is the THIRD optimism layer on the bytes side (after inv11's KV traffic and inv13's eta on the BW side): the
  roofline's bytes/param was a FLOOR (bare weight bits), not the full bytes/token. Quant metadata pushes the true
  bytes/token up, so the ceiling is even looser than previously stated -- but the deliverable's H* DECISION is
  INVARIANT to it (cancels in the ratio) and the VRAM gate TOLERATES it (overhead < tolerance). So the choice of
  hardware does not hinge on the quant format's metadata size. Honest-first: I do NOT claim the exact overhead (no
  safetensors header locally); I prove the decision does not depend on it and the gates tolerate a GENEROUS upper bound.

## honest boundary (NOT loosened)
- META_BYTES_PER_PARAM=4/128 is a GENEROUS UPPER bound (fp16 scale + fp16 zero-point per 128-param group); using the
  upper bound makes the conclusion conservative (if even the largest plausible overhead fits, the real one does).
- exact quant overhead not 一手✓ (no local safetensors header, no transformers, ENV-BLOCKED); the INVARIANCE + TOLERANCE
  proofs make it unnecessary.
- throughput still roofline ceiling / community R; first-hand vLLM single-stream BLOCKED (Apple Silicon no CUDA).
- A100-40 bw 一手✓ BLOCKED (not fabricated); 5090/4090 branches 一手✓ grounded (inv8).

## precise blocking (deliverable advances ONLY on these; this round bounded the quant-metadata premise)
1. form-factor = USER (Q1). 2. refurb A100-40 quote vs $1735 = USER/market (Q2). 3. refurb RTX 4090 quote vs $1124
= USER/market (Q3). 4. first-hand single-stream vLLM = ENV (no CUDA) -- also answers the eta question (inv13).

## next concrete action
- premise chain now complete through the bytes-per-param floor: regime (inv10) + traffic terms (inv11 KV-bytes, inv15
  attention-flops) + cache-cannot-absorb (inv16) + sparsity-invariance (inv17) + quant-metadata-overhead (inv18) +
  eta (inv13) + constants (inv8/inv14) + cross-file (inv12) + tree (r17/inv9). Every remaining unknown is ENV/USER-gated.
  Offline advance genuinely exhausted.