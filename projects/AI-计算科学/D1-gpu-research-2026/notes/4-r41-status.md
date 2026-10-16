origin: ai
time: 2026-09-28T14:10+08:00
stage: 04 / round: r41 / status: DONE (IMPLEMENTATION: FIRST attack on the denominator C's NET-vs-GROSS basis -- is the sticker the FINAL cost? inv25 attacked C's CONTENT (energy, additive recurring OPEX over lifetime), inv29 attacked C's TEMPORAL validity (obsolescence, multiplicative decay of relative value), inv30 attacked C's SCOPE (host, additive one-time CAPEX of non-card hardware) -- but ALL of them priced C as the GROSS sticker, silently assuming the card is FULLY SUNK -- recovered to ZERO at end of life. But task says RUN -> a deployed card is SOLD AGAIN at end of life -> hardware retains RESIDUAL VALUE -> net cost = sticker*(1-resid) < sticker -> C OVER-counts the sunk cost -> the ranking is RESIDUAL-BLIND. Encoded as inv31 into roofline_verify.py + Q12 registered into resolve_hstar.py.)

# cursor: 04/r41 = criterion C(H*) has ALWAYS been the GROSS sticker price, silently assuming the card is FULLY SUNK (recovered to zero at end of life); task says RUN -> a deployed card is SOLD AGAIN at end of life -> hardware retains RESIDUAL VALUE -> net cost = sticker*(1-resid) < sticker -> C OVER-counted the sunk cost -> the ranking is RESIDUAL-BLIND. The teeth: the consumer RTX_5090 holds value HARD (strong secondary market, gamers keep buying used) while the legacy datacenter A100-40 is EOL-adjacent and finds few buyers -> the consumer card recovers MORE residual -> at plausible residual (A100 0.20 vs 5090 0.30) the sticker $/tok gap $13.5 erodes to $7.3 (ranking residual-robust, A100 still cheaper net $/tok) BUT a strong consumer resale (5090 resid 0.75) FLIPS net $/tok to the consumer RTX_5090 -> the sticker-cheap legacy card is the WRONG buy once you net the sunk cost against resale -> RESIDUAL VALUE / NET-COST-of-ownership is NEW required input Q12

## ground-truth (re-confirm, honest-first)
- real cursor was notes/4-r40-status.md (r40 = inv30 system-level BOM / host-cost). This round attacks a NEW axis --
  the denominator C's NET-vs-GROSS basis (is the sticker the FINAL cost, or does the card retain resale value?) -- not a followup. Stayed GPU thread, did not restart.
- REJECTED-DUPLICATE (honest-first): grep confirmed residual / resale / net-cost / net_cost / recovered-at-end / sold-again appear NOWHERE
  in roofline_verify.py or resolve_hstar.py -> genuinely unattacked. The only hits were unrelated: inv20 "recovered roofline" (a rate, not
  money recovered), inv29 "DEPRECIATION HORIZON" (relative-value decay over years, not a terminal resale credit), "sunk price" (the word sunk
  used about the sticker being ignored, not the card being recovered). Not a duplicate.

## the genuine NEW unattacked silent assumption this round (C is priced as the GROSS sticker, i.e. the card as fully sunk)
- R=P/C has always set C = the card's GROSS sticker price. That silently assumes the card is ENTIRELY SUNK -- at end of life it is worth
  ZERO, every dollar spent is gone forever. But a deployed RUN is not a donation -- hardware retains RESIDUAL VALUE: a card pulled from a
  decommissioned server is SOLD AGAIN on the used market. The true economic cost is the NET cost = sticker - resale = sticker*(1-resid),
  strictly less than the sticker. R over-counted the sunk portion.
- KEY STRUCTURAL FINDING: this is the FIRST attack on the denominator's NET-vs-GROSS basis -- whether C is the amount PAID or the amount
  FORFEITED. inv25 extended C's CONTENT (energy added on top), inv29 extended C's TEMPORAL validity (obsolescence decay of the ratio),
  inv30 extended C's SCOPE (host hardware added on top); none ever asked whether the sticker is the FINAL number or whether part of it comes
  back as resale.
- The teeth (the load-bearing asymmetry): the consumer RTX 5090 holds value HARD -- a strong secondary market, gamers keep buying used cards
  -> a HIGH residual fraction. The legacy datacenter A100-40 is EOL-adjacent and finds few buyers -> a LOW residual fraction. So the
  sticker-cheap legacy card recovers LESS at end of life -> netting the sunk cost against resale SHRINKS its advantage -> at a strong
  consumer resale the ranking can FLIP to the consumer card.

## done this round (implementation + verification)
### roofline_verify.py -- inv31 (residual-value / net-cost-of-ownership axis)
- RESID = {A100-40:0.20, RTX_5090:0.30} (fraction of sticker recoverable at end of life; DIRECTION 一手✓ established fact -- consumer
  cards hold value on a strong used market, legacy datacenter cards are EOL-adjacent and find few buyers; exact residual_frac USER/market
  Q12). guard inv31(0): each residual must lie in [0,1] else the net-cost model is broken.
- net_cpt_a = 1200*(1-0.20)/roofline_sustained(A100-40,INT8) = $17.5 ; net_cpt_s = 1999*(1-0.30)/roofline_sustained(5090,INT8) = $24.8
  -> A100 still cheaper net $/tok at plausible residual (premise H*=A100 today holds), BUT the sticker $/tok gap $13.5 ERODES to $7.3
  because the consumer card recovers MORE residual (0.30 > 0.20) -> C over-counted the sunk cost.
- teeth AGGRESSIVE: RESID_AGG = {A100-40:0.20, RTX_5090:0.75} (consumer 5090 holds value HARD, strong used market) -> net_cpt_s_agg =
  1999*(1-0.75)/roofline_sustained = $8.9 < $17.5 -> ranking FLIPS to the consumer RTX_5090 once you price the RESIDUAL -> the
  sticker-cheap legacy card is the WRONG buy -> genuinely able to fail.
- canary: force EQUAL residual (both rc=0.30) -> net $/tok A100 $17.5 < 5090 $24.8 -> NO flip -> proves the flip is RESIDUAL-VALUE-
  asymmetry-driven (consumer holds harder than legacy), not decorative.
### resolve_hstar.py -- register Q12 RESIDUAL VALUE / NET-COST-of-ownership as a required input
- REQUIRED_INPUTS += "Q12 RESIDUAL VALUE / NET-COST-of-ownership (...)".
- guard: fails if "Q12 RESIDUAL VALUE" not declared -> the tree must never price H* on the GROSS sticker, silently assuming the card is
  fully sunk with zero resale.

## teeth-proven (EXIT captured DIRECTLY -- no grep-pipe PIPESTATUS reset; zsh ${PIPESTATUS[0]} returns empty, use $? after direct run)
- roofline_verify.py: [A] normal EXIT=0 (prints inv31 lines: net $/tok A100 $17.5 vs 5090 $24.8, sticker gap $13.5 eroded to $7.3; teeth
  resid 0.30->0.75 -> net $/tok 5090 $24.8->$8.9 < $17.5 -> FLIP; canary equal 0.30 -> $17.5 < $24.8 NO flip; + RESULT ALL ASSERTS
  PASS ✓); [B] teeth canary equalize aggressive consumer residual (`RESID_AGG = {"RTX_5090":0.75`->`0.30`) -> teeth fires RED 'aggressive
  consumer residual did NOT flip net $/tok to the 5090 -> teeth decorative' -> TEETH_EXIT=1 ✓ (ran INSIDE tasks/ via cp to avoid the
  recurring /tmp ModuleNotFoundError false-teeth); [C] rm canary + run_all EXIT=0.
- resolve_hstar.py: [B'] canary sed delete ONLY the Q12 dict entry (`/^    "Q12 RESIDUAL VALUE/d` -- the `^    "Q12` indent anchor does
  NOT match the guard line which starts `if "Q12`, so the guard survives) -> grep -c BEFORE=2 AFTER=1 -> fires RED RIGHT reason
  'RESIDUAL-VALUE/NET-COST NOT declared a required input' EXIT=1 ✓ captured directly no pipe; [C] restore (grep -c RESTORED=2) +
  run_all EXIT=0. NOTE: an earlier guard canary was copied to /tmp and raised ModuleNotFoundError (sys.path resolves to /tmp) -> FALSE teeth
  EXIT=1 wrong cause; RE-RAN inside tasks/ via cp -> confirmed the TRUE semantic RED (RESULT: FAIL -> inv31 ... NOT declared), not a crash.

## why this matters (advance, not restate)
- The denominator C has now been attacked on FOUR axes: CONTENT (inv25 energy, additive opex over lifetime), TEMPORAL validity (inv29
  obsolescence, multiplicative over years), SCOPE (inv30 host, additive one-time capex of non-card hardware), and now the NET-vs-GROSS
  basis (inv31, does the sticker stay sunk or does part of it come back as resale?). The last is the structural point: every prior C was
  the amount PAID; none ever asked whether it is the amount FORFEITED.
- The two-sided result is the point again: at plausible residual the ranking is RESIDUAL-ROBUST (A100 still cheaper net $/tok, but the
  sticker gap $13.5 already eroded to $7.3 -- the consumer card's stronger resale ate $6.2 of the edge); BUT the teeth proves that a strong
  consumer resale (5090 resid 0.75) FLIPS net $/tok to the consumer RTX_5090. That converts "the sticker is the final cost" from an implicit
  premise into a named, testable dependency (Q12: the end-of-life residual/resale fraction per card).
- The distinctness is the point: inv31 (resale) attacks C by SUBTRACTING a terminal credit recovered FROM the card; inv25 (energy) ADDS a
  recurring OPEX bill ON TOP over the lifetime -- opposite sign, opposite timing; inv30 (host) ADDS a one-time CAPEX of NON-card hardware
  -- this SUBTRACTS from the card itself; inv29 (obsolescence) MULTIPLICATIVELY decays the relative ratio over years -- this is a one-time
  SUBTRACTIVE terminal adjustment to the absolute cost, no decay rate.

## honest boundary (NOT loosened)
- the end-of-life residual / resale fraction per card = USER/market (Q12). The residual DIRECTION (a consumer RTX 5090 holds value on a
  strong used market while a legacy EOL-adjacent datacenter A100-40 finds few buyers) is 一手✓ established fact (consumer secondary-market
  liquidity vs datacenter EOL thin demand); the exact residual fractions are illustrative-plausible, MARKET-BLOCKED (no live resale quote)
  -- same first-hand gap as all price/throughput numbers. No fabricated resale value.

## precise blocking (deliverable advances ONLY on these; unchanged from r40, plus the new Q12)
1. form-factor = USER (Q1). 2. refurb A100-40 quote vs $1735(decode)/$1995(prefill) = USER/market (Q2). 3. refurb RTX 4090 quote vs
$1124 = USER/market (Q3). 4. batch size = USER/market (Q4). 5. working-sequence-length / CTX = USER/market (Q5). 6. Q6 ENERGY/TCO =
$/kWh + deployment lifetime + A100 TDP variant confirmation (PCIe 250 vs SXM 400) = USER/market/hardware-spec. 7. Q7 OUTPUT QUALITY =
acceptable-accuracy bar / eval-delta per quant = USER/market. 8. Q8 LATENCY/TTFT = interactive? max acceptable TTFT? typical generation
length G = USER/market. 9. Q9 SUSTAINED/THERMAL-DERATE = sustained soak bw / thermal envelope / duty cycle per card = USER/market/
hardware. 10. Q10 DEPLOYMENT-LIFETIME / OBSOLESCENCE-RATE = how many years will this deployment run? per-card obsolescence/support-decay
rate = USER/market. 11. Q11 SYSTEM-LEVEL BOM / HOST-COST = the non-card host BOM per deployment (server-class vs desktop) + whether the
card must live in a rack = USER/market. 12. NEW Q12 RESIDUAL VALUE / NET-COST-of-ownership = the end-of-life residual / resale fraction
per card (consumer 5090 holds value hard vs legacy EOL-adjacent A100-40 finds few buyers) = USER/market. 13. first-hand single-stream
vLLM = ENV (no CUDA) -- settles eta (inv13), KV dtype (inv19), prefill/decode ratio (inv20), sm_100 kernel-ready (inv21), A100-40 bw
(inv8), batch regime/B* (inv22), working-context/KV footprint (inv23), quant-recipe/FP16_LAYER_FRAC (inv24), real sustained board power
/ efficiency-under-load (inv25), real perplexity/eval-delta per quant (inv26), real measured TTFT / end-to-end latency vs the SLA
(inv27), real sustained soak bw / thermal throttle behavior per card (inv28), the real street-price trajectory / per-card EOL calendar
that would settle the obsolescence rates (inv29), the real vendor quote for a full HOST BOM (server-class vs desktop) (inv30), and NOW
the real resale / end-of-life residual quote per card that would settle whether the sticker-cheap legacy card's edge survives netting
against resale (inv31).

## next concrete action
- premise chain complete through PHASE / GATE / BATCH / CTX / WEIGHT-PRECISION-LAYERING / ENERGY-COST / OUTPUT-QUALITY / LATENCY-
DIMENSION / SUSTAINED-THERMAL / RANKING-TEMPORAL-VALIDITY / SYSTEM-BOM-SCOPE / RESIDUAL-NET-COST domains, all encoded AND every asserted
number machine-computed, and the criterion now attacked on BOTH sides (denominator C: r35 energy-content + r39 ranking-temporal + r40
system-scope + r41 residual-net-basis) AND the numerator on four axes (size/count inv8..25, meaning inv26, dimension inv27, temporal-
validity inv28). Offline advance genuinely exhausted -- HOLD awaiting user Q1-Q12 / market quotes / hardware / eval / lifetime / host-BOM
/ residual-resale. The loop does not stop; it records the exact reason and resumes when any input lands.

## r41 housekeeping
- persisted r41 cursor (this file); advanced INDEX.md cursor pointer r39->r41 (r40 had left the cursor line stale at r39) + appended the
  r41 inv31 entry to the r-chain; added the inv31 block to the durable conclusion (04.5-r6-roofline-bound-conclusion.md); registered Q12
  RESIDUAL-VALUE/NET-COST into resolve_hstar.py's REQUIRED_INPUTS + guard (dict-entry-only sed anchor `^    "Q12 RESIDUAL VALUE` -> guard
  survives -> teeth RED right reason EXIT=1, ran canary INSIDE tasks/ to avoid the /tmp ModuleNotFoundError false-teeth); refreshed
  MEMORY.md index line with inv31 + the new Q12 + extended the first-hand-decouple list with residual-value-net-cost-resale-fraction-per-
  card.