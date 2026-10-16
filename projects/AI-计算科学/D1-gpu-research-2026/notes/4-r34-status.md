origin: ai
time: 2026-09-28T08:00+08:00
stage: 04 / round: r34 / status: DONE (IMPLEMENTATION: attack the WEIGHT-PRECISION-UNIFORMITY silent assumption -- the roofline's bytes/token = PARAMS*prec assumes EVERY parameter sits at the quant precision, but real GPTQ/AWQ/AutoQuant keep SENSITIVE LAYERS (first/last block, attention out-proj) in FP16 for accuracy -> a fraction FP16_LAYER_FRAC of the 27B params stays at 2 bytes -> effective bytes/param = prec*(1-f)+2*f > prec -> bytes/token RISES -> roofline_true even LOWER (FIFTH optimism layer, SAME direction as inv11/18/19). Encoded as inv24 into roofline_verify.py. DISTINCT from inv18 (metadata WITHIN a quant: scale/zero-point, not WHICH layers) and inv19 (KV precision: the KV cache, not the WEIGHTS).)

# cursor: 04/r34 = the roofline's bytes/token assumed ALL weights at the quant precision -- real GPTQ/AWQ keep ~10% FP16 -> true bytes/token higher -> ceiling valid but looser (5th optimism layer); H* DECISION mixed-precision-invariant IF both cards run the same recipe

## ground-truth (re-confirm, honest-first)
- real cursor was notes/4-r33-status.md (r33 = inv23(2) L* computed+verified). This round attacks a NEW silent
  assumption, not a followup. Stayed GPU thread, did not restart.
- REJECTED-DUPLICATE (honest-first): the FIRST r34 candidate ("roofline divides by PEAK bw, never achievable sustained
  DRAM bw") was caught as a DUPLICATE of inv13 (eta -- uniform cancels / per-card flips). grep confirmed inv13 already
  covers peak-vs-achievable. Discarded the draft; found the genuinely-unattacked axis via grep (mixed-precision /
  FP16_LAYER_FRAC returned nothing).

## the genuine NEW unattacked silent assumption this round (WHICH weight layers are quantized)
- the roofline's bytes/token = PARAMS*prec treats ALL 27B params as at the quant precision. Real GPTQ/AWQ/AutoQuant
  keep sensitive layers in FP16 for accuracy -> a fraction f of the params stays at 2 bytes -> eff bytes/param =
  prec*(1-f)+2*f > prec -> bytes/token RISES -> roofline_true even LOWER. This is the FIFTH stacked optimism layer on
  the bytes side: bare weight bits -> +KV traffic [inv11] -> +weight metadata [inv18] -> +KV precision FP16 [inv19]
  -> +mixed-precision WEIGHT layering [inv24]. Each pushes true bytes/token UP so the ceiling is known looser but
  NEVER exceeded.
- DISTINCTness: inv24 (WHICH layers are quantized) vs inv18 (metadata WITHIN a quant: scale/zero-point, not which
  layers) vs inv19 (the KV cache precision, not the WEIGHTS). Three different bytes-side axes, none a duplicate.

## done this round (implementation + verification)
### roofline_verify.py -- inv24 (the roofline-side proof)
- FP16_LAYER_FRAC=0.10 (illustrative; real GPTQ/AWQ ~5-15%; ENV-BLOCKED -- no safetensors header locally / no CUDA).
- eff_bytes_per_param(prec,f)=prec*(1-f)+BF16_BYTES*f. inv24(0) sanity: eff bytes/param > uniform prec (FP16 layers
  genuinely add bytes).
- inv24(1) ceiling STILL VALID (looser): mixed-prec raises bytes/token -> roofline_true < bare ceiling. INT4 eff
  bytes/param 0.50->0.65 (1.30x), weights 13.50->17.55GB, roofline_true=95.5<=ceiling=132.7; INT8 eff 1.00->1.10
  (1.10x), weights 27.00->29.70GB, roofline_true=58.0<=ceiling=66.4.
- inv24(2) H* DECISION MIXED-PRECISION-INVARIANT IF BOTH CARDS RUN THE SAME RECIPE: the FP16-layer fraction scales
  BOTH cards' bytes/token identically (same model+quant) -> cancels in the ratio -> be=$1735 unchanged.
- teeth: DIFFERENT recipes (A100 forced to keep 20% FP16 because its INT8 quant path is less accurate vs the 5090's
  10%) -> the FP16 fraction does NOT cancel -> be MOVES $1735->$1590 (-8.3%) -> the ranking is NOT guaranteed robust
  -> the same-recipe assumption is LOAD-BEARING -> genuinely able to fail.

## teeth-proven (EXIT captured DIRECTLY -- no grep-pipe PIPESTATUS reset)
- roofline_verify.py: [A] normal EXIT=0 (prints inv24 lines + RESULT ALL ASSERTS PASS ✓); [B] canary sed
  f_a100=FP16_LAYER_FRAC (recipes made EQUAL -> be should NOT move -> teeth must fire) -> teeth fires RED
  'differing recipes did NOT move be -> teeth decorative (per-card FP16 fraction invisible)' EXIT=1 ✓; [C] restore
  f_a100=0.20 + run_all.py EXIT=0.

## why this matters (advance, not restate)
- This is the FIFTH independent optimism layer on the bytes side, and the FIRST that attacks WHICH weights are
  quantized (inv18 was metadata within a quant, inv19 was the KV cache). The two-sided result is the point: the
  ceiling stays valid (looser) AND the H* DECISION is mixed-precision-invariant ONLY under the SAME-RECIPE condition
  -- the teeth shows differing recipes MOVE the break-even (-8.3%), so the same-recipe assumption is LOAD-BEARING and
  genuinely able to fail. That converts an implicit premise into a named, testable dependency.

## honest boundary (NOT loosened)
- exact FP16_LAYER_FRAC is ENV-BLOCKED (depends on the actual quant recipe / AutoQuant accuracy sweep; no safetensors
  header locally, no CUDA). The DIRECTION (mixed-prec raises bytes/token -> ceiling looser) is proven 一手✓ arithmetic;
  the SAME-RECIPE invariance is proven 一手✓ algebraically (cancels in the ratio); the per-card-fraction sensitivity
  (teeth) is proven by construction.

## precise blocking (deliverable advances ONLY on these; unchanged from r33, plus the new ENV item)
1. form-factor = USER (Q1). 2. refurb A100-40 quote vs $1735(decode)/$1995(prefill) = USER/market (Q2). 3. refurb
RTX 4090 quote vs $1124 = USER/market (Q3). 4. batch size = USER/market (Q4). 5. working-sequence-length / CTX =
USER/market (Q5). 6. first-hand single-stream vLLM = ENV (no CUDA) -- settles eta (inv13), KV dtype (inv19),
prefill/decode ratio (inv20), sm_100 kernel-ready (inv21), A100-40 bw (inv8), batch regime/B* (inv22),
working-context/KV footprint (inv23), and NOW the actual quant recipe / FP16_LAYER_FRAC (inv24, the mixed-precision
WEIGHT layering -- confirms both cards run the SAME recipe so the be stays $1735, or reveals a per-card split that
moves it).

## next concrete action
- premise chain complete through PHASE / GATE / BATCH / CTX / WEIGHT-PRECISION-LAYERING domains, all encoded AND every
  asserted number machine-computed. Offline advance genuinely exhausted -- HOLD awaiting user Q1-Q5 / market quotes /
  hardware. The loop does not stop; it records the exact reason and resumes when any input lands.

## r34 housekeeping
- persisted r34 cursor (this file); advanced INDEX.md cursor pointer r33->r34 + appended the r34 entry to the r-chain;
  added `## inv24 (r34)` to the durable memory + bumped the bytes-side optimism enumeration to FIFTH + extended the
  first-hand vLLM list to OCTUPLE (adds quant-recipe/FP16_LAYER_FRAC); refreshed MEMORY.md index line with inv24 +
  OCTUPLE.