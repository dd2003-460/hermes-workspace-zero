origin: ai
time: 2026-09-28T07:00+08:00
stage: 04 / round: r33 / status: DONE (HARDENING: honest-first caught that the r32 status/memory asserted critical context `L*~96K` but NO code COMPUTED it -- a number in prose must be COMPUTED somewhere or labeled a guess. 一手✓ recompute under the inv23 model: vram_gb_at(96K,INT8)=31.45GB < 32GB -> 96K actually FITS (the prose figure was WRONG, no overflow there); the TRUE crossing is L*≈122K (analytic closed form 125185; coarse scan first_overflow_ctx=125952≈123K). Upgraded inv23(2) from a fits8/not-fits128 binary to a COMPUTED+VERIFIED critical-context (scan==analytic + monotone single crossing), and corrected all three prose files ~96K->~122K. H* VALUE & ranking UNCHANGED -- this hardened an already-proven invariant's NUMBER, not a new axis.)

# cursor: 04/r33 = the inv23 critical-context L* was a PROSE-GUESS (~96K) with NO code behind it -- 一手✓ recomputed it to ~122K and machine-verified the crossing (scan==analytic, monotone)

## ground-truth (re-confirm, honest-first)
- real cursor was notes/4-r32-status.md (r32 = inv23 CTX-domain). This round is a FOLLOWUP on r32's inv23, not a new
  axis: it attacks the NUMBER "~96K" that r32 asserted but never computed. Stayed GPU thread, did not restart.
- guardrail satisfied: r32 attacked the CTX axis (feasibility gate); r33 hardens the SAME axis's critical-context
  figure from a guess to a machine-checked value (same teeth-proven discipline, not a new premise).

## the genuine gap this round (a number in prose with no code behind it)
- r32 status line 28/58/61/73 + durable memory line 287/304/316 + MEMORY.md all asserted `L*~96K`, but grep showed
  NO code COMPUTED L* -- roofline_verify inv23 only checked `fits8 and not fits128` (a binary at two endpoints), never
  solved for WHERE the crossing is. 违反诚实第一: a verifiable number was asserted without being computed.
- 一手✓ recompute (python, inv23 model): vram_gb_at(96K,INT8)=31.45GB < 32GB -> **96K FITS** (no overflow!). The
  prose "~96K" was simply WRONG. The true crossing: solve vram_gb_at(L*)=32 for kv_tokens -> L*=(kv_star -
  SLIDING_LAYERS*SLIDING_WINDOW)/FULL_LAYERS = 125185 ≈ 122K. A coarse scan (ctx+=1024 until vram>ceiling) gives
  first_overflow=125952 ≈ 123K. scan==analytic within 2*STEP ✓.

## done this round (implementation + verification)
### roofline_verify.py -- inv23(2) upgraded from binary to COMPUTED+VERIFIED critical context
- first_overflow_ctx(prec,ceiling,step): scans ctx+=step until vram_gb_at(ctx)>ceiling -> returns first overflow ctx.
- analytic L*: kv_star=(ceiling - weights - overhead)*1e9/(2*KV_HEADS*HEAD_DIM*prec); L*=(kv_star -
  SLIDING_LAYERS*SLIDING_WINDOW)/FULL_LAYERS.
- inv23(2) now asserts: (a) scan==analytic (|Lstar_scan - Lstar_exact| <= 2*STEP), (b) MONOTONE single crossing
  (vram(L*-STEP)<=ceiling<vram(L*)). Output: L*=125952 (~123K scan / ~122K analytic), monotone 31.99<=32<32.02.
- teeth: the monotone check would BREAK if the crossing were non-monotone (e.g. a KV term that dips then rises) -> it
  genuinely BITES against a mis-attributed boundary, not a strawman.
### prose correction (all three files)
- notes/4-r32-status.md, durable memory project/d1-gpu-27b-roofline-bound.md, MEMORY.md: `~96K`->`~122K` (replace_all).
- appended an honest-first correction block to the r32 status recording the self-caught gap + its closure.

## teeth-proven (EXIT captured DIRECTLY -- no grep-pipe PIPESTATUS reset)
- roofline_verify.py: normal EXIT=0; the new inv23(2) line prints "CRITICAL CONTEXT L* = 125952 ... scan==analytic
  125185; monotone 31.99GB<=32<32.02GB" + RESULT ALL ASSERTS PASS ✓. run_all.py EXIT=0.

## why this matters (advance, not restate)
- This is the loop's OWN integrity: every prior round (inv11..23) proved an invariant's DIRECTION (overflows / flips /
  cancels) with teeth. This round proved an invariant's NUMBER (WHERE it crosses) was not fabricated. The lesson is
  general and reusable: a verifiable figure in prose must be COMPUTED somewhere or explicitly labeled a guess -- the
  same teeth-proven standard applied to constants, not just to verdicts.
- Honest boundary UNCHANGED: L*≈122K is a roofline-model figure at the stored-KV accounting (FULL_LAYERS=10,
  kv_per_token_fp16); exact crossover still depends on the real KV dtype (inv19, ENV-BLOCKED) and the real prompt/gen
  split (inv20, ENV-BLOCKED). The H* VALUE and the ceiling-based RANKING are CTX-invariant (be $1735/$1995 unchanged)
  -- only the feasible SET moves, so correcting 96K->122K changes no recommendation, only the honesty of the claim.

## precise blocking (deliverable advances ONLY on these; unchanged from r32)
1. form-factor = USER (Q1). 2. refurb A100-40 quote vs $1735(decode)/$1995(prefill) = USER/market (Q2). 3. refurb
RTX 4090 quote vs $1124 = USER/market (Q3). 4. batch size = USER/market (Q4). 5. working-sequence-length / CTX =
USER/market (Q5) -- the VRAM gate is CTX=8K; a deployment above L*≈122K (NOT 96K, corrected) makes the 5090 INT8
infeasible, needs INT4 (inv21 kernel-unready!) or a 40/48GB card. 6. first-hand single-stream vLLM = ENV (no CUDA) --
settles eta (inv13), KV dtype (inv19), prefill/decode ratio (inv20), sm_100 kernel-ready (inv21), A100-40 bw (inv8),
batch regime/B* (inv22), working-context/KV footprint (inv23).

## next concrete action
- premise chain complete through PHASE / GATE / BATCH / CTX domains, all encoded AND now every asserted NUMBER is
  machine-computed (L* corrected). Offline advance genuinely exhausted -- HOLD awaiting user Q1-Q5 / market quotes /
  hardware. The loop does not stop; it records the exact reason and resumes when any input lands.

## r33 housekeeping
- persisted r33 cursor (this file); advanced INDEX.md cursor pointer r32->r33 + appended the r33 entry to the r-chain;
  corrected ~96K->~122K in the r32 status, the durable memory, and MEMORY.md; appended an honest-first correction block
  to the r32 status.