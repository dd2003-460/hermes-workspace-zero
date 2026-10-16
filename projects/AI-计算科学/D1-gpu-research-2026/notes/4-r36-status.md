origin: ai
time: 2026-09-28T10:00+08:00
stage: 04 / round: r36 / status: DONE (IMPLEMENTATION: FIRST attack on the criterion's NUMERATOR MEANING. inv8..25 all bounded the COUNT of tokens -- bytes/traffic/phase/batch/ctx on P, or the cost C in inv25 -- NONE ever asked whether the tokens are CORRECT / have equal VALUE. The criterion R=P/C counts RAW tokens/s and treats every token as WORTH THE SAME, but quantization TRADES throughput for OUTPUT QUALITY -> R can rank a FAST-BUT-DEGRADED config ABOVE a slower-but-accurate one with ZERO quality penalty. Encoded as inv26 into roofline_verify.py + Q7 registered into resolve_hstar.py.)

# cursor: 04/r36 = the criterion's numerator P was RAW tokens/s treating every token as EQUALLY VALUABLE; task says RUN -> a deployed system must produce USEFUL/ACCURATE tokens -> quant trades throughput for accuracy -> R over-rewards the aggressive quant with zero quality penalty -> ranking is QUALITY-ROBUST at a plausible tuned gap BUT flips to the accurate config under an un-tuned INT4 that fails a math/code eval -> OUTPUT QUALITY is NEW required input Q7

## ground-truth (re-confirm, honest-first)
- real cursor was notes/4-r35-status.md (r35 = inv25 energy/TCO on the COST denominator). This round attacks a NEW axis
  (the numerator's MEANING), not a followup. Stayed GPU thread, did not restart.
- REJECTED-DUPLICATE (honest-first): grep confirmed accuracy/perplexity/quality/token-value appear NOWHERE in
  roofline_verify.py or resolve_hstar.py -> genuinely unattacked. All prior invariants bounded the token COUNT or the
  cost; this is the first attack on the token VALUE / numerator meaning. Not a duplicate.

## the genuine NEW unattacked silent assumption this round (numerator P = raw tokens/s, every token equal value)
- the criterion R(H*) = P(H*)/C(H*) silently set P = RAW tokens/s, i.e. every generated token is WORTH THE SAME. But
  quantization TRADES throughput for OUTPUT QUALITY: a coarser quant (INT4) runs ~2x faster than INT8 yet has HIGHER
  perplexity / lower accuracy (GPTQ/AWQ degrade reasoning & code). So R can rank a FAST-BUT-DEGRADED config ABOVE a
  slower-but-accurate one with ZERO quality penalty -> R=P/C is NOT a proxy for USEFUL throughput.
- KEY STRUCTURAL FINDING: this is the FIRST attack on the numerator's MEANING (prior inv8..25 bounded its SIZE /
  COUNT / bytes / bw / phase / batch / ctx, or the cost C in inv25). The criterion never priced whether the tokens are
  CORRECT. The deliverable ITSELF offers INT8-vs-INT4 as alternatives and routes the 5090 to INT8 (inv21 compat) while
  considering INT4 elsewhere -> the headline comparison is QUALITY-MISMATCHED (different quants compared on raw R).
- ROBUSTNESS at a PLAUSIBLE tuned gap (INT4=0.95 vs INT8=0.98): the raw cost-perf gap DOMINATES the small quality gap
  -> the ranking is QUALITY-ROBUST at plausible degradation (parallel to inv25's nominal-efficiency robustness), BUT
  robustness is CONDITIONAL on the tuned gap -> an un-tuned INT4 that FAILS a math/code eval flips it to the accurate
  config. So output quality is a named, load-bearing, testable dependency, not a free omission.

## done this round (implementation + verification)
### roofline_verify.py -- inv26 (output-quality / token-value axis)
- QUALITY_W = {"BF16":1.0, "INT8":0.98, "INT4":0.95} tuned-plausible (exact ENV-BLOCKED -- no eval harness / no GPU;
  the ORDERING coarser->worse is a well-established 一手✓ fact, the magnitudes are illustrative).
- R_raw(card,prec) = roofline/price (criterion as-is, tok/s per $); R_eff = R_raw * QUALITY_W[prec] (quality-adjusted).
- inv26(1) THE DEFECT: R_raw 5090 INT4=0.06640 > INT8=0.03320 (coarser quant scores HIGHER cost-perf) yet INT4
  quality 0.95 < INT8 0.98 -> R rewards the DEGRADED config with ZERO quality penalty -> R=P/C NOT a proxy for USEFUL
  throughput.
- inv26(2): deliverable compares 5090@INT4 (R=0.06640) vs A100-40@INT8 (R=0.04799) -> DIFFERENT quants = QUALITY-
  MISMATCHED apples-to-oranges on accuracy; be $1735 is quant-invariant ONLY for the SAME quant (inv7).
- robustness: 4090@INT4 vs 5090@INT8 raw R gap 1.324x >> quality gap 0.969 -> ranking QUALITY-ROBUST at plausible
  tuned degradation.
- teeth: AGGRESSIVE un-tuned INT4 (quality 0.95->0.70, fails a math/code eval) -> R_eff 4090@INT4=0.03076 <
  5090@INT8=0.03254 -> ranking FLIPS to the ACCURATE config -> R genuinely QUALITY-DEPENDENT; canary force quality
  CONSTANT (=1 all) -> R_eff==R_raw -> flip VANISHES -> proves the flip is quality-driven not decorative.
### resolve_hstar.py -- register Q7 OUTPUT QUALITY as a required input
- REQUIRED_INPUTS += "Q7 OUTPUT QUALITY / accuracy bar (criterion numerator P = RAW tokens/s silently treats every
  token as EQUALLY VALUABLE; quant trades throughput for ACCURACY ...)".
- guard: fails if "Q7 OUTPUT QUALITY" not declared -> the tree must never rank H* on raw tokens/s alone, ignoring that
  a deployed RUN must produce ACCURATE tokens.

## teeth-proven (EXIT captured DIRECTLY -- no grep-pipe PIPESTATUS reset)
- roofline_verify.py: [A] normal EXIT=0 (prints inv26 lines + RESULT ALL ASSERTS PASS ✓); [B] canary weaken the
  aggressive collapse (`"INT4":0.70}`->`"INT4":0.99}` unique to QW_AGG) -> quality gap too small to overcome the raw
  gap -> teeth fires RED 'aggressive INT4 collapse did NOT flip ranking -> teeth decorative' -> REAL_EXIT=1 ✓; [C]
  restore + run_all EXIT=0. (teeth BUG caught THIS round: the first sed pattern `"INT4":0.70   # un-tuned` missed the
  `}` before the comment -> file UNCHANGED -> FALSE GREEN teeth EXIT=0; re-scoped to `"INT4":0.70}` -> bites red.)
- resolve_hstar.py: [B] canary sed delete ONLY the Q7 dict entry (`/^    "Q7 OUTPUT QUALITY/d`) -> guard survives ->
  fires RED RIGHT reason 'OUTPUT QUALITY NOT declared a required input' EXIT=1 ✓; [C] restore + run_all EXIT=0.
  (ran the canary INSIDE tasks/ via symlink so roofline_verify imports resolve -- the /tmp-copy ModuleNotFoundError
  class of false-teeth from r30/r31 was avoided by construction.)

## why this matters (advance, not restate)
- The criterion has TWO sides. r35 attacked the DENOMINATOR C (cost); r36 attacks the NUMERATOR P's MEANING (token
  value). Every prior invariant hardened the numerator's SIZE/COUNT; none ever asked if the tokens are CORRECT. The
  task's own word "RUN" contradicts raw-token counting -- a deployed system must produce USEFUL tokens.
- The two-sided result is the point: at a plausible tuned quant gap the ranking is QUALITY-ROBUST (the raw cost-perf
  gap dominates the small quality gap -- a non-obvious quantitative fact), so the deliverable's recommendation does NOT
  change; BUT the robustness is CONDITIONAL on the tuned gap, and the teeth proves it flips to the ACCURATE config
  under an un-tuned INT4 that fails a math/code eval. That converts "all tokens are equally good" from an implicit
  premise into a named, testable dependency (Q7).

## honest boundary (NOT loosened)
- exact perplexity / eval-delta per quant = USER/market (Q7) + first-hand eval = ENV-BLOCKED (no eval harness / no
  GPU). The QUALITY_W magnitudes are illustrative; the DIRECTION (coarser quant -> worse accuracy) is a well-established
  一手✓ fact (GPTQ/AWQ accuracy degradation is documented across the quantization literature). The robustness margin
  (raw gap 1.324x >> quality gap 0.969) and the flip horizon are proven 一手✓ arithmetic.

## precise blocking (deliverable advances ONLY on these; unchanged from r35, plus the new Q7)
1. form-factor = USER (Q1). 2. refurb A100-40 quote vs $1735(decode)/$1995(prefill) = USER/market (Q2). 3. refurb
RTX 4090 quote vs $1124 = USER/market (Q3). 4. batch size = USER/market (Q4). 5. working-sequence-length / CTX =
USER/market (Q5). 6. Q6 ENERGY/TCO = $/kWh + deployment lifetime + A100 TDP variant confirmation (PCIe 250 vs SXM
400) = USER/market/hardware-spec. 7. NEW Q7 OUTPUT QUALITY = acceptable-accuracy bar / eval-delta per quant =
USER/market. 8. first-hand single-stream vLLM = ENV (no CUDA) -- settles eta (inv13), KV dtype (inv19), prefill/
decode ratio (inv20), sm_100 kernel-ready (inv21), A100-40 bw (inv8), batch regime/B* (inv22), working-context/KV
footprint (inv23), quant-recipe/FP16_LAYER_FRAC (inv24), real sustained board power / efficiency-under-load (inv25),
and NOW the real perplexity/eval-delta per quant (inv26 -- settles whether the tuned quality gap holds or an aggressive
quant degrades enough to flip the ranking to the accurate config).

## next concrete action
- premise chain complete through PHASE / GATE / BATCH / CTX / WEIGHT-PRECISION-LAYERING / ENERGY-COST / OUTPUT-QUALITY
  domains, all encoded AND every asserted number machine-computed, and BOTH sides of the criterion now attacked (denom
  C in r35, numerator MEANING in r36). Offline advance genuinely exhausted -- HOLD awaiting user Q1-Q7 / market quotes /
  hardware / eval. The loop does not stop; it records the exact reason and resumes when any input lands.

## r36 housekeeping
- persisted r36 cursor (this file); advanced INDEX.md cursor pointer r35->r36 + appended the r36 entry to the r-chain;
  added the inv26 block to the durable conclusion (04.5-r6-roofline-bound-conclusion.md); registered Q7 OUTPUT QUALITY
  into resolve_hstar.py's REQUIRED_INPUTS + guard; refreshed MEMORY.md index line with inv26 + the new Q7.