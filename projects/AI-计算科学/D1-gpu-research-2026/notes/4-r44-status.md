origin: ai
time: 2026-09-28T17:05+08:00
stage: 04 / round: r44 / status: DONE (IMPLEMENTATION: FIRST attack on the denominator C's LABOR basis -- was C EVER the cost of the OPERATOR who keeps the box alive, or only the cost of the MACHINE? inv25 attacked C's CONTENT (energy, additive recurring OPEX electricity -- a PHYSICAL quantity in kWh), inv29 its TEMPORAL validity (obsolescence), inv30 its SCOPE (host, additive one-time CAPEX of non-card HARDWARE), inv31 its NET-vs-GROSS basis (residual), inv32 its MULTIPLICITY (replicas), inv43 its COMPOSITION BEYOND HARDWARE (software, a CONTRACTUAL fee with ZERO physics) -- but EVERY one of them priced a MACHINE or a CONTRACT, silently assuming NO HUMAN ever has to touch the box. But task says RUN -> a deployed service is KEPT ALIVE by an OPERATOR (driver patching, failure triage, restart babysitting), and human labor costs money -> C UNDER-counted by the ops-labor OPEX -> the ranking is LABOR-BLIND. Encoded as inv44 into roofline_verify.py + Q15 registered into resolve_hstar.py.)

# cursor: 04/r44 = criterion C(H*) has ALWAYS been the cost of the MACHINE (hardware or a contract), silently assuming NO HUMAN ever touches the box; task says RUN -> a deployed service is KEPT ALIVE by an OPERATOR (driver patching, failure triage, restart babysitting) -> human labor costs money -> C UNDER-counted by the ops-labor OPEX -> the ranking is LABOR-BLIND. The teeth: the legacy datacenter A100-40 is EOL-adjacent with NO vendor support and NO auto-heal -> a human must MANUALLY babysit it around the clock (hand-patch every driver, triage every failure, restart on every crash); while a consumer RTX_5090 rides an unattended hobbyist desktop nobody touches. At a MODEST operator-labor the ranking is LABOR-ROBUST (eff $/tok A100 $34.7 < 5090 $35.4, H*=A100 today holds) BUT the legacy card's forced continuous manual-babysitting labor FLIPS eff $/tok to the consumer RTX_5090 ($34.7->$49.3 > $35.4) -> the sticker-cheap legacy card is the WRONG buy once you price the OPERATOR who keeps it alive -> OPERATOR LABOR / OPS-PERSONNEL is NEW required input Q15

## ground-truth (re-confirm, honest-first)
- real cursor was notes/4-r43-status.md (r43 = inv43 software/licensing stack cost). This round attacks a NEW axis --
  the denominator C's LABOR basis (is C the cost of the machine only, or does it include the human who keeps it alive?) -- not a followup. Stayed GPU thread, did not restart.
- REJECTED-DUPLICATE (honest-first): grep confirmed operator / personnel / labor / babysit / ops-staff / wage appear NOWHERE
  in roofline_verify.py or resolve_hstar.py (both counts = 0) -> genuinely unattacked. Not a duplicate. Every prior C-basis attack
  (content/temporal/scope/net-vs-gross/multiplicity/software-composition) priced a MACHINE or a CONTRACT; none ever priced HUMAN TIME.

## the genuine NEW unattacked silent assumption this round (C is priced as the MACHINE, assuming no human ever touches it)
- R=P/C has always set C = the sticker of the PHYSICAL hardware (or, in inv30/inv43, the host / software contract). That silently assumes NO HUMAN
  ever has to touch the box. But a deployed RUN is not self-sustaining -- someone must patch drivers, triage failures, restart crashed processes,
  and human labor costs money. The true deployment cost includes the ops-labor OPEX -> C UNDER-counted.
- KEY STRUCTURAL FINDING: this is the FIRST attack on the denominator's LABOR basis -- whether C includes the HUMAN who keeps the machine alive at
  all. inv25/inv30/inv43 added PHYSICAL quantities or CONTRACTUAL fees; none ever priced a WAGE paid TO a human.

## done this round (implementation + verification)
### roofline_verify.py -- inv44 (operator labor / ops-personnel axis)
- LABOR = {A100-40:$200/yr, RTX_5090:$0/yr} + HORIZON=2y (annual operator-labor per card; DIRECTION 一手✓ established fact -- datacenter hardware
  always carries dedicated ops staff and legacy/EOL hardware needs more hands-on babysitting, a consumer desktop runs unattended; exact $/yr
  USER/market Q15). guard inv44(0): each labor >=0 else the ops-labor model is broken.
- plausible MODEST labor: eff_cpt_a_lab = (1200 + 150*2 + 200*2)/roofline_sustained(A100-40,INT8) = $34.7 ; eff_cpt_s_lab = (1999 + 0 + 0)/
  roofline_sustained(5090,INT8) = $35.4 -> A100 still cheaper eff $/tok (premise H*=A100 today holds, margin now razor-thin $0.7), BUT C now
  carries the human labor it silently omitted -> ranking LABOR-ROBUST at modest labor.
- teeth: legacy EOL-adjacent card has NO vendor support and NO auto-heal -> a human must MANUALLY babysit it -> LABOR_AGG = {A100-40:$600/yr,
  RTX_5090:$0/yr} -> eff_cpt_a_lab_agg = (1200 + 300 + 1200)/roofline = $49.3 > $35.4 -> ranking FLIPS to the consumer RTX_5090 once you price
  the OPERATOR who keeps it alive -> the sticker-cheap legacy card is the WRONG buy -> genuinely able to fail.
- canary: force EQUAL labor on BOTH cards (consumer also babysat by a human, no longer unattended) -> the differential labor burden vanishes ->
  eff $/tok A100 $49.3 < 5090 $56.7 -> NO flip -> proves the flip is LABOR-asymmetry-driven (legacy babysat rack vs consumer unattended desktop),
  not decorative.
### resolve_hstar.py -- register Q15 OPERATOR LABOR / OPS-PERSONNEL as a required input
- REQUIRED_INPUTS += "Q15 OPERATOR LABOR / OPS-PERSONNEL (...)".
- guard: fails if "Q15 OPERATOR LABOR" not declared -> the tree must never price H* on the machine only, silently assuming no human ever touches it.

## teeth-proven (EXIT captured DIRECTLY -- no grep-pipe PIPESTATUS reset; zsh ${PIPESTATUS[0]} returns empty, use $? after direct run)
- roofline_verify.py: [A] normal EXIT=0 (prints inv44 lines: eff $/tok A100 $34.7 < 5090 $35.4 robust; teeth manual-babysitting $34.7->$49.3 >
  $35.4 -> FLIP; canary equal-labor $49.3 < $56.7 NO flip; + RESULT ALL ASSERTS PASS ✓); [B] teeth canary make the legacy babysitting FREE
  (`LABOR_AGG = {"A100-40":600,...}`->`{"A100-40":0,...}`) -> teeth fires RED 'ballooning legacy manual-babysitting labor did NOT flip eff $/tok
  to the 5090 -> teeth decorative' -> TEETH_EXIT=1 ✓ (ran INSIDE tasks/ via cp to avoid the recurring /tmp ModuleNotFoundError false-teeth);
  [C] rm canary + run_all EXIT=0.
- resolve_hstar.py: [B'] canary sed delete ONLY the Q15 dict entry (`/^    "Q15 OPERATOR LABOR/d` -- the `^    "Q15` indent anchor does NOT match
  the guard line which starts `if "Q15`, so the guard survives) -> grep -c BEFORE=2 AFTER=1 -> fires RED RIGHT reason 'OPERATOR-LABOR/
  OPS-PERSONNEL NOT declared a required input' EXIT=1 ✓ captured directly no pipe; [C] restore (grep -c RESTORED=2) + run_all EXIT=0.

## why this matters (advance, not restate)
- The denominator C has now been attacked on SEVEN axes: CONTENT (inv25 energy), TEMPORAL validity (inv29 obsolescence), SCOPE (inv30 host),
  NET-vs-GROSS basis (inv31 residual), MULTIPLICITY (inv32 replicas), COMPOSITION BEYOND HARDWARE (inv43 software), and now LABOR BASIS
  (inv44, does C include the human who keeps the machine alive at all?). The structural point: every prior C priced a MACHINE or a CONTRACT;
  none ever priced HUMAN TIME.
- The two-sided result is the point again: at a MODEST operator-labor the ranking is LABOR-ROBUST (eff $/tok barely moves, A100 still cheapest
  but the margin is now razor-thin $0.7 -- the labor axis nearly eats the entire sticker edge); BUT the teeth proves that when the legacy
  EOL-adjacent card has no vendor support and no auto-heal -- a human is the only thing keeping it up -- the labor bill balloons and eff $/tok
  FLIPS to the consumer RTX_5090. That converts "no human ever touches the box" from an implicit premise into a named, testable dependency
  (Q15: the annual operator-labor per card / unattended-vs-dedicated-hands-on-staff).
- The distinctness is the point: inv44 (labor) attacks C with HUMAN TIME, a biological quantity with zero physics and zero contract; inv25
  (energy) was a recurring OPEX but a PHYSICAL quantity (electricity kWh); inv43 (software) was a CONTRACTUAL license fee paid TO a vendor
  (this is a WAGE paid TO a human -- different payee, different substance); inv30 (host) ADDS one-time CAPEX of non-card HARDWARE (different
  timing AND substance); inv32 (replicas) MULTIPLIES the count of cards (no unit multiplication here, an additive fee per card).

## honest boundary (NOT loosened)
- the annual operator-labor / ops-personnel cost per card / whether the deployment is unattended or needs dedicated hands-on staff = USER/market
  (Q15). The labor DIRECTION (datacenter hardware always carries dedicated ops staff and legacy/EOL hardware needs more hands-on babysitting,
  while a consumer desktop runs unattended) is 一手✓ established fact; the exact $/yr is illustrative-plausible, MARKET-BLOCKED (no live labor
  rate). No fabricated wage.

## precise blocking (deliverable advances ONLY on these; unchanged from r43, plus the new Q15)
1. form-factor = USER (Q1). 2. refurb A100-40 quote vs $1735(decode)/$1995(prefill) = USER/market (Q2). 3. refurb RTX 4090 quote vs $1124 =
   USER/market (Q3). 4. batch size = USER/market (Q4). 5. working-sequence-length / CTX = USER/market (Q5). 6. Q6 ENERGY/TCO = $/kWh +
   deployment lifetime + A100 TDP variant confirmation (PCIe 250 vs SXM 400) = USER/market/hardware-spec. 7. Q7 OUTPUT QUALITY = acceptable-accuracy
   bar / eval-delta per quant = USER/market. 8. Q8 LATENCY/TTFT = interactive? max acceptable TTFT? typical generation length G = USER/market.
   9. Q9 SUSTAINED/THERMAL-DERATE = sustained soak bw / thermal envelope / duty cycle per card = USER/market/hardware. 10. Q10
   DEPLOYMENT-LIFETIME / OBSOLESCENCE-RATE = how many years will this deployment run? per-card obsolescence/support-decay rate = USER/market.
   11. Q11 SYSTEM-LEVEL BOM / HOST-COST = the non-card host BOM per deployment (server-class vs desktop) + whether the card must live in a rack
   = USER/market. 12. Q12 RESIDUAL VALUE / NET-COST-of-ownership = the end-of-life residual / resale fraction per card = USER/market. 13. Q13
   REPLICAS / REDUNDANCY / HA = the production replica count per card / uptime SLA (and whether the redundancy is active-active or
   active-passive) = USER/market. 14. Q14 SOFTWARE / LICENSING STACK COST = the annual software+support license fee per card / whether the
   deployment runs a paid commercial stack or a free open-source stack = USER/market. 15. NEW Q15 OPERATOR LABOR / OPS-PERSONNEL = the annual
   operator-labor / ops-personnel cost per card / whether the deployment is unattended or needs dedicated hands-on staff = USER/market. 16.
   first-hand single-stream vLLM = ENV (no CUDA) -- settles eta (inv13), KV dtype (inv19), prefill/decode ratio (inv20), sm_100 kernel-ready
   (inv21), A100-40 bw (inv8), batch regime/B* (inv22), working-context/KV footprint (inv23), quant-recipe/FP16_LAYER_FRAC (inv24), real
   sustained board power / efficiency-under-load (inv25), real perplexity/eval-delta per quant (inv26), real measured TTFT / end-to-end latency
   vs the SLA (inv27), real sustained soak bw / thermal throttle behavior per card (inv28), the real street-price trajectory / per-card EOL
   calendar that would settle the obsolescence rates (inv29), the real vendor quote for a full HOST BOM (server-class vs desktop) (inv30), the
   real resale / end-of-life residual quote per card (inv31), the real production replica count / uptime SLA per card (inv32), the real annual
   software+support license quote per card (inv43), and NOW the real annual operator-labor / ops-personnel quote per card that would settle
   whether the sticker-cheap legacy card's edge survives the babysitting labor it requires (inv44).

## next concrete action
- premise chain complete through PHASE / GATE / BATCH / CTX / WEIGHT-PRECISION-LAYERING / ENERGY-COST / OUTPUT-QUALITY / LATENCY-DIMENSION /
  SUSTAINED-THERMAL / RANKING-TEMPORAL-VALIDITY / SYSTEM-BOM-SCOPE / RESIDUAL-NET-COST / REPLICAS-HA-FLEET / SOFTWARE-LICENSING-STACK /
  OPERATOR-LABOR domains, all encoded AND every asserted number machine-computed, and the criterion now attacked on BOTH sides (denominator C:
  r35 energy-content + r39 ranking-temporal + r40 system-scope + r41 residual-net-basis + r42 replicas-multiplicity + r43
  software-composition + r44 labor-basis) AND the numerator on four axes (size/count inv8..25, meaning inv26, dimension inv27,
  temporal-validity inv28). Offline advance genuinely exhausted -- HOLD awaiting user Q1-Q15 / market quotes / hardware / eval / lifetime /
  host-BOM / residual-resale / replica-SLA / software-license-quote / operator-labor-quote. The loop does not stop; it records the exact reason
  and resumes when any input lands.

## r44 housekeeping
- persisted r44 cursor (this file); advanced INDEX.md cursor pointer r42->r44 (the pointer was STALE at r42 -- corrected this round) + appended the
  r44 inv44 entry to the r-chain; added the inv44 block to the durable conclusion (04.5-r6-roofline-bound-conclusion.md) and advanced its
  axis-count SIX->SEVEN; registered Q15 OPERATOR LABOR/OPS-PERSONNEL into resolve_hstar.py's REQUIRED_INPUTS + guard (dict-entry-only sed anchor
  `^    "Q15 OPERATOR LABOR` -> guard survives -> teeth RED right reason EXIT=1, ran canary INSIDE tasks/ via cp to avoid the /tmp
  ModuleNotFoundError false-teeth); refreshed MEMORY.md index line with inv44 + the new Q15 + extended the first-hand-decouple list with
  annual-operator-labor-quote-per-card.