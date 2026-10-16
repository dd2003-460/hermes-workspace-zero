origin: ai
time: 2026-09-28T09:00+08:00
stage: 04 / round: r35 / status: DONE (IMPLEMENTATION: FIRST attack on the COST DENOMINATOR C(H*). inv8..24 ALL attacked the NUMERATOR P (bw/eta/params/bytes/phase/gate/batch/ctx); NONE ever touched C. The criterion R=P/C silently set C = STICKER PRICE, but the task says RUN = deployment -> a deployed card pays ELECTRICITY for its whole lifetime -> true cost = TCO = sticker + energy*lifetime. This is the first-ever denominator-side attack. Encoded as inv25 into roofline_verify.py + Q6 registered into resolve_hstar.py.)

# cursor: 04/r35 = the criterion's cost denominator C(H*) was silently STICKER-only; task says RUN -> operating ENERGY enters -> energy/token ~EQUAL (throughput~power offset) so sticker ranking is ENERGY-ROBUST at nominal efficiency, BUT flips under degraded efficiency within a deployment lifetime -> ENERGY is NEW required input Q6

## ground-truth (re-confirm, honest-first)
- real cursor was notes/4-r34-status.md (r34 = inv24 mixed-precision weight layering). This round attacks a NEW axis
  (the COST denominator), not a followup. Stayed GPU thread, did not restart.
- REJECTED-DUPLICATE (honest-first): grep confirmed energy/power/TCO/kWh/$/W appear NOWHERE in roofline_verify.py
  or resolve_hstar.py, and CARDS carried NO power field -> genuinely unattacked. All prior invariants were numerator-
  side; this is the first denominator-side attack. Not a duplicate.

## the genuine NEW unattacked silent assumption this round (C = sticker price, ignoring operating energy)
- the criterion R(H*) = P(H*)/C(H*) silently set C = STICKER PRICE. But the task is RUN (inference DEPLOYMENT), and a
  deployed card draws board power (TDP) continuously for its whole lifetime -> the true cost is TCO = sticker + energy*
  lifetime. Sticker-price ranking is NOT energy-invariant: a card can win on bw/price yet lose on energy-per-token.
- KEY STRUCTURAL FINDING: energy/token = watts/throughput. Throughput scales WITH power (the faster card draws
  proportionally more watts), so the two OFFSET -> energy/token is NEARLY EQUAL across the two candidates. This makes
  the sticker ranking ENERGY-ROBUST at nominal efficiency (the naive "5090 costs more to run" worry FAILS), BUT the
  robustness is CONDITIONAL on nominal efficiency -- degrade the 5090's efficiency and the ranking flips within a
  deployment lifetime. So energy is a named, load-bearing, testable dependency, not a free omission.

## done this round (implementation + verification)
### roofline_verify.py -- inv25 (energy/TCO axis)
- POWER_W = {"RTX_5090":575 (一手✓ WebFetch Wikipedia GeForce RTX 50 series THIS round), "A100-40":250 (PCIe 厂商规格
  社区R; SXM variant=400W -> variant is LOAD-BEARING, honest boundary)}. KWH=0.15 illustrative (USER/market).
- energy_per_token(card,prec)=POWER_W/roofline(card,prec) = W/(tok/s) = J/token. energy_usd_per_token = J/3.6e6*$kWh.
- inv25(1) STRIKING: energy/token ~EQUAL (ratio 0.998): throughput ratio 132.7/57.6=2.30x ~= power ratio 575/250=2.30x
  -> they OFFSET -> J/token ~equal (5090=4.332J vs A100=4.341J).
- inv25(2): sticker gap $799 NEVER closes under energy accumulation -- per-token energy diff ~0, even slightly FAVORS
  5090 (0.180e-6 vs 0.181e-6 USD/token) -> the naive "5090 costs more to run" worry FAILS -> sticker ranking ENERGY-
  ROBUST at nominal efficiency.
- teeth: DEGRADE the 5090's efficiency (same 575W, HALF throughput -- power-limited / worse kernel) -> energy/token
  4.33->8.66J -> now WORSE than A100 by 0.180e-6 USD/token -> $799 sticker gap CLOSES at 4.44e9 tokens ~= 387 days
  of 24/7 running -> ranking FLIPS -> genuinely able to fail.
### resolve_hstar.py -- register Q6 ENERGY/TCO as a required input
- REQUIRED_INPUTS += "Q6 ENERGY / TCO (criterion C(H*) silently = STICKER PRICE; task says RUN -> operating ENERGY
  enters -> needs board TDP + $/kWh + deployment lifetime ...)".
- guard: fails if "Q6 ENERGY" not declared -> the tree must never price H* on sticker alone, ignoring electricity a
  deployed card pays for its whole lifetime.

## teeth-proven (EXIT captured DIRECTLY -- no grep-pipe PIPESTATUS reset)
- roofline_verify.py: [A] normal EXIT=0 (prints inv25 lines + RESULT ALL ASSERTS PASS ✓); [B] canary sed remove the
  degradation (`*0.5`->`*1.0`) -> energy/token does NOT exceed A100 -> teeth fires RED 'degraded 5090 energy/token did
  NOT exceed A100 -> teeth decorative' + 'break-even -184066 days not a plausible deployment lifetime -> teeth not
  biting' -> REAL_EXIT=1 ✓; [C] restore + run_all EXIT=0.
- resolve_hstar.py: [B] canary sed delete ONLY the Q6 dict entry (`/^    "Q6 ENERGY \/ TCO/d`) -> guard survives ->
  fires RED RIGHT reason 'ENERGY/TCO NOT declared a required input' EXIT=1 ✓; [C] restore + run_all EXIT=0.
  (same class of teeth-bug as r31/r32: a broad `/Q6 ENERGY/d` deleted BOTH the dict entry AND the guard -> FALSE PASS
  EXIT=0 -> caught, re-scoped to the dict-entry-unique pattern -> guard survives -> bites red.)

## why this matters (advance, not restate)
- This is the FIRST of the criterion's two sides to be questioned: every prior invariant hardened the NUMERATOR P;
  the DENOMINATOR C was taken as given (sticker price). The task's own word "RUN" contradicts sticker-only costing.
- The two-sided result is the point: at nominal efficiency the ranking is ENERGY-ROBUST (energy/token ~equal because
  throughput~power offset -- a non-obvious physical fact, not an assumption), so the deliverable's recommendation does
  NOT change; BUT the robustness is CONDITIONAL, and the teeth proves it flips under a degraded-efficiency regime
  within ~387 days of 24/7 running. That converts "energy doesn't matter" from an implicit premise into a named,
  testable dependency (Q6) with a quantified flip horizon.

## honest boundary (NOT loosened)
- exact $/kWh + deployment lifetime = USER/market (Q6). A100-40 TDP variant (PCIe 250W vs SXM 400W) = hardware spec
  to confirm (the variant is LOAD-BEARING -- an SXM A100 would draw 400W and change the energy/token balance). RTX
  5090 TDP=575W 一手✓ (Wikipedia GeForce RTX 50 series, fetched this round). The DIRECTION (energy/token ~equal via
  throughput~power offset) and the flip horizon are proven 一手✓ arithmetic; the absolute $/kWh is illustrative.

## precise blocking (deliverable advances ONLY on these; unchanged from r34, plus the new Q6)
1. form-factor = USER (Q1). 2. refurb A100-40 quote vs $1735(decode)/$1995(prefill) = USER/market (Q2). 3. refurb
RTX 4090 quote vs $1124 = USER/market (Q3). 4. batch size = USER/market (Q4). 5. working-sequence-length / CTX =
USER/market (Q5). 6. NEW Q6 ENERGY/TCO = $/kWh + deployment lifetime + A100 TDP variant confirmation (PCIe 250 vs
SXM 400) = USER/market/hardware-spec. 7. first-hand single-stream vLLM = ENV (no CUDA) -- settles eta (inv13), KV
dtype (inv19), prefill/decode ratio (inv20), sm_100 kernel-ready (inv21), A100-40 bw (inv8), batch regime/B*
(inv22), working-context/KV footprint (inv23), quant-recipe/FP16_LAYER_FRAC (inv24), and NOW the real sustained
board power / efficiency-under-load (inv25 -- settles whether the throughput~power offset holds at first-hand
efficiency, or the 5090 degrades enough to flip the ranking within the deployment lifetime).

## next concrete action
- premise chain complete through PHASE / GATE / BATCH / CTX / WEIGHT-PRECISION-LAYERING / ENERGY-COST domains, all
  encoded AND every asserted number machine-computed, and the criterion's DENOMINATOR now attacked for the first time.
  Offline advance genuinely exhausted -- HOLD awaiting user Q1-Q6 / market quotes / hardware. The loop does not stop;
  it records the exact reason and resumes when any input lands.

## r35 housekeeping
- persisted r35 cursor (this file); advanced INDEX.md cursor pointer r34->r35 + appended the r35 entry to the r-chain;
  added the inv25 block to the durable conclusion (04.5-r6-roofline-bound-conclusion.md); registered Q6 ENERGY/TCO
  into resolve_hstar.py's REQUIRED_INPUTS + guard; refreshed MEMORY.md index line with inv25 + the new Q6.