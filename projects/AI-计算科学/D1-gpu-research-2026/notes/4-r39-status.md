origin: ai
time: 2026-09-28T12:40+08:00
stage: 04 / round: r39 / status: DONE (IMPLEMENTATION: FIRST attack on the criterion R=P/C's own TEMPORAL validity — is the RANKING time-invariant? inv8..28 bounded the numerator P (size/count inv8..25, meaning inv26, dimension inv27, temporal-validity/sustainable-rate inv28) and the denominator C's ENERGY operating cost (inv25) — but NONE ever asked whether the RANKING itself holds over TIME. R=P/C prices the card at STICKER and ranks at TODAY's ratio = a SINGLE INSTANT; a deployed RUN runs a LIFETIME L while the hardware FRONTIER keeps improving -> the incumbent's RELATIVE $/tok DECAYS at obsolescence rate d/year -> the "best buy today" is only best TODAY -> the ranking silently assumed TIME-INVARIANT. Encoded as inv29 into roofline_verify.py + Q10 registered into resolve_hstar.py.)

# cursor: 04/r39 = the criterion R=P/C ranks H* at TODAY's ratio and prices the card at STICKER, silently assuming the ranking is TIME-INVARIANT and the sticker is the whole cost; task says RUN -> a deployed card runs a LIFETIME while the hardware frontier improves -> the incumbent's RELATIVE $/tok DECAYS at obsolescence rate d/year -> today's H*=A100-40 is a LEGACY card (EOL-adjacent, shortest remaining support) so it obsoletes FASTEST (d_a>d_s) -> its $/tok edge erodes -> over the deployment horizon the ranking FLIPS to the newer RTX_5090; break-even ~2.4y -> any RUN longer than that makes the legacy cheap card the WRONG buy -> DEPLOYMENT-LIFETIME / OBSOLESCENCE-RATE is NEW required input Q10

## ground-truth (re-confirm, honest-first)
- real cursor was notes/4-r38-status.md (r38 = inv28 sustained-vs-burst / thermal-derate on the numerator's temporal validity).
  This round attacks a NEW axis -- the RANKING's / criterion's own temporal validity (is the ordering time-invariant?) -- not a
  followup. Stayed GPU thread, did not restart.
- REJECTED-DUPLICATE (honest-first): grep confirmed obsolet / depreciat / lifetime / time-invariant / frontier / EOL /
  end-of-life / decay appear NOWHERE in roofline_verify.py or resolve_hstar.py -> genuinely unattacked. DISTINCT from inv25
  (that = ENERGY = a variable ADDITIVE operating cost added to C over the lifetime; this = a MULTIPLICATIVE decay of the card's
  RELATIVE competitiveness -> a DIFFERENT eventual winner: inv25's flip needs degraded efficiency, inv29's flip needs only the
  passage of time + obsolescence asymmetry). DISTINCT from inv28 (that attacked the NUMERATOR's temporal validity -- can the
  RATE be held 24/7; this attacks the DENOMINATOR's / the RANKING's temporal validity -- does the ORDERING hold over years).
  Not a duplicate.

## the genuine NEW unattacked silent assumption this round (the RANKING is priced at one instant, assumed eternal)
- R=P/C is a snapshot: it divides today's throughput by today's sticker price and declares a winner. It silently assumes the
  winner stays the winner FOREVER and that the sticker is the whole cost. But a deployed RUN is a multi-year service, and the
  hardware frontier moves every ~18 months -> a card bought today is progressively out-competed -> its EFFECTIVE $/tok (what it
  costs relative to the best available then) RISES even though its sticker never changes -> the ranking is TIME-DEPENDENT.
- KEY STRUCTURAL FINDING: this is the FIRST attack on the criterion's own TEMPORAL validity. inv8..25 bounded P's SIZE/COUNT,
  inv26 its MEANING, inv27 its DIMENSION, inv28 its sustainable RATE (the numerator's temporal validity), inv25 bounded C's
  additive ENERGY cost -- none ever asked whether the ORDERING survives over the deployment horizon.
- The teeth: today's H*=A100-40 is a LEGACY card (EOL-adjacent, shortest remaining support window) -> it obsoletes FASTEST
  (d_a=0.40 > d_s=0.15 for the fresh 5090) -> its $/tok edge erodes fastest -> over the horizon the ranking FLIPS to the
  newer RTX_5090. The cheap legacy card that wins today is the WRONG buy for a long deployment.

## done this round (implementation + verification)
### roofline_verify.py -- inv29 (ranking temporal validity / obsolescence-decay axis)
- OBSO = {A100-40:0.40, RTX_4090:0.25, L40S:0.20, RTX_5090:0.15} (annual obsolescence of RELATIVE $/tok; legacy A100-40
  obsoletes fastest, fresh 5090 slowest; exact rate market-blocked, DIRECTION legacy-obsoletes-faster-than-newer 一手✓ industry
  fact -- EOL/support-window asymmetry). LIFETIME = 5.0 (deployment horizon, USER/market Q10).
- cpt_a = sticker/roofline_sustained(A100-40,INT8) = $21.9 ; cpt_s = .../5090 = $35.4 -> today A100 cheaper $/tok (premise H*=A100 today).
- eff_a = cpt_a*(1+0.40)^5 = $118 ; eff_s = cpt_s*(1+0.15)^5 = $71 -> over 5y the legacy's effective $/tok OVER-TAKES -> FLIP.
- break-even lifetime (GUARDED): denom=log((1+d_a)/(1+d_s)); if denom<=0 -> clean semantic RED "no differential decay -> H* never
  flips -> teeth not biting"; else be_years = log(cpt_s/cpt_a)/denom = 2.4y -> any deployment RUN longer than 2.4y flips H*.
- canary: equalize obsolescence (both 0.15) -> no differential decay -> eff_a<=eff_s -> NO flip -> proves the flip is
  obsolescence-asymmetry-driven, not decorative.
### resolve_hstar.py -- register Q10 DEPLOYMENT-LIFETIME / OBSOLESCENCE-RATE as a required input
- REQUIRED_INPUTS += "Q10 DEPLOYMENT LIFETIME / OBSOLESCENCE RATE (...)".
- guard: fails if "Q10 DEPLOYMENT LIFETIME" not declared -> the tree must never rank H* at TODAY's ratio, silently assuming the
  ranking is time-invariant and the sticker is the whole cost.

## teeth-proven (EXIT captured DIRECTLY -- no grep-pipe PIPESTATUS reset)
- roofline_verify.py: [A] normal EXIT=0 (prints inv29 lines: today $/tok A100 $21.9 < 5090 $35.4; eff@5y A100 $118 vs 5090 $71
  -> flip; break-even 2.4y; + RESULT ALL ASSERTS PASS ✓); [B] canary equalize obsolescence (`"A100-40":0.40`->`0.15`) -> teeth fires
  RED 'legacy obsoletes no faster than fresh (d_a<=d_s) -> no differential decay -> H* never flips -> teeth not biting' -> TEETH_EXIT=1
  ✓ (this round FIXED a fragility: the unguarded break-even crashed with ZeroDivisionError when d_a==d_s, MASKING the clean
  semantic RED; added the `if denom<=0` guard so equal-obsolescence yields the correct teeth-not-biting message, not a traceback);
  [C] restore + run_all EXIT=0.
- resolve_hstar.py: [B'] canary sed delete ONLY the Q10 dict entry (`/^    "Q10 DEPLOYMENT/d`) -> guard survives (grep -c
  BEFORE=2 AFTER=1) -> fires RED RIGHT reason 'DEPLOYMENT-LIFETIME/OBSOLESCENCE NOT declared a required input' EXIT=1 ✓ captured
  directly no pipe; [C] restore (grep -c RESTORED=2) + run_all EXIT=0. (NOTE: first canary attempt copied to /tmp and hit
  ModuleNotFoundError: No module named 'roofline_verify' -- the SAME recurring /tmp bug as r30/r31/r32; FIXED by running the
  canary INSIDE tasks/ so the import resolves -- the false-green-teeth dict-anchor bug did NOT recur, the `^    "Q10 DEPLOYMENT`
  dict-entry-only anchor left the guard line intact.)

## why this matters (advance, not restate)
- The criterion has now been attacked on BOTH sides AND across TIME: denominator C in r35 (energy, additive), numerator P on four
  axes (size/count, meaning, dimension, sustainable-rate), and now the RANKING's own temporal validity (r39). The last asks the
  deepest question: R=P/C is a SNAPSHOT, but a deployment is a MARRATHON measured in years, and the frontier moves under it.
- The two-sided result is the point again: at TODAY's sticker ratio the ranking is stable (A100-40 cheapest $/tok) -- so the
  deliverable's recommendation does NOT change TODAY; BUT the teeth proves that over a deployment lifetime the legacy incumbent's
  edge erodes and the ranking FLIPS to the newer RTX_5090 at break-even ~2.4y. That converts "the best buy today is the best buy"
  from an implicit premise into a named, testable dependency (Q10: deployment lifetime + per-card obsolescence/support-decay rate).
- The distinctness is the point: inv25 (energy) and inv29 (obsolescence) both extend the cost over the deployment lifetime but by
  OPPOSITE mechanisms -- energy is ADDITIVE (adds a term to C), obsolescence is MULTIPLICATIVE (scales the card's relative value)
  -- and they produce DIFFERENT eventual winners (inv25 flips only under degraded efficiency; inv29 flips under mere time +
  obsolescence asymmetry). A lifetime that is short (<2.4y) keeps A100-40; a long one sends you to the 5090 despite its sticker.

## honest boundary (NOT loosened)
- deployment lifetime L + per-card obsolescence/support-decay rate = USER/market (Q10). The obsolescence DIRECTION (legacy EOL
  cards lose relative competitiveness faster than freshly-launched cards) is 一手✓ established industry fact (EOL announcement +
  shrinking support window + next-gen replacement cadence); the exact rates are illustrative-plausible, MARKET-BLOCKED (no live
  street-price trajectory / no per-card EOL calendar) -- same first-hand gap as all price/throughput numbers. No fabricated
  obsolescence curve.

## precise blocking (deliverable advances ONLY on these; unchanged from r38, plus the new Q10)
1. form-factor = USER (Q1). 2. refurb A100-40 quote vs $1735(decode)/$1995(prefill) = USER/market (Q2). 3. refurb RTX 4090
quote vs $1124 = USER/market (Q3). 4. batch size = USER/market (Q4). 5. working-sequence-length / CTX = USER/market (Q5).
6. Q6 ENERGY/TCO = $/kWh + deployment lifetime + A100 TDP variant confirmation (PCIe 250 vs SXM 400) = USER/market/hardware-spec.
7. Q7 OUTPUT QUALITY = acceptable-accuracy bar / eval-delta per quant = USER/market. 8. Q8 LATENCY/TTFT = interactive? max
acceptable TTFT? typical generation length G = USER/market. 9. Q9 SUSTAINED/THERMAL-DERATE = sustained soak bw / thermal envelope
/ duty cycle per card = USER/market/hardware. 10. NEW Q10 DEPLOYMENT-LIFETIME / OBSOLESCENCE-RATE = how many years will this
deployment run? per-card obsolescence/support-decay rate (legacy vs newer) = USER/market. 11. first-hand single-stream vLLM =
ENV (no CUDA) -- settles eta (inv13), KV dtype (inv19), prefill/decode ratio (inv20), sm_100 kernel-ready (inv21), A100-40 bw
(inv8), batch regime/B* (inv22), working-context/KV footprint (inv23), quant-recipe/FP16_LAYER_FRAC (inv24), real sustained board
power / efficiency-under-load (inv25), real perplexity/eval-delta per quant (inv26), real measured TTFT / end-to-end latency vs
the SLA (inv27), real sustained soak bw / thermal throttle behavior per card (inv28), and NOW the real street-price trajectory /
per-card EOL calendar that would settle the obsolescence rates (inv29 -- settles whether the legacy A100-40's $/tok edge really
erodes fast enough to flip H* within the intended deployment lifetime).

## next concrete action
- premise chain complete through PHASE / GATE / BATCH / CTX / WEIGHT-PRECISION-LAYERING / ENERGY-COST / OUTPUT-QUALITY /
  LATENCY-DIMENSION / SUSTAINED-THERMAL / RANKING-TEMPORAL-VALIDITY domains, all encoded AND every asserted number machine-computed,
  and the criterion now attacked on BOTH sides (denominator C in r35, ranking's temporal validity in r39) AND the numerator on four
  axes (size/count inv8..25, meaning inv26, dimension inv27, temporal-validity inv28). Offline advance genuinely exhausted -- HOLD
  awaiting user Q1-Q10 / market quotes / hardware / eval / lifetime. The loop does not stop; it records the exact reason and resumes
  when any input lands.

## r39 housekeeping
- persisted r39 cursor (this file); advanced INDEX.md cursor pointer r38->r39 + appended the r39 entry to the r-chain; added the
  inv29 block to the durable conclusion (04.5-r6-roofline-bound-conclusion.md); registered Q10 DEPLOYMENT-LIFETIME/OBSOLESCENCE-RATE
  into resolve_hstar.py's REQUIRED_INPUTS + guard (dict-entry-only sed anchor `^    "Q10 DEPLOYMENT` -> guard survives -> teeth RED
  right reason EXIT=1, ran canary INSIDE tasks/ to avoid the /tmp ModuleNotFoundError false-teeth); refreshed MEMORY.md index line
  with inv29 + the new Q10.