origin: ai
time: 2026-09-28T18:20+08:00
stage: 04 / round: r45 / status: DONE (IMPLEMENTATION: FIRST META-ATTACK of the criterion itself -- not a new cost term but an audit of whether the SEVEN existing C-axes COMPOSE consistently. Every prior C-axis attack (inv25 energy-content / inv29 temporal-decay / inv30 host-scope / inv31 residual-net / inv32 replica-multiplicity / inv43 software-composition / inv44 labor-basis) added ONE thing to C IN ISOLATION and asked 'does THIS one flip?'; none ever STACKED them; but a deployed RUN pays ALL seven AT ONCE and R=P/C never checked whether they COMPOSE consistently (signs agree, no double-count, cumulative flip). Encoded as inv45 into roofline_verify.py + Q16 registered into resolve_hstar.py.)

# cursor: 04/r45 = criterion R=P/C silently priced each C-axis IN ISOLATION and never STACKED them -> the FIRST META-ATTACK audits the criterion's INTERNAL CONSISTENCY across the seven C-axes (sign consistency, no double-count, cumulative flip); the audit stacks sticker + host(+one-time CAPEX) - sticker*resid(-terminal credit) + energy(+recurring physical OPEX) + software(+recurring contractual OPEX) + labor(+recurring human OPEX) into total_deployed_usd -> 6 mutually-distinct signed terms, no double-count, signs consistent -> the seven COMPOSE cleanly; KEY finding invisible to any single axis: inv25 found ENERGY PER TOKEN ~EQUAL (throughput~power offset) BUT stacked over LIFETIME=5y the FASTER 5090 serves ~2x more tokens -> its TOTAL energy bill is ~2x the A100's ($3211 vs $1560, ratio 2.06x) -> per-token parity does NOT imply lifetime-TOTAL parity, the asymmetry lives in the INTEGRATION not in any single C-axis

## ground-truth (re-confirm, honest-first)
- real cursor was notes/4-r44-status.md (r44 = inv44 operator-labor). This round does NOT add a new cost term -- it is the FIRST META-ATTACK,
  auditing whether the SEVEN already-added C-axes COMPOSE consistently. Stayed GPU thread, did not restart.
- REJECTED-DUPLICATE (honest-first): grep confirmed compose / integration / stack-all-at-once / total_deployed appear NOWHERE in roofline_verify.py
  or resolve_hstar.py before this round (counts = 0) -> genuinely unattacked. Not a duplicate. Every prior C-axis attack added ONE term and asked
  'does THIS flip?'; none ever asked 'do the SEVEN compose?'.

## the genuine NEW unattacked silent assumption this round (the criterion prices each C-axis IN ISOLATION, never STACKED)
- R=P/C has been attacked on SEVEN separate denominator axes, but every attack added ONE thing to C IN ISOLATION and tested whether THAT one
  flipped the ranking. None ever checked whether the seven COMPOSE -- whether their SIGNS agree, whether any DOUBLE-COUNTS the same dollar, and
  whether the FULL cumulative load finally FLIPS. A deployed RUN pays all seven AT ONCE. This attacks the criterion's INTERNAL CONSISTENCY (a
  structural/meta property), not a new cost term.
- KEY STRUCTURAL FINDING: per-token energy parity (inv25, throughput~power offset) does NOT imply lifetime-TOTAL energy parity -- the faster 5090
  serves ~2x more tokens over the deployment lifetime so its TOTAL energy bill is ~2x the A100's. The asymmetry lives in the INTEGRATION, not in
  any single C-axis. No single-axis view could ever see this.

## done this round (implementation + verification)
### roofline_verify.py -- inv45 (composition / integration audit -- the FIRST META-ATTACK)
- SPY=365*24*3600; energy_total_usd(card,prec)=energy_usd_per_token*roofline_sustained*SPY*LIFETIME; total_deployed_usd(card,prec,host,lic,labor)
  = sticker + host - sticker*RESID + energy_total_usd + lic*HORIZON + labor*HORIZON. guard inv45(0): each add-on carries the right sign
  (host/energy/lic/labor >=0, 0<=RESID<=1) else the deployed-cost composition is inconsistent.
- nominal stack: total deployed $/tok A100 $73.5 < 5090 $88.8 -> ranking INTEGRATION-ROBUST, H*=A100 today survives the cumulative load.
- NEW finding printed: TOTAL energy bill 5090 $3211 vs A100 $1560 (ratio 2.06x) -> per-token parity does NOT imply lifetime-TOTAL parity.
- inv45(2) NO-DOUBLE-COUNT: the stacked $ decomposes into 6 mutually-distinct signed terms (sticker / host+one-time non-card HW / energy+recurring
  physical OPEX / software+recurring contractual OPEX / labor+recurring human OPEX / residual-terminal credit FROM card) -> each dollar counted
  exactly once with a distinct substance AND timing -> the seven C-axes COMPOSE cleanly.
- teeth: legacy pays EVERY add-on at its WORST simultaneously (server rack host $800->$1800 + rented enterprise software $150->$500/yr +
  manual-babysitting labor $200->$600/yr) -> total deployed $/tok A100 $73.5->$119.2 > 5090 $88.8 -> the FULL cumulative stack finally FLIPS
  the ranking to the consumer RTX_5090 -> genuinely able to fail.
- canary: force EQUAL add-ons on both (same host/software/labor) -> total deployed $/tok A100 $119.2 < 5090 $152.6 -> NO flip -> proves the
  flip is ADD-ON-ASYMMETRY-driven (legacy pays host+software+labor at their worst vs consumer light), not decorative.
### resolve_hstar.py -- register Q16 DEPLOYED-COST COMPOSITION / INTEGRATION MODEL as a required input
- REQUIRED_INPUTS += "Q16 DEPLOYED-COST COMPOSITION / INTEGRATION MODEL (...)" -- the FIRST META-ATTACK of the criterion, not a new cost term.
- guard: fails if "Q16 DEPLOYED-COST COMPOSITION" not declared -> the tree must never price each C-axis IN ISOLATION and never STACK them.

## teeth-proven (EXIT captured DIRECTLY -- no grep-pipe PIPESTATUS reset; zsh ${PIPESTATUS[0]} returns empty, use $? after direct run)
- roofline_verify.py: [A] normal EXIT=0 (prints inv45 lines: nominal total deployed $/tok A100 $73.5 < 5090 $88.8 robust; energy ratio 2.06x
  $3211 vs $1560; teeth agg add-ons $73.5->$119.2 > $88.8 FLIP; canary equal add-ons $119.2 < $152.6 NO flip; + RESULT ALL ASSERTS PASS ✓);
  [B] teeth canary make the legacy agg add-ons FREE (sed neutralize host=1800,lic=500,labor=600 -> nominal) -> teeth fires RED 'the FULL
  stacked legacy load did NOT flip total deployed $/tok to the 5090 -> teeth decorative' -> TEETH_EXIT=1 ✓ (ran INSIDE tasks/ via cp
  rv_canary_local.py to avoid the recurring /tmp ModuleNotFoundError false-teeth); [C] rm canary + run_all EXIT=0.
- resolve_hstar.py: [B'] canary sed delete ONLY the Q16 dict entry (`/^    "Q16 DEPLOYED-COST COMPOSITION/d` -- the `^    "Q16` indent anchor does
  NOT match the guard line which starts `if "Q16`, so the guard survives) -> grep -c BEFORE=2 AFTER=1 -> fires RED RIGHT reason 'DEPLOYED-COST
  COMPOSITION/INTEGRATION MODEL NOT declared a required input' EXIT=1 ✓ captured directly no pipe; [C] restore (grep -c RESTORED=2) + run_all
  EXIT=0.

## why this matters (advance, not restate)
- This is the FIRST time the criterion itself has been audited rather than a new cost added. The denominator C has now been attacked on EIGHT axes:
  CONTENT (inv25 energy), TEMPORAL validity (inv29 obsolescence), SCOPE (inv30 host), NET-vs-GROSS basis (inv31 residual), MULTIPLICITY
  (inv32 replicas), COMPOSITION BEYOND HARDWARE (inv43 software), LABOR BASIS (inv44 operator), and now COMPOSITION/INTEGRATION AUDIT (inv45,
  do the seven COMPOSE consistently?). The first seven ADDED something; the eighth AUDITS how they COMPOSE.
- The two-sided result is the point again: at nominal add-ons the ranking is INTEGRATION-ROBUST (total deployed $/tok A100 $73.5 < 5090 $88.8,
  H*=A100 today survives the cumulative load, margin razor-thin); BUT the teeth proves that when the legacy card pays EVERY add-on at its WORST
  simultaneously the FULL cumulative stack finally FLIPS total deployed $/tok to the consumer RTX_5090 ($73.5->$119.2 > $88.8). That converts
  'each axis priced in isolation' from an implicit premise into a named, testable dependency (Q16: the full deployed-cost composition model).
- The distinctness is the point: inv45 is DISTINCT from EVERY prior single-axis attack -- each prior attack added ONE term and asked 'does THIS
  flip?'; none ever asked 'do the SEVEN compose?'. inv45 audits sign consistency + no-double-count + cumulative flip -- a structural property of
  the criterion, not a new dollar.

## honest boundary (NOT loosened)
- the full deployed-cost COMPOSITION / INTEGRATION MODEL -- how the axes combine (additive vs multiplicative), their signs, whether energy scales
  with lifetime, whether replicas multiply the whole stack -- = USER/market (Q16). The DIRECTION (a deployed RUN pays all add-ons at once; the
  faster card serves more tokens so its lifetime-total energy is higher) is 一手✓ established arithmetic; the exact magnitudes are illustrative-plausible,
  MARKET-BLOCKED (no live quotes). No fabricated price.

## precise blocking (deliverable advances ONLY on these; unchanged from r44, plus the new Q16)
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
   deployment runs a paid commercial stack or a free open-source stack = USER/market. 15. Q15 OPERATOR LABOR / OPS-PERSONNEL = the annual
   operator-labor / ops-personnel cost per card / whether the deployment is unattended or needs dedicated hands-on staff = USER/market. 16.
   NEW Q16 DEPLOYED-COST COMPOSITION / INTEGRATION MODEL = how the seven C-axes COMPOSE (additive vs multiplicative), their signs, whether
   energy scales with lifetime, whether replicas multiply the whole stack = USER/market. first-hand single-stream vLLM = ENV (no CUDA) -- settles
   eta (inv13), KV dtype (inv19), prefill/decode ratio (inv20), sm_100 kernel-ready (inv21), A100-40 bw (inv8), batch regime/B* (inv22),
   working-context/KV footprint (inv23), quant-recipe/FP16_LAYER_FRAC (inv24), real sustained board power / efficiency-under-load (inv25), real
   perplexity/eval-delta per quant (inv26), real measured TTFT / end-to-end latency vs the SLA (inv27), real sustained soak bw / thermal throttle
   behavior per card (inv28), the real street-price trajectory / per-card EOL calendar that would settle the obsolescence rates (inv29), the real
   vendor quote for a full HOST BOM (server-class vs desktop) (inv30), the real resale / end-of-life residual quote per card (inv31), the real
   production replica count / uptime SLA per card (inv32), the real annual software+support license quote per card (inv43), the real annual
   operator-labor / ops-personnel quote per card (inv44), and NOW the real deployed-cost COMPOSITION / INTEGRATION MODEL that would settle whether
   the seven axes compose and whether the cumulative stack flips the ranking (inv45).

## next concrete action
- premise chain complete through PHASE / GATE / BATCH / CTX / WEIGHT-PRECISION-LAYERING / ENERGY-COST / OUTPUT-QUALITY / LATENCY-DIMENSION /
  SUSTAINED-THERMAL / RANKING-TEMPORAL-VALIDITY / SYSTEM-BOM-SCOPE / RESIDUAL-NET-COST / REPLICAS-HA-FLEET / SOFTWARE-LICENSING-STACK /
  OPERATOR-LABOR / COMPOSITION-INTEGRATION-AUDIT domains, all encoded AND every asserted number machine-computed, and the criterion now attacked
  on BOTH sides (denominator C: r35 energy-content + r39 ranking-temporal + r40 system-scope + r41 residual-net-basis + r42
  replicas-multiplicity + r43 software-composition + r44 labor-basis + r45 composition-integration-audit) AND the numerator on four axes
  (size/count inv8..25, meaning inv26, dimension inv27, temporal-validity inv28). Offline advance genuinely exhausted -- HOLD awaiting user
  Q1-Q16 / market quotes / hardware / eval / lifetime / host-BOM / residual-resale / replica-SLA / software-license-quote / operator-labor-quote
  / deployed-cost-composition-model. The loop does not stop; it records the exact reason and resumes when any input lands.

## r45 housekeeping
- persisted r45 cursor (this file); advanced INDEX.md cursor pointer r44->r45 + appended the r45 inv45 entry to the r-chain; added the inv45 block
  to the durable conclusion (04.5-r6-roofline-bound-conclusion.md) and advanced its axis-count SEVEN->EIGHT; registered Q16 DEPLOYED-COST
  COMPOSITION/INTEGRATION MODEL into resolve_hstar.py's REQUIRED_INPUTS + guard (dict-entry-only sed anchor `^    "Q16 DEPLOYED-COST COMPOSITION`
  -> guard survives -> teeth RED right reason EXIT=1, ran canary INSIDE tasks/ via cp to avoid the /tmp ModuleNotFoundError false-teeth); refreshed
  MEMORY.md index line with inv45 + the new Q16 + extended the first-hand-decouple list with deployed-cost-composition-model.