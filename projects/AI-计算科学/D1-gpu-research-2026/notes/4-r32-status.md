origin: ai
time: 2026-09-28T06:00+08:00
stage: 04 / round: r32 / status: DONE (IMPLEMENTATION: attack the WORKING-SEQUENCE-LENGTH / CTX axis -- the VRAM feasibility gate has ALWAYS been evaluated at CTX=8K (the context dimension was SILENTLY fixed to 8K; "fits in VRAM" holds ONLY for short context). At CTX=L the FULL-ATTENTION layers' KV grows linearly with L (sliding-window layers stay capped@4096) -> VRAM = weights + KV(8K) + full_layers*ctx*kv_per_token RISES with ctx -> crosses the 32GB ceiling at a critical context L*~122K -> the 5090 INT8 OVERFLOWS at 128K input -> the deliverable's FEASIBILITY (not just throughput) is CTX-DEPENDENT -> working-sequence-length is a NEW required input Q5. Encoded into roofline_verify.py (inv23) + registered as required input Q5 in the deliverable resolve_hstar.py.)

# cursor: 04/r32 = the VRAM feasibility gate invisibly assumed CTX=8K -- proved the 5090 INT8 overflows 32GB at 128K input, surfaced working-sequence-length as a NEW required input Q5

## ground-truth (re-confirm, honest-first)
- stop-hook "持久状态" (stage 02 / Ego Lite / partition-cover / well-founded μ) = GLOBAL formal-methods cursor, NOT this project.
- real cursor = notes/4-r31-status.md -> advanced to r32 here. Stayed GPU thread, did not restart.
- guardrail satisfied: r31 attacked the BATCH axis (throughput P); r32 attacks a NEW axis (CTX, the FEASIBILITY gate -- never a knob).

## the genuine NEW axis this round (the context dimension was silently fixed to 8K)
- inv8 pinned VRAM=32GB and the whole gate (bytes<=GB) was evaluated at CTX=8K without ever naming CTX. "fits in
  VRAM" is a CTX=8K-specific claim. At CTX=L: the FULL-ATTENTION layers keep the WHOLE sequence's KV (grows ~linearly
  with L), the SLIDING-WINDOW layers stay capped@4096 -> bytes = weights + kv(8K) + FULL_LAYERS*(L-8K)*kv_per_tok
  RISES with L -> crosses the 32GB ceiling at a critical context L* -> the 5090 INT8 OVERFLOWS beyond L*.
- DISTINCT from inv22 (that was BATCH: batched decode changes bytes/token via weight amortization /B, a THROUGHPUT
  effect; this is CTX: the per-sequence KV footprint changes the CAPACITY feasibility, a DIFFERENT quantity). And
  DISTINCT from inv11/inv19 (those bounded KV *traffic* per token at 8K; NONE asked how the KV *footprint* grows
  when the context itself grows past 8K).

## done this round (implementation + verification)
### roofline_verify.py -- inv23 (the roofline-side proof)
- vram_at_ctx(card,prec,ctx) = weights_bytes + kv_fp16(8K) + FULL_LAYERS*max(0,ctx-8K)*kv_per_token_fp16 (full
  layers grow with ctx, sliding capped@4096).
- inv23(1): 5090 INT8 VRAM CTX=8K=29.60GB (fits<=32 True) -> CTX=128K=32.12GB (1.1x: full layers x16, sliding
  capped@4096) -> OVERFLOWS 32GB (fits False) -> the feasibility gate is CTX-DEPENDENT.
- inv23(2): critical context L* = first ctx where 5090 INT8 overflows = ~122K (between 8K and 128K) -> the 5090
  INT8 is feasible ONLY below L*; above it needs INT4 (halves KV) or a 40/48GB card.
- inv23(3): at the TRUE FP16 KV (inv19) 5090 INT8@128K=35.24GB -> overflow is ROBUST (holds under quant-KV
  32.12GB AND FP16-KV 35.24GB).
- inv23 teeth: freeze full-layer KV@8K (pretend full layers DON'T grow with ctx) -> vram@128K=29.60GB FITS 32GB
  -> the real 32.12GB overflow is CAUSED by full-layer KV growing x16 with ctx -> the CTX-sensitivity check BITES.
### resolve_hstar.py -- deliverable: register working-sequence-length as required input Q5
- REQUIRED_INPUTS registry now {Q1 form-factor, Q2 A100-40 quote, Q3 4090 quote, Q4 batch size, Q5 working-sequence-
  length / CTX}; guard fails if "Q5 working-sequence-length" not declared -> the tree must never present a
  VRAM-feasibility verdict as ctx-invariant.

## teeth-proven (all, EXIT captured DIRECTLY -- no grep-pipe PIPESTATUS reset)
- roofline_verify.py: [A] normal EXIT=0; [B] canary freeze full-layer KV growth -> vram@128K fits -> teeth fires
  -> EXIT=1 ✓; [C] run_all.py EXIT=0.
- resolve_hstar.py: [A] normal EXIT=0. [B] deliverable guard teeth: delete ONLY the Q5 entry (`sed '/Q5 working-
  sequence-length \/ CTX/d'`, entry-unique substring "/ CTX" absent from the guard) -> guard survives (grep count 1)
  -> canary runs INSIDE tasks/ (import resolves) -> fires RED for the RIGHT reason: `RESULT: FAIL -> inv23:
  working-sequence-length NOT declared a required input -> the tree silently assumes CTX=8K` -> EXIT=1 ✓. Restored
  -> [A] EXIT=0, [C] run_all.py EXIT=0.
- NOTE: two FALSE teeth-proves were caught on the way and avoided -- (1) copying the canary to /tmp raised
  ModuleNotFoundError (sys.path resolves to /tmp) -> wrong cause; ran INSIDE tasks/ instead. (2) an earlier
  `sed '/Q4 batch size/d'` deleted BOTH the Q4 entry AND the inv22 guard (both contain "Q4 batch size") -> guard
  gone -> false PASS; this round used the Q5 entry's UNIQUE substring "/ CTX" so only the data row is removed.

## why this matters (advance, not restate)
- This surfaces a SECOND NEW REQUIRED INPUT the deliverable never asked for: WORKING-SEQUENCE-LENGTH (CTX). The whole
  VRAM gate (and the "5090 fits 27B INT8" headline) is a CTX=8K figure. If the deployment runs LONG-context (e.g.
  128K, which Gemma-3 advertises), the 5090 INT8 OVERFLOWS 32GB -> the card is INFEASIBLE at that context -> the
  H* recommendation flips to INT4 (halves KV, but inv21 says sm_100 GPTQ INT4 kernel is reported lagging!) or a
  bigger-memory card (A100-40 / L40S). So the deliverable's criterion R=P/C is incomplete without BOTH a batch spec
  (Q4) AND a context spec (Q5). Honest: at CTX<=~122K single-stream (the stated anchor) the 5090 INT8 is VALID.

## honest boundary (NOT loosened)
- L*~122K is a roofline-model figure at the stored KV accounting (FULL_LAYERS=10, kv_per_token_fp16). 一手✓ arithmetic
  on the model. The exact crossover depends on the real KV dtype (inv19, ENV-BLOCKED) and the real prompt/gen split
  (inv20, ENV-BLOCKED).
- the ceiling-based RANKING (bw/weights ratio -> be $1735/$1995) is CTX-INVARIANT (ctx cancels in bw/bytes) -> the
  break-even does NOT move with CTX; only the FEASIBILITY (fits-or-not) moves. So inv23 changes the feasible SET,
  not the be (same shape as inv21 COMPAT: shrinks the set, leaves the arithmetic).
- at 128K the 5090 INT8 needs INT4 to fit, but inv21 flags sm_100 GPTQ INT4 as kernel-unready -> a genuine
  cross-invariant tension: the card that wins on cost-perf at 8K may not RUN the quant needed to fit at 128K.

## precise blocking (deliverable advances ONLY on these; this round added Q5 working-sequence-length)
1. form-factor = USER (Q1). 2. refurb A100-40 quote vs $1735(decode)/$1995(prefill) = USER/market (Q2). 3. refurb
RTX 4090 quote vs $1124 = USER/market (Q3). 4. batch size = USER/market (Q4). 5. NEW: working-sequence-length / CTX
= USER/market (Q5) -- the VRAM gate is CTX=8K; a long-context deployment (>~122K) makes the 5090 INT8 infeasible,
needs INT4 (inv21 kernel-unready!) or a 40/48GB card. 6. first-hand single-stream vLLM = ENV (no CUDA) -- settles
eta (inv13), KV dtype (inv19), prefill/decode ratio (inv20), sm_100 kernel-ready (inv21), A100-40 bw (inv8), batch
regime/B* (inv22), and now the actual working-context / KV footprint (inv23).

## next concrete action
- premise chain complete through the PHASE boundary, the GATE structure, the BATCH domain, AND now the CTX domain,
  all encoded: regime (inv10) + traffic (inv11/15) + cache (inv16) + sparsity (inv17) + quant-meta (inv18) +
  KV-precision (inv19) + PHASE-domain (inv20) + GATE-structure/COMPAT (inv21) + BATCH-domain (inv22) + CTX-domain
  (inv23) + eta (inv13) + constants (inv8/14) + cross-file (inv12) + tree (r17/inv9). Every remaining unknown is
  ENV/USER-gated. Offline advance genuinely exhausted -- HOLD awaiting user Q1-Q5 / market quotes / hardware.

## r32 housekeeping DONE
- persisted r32 cursor; advanced INDEX.md cursor pointer r31->r32 + added the inv23 entry; updated durable memory
  with inv23 (CTX-domain) + upgraded the first-hand vLLM list to SEPTUPLE (adds working-context/KV-footprint
  confirmation); refreshed MEMORY.md index line with inv23 + Q5 + SEPTUPLE.

### honest-first verification of the above claim (self-caught gap, now closed)
- HONEST: the "housekeeping DONE" assertion was checked by grep/read and was initially FALSE -- the INDEX cursor
  pointer, the durable-memory inv23 section, and the MEMORY.md line were all still empty/stale (r31, SEXTUPLE). The
  code-level inv23/Q5 work WAS genuinely present+green, but the persistence half had never been executed.
- Fixed this turn; now grep-confirmed all four layers: INDEX cursor `4-r32-status.md`=当前cursor (1, r31 gone=0) +
  r-chain `r32 一手✓ inv23 CTX-domain` (1); durable memory `## inv23 (r32) CTX-domain` (1) + SEPTUPLE (1, SEXTUPLE
  gone=0); MEMORY.md inv23 (1) + SEPTUPLE (1, SEXTUPLE gone=0).
- suites re-run after the edits (markdown/memory only, code untouched): roofline EXIT=0, resolve EXIT=0, run_all
  EXIT=0 -- green gate intact.

### honest-first correction r32-followup (一手✓ COMPUTED -- the prose '~96K' was WRONG)
- GAP FOUND: the status/memory asserted critical context `L*~96K`, but NO code computed it -- it was a prose guess.
  一手✓ recompute under the inv23 model: vram_gb_at(96K,INT8)=31.45GB < 32GB -> **96K actually FITS** (no
  overflow!). The true crossing is L*≈122K (analytic closed form 125185; coarse scan first_overflow=125952≈123K).
- Fixed: roofline_verify inv23(2) now COMPUTES+VERIFIES L* (scan==analytic, monotone single crossing 31.99<=32<32.02),
  and all three prose files corrected `~96K`->`~122K`. Honest lesson: a number in prose must be COMPUTED somewhere or
  labeled a guess -- this round turned a guessed figure into a machine-checked one (the same teeth-proven discipline).
- suites re-run after the code+prose edits: roofline EXIT=0, run_all EXIT=0 -- green gate intact.