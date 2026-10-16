origin: ai
time: 2026-09-28T00:20+08:00
stage: 04 / round: r27 / status: DONE (inv19 KV-cache precision: inv11/inv18 computed KV bytes/token AND KV VRAM with GATE[prec] = the SAME bytes/param as the WEIGHTS, but real inference engines (vLLM/TGI) store the KV cache in FP16 INDEPENDENTLY of the weight quant (GPTQ/AWQ INT4 loads INT4 weights yet ALLOCATES an FP16 KV cache) -> true KV bytes/token = kv_elems*2.0 not kv_elems*GATE -> inv11 UNDERSTATED KV traffic by 4x(INT4)/2x(INT8) -> roofline OVERESTIMATES throughput AND UNDERSTATES VRAM by the KV-precision gap; 4th optimism layer on the bytes side, DISTINCT from inv18 (weight metadata != KV precision); proved EXACTNESS UNNECESSARY -- ceiling still valid (FP16 KV > quant-KV -> roofline_true even lower), H* DECISION KV-precision-invariant (same model+engine -> FP16-KV term cancels in the break-even ratio -> be=$1735 unchanged), VRAM gate survives (recompute every fit with REAL FP16 KV -> no fit flips; tightest INT8/5090 tol 6.6% > band))

# cursor: 04/r27 = the KV cache is FP16, not the weight quant -- the 4th bytes-side optimism layer, bounded and the decision invariant to it

## ground-truth (re-confirm, honest-first)
- stop-hook "持久状态" (stage 02 / Ego Lite / partition-cover / well-founded μ) = GLOBAL formal-methods cursor, NOT this project.
- real cursor = notes/4-r26-status.md -> advanced to r27 here. Stayed GPU thread, did not restart.

## done this round (验证, not analysis — per "上一多为分析结论 -> 本轮验证")
inv11/inv18 computed the KV-cache bytes/token (and KV VRAM) with GATE[prec] -- the SAME bytes/param as the WEIGHTS.
But real inference engines (vLLM, TGI) store the KV cache in FP16 (or opt-in FP8) INDEPENDENTLY of the weight
quantization: a GPTQ/AWQ INT4 checkpoint loads INT4 weights yet ALLOCATES an FP16 KV cache (the running attention
state stays high-precision; only the static weights are quantized). So the TRUE KV bytes/token = kv_elems*2.0 (FP16),
NOT kv_elems*GATE[prec] -> inv11 UNDERSTATED KV traffic by 4x (INT4) / 2x (INT8) -> the roofline OVERESTIMATES
throughput AND UNDERSTATES VRAM by the KV-precision gap. No local vLLM / no safetensors runtime -> cannot confirm
the exact KV dtype 一手✓ (ENV-BLOCKED). Prove EXACTNESS IS UNNECESSARY (inv14/17/18 pattern):
- (1) ceiling STILL VALID (4th optimism layer, SAME direction as inv11/inv18): FP16 KV > quantized-KV -> more
  bytes/token -> roofline_true even LOWER than inv11's quantized-KV estimate, strictly below the bare ceiling.
  INT4: KV FP16=1.21GB vs quant-KV=0.30GB (4x) -> overhead 8.9% of weights -> roof_true=121.8<=ceiling=132.7;
  INT8: KV FP16=1.21GB vs quant-KV=0.60GB (2x) -> overhead 4.5% -> roof_true=63.5<=ceiling=66.4.
- (2) H* DECISION KV-PRECISION-INVARIANT: FP16 KV adds the SAME bytes/token to BOTH cards (same model + same engine)
  -> cancels in the break-even RATIO -> be=$1735 unchanged. The hardware choice does not depend on the KV dtype.
- (3) VRAM gate SURVIVES: recompute EVERY fit with the REAL FP16 KV cache -> no fit verdict flips; the tightest
  (INT8/5090) tolerance shrinks to 6.6% but stays > band 2% -> FP16 KV does NOT loosen the gate.

## teeth-proven
- teeth(a): leaky break-even (FP16-KV on the A100 numerator only, quant-KV denominator) = $1697 != $1735 -> MOVES
  -> the invariance test DETECTS a future formula that lets the KV dtype leak into the decision.
- teeth(b): inflate the KV dtype past the INT8/5090 tolerance -> OOM -> the gate check BITES against the real threat.
- [A] normal: green exit0, prints 4x/2x KV inflation, be=$1735 invariant, teeth(a)=$1697 moves.
- [B] canary: sed KV_PREC_BYTES 2.0->4.5 -> INT8/5090 total=31.72GB still <=32 but tolerance collapses to
  1.0% < band 2% -> inv19(3) RED exit1 ✓ (proves the tolerance check bites against a real KV-precision inflation,
  not a strawman). Restored -> green exit0.
- [C] full gate: run_all.py 3 suites ALL GREEN exit0.

## why this matters (advance, not restate)
- This is the FOURTH optimism layer on the bytes side (after inv11 KV-existence, inv13 eta on the BW side, inv18
  weight-metadata) and is DISTINCT from inv18: inv18 was about the WEIGHTS' per-group scale/zero-point; inv19 is
  about the KV cache's PRECISION being decoupled from the weight quant. Together the bytes/token is now bounded from
  four independent directions (weights bare bits -> +KV traffic -> +weight meta -> +KV precision), each pushing the
  true bytes/token UP so the ceiling is known looser but NEVER exceeded. Honest-first: I do NOT claim the exact KV
  dtype (no local vLLM runtime); I use FP16 (the LARGER realistic default, vLLM dtype='auto'->fp16/bf16) which is
  CONSERVATIVE -- if even FP16 KV fits, the opt-in FP8 does too -- and prove the H* DECISION is invariant to it.

## honest boundary (NOT loosened)
- KV cache dtype not 一手✓ (no local vLLM/TGI runtime, ENV-BLOCKED); FP16 = well-known default (社区R), used as a
  GENEROUS upper bound (FP8 is opt-in and smaller) -> conclusion conservative.
- exact quant overhead (inv18) and KV dtype (inv19) both not 一手✓; the INVARIANCE + TOLERANCE proofs make them
  unnecessary for the deliverable.
- throughput still roofline ceiling / community R; first-hand vLLM single-stream BLOCKED (Apple Silicon no CUDA) --
  which would also settle both the eta (inv13) and the real KV-dtype questions at once.
- A100-40 bw 一手✓ BLOCKED (not fabricated); 5090/4090 branches 一手✓ grounded (inv8).

## precise blocking (deliverable advances ONLY on these; this round bounded the KV-precision premise)
1. form-factor = USER (Q1). 2. refurb A100-40 quote vs $1735 = USER/market (Q2). 3. refurb RTX 4090 quote vs $1124
= USER/market (Q3). 4. first-hand single-stream vLLM = ENV (no CUDA) -- also answers eta (inv13) AND KV dtype (inv19).

## next concrete action
- premise chain now complete through the KV-cache precision floor: regime (inv10) + traffic terms (inv11 KV-bytes,
  inv15 attention-flops) + cache-cannot-absorb (inv16) + sparsity-invariance (inv17) + quant-metadata-overhead
  (inv18) + KV-PRECISION (inv19) + eta (inv13) + constants (inv8/inv14) + cross-file (inv12) + tree (r17/inv9).
  Every remaining unknown is ENV/USER-gated. Offline advance genuinely exhausted.