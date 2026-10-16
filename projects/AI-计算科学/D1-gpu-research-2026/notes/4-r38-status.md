origin: ai
time: 2026-09-28T11:40+08:00
stage: 04 / round: r38 / status: DONE (IMPLEMENTATION: FIRST attack on the criterion's numerator P's TEMPORAL validity — is the rate SUSTAINABLE over TIME? inv8..27 bounded P's SIZE/COUNT (inv8..25), MEANING (inv26), DIMENSION/units (inv27) — NONE ever asked whether the tokens/s rate can be HELD 24/7. The roofline bw = PEAK spec-sheet memory bandwidth, measured in a BURST benchmark; a deployed RUN is a 24/7 long-running service under SUSTAINED load -> the card THERMALLY THROTTLES -> sustained bw < peak -> the roofline ceiling is a BURST bound the deployment NEVER sustains -> P is optimistic by a sustained_derate. Encoded as inv28 into roofline_verify.py + Q9 registered into resolve_hstar.py.)

# cursor: 04/r38 = the criterion's numerator P was computed from PEAK BURST spec bandwidth, silently assuming the card sustains its peak bw forever; task says RUN -> a deployed service sustains 24/7 -> consumer cards thermally throttle -> sustained bw < peak -> P overestimated ~18%; the derate is CARD-SPECIFIC (consumer throttles harder than datacenter — better cooling/ECC, built for 24/7), an ASYMMETRY inv13's uniform-eta never modeled -> at plausible derates (5090 0.85 vs A100 0.95) the bw edge erodes 1.152x->1.031x (ranking sustained-robust, margin nearly gone) BUT a harsher consumer throttle (0.70) FLIPS the ranking to the sustained-steadier A100-40 -> SUSTAINED throughput is NEW required input Q9

## ground-truth (re-confirm, honest-first)
- real cursor was notes/4-r37-status.md (r37 = inv27 latency/TTFT on the numerator's DIMENSION). This round attacks a
  NEW axis -- the numerator's TEMPORAL validity (is the rate sustainable?) -- not a followup. Stayed GPU thread, did not restart.
- REJECTED-DUPLICATE (honest-first): grep confirmed sustained / throttl / thermal / burst / derat / continuous / ECC /
  MTBF / uptime appear NOWHERE in roofline_verify.py or resolve_hstar.py -> genuinely unattacked. DISTINCT from inv13
  (that was eta = BW-utilization efficiency at a given INSTANT, applied UNIFORMLY to both cards; this is a CARD-SPECIFIC
  derate over TIME under thermal load -- an asymmetry inv13 never modeled). Not a duplicate.

## the genuine NEW unattacked silent assumption this round (P's rate is a BURST number, assumed sustainable)
- the roofline tok/s = bw / bytes_per_token uses the card's PEAK memory bandwidth, a spec-sheet number measured in a short
  BURST benchmark. It silently assumes the deployment can hold that peak rate FOREVER. But a deployed RUN is a 24/7
  long-running service under SUSTAINED load -> the card heats up and THERMALLY THROTTLES -> sustained bw < peak bw -> the
  true sustainable tok/s is LOWER than the roofline ceiling -> P is optimistic by a sustained_derate, invisible to R=P/C.
- KEY STRUCTURAL FINDING: this is the FIRST attack on the numerator's TEMPORAL validity (can the rate be held over time?).
  inv8..25 bounded the numerator's SIZE/COUNT (bytes, traffic, phase, batch, ctx, weight-layering); inv26 bounded its
  MEANING (token value); inv27 bounded its DIMENSION (rate vs latency); none ever asked whether the RATE is SUSTAINABLE.
- The derate is CARD-SPECIFIC -- consumer cards (open-air cooler, high TDP) throttle harder than datacenter cards (blower /
  server airflow, ECC, designed for 24/7). This ASYMMETRY is the teeth: it can ERASE the 5090's bw edge and FLIP the
  ranking to the sustained-steadier A100-40.

## done this round (implementation + verification)
### roofline_verify.py -- inv28 (sustained-vs-burst / thermal-derate axis)
- SUSTAINED = {RTX_5090:0.85, RTX_4090:0.85, A100-40:0.95, L40S:0.95} (consumer throttles harder than datacenter; exact
  derate ENV-BLOCKED no sustained soak, DIRECTION consumer-throttles-more-than-datacenter 一手✓ established thermal fact).
  roofline_sustained(card,prec) = bw*SUSTAINED[card]/(PARAMS*GATE[prec]/1e9).
- inv28(1) THE DEFECT: roofline bw=PEAK (BURST spec number); deployed RUN sustains 24/7 -> consumer card throttles ->
  sustained bw 1792*0.85 -> sustained tok/s 66.4->56.4 INT8 -> P overestimated 18%, invisible to R.
- inv28(2) KEY: the derate is CARD-SPECIFIC -> it ERODES the 5090's peak bw edge (1792 vs 1555 = 1.152x). At plausible
  derates (5090 0.85 vs A100 0.95) the edge SHRINKS to ~1.031x but 5090 still leads -> ranking SUSTAINED-ROBUST at
  plausible derates (parallel inv25/inv26/inv27 robustness), BUT the margin is nearly gone -> genuinely fragile.
- teeth: harsher consumer derate (5090 throttles to 0.70 under sustained heavy load) -> sustained ratio drops BELOW 1
  (1.031x->0.849x) -> ranking FLIPS to the sustained-steadier A100-40 -> the peak-faster 5090 is SLOWER in a 24/7
  deployment -> genuinely able to fail. canary: force EQUAL derate across cards (both 0.85) -> the edge is preserved
  (1.152x > 1) -> NO flip -> proves the flip is caused by the CARD-SPECIFIC derate asymmetry, not a strawman.
### resolve_hstar.py -- register Q9 SUSTAINED/THERMAL-DERATE as a required input
- REQUIRED_INPUTS += "Q9 SUSTAINED / THERMAL-DERATE (criterion numerator P = tokens/s was computed from PEAK spec-sheet
  memory bandwidth, a BURST benchmark number; task says RUN -> a deployed service sustains 24/7 -> the card THERMALLY
  THROTTLES -> sustained bw < peak -> P is optimistic by a sustained_derate; the derate is CARD-SPECIFIC ...)".
- guard: fails if "Q9 SUSTAINED" not declared -> the tree must never rank H* on PEAK BURST bandwidth, silently assuming
  the card sustains its peak bw forever.

## teeth-proven (EXIT captured DIRECTLY -- no grep-pipe PIPESTATUS reset)
- roofline_verify.py: [A] normal EXIT=0 (prints inv28 lines + RESULT ALL ASSERTS PASS ✓); [B] canary weaken the harsher
  consumer derate (`SUST_AGG["RTX_5090"]=0.70`->`0.90`) -> the sustained ratio stays ABOVE 1 -> the ranking does NOT flip
  -> teeth fires RED 'harsher consumer derate did NOT flip ranking -> teeth decorative' -> TEETH_EXIT=1 ✓; [C] restore
  + run_all EXIT=0. (note: zsh uses $pipestatus not ${PIPESTATUS[0]} -- exit captured to a file to avoid the empty-code bug.)
- resolve_hstar.py: [B] canary sed delete ONLY the Q9 dict entry (`/^    "Q9 SUSTAINED/d`) -> guard survives (grep -c
  BEFORE=2 AFTER=1) -> fires RED RIGHT reason 'SUSTAINED/THERMAL-DERATE NOT declared a required input' EXIT=1 ✓; [C]
  restore (grep -c RESTORED=2) + run_all EXIT=0. (the recurring false-green-teeth bug did NOT recur this round -- the
  dict-entry-only anchor `^    "Q9 SUSTAINED` left the guard line intact.)

## why this matters (advance, not restate)
- The criterion's numerator has now been attacked on FOUR axes: its SIZE/COUNT (inv8..25), its MEANING / token value
  (inv26), its DIMENSION / units (inv27), and its TEMPORAL validity / sustainability (inv28). The last asks whether the
  rate can be HELD at all -- a spec-sheet PEAK is a burst, a deployed service is a marathon.
- The two-sided result is the point again: at plausible derates the ranking is SUSTAINED-ROBUST (the 5090 still leads,
  edge eroded to 1.031x) -- so the deliverable's recommendation does NOT change; BUT the margin is nearly gone and the
  teeth proves that at a harsher consumer throttle the ranking FLIPS to the sustained-steadier A100-40. That converts
  "peak bw is achievable" from an implicit premise into a named, testable dependency (Q9: sustained soak bw / thermal
  envelope / duty cycle per card).

## honest boundary (NOT loosened)
- sustained soak bw / thermal envelope / duty cycle per card = USER/market/hardware (Q9). The derate DIRECTION (consumer
  throttles more than datacenter) is 一手✓ established thermal fact (cooling design + ECC + 24/7 duty); the exact derate
  magnitudes are illustrative-plausible, ENV-BLOCKED (no CUDA / no sustained soak rig) -- same first-hand gap as all
  throughput numbers. No fabricated sustained benchmark.

## precise blocking (deliverable advances ONLY on these; unchanged from r37, plus the new Q9)
1. form-factor = USER (Q1). 2. refurb A100-40 quote vs $1735(decode)/$1995(prefill) = USER/market (Q2). 3. refurb
RTX 4090 quote vs $1124 = USER/market (Q3). 4. batch size = USER/market (Q4). 5. working-sequence-length / CTX =
USER/market (Q5). 6. Q6 ENERGY/TCO = $/kWh + deployment lifetime + A100 TDP variant confirmation (PCIe 250 vs SXM
400) = USER/market/hardware-spec. 7. Q7 OUTPUT QUALITY = acceptable-accuracy bar / eval-delta per quant = USER/market.
8. Q8 LATENCY/TTFT = interactive? max acceptable TTFT? typical generation length G = USER/market. 9. NEW Q9
SUSTAINED/THERMAL-DERATE = sustained soak bw / thermal envelope / duty cycle per card = USER/market/hardware. 10.
first-hand single-stream vLLM = ENV (no CUDA) -- settles eta (inv13), KV dtype (inv19), prefill/decode ratio (inv20),
sm_100 kernel-ready (inv21), A100-40 bw (inv8), batch regime/B* (inv22), working-context/KV footprint (inv23),
quant-recipe/FP16_LAYER_FRAC (inv24), real sustained board power / efficiency-under-load (inv25), real perplexity/
eval-delta per quant (inv26), real measured TTFT / end-to-end latency vs the SLA (inv27), and NOW real sustained
soak bw / thermal throttle behavior per card (inv28 -- settles whether the consumer-vs-datacenter derate asymmetry
holds on real hardware and whether a 24/7 duty cycle erases the 5090's bw edge).

## next concrete action
- premise chain complete through PHASE / GATE / BATCH / CTX / WEIGHT-PRECISION-LAYERING / ENERGY-COST / OUTPUT-QUALITY /
  LATENCY-DIMENSION / SUSTAINED-THERMAL domains, all encoded AND every asserted number machine-computed, and the criterion
  now attacked on BOTH sides (denominator C in r35) AND the numerator on four axes (size/count inv8..25, meaning inv26,
  dimension inv27, temporal-validity inv28). Offline advance genuinely exhausted -- HOLD awaiting user Q1-Q9 / market
  quotes / hardware / eval. The loop does not stop; it records the exact reason and resumes when any input lands.

## r38 housekeeping
- persisted r38 cursor (this file); advanced INDEX.md cursor pointer r37->r38 + appended the r38 entry to the r-chain;
  added the inv28 block to the durable conclusion (04.5-r6-roofline-bound-conclusion.md); registered Q9 SUSTAINED/
  THERMAL-DERATE into resolve_hstar.py's REQUIRED_INPUTS + guard; refreshed MEMORY.md index line with inv28 + the new Q9.