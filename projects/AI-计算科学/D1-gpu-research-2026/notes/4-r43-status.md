origin: ai
time: 2026-09-28T16:10+08:00
stage: 04 / round: r43 / status: DONE (IMPLEMENTATION: FIRST attack on the denominator C's COMPOSITION BEYOND HARDWARE -- was C EVER the cost of the SOFTWARE STACK, or only the cost of the PHYSICAL box? inv25 attacked C's CONTENT (energy, additive recurring OPEX electricity -- a PHYSICAL quantity in kWh), inv29 its TEMPORAL validity (obsolescence, multiplicative decay of the ratio), inv30 its SCOPE (host, additive one-time CAPEX of non-card HARDWARE), inv31 its NET-vs-GROSS basis (residual, subtractive terminal credit recovered FROM the card), inv32 its MULTIPLICITY (replicas, multiplicative count of cards) -- but EVERY one of them priced C as PHYSICAL HARDWARE ONLY, silently assuming the SOFTWARE you must run to serve a model is FREE. But task says RUN -> a deployed inference service runs a SOFTWARE STACK (OS + drivers + CUDA + inference engine + orchestration + monitoring), and much of that carries a LICENSE / support SUBSCRIPTION fee -> C UNDER-counted by the software OPEX -> the ranking is SOFTWARE-BLIND. Encoded as inv43 into roofline_verify.py + Q14 registered into resolve_hstar.py.)

# cursor: 04/r43 = criterion C(H*) has ALWAYS been the cost of the PHYSICAL HARDWARE, silently assuming the SOFTWARE STACK you must run to serve a model is FREE; task says RUN -> a deployed service runs OS+drivers+CUDA+inference-engine+orchestration+monitoring, much of it carrying a LICENSE / support SUBSCRIPTION -> C UNDER-counted by the software OPEX -> the ranking is SOFTWARE-BLIND. The teeth: the legacy datacenter A100-40 is EOL-adjacent -> it CANNOT run an unsupported free stack on live traffic -> it must rent a FULL commercial enterprise inference stack + enterprise OS support tied to its vendor support contract -> its software bill balloons; while a consumer RTX_5090 runs a FREE desktop stack (Ubuntu + open-source vLLM, no license fee). At a MODEST license the ranking is SOFTWARE-ROBUST (eff $/tok A100 $27.4 < 5090 $35.4, H*=A100 today holds) BUT the legacy card's forced enterprise-stack license FLIPS eff $/tok to the consumer RTX_5090 ($27.4->$40.2 > $35.4) -> the sticker-cheap legacy card is the WRONG buy once you price the SOFTWARE it must rent -> SOFTWARE / LICENSING STACK COST is NEW required input Q14

## ground-truth (re-confirm, honest-first)
- real cursor was notes/4-r42-status.md (r42 = inv32 replicas / redundancy / HA). This round attacks a NEW axis --
  the denominator C's COMPOSITION BEYOND HARDWARE (is C the cost of the physical box only, or does it include the software stack?) -- not a followup. Stayed GPU thread, did not restart.
- REJECTED-DUPLICATE (honest-first): grep confirmed license / subscription / software / stack_cost / commercial_stack / free_desktop appear NOWHERE
  in roofline_verify.py or resolve_hstar.py (both counts = 0) -> genuinely unattacked. Not a duplicate. Every prior C-basis attack (content/temporal/scope/net-vs-gross/multiplicity) priced HARDWARE only.

## the genuine NEW unattacked silent assumption this round (C is priced as the PHYSICAL box, assuming the software stack is free)
- R=P/C has always set C = the sticker of the PHYSICAL hardware. That silently assumes the SOFTWARE you must run to serve a model costs NOTHING.
  But a deployed RUN is not just a box -- to actually serve tokens you run OS + drivers + CUDA + an inference engine + orchestration + monitoring,
  and much of that carries a LICENSE / support SUBSCRIPTION fee. The true deployment cost includes the software OPEX -> C UNDER-counted.
- KEY STRUCTURAL FINDING: this is the FIRST attack on the denominator's COMPOSITION BEYOND HARDWARE -- whether C includes the SOFTWARE layer at
  all. inv25/inv30 added PHYSICAL quantities (energy in kWh, host in $ of non-card hardware); none ever priced a CONTRACTUAL software fee.

## done this round (implementation + verification)
### roofline_verify.py -- inv43 (software / licensing stack cost axis)
- LIC = {A100-40:$150/yr, RTX_5090:$0/yr} + HORIZON=2y (annual software+support subscription per card; DIRECTION 一手✓ established fact --
  datacenter/enterprise software is licensed per-node under paid vendor support contracts, consumer/desktop stacks are free open-source; exact
  $/yr USER/market Q14). guard inv43(0): each license >=0 and horizon >=1 else the software-cost model is broken.
- plausible MODEST license: eff_cpt_a = (1200 + 150*2)/roofline_sustained(A100-40,INT8) = $27.4 ; eff_cpt_s = (1999 + 0*2)/roofline_sustained
  (5090,INT8) = $35.4 -> A100 still cheaper eff $/tok (premise H*=A100 today holds), BUT C now carries the software layer it silently omitted
  -> ranking SOFTWARE-ROBUST at modest license.
- teeth: legacy EOL-adjacent card CANNOT run an unsupported free stack on live traffic -> must rent a FULL commercial enterprise inference stack +
  enterprise OS support -> LIC_AGG = {A100-40:$500/yr, RTX_5090:$0/yr} -> eff_cpt_a_agg = (1200 + 500*2)/roofline = $40.2 > $35.4 -> ranking
  FLIPS to the consumer RTX_5090 once you price the SOFTWARE it must rent -> the sticker-cheap legacy card is the WRONG buy -> genuinely able to fail.
- canary: force EQUAL license on BOTH cards (consumer also pays the same $500/yr enterprise stack, no longer free) -> the differential software
  burden vanishes -> eff $/tok A100 $40.2 < 5090 $53.2 -> NO flip -> proves the flip is SOFTWARE-COST-asymmetry-driven (legacy paid enterprise
  stack vs consumer FREE desktop stack), not decorative.
### resolve_hstar.py -- register Q14 SOFTWARE / LICENSING STACK COST as a required input
- REQUIRED_INPUTS += "Q14 SOFTWARE / LICENSING STACK COST (...)".
- guard: fails if "Q14 SOFTWARE" not declared -> the tree must never price H* on the physical hardware only, silently assuming the software stack is free.

## teeth-proven (EXIT captured DIRECTLY -- no grep-pipe PIPESTATUS reset; zsh ${PIPESTATUS[0]} returns empty, use $? after direct run)
- roofline_verify.py: [A] normal EXIT=0 (prints inv43 lines: eff $/tok A100 $27.4 < 5090 $35.4 robust; teeth enterprise-stack $27.4->$40.2 >
  $35.4 -> FLIP; canary equal-license $40.2 < $53.2 NO flip; + RESULT ALL ASSERTS PASS ✓); [B] teeth canary make the legacy license FREE
  (`LIC_AGG = {"A100-40":500,...}`->`{"A100-40":0,...}`) -> teeth fires RED 'ballooning legacy enterprise-stack license did NOT flip eff $/tok to
  the 5090 -> teeth decorative' -> TEETH_EXIT=1 ✓ (ran INSIDE tasks/ via cp to avoid the recurring /tmp ModuleNotFoundError false-teeth);
  [C] rm canary + run_all EXIT=0.
- resolve_hstar.py: [B'] canary sed delete ONLY the Q14 dict entry (`/^    "Q14 SOFTWARE/d` -- the `^    "Q14` indent anchor does NOT match the
  guard line which starts `if "Q14`, so the guard survives) -> grep -c BEFORE=2 AFTER=1 -> fires RED RIGHT reason 'SOFTWARE/LICENSING STACK COST
  NOT declared a required input' EXIT=1 ✓ captured directly no pipe; [C] restore (grep -c RESTORED=2) + run_all EXIT=0.

## why this matters (advance, not restate)
- The denominator C has now been attacked on SIX axes: CONTENT (inv25 energy, additive opex over lifetime), TEMPORAL validity (inv29 obsolescence,
  multiplicative over years), SCOPE (inv30 host, additive one-time capex of non-card hardware), NET-vs-GROSS basis (inv31 residual, subtractive
  terminal credit recovered FROM the card), MULTIPLICITY (inv32 replicas, multiplicative count of cards), and now COMPOSITION BEYOND HARDWARE
  (inv43 software, does C include the licensed software layer at all?). The last is the structural point: every prior C was the cost of a PHYSICAL
  box; none ever priced a CONTRACTUAL software fee.
- The two-sided result is the point again: at a MODEST license the ranking is SOFTWARE-ROBUST (eff $/tok unchanged, A100 still cheapest); BUT the
  teeth proves that when the legacy EOL-adjacent card cannot run an unsupported free stack on live traffic -- it must rent a paid enterprise
  inference + OS-support stack -- the software bill balloons and eff $/tok DOUBLES-ish and the ranking FLIPS to the consumer RTX_5090. That converts
  "the software stack is free" from an implicit premise into a named, testable dependency (Q14: the annual software+support license fee per card /
  paid-commercial-vs-free-open-source).
- The distinctness is the point: inv43 (software) attacks C with a CONTRACTUAL legal-commercial fee with ZERO physics; inv25 (energy) was a
  recurring OPEX but a PHYSICAL quantity (electricity kWh x $/kWh, pure physics); inv30 (host) ADDS one-time CAPEX of non-card HARDWARE (different
  timing AND substance); inv31 (residual) SUBTRACTS a terminal credit recovered FROM the card (opposite sign, paid TO a vendor here); inv32
  (replicas) MULTIPLIES the count of cards (no unit multiplication here, an additive fee per card).

## honest boundary (NOT loosened)
- the annual software+support license fee per card / whether the deployment runs a paid commercial stack or a free open-source stack = USER/market
  (Q14). The software-cost DIRECTION (datacenter/enterprise software is licensed per-node under paid vendor support contracts, while consumer/desktop
  stacks are free open-source) is 一手✓ established fact (the licensing asymmetry between enterprise and consumer software); the exact $/yr is
  illustrative-plausible, MARKET-BLOCKED (no live vendor quote). No fabricated license price.

## precise blocking (deliverable advances ONLY on these; unchanged from r42, plus the new Q14)
1. form-factor = USER (Q1). 2. refurb A100-40 quote vs $1735(decode)/$1995(prefill) = USER/market (Q2). 3. refurb RTX 4090 quote vs $1124 =
   USER/market (Q3). 4. batch size = USER/market (Q4). 5. working-sequence-length / CTX = USER/market (Q5). 6. Q6 ENERGY/TCO = $/kWh +
   deployment lifetime + A100 TDP variant confirmation (PCIe 250 vs SXM 400) = USER/market/hardware-spec. 7. Q7 OUTPUT QUALITY = acceptable-accuracy
   bar / eval-delta per quant = USER/market. 8. Q8 LATENCY/TTFT = interactive? max acceptable TTFT? typical generation length G = USER/market.
   9. Q9 SUSTAINED/THERMAL-DERATE = sustained soak bw / thermal envelope / duty cycle per card = USER/market/hardware. 10. Q10
   DEPLOYMENT-LIFETIME / OBSOLESCENCE-RATE = how many years will this deployment run? per-card obsolescence/support-decay rate = USER/market.
   11. Q11 SYSTEM-LEVEL BOM / HOST-COST = the non-card host BOM per deployment (server-class vs desktop) + whether the card must live in a rack =
   USER/market. 12. Q12 RESIDUAL VALUE / NET-COST-of-ownership = the end-of-life residual / resale fraction per card = USER/market. 13. Q13
   REPLICAS / REDUNDANCY / HA = the production replica count per card / uptime SLA (and whether the redundancy is active-active or active-passive) =
   USER/market. 14. NEW Q14 SOFTWARE / LICENSING STACK COST = the annual software+support license fee per card / whether the deployment runs a paid
   commercial stack or a free open-source stack = USER/market. 15. first-hand single-stream vLLM = ENV (no CUDA) -- settles eta (inv13), KV dtype
   (inv19), prefill/decode ratio (inv20), sm_100 kernel-ready (inv21), A100-40 bw (inv8), batch regime/B* (inv22), working-context/KV footprint
   (inv23), quant-recipe/FP16_LAYER_FRAC (inv24), real sustained board power / efficiency-under-load (inv25), real perplexity/eval-delta per quant
   (inv26), real measured TTFT / end-to-end latency vs the SLA (inv27), real sustained soak bw / thermal throttle behavior per card (inv28), the real
   street-price trajectory / per-card EOL calendar that would settle the obsolescence rates (inv29), the real vendor quote for a full HOST BOM
   (server-class vs desktop) (inv30), the real resale / end-of-life residual quote per card (inv31), the real production replica count / uptime SLA
   per card (inv32), and NOW the real annual software+support license quote per card that would settle whether the sticker-cheap legacy card's edge
   survives the enterprise-stack software OPEX it must rent (inv43).

## next concrete action
- premise chain complete through PHASE / GATE / BATCH / CTX / WEIGHT-PRECISION-LAYERING / ENERGY-COST / OUTPUT-QUALITY / LATENCY-DIMENSION /
  SUSTAINED-THERMAL / RANKING-TEMPORAL-VALIDITY / SYSTEM-BOM-SCOPE / RESIDUAL-NET-COST / REPLICAS-HA-FLEET / SOFTWARE-LICENSING-STACK domains, all
  encoded AND every asserted number machine-computed, and the criterion now attacked on BOTH sides (denominator C: r35 energy-content + r39
  ranking-temporal + r40 system-scope + r41 residual-net-basis + r42 replicas-multiplicity + r43 software-composition) AND the numerator on four
  axes (size/count inv8..25, meaning inv26, dimension inv27, temporal-validity inv28). Offline advance genuinely exhausted -- HOLD awaiting user
  Q1-Q14 / market quotes / hardware / eval / lifetime / host-BOM / residual-resale / replica-SLA / software-license-quote. The loop does not stop;
  it records the exact reason and resumes when any input lands.

## r43 housekeeping
- persisted r43 cursor (this file); advanced INDEX.md cursor pointer r42->r43 + appended the r43 inv43 entry to the r-chain; added the inv43 block
  to the durable conclusion (04.5-r6-roofline-bound-conclusion.md); registered Q14 SOFTWARE/LICENSING STACK COST into resolve_hstar.py's
  REQUIRED_INPUTS + guard (dict-entry-only sed anchor `^    "Q14 SOFTWARE` -> guard survives -> teeth RED right reason EXIT=1, ran canary INSIDE
  tasks/ via cp to avoid the /tmp ModuleNotFoundError false-teeth); refreshed MEMORY.md index line with inv43 + the new Q14 + extended the
  first-hand-decouple list with annual-software-support-license-quote-per-card.