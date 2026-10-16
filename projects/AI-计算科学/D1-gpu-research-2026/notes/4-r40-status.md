origin: ai
time: 2026-09-28T13:20+08:00
stage: 04 / round: r40 / status: DONE (IMPLEMENTATION: FIRST attack on the denominator C's SCOPE -- is C the WHOLE SYSTEM? inv25 attacked C's CONTENT (energy, additive recurring OPEX over lifetime), inv29 attacked C's TEMPORAL validity (obsolescence, multiplicative decay of relative value) -- but NONE ever asked whether C covers the WHOLE deployed system. C(H*) has ALWAYS been a SINGLE-CARD sticker price, silently assuming the GPU is the whole bill. But task says RUN -> a deployed inference service is a SYSTEM: a GPU cannot serve alone, it needs a HOST (CPU + motherboard + RAM + PSU + chassis + storage); a datacenter PCIe/SXM card needs a SERVER-class host while a consumer card rides a cheap desktop platform -> the sticker is NOT the whole bill -> C under-counts the non-card hardware -> the ranking is HOST-COST-BLIND. Encoded as inv30 into roofline_verify.py + Q11 registered into resolve_hstar.py.)

# cursor: 04/r40 = criterion C(H*) has ALWAYS been a SINGLE-CARD sticker price, silently assuming the GPU is the whole bill; task says RUN -> a deployed inference service is a SYSTEM -> the GPU cannot serve alone, it needs a HOST (CPU/mobo/RAM/PSU/chassis/storage) -> a datacenter PCIe/SXM card needs a SERVER-class host while a consumer card rides a cheap desktop -> the cheap legacy H*=A100-40 carries the LARGER host premium -> its sticker edge ERODES at system level; at plausible host BOM (A100 server $800 vs 5090 desktop $400) the sticker gap $799 erodes to $399 (ranking host-cost-robust, A100 still cheaper $/tok) BUT a full server chassis/rack premium ($1800) FLIPS system $/tok to the consumer RTX_5090 -> the cheap-card system is the WRONG buy once you price the host -> SYSTEM-LEVEL BOM / HOST-COST is NEW required input Q11

## ground-truth (re-confirm, honest-first)
- real cursor was notes/4-r39-status.md (r39 = inv29 ranking temporal validity / obsolescence). This round attacks a NEW axis --
  the denominator C's SCOPE (what does C cover? a single card or the whole system?) -- not a followup. Stayed GPU thread, did not restart.
- REJECTED-DUPLICATE (honest-first): grep confirmed host / platform / psu / motherboard / bom / chassis / power supply / system cost /
  peripheral / node cost / rack appear NOWHERE in roofline_verify.py or resolve_hstar.py -> genuinely unattacked. DISTINCT from inv25
  (that = ENERGY, an additive recurring OPEX electricity bill over the lifetime; this = the HOST, an additive one-time CAPEX non-card
  hardware bill -- different cost category, opex vs capex). DISTINCT from inv29 (that = MULTIPLICATIVE temporal decay of the card's
  relative value over years; this = ADDITIVE scope expansion of C from the card to the whole system, no time dimension). Not a duplicate.

## the genuine NEW unattacked silent assumption this round (C is priced as if the GPU were the whole bill)
- R=P/C has always set C = a single card's sticker price. That silently assumes the GPU is the ENTIRE bill. But a deployed RUN is not a
  bare board -- a GPU cannot serve alone. It needs a HOST: CPU + motherboard + RAM + PSU + chassis + storage. The non-card hardware is a
  real, load-bearing part of the deployment cost that R never counted.
- KEY STRUCTURAL FINDING: this is the FIRST attack on the denominator's SCOPE -- what C covers. inv25 extended C's CONTENT (energy,
  additive over the lifetime), inv29 extended C's TEMPORAL validity (obsolescence, multiplicative over years); neither ever asked whether
  C is the whole SYSTEM or just the GPU.
- The teeth (the load-bearing asymmetry): the cheap legacy H*=A100-40 is a datacenter PCIe/SXM card -> it needs a SERVER-class host
  (server motherboard, ECC RAM, server PSU, often a full rack) -> a LARGE host premium. The consumer RTX 5090 rides a CHEAP desktop
  platform -> a SMALL host premium. So the cheap card carries the EXPENSIVE host -> adding the host ERODES its sticker edge -> at
  system level the ranking can FLIP to the consumer card.

## done this round (implementation + verification)
### roofline_verify.py -- inv30 (system-level BOM / host-cost axis)
- HOST = {A100-40:800, RTX_5090:400} (non-card system BOM; server-class host for the datacenter card vs cheap desktop for the consumer
  card; DIRECTION 一手✓ established fact -- datacenter PCIe/SXM needs server board/ECC/server PSU, consumer rides ATX; exact BOM
  USER/market Q11).
- sys_cpt_a = (1200+800)/roofline_sustained(A100-40,INT8) = $36.6 ; sys_cpt_s = (1999+400)/roofline_sustained(5090,INT8) = $42.5 ->
  A100 still cheaper $/tok at plausible host (premise H*=A100 today holds), BUT the sticker gap $799 ERODES to $399 because the
  datacenter card's host premium ($800) exceeds the consumer's ($400).
- teeth AGGRESSIVE: HOST_AGG = {A100-40:1800, RTX_5090:400} (A100 in a full server chassis/rack, dense PCIe or SXM carrier -> host
  premium balloons) -> sys_cpt_a_agg = (1200+1800)/roofline_sustained = $54.8 > $42.5 -> ranking FLIPS to the consumer 5090 once you
  price the host -> the cheap-card system is the WRONG buy -> genuinely able to fail.
- canary: force HOST=0 (card-only, both) -> system $/tok == sticker -> A100 $21.9 < 5090 $35.4 -> NO flip -> proves the flip is
  HOST-BOM-asymmetry-driven (server-class vs desktop), not decorative.
### resolve_hstar.py -- register Q11 SYSTEM-LEVEL BOM / HOST-COST as a required input
- REQUIRED_INPUTS += "Q11 SYSTEM-LEVEL BOM / HOST-COST (...)".
- guard: fails if "Q11 SYSTEM-LEVEL BOM" not declared -> the tree must never price H* on a single-card sticker, silently assuming the
  GPU is the whole bill.

## teeth-proven (EXIT captured DIRECTLY -- no grep-pipe PIPESTATUS reset)
- roofline_verify.py: [A] normal EXIT=0 (prints inv30 lines: sticker gap $799 -> system $/tok A100 $36.6 vs 5090 $42.5, gap eroded to
  $399; teeth host $800->$1800 -> system $/tok $36.6->$54.8 > $42.5 -> FLIP; canary host=0 -> $21.9 < $35.4 NO flip; + RESULT ALL
  ASSERTS PASS ✓); [B] teeth canary equalize aggressive host premium (`HOST_AGG = {"A100-40":1800`->`400`) -> teeth fires RED 'aggressive
  server-host premium did NOT flip system $/tok to the 5090 -> teeth decorative' -> TEETH_EXIT=1 ✓ (ran INSIDE tasks/ via cp to avoid the
  recurring /tmp ModuleNotFoundError false-teeth); [C] rm canary + run_all EXIT=0.
- resolve_hstar.py: [B'] canary sed delete ONLY the Q11 dict entry (`/^    "Q11 SYSTEM-LEVEL BOM/d` -- the `^    "Q11` indent anchor does
  NOT match the guard line which starts `if "Q11`, so the guard survives) -> grep -c BEFORE=2 AFTER=1 -> fires RED RIGHT reason
  'SYSTEM-LEVEL-BOM/HOST-COST NOT declared a required input' EXIT=1 ✓ captured directly no pipe; [C] restore (grep -c RESTORED=2) +
  run_all EXIT=0. (NOTE: a first print-edit accidentally matched only the Q10 print line's PREFIX and orphaned its tail onto the inv30
  print line -- caught by re-reading line 140 and FIXED by splitting into a correct inv30 print + fully-restored Q10 print; the full gate
  then went GREEN, confirming the repair.)

## why this matters (advance, not restate)
- The denominator C has now been attacked on THREE axes: CONTENT (inv25 energy, additive opex over lifetime), TEMPORAL validity (inv29
  obsolescence, multiplicative over years), and now SCOPE (inv30, does C cover the whole system or just the GPU?). The last is the
  structural point: R=P/C has ALWAYS priced a single card, but a deployed RUN is a SYSTEM -- the GPU is only one line item.
- The two-sided result is the point again: at plausible host BOM the ranking is HOST-COST-ROBUST (A100 still cheaper $/tok, but the
  sticker gap $799 already eroded to $399 -- the host asymmetry ate $400 of the edge); BUT the teeth proves that a full server
  chassis/rack premium ($1800) FLIPS system $/tok to the consumer RTX_5090. That converts "the sticker is the whole bill" from an implicit
  premise into a named, testable dependency (Q11: the non-card host BOM per deployment + whether the card must live in a rack).
- The distinctness is the point: inv25 (energy) and inv30 (host) both ADD to C but by OPPOSITE cost categories -- energy is recurring
  OPEX (electricity, grows with runtime), the host is one-time CAPEX (non-card hardware, paid once regardless of uptime) -- and they
  produce DIFFERENT failure modes (inv25 flips only under degraded efficiency; inv30 flips under mere rack-class host cost).

## honest boundary (NOT loosened)
- the non-card host BOM per deployment (server-class vs desktop) + whether the card must live in a rack = USER/market (Q11). The
  host-cost DIRECTION (a datacenter PCIe/SXM card needs a server-class host costing more than the cheap desktop platform a consumer card
  rides on) is 一手✓ established fact (server motherboard + ECC RAM + server PSU + chassis vs consumer ATX); the exact BOM magnitudes
  are illustrative-plausible, MARKET-BLOCKED (no live vendor quote for a full host) -- same first-hand gap as all price/throughput
  numbers. No fabricated BOM.

## precise blocking (deliverable advances ONLY on these; unchanged from r39, plus the new Q11)
1. form-factor = USER (Q1). 2. refurb A100-40 quote vs $1735(decode)/$1995(prefill) = USER/market (Q2). 3. refurb RTX 4090 quote vs
$1124 = USER/market (Q3). 4. batch size = USER/market (Q4). 5. working-sequence-length / CTX = USER/market (Q5). 6. Q6 ENERGY/TCO =
$/kWh + deployment lifetime + A100 TDP variant confirmation (PCIe 250 vs SXM 400) = USER/market/hardware-spec. 7. Q7 OUTPUT QUALITY =
acceptable-accuracy bar / eval-delta per quant = USER/market. 8. Q8 LATENCY/TTFT = interactive? max acceptable TTFT? typical generation
length G = USER/market. 9. Q9 SUSTAINED/THERMAL-DERATE = sustained soak bw / thermal envelope / duty cycle per card = USER/market/
hardware. 10. Q10 DEPLOYMENT-LIFETIME / OBSOLESCENCE-RATE = how many years will this deployment run? per-card obsolescence/support-decay
rate = USER/market. 11. NEW Q11 SYSTEM-LEVEL BOM / HOST-COST = the non-card host BOM per deployment (server-class vs desktop) +
whether the card must live in a rack = USER/market. 12. first-hand single-stream vLLM = ENV (no CUDA) -- settles eta (inv13), KV dtype
(inv19), prefill/decode ratio (inv20), sm_100 kernel-ready (inv21), A100-40 bw (inv8), batch regime/B* (inv22), working-context/KV
footprint (inv23), quant-recipe/FP16_LAYER_FRAC (inv24), real sustained board power / efficiency-under-load (inv25), real perplexity/
eval-delta per quant (inv26), real measured TTFT / end-to-end latency vs the SLA (inv27), real sustained soak bw / thermal throttle
behavior per card (inv28), the real street-price trajectory / per-card EOL calendar that would settle the obsolescence rates (inv29),
and NOW the real vendor quote for a full HOST BOM (server-class vs desktop) that would settle whether the cheap legacy card's sticker edge
really survives the host bill (inv30).

## next concrete action
- premise chain complete through PHASE / GATE / BATCH / CTX / WEIGHT-PRECISION-LAYERING / ENERGY-COST / OUTPUT-QUALITY /
  LATENCY-DIMENSION / SUSTAINED-THERMAL / RANKING-TEMPORAL-VALIDITY / SYSTEM-BOM-SCOPE domains, all encoded AND every asserted number
  machine-computed, and the criterion now attacked on BOTH sides (denominator C in r35 energy + r40 host-scope + r39 ranking-temporal)
  AND the numerator on four axes (size/count inv8..25, meaning inv26, dimension inv27, temporal-validity inv28). Offline advance
  genuinely exhausted -- HOLD awaiting user Q1-Q11 / market quotes / hardware / eval / lifetime / host-BOM. The loop does not stop; it
  records the exact reason and resumes when any input lands.

## r40 housekeeping
- persisted r40 cursor (this file); advanced INDEX.md cursor pointer r39->r40 + appended the r40 entry to the r-chain; added the inv30
  block to the durable conclusion (04.5-r6-roofline-bound-conclusion.md); registered Q11 SYSTEM-LEVEL-BOM/HOST-COST into resolve_hstar.
  py's REQUIRED_INPUTS + guard (dict-entry-only sed anchor `^    "Q11 SYSTEM-LEVEL BOM` -> guard survives -> teeth RED right reason EXIT=1,
  ran canary INSIDE tasks/ to avoid the /tmp ModuleNotFoundError false-teeth); refreshed MEMORY.md index line with inv30 + the new Q11.