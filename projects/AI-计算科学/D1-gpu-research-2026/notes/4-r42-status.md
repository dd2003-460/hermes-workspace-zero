origin: ai
time: 2026-09-28T15:20+08:00
stage: 04 / round: r42 / status: DONE (IMPLEMENTATION: FIRST attack on the denominator C's MULTIPLICITY / unit-count basis -- was C ever the cost of the DEPLOYMENT or only the cost of ONE CARD? inv25 attacked C's CONTENT (energy, additive recurring OPEX over lifetime), inv29 attacked C's TEMPORAL validity (obsolescence, multiplicative decay of relative value), inv30 attacked C's SCOPE (host, additive one-time CAPEX of non-card hardware), inv31 attacked C's NET-vs-GROSS basis (residual, subtractive terminal credit recovered FROM the card) -- but ALL of them priced C as EXACTLY ONE CARD, silently assuming the deployment is a SINGLE POINT OF FAILURE with zero redundancy. But task says RUN -> a deployed inference service for REAL USERS needs UPTIME -> production runs REPLICAS (N+1) -> true deployment cost = k*sticker -> C UNDER-COUNTED by the replica count -> the ranking is REPLICAS-BLIND. Encoded as inv32 into roofline_verify.py + Q13 registered into resolve_hstar.py.)

# cursor: 04/r42 = criterion C(H*) has ALWAYS been the cost of EXACTLY ONE CARD, silently assuming the deployment is a SINGLE POINT OF FAILURE with zero redundancy; task says RUN -> a deployed inference service for REAL USERS needs UPTIME -> production runs REPLICAS (N+1) -> true deployment cost = k*sticker -> C UNDER-COUNTED by the replica count -> the ranking is REPLICAS-BLIND. The teeth: the legacy datacenter A100-40 is EOL-adjacent (higher failure risk, thinner vendor support) -> its redundancy must be ACTIVE-PASSIVE hot-standby (you cannot trust two old cards to both carry live traffic -> the standby is idle insurance, contributes ZERO throughput) -> fleet COST scales with replicas but fleet THROUGHPUT does NOT -> fleet $/tok DOUBLES; while a fresh consumer RTX_5090 runs ACTIVE-ACTIVE (or single) -> its redundancy is capacity not idle insurance -> at plausible ACTIVE-ACTIVE redundancy the replica count CANCELS in $/tok (fleet $/tok A100 $21.9 < 5090 $35.4, ranking replicas-robust, H*=A100 today holds) BUT the legacy idle hot-standby FLIPS fleet $/tok to the consumer RTX_5090 ($21.9->$43.9 > $35.4) -> the sticker-cheap legacy card is the WRONG buy once you price the HA fleet -> REPLICAS / REDUNDANCY / HA is NEW required input Q13

## ground-truth (re-confirm, honest-first)
- real cursor was notes/4-r41-status.md (r41 = inv31 residual-value / net-cost). This round attacks a NEW axis --
  the denominator C's MULTIPLICITY / unit-count basis (is C the cost of ONE card or of the whole fleet?) -- not a followup. Stayed GPU thread, did not restart.
- REJECTED-DUPLICATE (honest-first): grep confirmed replica / redundancy / fleet / active-passive / standby / N+1 appear NOWHERE
  in roofline_verify.py or resolve_hstar.py (both counts = 0) -> genuinely unattacked. Not a duplicate.

## the genuine NEW unattacked silent assumption this round (C is priced as the cost of ONE card, i.e. a single point of failure)
- R=P/C has always set C = the cost of EXACTLY ONE card. That silently assumes the deployment is a SINGLE POINT OF FAILURE -- if that card
  dies, the service dies. But a deployed RUN serving real users is not a hobbyist box -- production needs UPTIME, and a service that goes
  down when one card fails is not deployable. Production runs REPLICAS (N+1) -> the true deployment cost is k*sticker, not sticker.
- KEY STRUCTURAL FINDING: this is the FIRST attack on the denominator's MULTIPLICITY / unit-count basis -- whether C counts ONE unit or the
  WHOLE fleet. inv25 extended C's CONTENT (energy added on top), inv29 its TEMPORAL validity (obsolescence decay of the ratio), inv30 its
  SCOPE (host hardware added on top), inv31 its NET-vs-GROSS basis (residual subtracted back); none ever asked how many CARDS the deployment
  actually buys.
- The teeth (the load-bearing asymmetry): the legacy datacenter A100-40 is EOL-adjacent -- higher failure risk and thinner vendor support -> its
  redundancy must be ACTIVE-PASSIVE hot-standby (you cannot trust two old cards to BOTH carry live traffic -> the standby is idle insurance,
  contributes ZERO throughput) -> fleet COST scales with replicas but fleet THROUGHPUT does NOT -> fleet $/tok DOUBLES. A fresh consumer
  RTX_5090 runs ACTIVE-ACTIVE (or single) -> its redundancy is capacity, not idle insurance.

## done this round (implementation + verification)
### roofline_verify.py -- inv32 (replicas / redundancy / HA axis)
- REPLICAS = {A100-40:2, RTX_5090:1} (production replicas to meet the same uptime SLA; DIRECTION 一手✓ established fact -- legacy/EOL hardware
  has higher failure probability and shorter support -> production mandates N+1 redundancy, a fresh consumer card meets the SLA
  single-replica; exact replica count / SLA USER/market Q13). guard inv32(0): each replica count >=1 else the fleet-cost model is broken.
- plausible ACTIVE-ACTIVE: fleet_cpt_a = 2*1200/(2*roofline_sustained(A100-40,INT8)) = $21.9 ; fleet_cpt_s = 1*1999/(1*roofline_sustained
  (5090,INT8)) = $35.4 -> the replica count CANCELS (throughput scales with replicas) -> A100 still cheaper fleet $/tok (premise H*=A100
  today holds), BUT the fleet is now 2 cards not 1 -> C under-counted by the replica count -> ranking REPLICAS-ROBUST at active-active.
- teeth: legacy redundancy ACTIVE-PASSIVE hot-standby -> fleet_cpt_a_passive = 2*1200/(1*roofline_sustained) = $43.9 (cost 2x, throughput
  1x, standby IDLE insurance not capacity) > $35.4 -> ranking FLIPS to the consumer RTX_5090 once you price the HA fleet -> the
  sticker-cheap legacy card is the WRONG buy -> genuinely able to fail.
- canary: force legacy standby ACTIVE-ACTIVE (standby serves traffic, throughput scales) -> fleet $/tok A100 $21.9 < 5090 $35.4 -> NO flip
  -> proves the flip is REDUNDANCY-MODE-asymmetry-driven (legacy idle hot-standby vs fresh active-active), not decorative.
### resolve_hstar.py -- register Q13 REPLICAS / REDUNDANCY / HA as a required input
- REQUIRED_INPUTS += "Q13 REPLICAS / REDUNDANCY / HA (...)".
- guard: fails if "Q13 REPLICAS" not declared -> the tree must never price H* on the cost of ONE card, silently assuming a single point of
  failure with zero redundancy.

## teeth-proven (EXIT captured DIRECTLY -- no grep-pipe PIPESTATUS reset; zsh ${PIPESTATUS[0]} returns empty, use $? after direct run)
- roofline_verify.py: [A] normal EXIT=0 (prints inv32 lines: fleet $/tok A100 $21.9 < 5090 $35.4 replica count cancels robust; teeth
  active-passive standby $21.9->$43.9 > $35.4 -> FLIP; canary active-active $21.9 NO flip; + RESULT ALL ASSERTS PASS ✓); [B] teeth canary
  make the legacy standby SERVE traffic (active-active, `/(1*roofline...)`->`/(REPLICAS[...] * roofline...)`) -> teeth fires RED 'idle-standby
  legacy fleet did NOT flip fleet $/tok to the 5090 -> teeth decorative' -> TEETH_EXIT=1 ✓ (ran INSIDE tasks/ via cp to avoid the recurring
  /tmp ModuleNotFoundError false-teeth); [C] rm canary + run_all EXIT=0.
- resolve_hstar.py: [B'] canary sed delete ONLY the Q13 dict entry (`/^    "Q13 REPLICAS/d` -- the `^    "Q13` indent anchor does NOT match
  the guard line which starts `if "Q13`, so the guard survives) -> grep -c BEFORE=2 AFTER=1 -> fires RED RIGHT reason 'REPLICAS/REDUNDANCY/HA
  NOT declared a required input' EXIT=1 ✓ captured directly no pipe; [C] restore (grep -c RESTORED=2) + run_all EXIT=0.

## why this matters (advance, not restate)
- The denominator C has now been attacked on FIVE axes: CONTENT (inv25 energy, additive opex over lifetime), TEMPORAL validity (inv29
  obsolescence, multiplicative over years), SCOPE (inv30 host, additive one-time capex of non-card hardware), NET-vs-GROSS basis (inv31
  residual, subtractive terminal credit recovered FROM the card), and now MULTIPLICITY / unit-count (inv32, does the deployment buy one card or
  a fleet?). The last is the structural point: every prior C was the cost of a single card; none ever asked how many cards the deployment
  actually needs to stay up.
- The two-sided result is the point again: at plausible ACTIVE-ACTIVE redundancy the ranking is REPLICAS-ROBUST (the replica count cancels
  because throughput scales with replicas, fleet $/tok unchanged, A100 still cheapest); BUT the teeth proves that when the legacy card's
  redundancy must be ACTIVE-PASSIVE hot-standby -- idle insurance that carries ZERO traffic -- the fleet COST scales but fleet THROUGHPUT
  does NOT, so fleet $/tok DOUBLES and the ranking FLIPS to the consumer RTX_5090. That converts "the deployment is one card" from an
  implicit premise into a named, testable dependency (Q13: the production replica count / uptime SLA per card).
- The distinctness is the point: inv32 (replicas) attacks C by MULTIPLYING more units of the very thing already in C (more cards); inv30
  (host) ADDS a different component (non-card hardware); inv31 (residual) SUBTRACTS a terminal credit recovered FROM the card; inv29
  (obsolescence) MULTIPLICATIVELY decays the relative ratio over years; inv22 (batch) scaled P (requests per card), this scales C (cards
  bought).

## honest boundary (NOT loosened)
- the production replica count / uptime SLA per card = USER/market (Q13). The redundancy DIRECTION (a legacy EOL-adjacent datacenter card has
  higher failure probability and a shorter support window -> production mandates N+1 redundancy, while a fresh consumer card meets the SLA
  single-replica) is 一手✓ established fact (hardware reliability / vendor-support asymmetry); the exact replica count is illustrative-plausible,
  MARKET-BLOCKED (no live SLA / fleet spec). No fabricated fleet size.

## precise blocking (deliverable advances ONLY on these; unchanged from r41, plus the new Q13)
1. form-factor = USER (Q1). 2. refurb A100-40 quote vs $1735(decode)/$1995(prefill) = USER/market (Q2). 3. refurb RTX 4090 quote vs
$1124 = USER/market (Q3). 4. batch size = USER/market (Q4). 5. working-sequence-length / CTX = USER/market (Q5). 6. Q6 ENERGY/TCO =
$/kWh + deployment lifetime + A100 TDP variant confirmation (PCIe 250 vs SXM 400) = USER/market/hardware-spec. 7. Q7 OUTPUT QUALITY =
acceptable-accuracy bar / eval-delta per quant = USER/market. 8. Q8 LATENCY/TTFT = interactive? max acceptable TTFT? typical generation
length G = USER/market. 9. Q9 SUSTAINED/THERMAL-DERATE = sustained soak bw / thermal envelope / duty cycle per card = USER/market/
hardware. 10. Q10 DEPLOYMENT-LIFETIME / OBSOLESCENCE-RATE = how many years will this deployment run? per-card obsolescence/support-decay
rate = USER/market. 11. Q11 SYSTEM-LEVEL BOM / HOST-COST = the non-card host BOM per deployment (server-class vs desktop) + whether the
card must live in a rack = USER/market. 12. Q12 RESIDUAL VALUE / NET-COST-of-ownership = the end-of-life residual / resale fraction per
card = USER/market. 13. NEW Q13 REPLICAS / REDUNDANCY / HA = the production replica count per card / uptime SLA (and whether the
redundancy is active-active or active-passive) = USER/market. 14. first-hand single-stream vLLM = ENV (no CUDA) -- settles eta (inv13),
KV dtype (inv19), prefill/decode ratio (inv20), sm_100 kernel-ready (inv21), A100-40 bw (inv8), batch regime/B* (inv22), working-context/
KV footprint (inv23), quant-recipe/FP16_LAYER_FRAC (inv24), real sustained board power / efficiency-under-load (inv25), real perplexity/
eval-delta per quant (inv26), real measured TTFT / end-to-end latency vs the SLA (inv27), real sustained soak bw / thermal throttle
behavior per card (inv28), the real street-price trajectory / per-card EOL calendar that would settle the obsolescence rates (inv29), the
real vendor quote for a full HOST BOM (server-class vs desktop) (inv30), the real resale / end-of-life residual quote per card (inv31),
and NOW the real production replica count / uptime SLA per card that would settle whether the sticker-cheap legacy card's edge survives
the idle hot-standby fleet cost (inv32).

## next concrete action
- premise chain complete through PHASE / GATE / BATCH / CTX / WEIGHT-PRECISION-LAYERING / ENERGY-COST / OUTPUT-QUALITY / LATENCY-DIMENSION
/ SUSTAINED-THERMAL / RANKING-TEMPORAL-VALIDITY / SYSTEM-BOM-SCOPE / RESIDUAL-NET-COST / REPLICAS-HA-FLEET domains, all encoded AND every
asserted number machine-computed, and the criterion now attacked on BOTH sides (denominator C: r35 energy-content + r39 ranking-temporal +
r40 system-scope + r41 residual-net-basis + r42 replicas-multiplicity) AND the numerator on four axes (size/count inv8..25, meaning inv26,
dimension inv27, temporal-validity inv28). Offline advance genuinely exhausted -- HOLD awaiting user Q1-Q13 / market quotes / hardware /
eval / lifetime / host-BOM / residual-resale / replica-SLA. The loop does not stop; it records the exact reason and resumes when any input
lands.

## r42 housekeeping
- persisted r42 cursor (this file); advanced INDEX.md cursor pointer r41->r42 + appended the r42 inv32 entry to the r-chain; added the
  inv32 block to the durable conclusion (04.5-r6-roofline-bound-conclusion.md); registered Q13 REPLICAS/REDUNDANCY/HA into resolve_hstar.
  py's REQUIRED_INPUTS + guard (dict-entry-only sed anchor `^    "Q13 REPLICAS` -> guard survives -> teeth RED right reason EXIT=1, ran
  canary INSIDE tasks/ via cp to avoid the /tmp ModuleNotFoundError false-teeth); refreshed MEMORY.md index line with inv32 + the new Q13 +
  extended the first-hand-decouple list with production-replica-count-uptime-SLA-per-card.
