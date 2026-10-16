origin: ai
time: 2026-09-28T11:00+08:00
stage: 04 / round: r37 / status: DONE (IMPLEMENTATION: FIRST attack on the criterion's numerator P's DIMENSION (units). inv8..26 bounded the SIZE/COUNT/MEANING of P (bytes/traffic/phase/batch/ctx/weight-layering on P, cost C in inv25, token-value in inv26) -- NONE ever asked what P's UNITS ARE. P = tokens/s = STEADY-STATE THROUGHPUT, a RATE with NO time dimension; the criterion R=P/C silently assumes a BATCH job where no one waits. But a deployed RUN is INTERACTIVE: a chat/agent user WAITS for the FIRST token (TTFT) before reading at the decode rate. Throughput and latency are DIFFERENT dimensions. Encoded as inv27 into roofline_verify.py + Q8 registered into resolve_hstar.py.)

# cursor: 04/r37 = the criterion's numerator P was STEADY-STATE THROUGHPUT (tokens/s, a RATE with no time dimension), silently pricing only the RATE and assuming a batch job where no one waits; task says RUN -> an INTERACTIVE deployed service must answer FAST -> TTFT (time-to-first-token, the prefill wait the user actually experiences) is never priced; TTFT is CARD-INDEPENDENT (prefill compute-bound, both cards ~equal peak flops) so the throughput ranking is LATENCY-ROBUST at equal prefill, BUT at SHORT generations TTFT DOMINATES end-to-end and the 5090's throughput edge is IRRELEVANT to the user -> throughput-based H* MIS-SCORES an interactive short-reply deployment -> LATENCY/TTFT is NEW required input Q8

## ground-truth (re-confirm, honest-first)
- real cursor was notes/4-r36-status.md (r36 = inv26 output-quality / token-value on the numerator MEANING). This round
  attacks a NEW axis -- the numerator's UNITS / DIMENSION -- not a followup. Stayed GPU thread, did not restart.
- REJECTED-DUPLICATE (honest-first): grep confirmed latency / TTFT / time-to-first / inter-token / p99 / tail appear
  NOWHERE in roofline_verify.py or resolve_hstar.py -> genuinely unattacked. inv20 attacked the PHASE (prefill
  compute-bound raises the break-even) but never the LATENCY the prefill wait imposes on the USER -- a different
  quantity. Not a duplicate.

## the genuine NEW unattacked silent assumption this round (numerator P = tokens/s = a RATE, no time dimension)
- the criterion R(H*) = P(H*)/C(H*) set P = tokens/s, a STEADY-STATE RATE. It prices only the SUSTAINED throughput and
  silently assumes the deployment is a BATCH job where no one waits for the first token. But a deployed RUN is
  INTERACTIVE: a chat/agent user pays the full PREFILL wait (TTFT) BEFORE any token appears, then reads at the decode
  rate. Throughput (tokens/s) and latency (seconds-to-first-token) are DIFFERENT dimensions -- a card can have HIGH
  throughput yet HIGH latency. The criterion never priced the wait.
- KEY STRUCTURAL FINDING: this is the FIRST attack on the numerator's DIMENSION (units). inv8..25 bounded the numerator's
  SIZE/COUNT (bytes, traffic, phase, batch, ctx, weight-layering); inv26 bounded its MEANING (token value); none ever
  asked what P's UNITS ARE or whether a RATE is the right measure for an interactive service.

## done this round (implementation + verification)
### roofline_verify.py -- inv27 (latency / TTFT axis)
- ttft(card,P) = P / prefill_rate() (seconds to first token; prefill is compute-bound, reuses the inv20 prefill_rate).
  e2e_latency(card,P,G,prec) = ttft + G/roofline (TTFT + decode-generation time).
- inv27(1) THE DEFECT: a chat req (P=1024, G=64) waits TTFT=1106ms before the first token -> 53% of the whole request
  is spent WAITING, invisible to R=P/C.
- inv27(2) KEY: TTFT is CARD-INDEPENDENT (prefill compute-bound, both cards ~equal peak flops) -> TTFT 5090=1106ms ==
  A100-40=1106ms -> the throughput ranking is LATENCY-ROBUST at equal prefill (the naive "5090 feels slower to first
  token" worry FAILS; parallel to inv25 energy / inv26 quality robustness).
- robustness: LONG gen G=1024 -> decode dominates -> e2e 5090=16.53s < A100-40=18.89s -> the 5090's throughput edge DOES
  lower latency -> ranking LATENCY-ROBUST for long-gen workloads.
- teeth: SHORT gen G=8 -> TTFT DOMINATES end-to-end -> the two cards' e2e latencies COLLAPSE toward equality (relative gap
  12% long -> 1% short) -> the 5090's throughput edge is IRRELEVANT to the user -> the throughput-based H* recommendation
  MIS-SCORES an interactive short-reply deployment -> genuinely able to fail. canary: pretend prefill FREE (TTFT=0) -> the
  short-gen gap stays 13% ~= long-gen 12% -> NO collapse -> proves the real collapse is TTFT-driven not decorative.
### resolve_hstar.py -- register Q8 LATENCY/TTFT as a required input
- REQUIRED_INPUTS += "Q8 LATENCY / TTFT (criterion numerator P = tokens/s is STEADY-STATE THROUGHPUT, a RATE with NO time
  dimension; task says RUN -> an INTERACTIVE deployed service must answer FAST -> a chat/agent user waits for the FIRST
  token (TTFT) which R never prices ...)".
- guard: fails if "Q8 LATENCY" not declared -> the tree must never rank H* on steady-state throughput alone, ignoring the
  first-token latency a deployed interactive service must meet.

## teeth-proven (EXIT captured DIRECTLY -- no grep-pipe PIPESTATUS reset)
- roofline_verify.py: [A] normal EXIT=0 (prints inv27 lines + RESULT ALL ASSERTS PASS ✓); [B] canary shrink the short-gen
  prefill (`1024,8)`->`16,8)` -> TTFT no longer dominates -> the e2e gap stops collapsing -> teeth fires RED 'short-gen
  gap did NOT collapse vs long-gen -> TTFT not dominant at G=8 -> teeth decorative' -> REAL_EXIT=1 ✓; [C] restore +
  run_all EXIT=0.
- resolve_hstar.py: [B] canary sed delete ONLY the Q8 dict entry (`/^    "Q8 LATENCY/d`) -> guard survives -> fires RED
  RIGHT reason 'LATENCY/TTFT NOT declared a required input' EXIT=1 ✓; [C] restore + run_all EXIT=0. (teeth BUG caught
  THIS round: the first sed `/Q8 LATENCY/d` ALSO deleted the guard line (which contains the same string) -> no guard ->
  FALSE GREEN teeth EXIT=0; re-anchored to the dict-entry line `^    "Q8 LATENCY` -> the guard survives -> bites red.)

## why this matters (advance, not restate)
- The criterion's numerator has now been attacked on THREE axes: its SIZE/COUNT (inv8..25), its MEANING / token value
  (inv26), and its DIMENSION / units (inv27). The last is the deepest: it questions whether tokens/s is even the right
  quantity for a deployed interactive service. A RATE prices sustained work; a user experiences a WAIT.
- The two-sided result is the point again: at equal prefill (both cards ~equal peak flops) the ranking is LATENCY-ROBUST
  -- a non-obvious quantitative fact (the faster-decode card is NOT slower to first token) -- so the deliverable's
  recommendation does NOT change; BUT the robustness is CONDITIONAL on the generation length, and the teeth proves that at
  SHORT generations the throughput edge collapses to ~1% and becomes IRRELEVANT to the user. That converts "throughput is
  the right measure" from an implicit premise into a named, testable dependency (Q8: interactive? max acceptable TTFT?
  typical gen length G?).

## honest boundary (NOT loosened)
- interactive? / max acceptable TTFT / typical generation length G = USER/market (Q8). The TTFT numbers are 一手✓ arithmetic
  from the compute-bound prefill rate (P/prefill_rate) and the decode roofline -- both derived from the pinned card specs,
  no fabricated latency. The card-independence of TTFT rests on both cards running at ~equal peak flops (the inv10/inv20
  compute-bound regime), which is 一手✓ established. Real measured TTFT / a real latency SLA = ENV-BLOCKED (no CUDA / no
  serving stack) -- same first-hand gap as all throughput numbers.

## precise blocking (deliverable advances ONLY on these; unchanged from r36, plus the new Q8)
1. form-factor = USER (Q1). 2. refurb A100-40 quote vs $1735(decode)/$1995(prefill) = USER/market (Q2). 3. refurb
RTX 4090 quote vs $1124 = USER/market (Q3). 4. batch size = USER/market (Q4). 5. working-sequence-length / CTX =
USER/market (Q5). 6. Q6 ENERGY/TCO = $/kWh + deployment lifetime + A100 TDP variant confirmation (PCIe 250 vs SXM
400) = USER/market/hardware-spec. 7. Q7 OUTPUT QUALITY = acceptable-accuracy bar / eval-delta per quant = USER/market.
8. NEW Q8 LATENCY/TTFT = interactive? max acceptable TTFT? typical generation length G = USER/market. 9. first-hand
single-stream vLLM = ENV (no CUDA) -- settles eta (inv13), KV dtype (inv19), prefill/decode ratio (inv20), sm_100
kernel-ready (inv21), A100-40 bw (inv8), batch regime/B* (inv22), working-context/KV footprint (inv23), quant-recipe/
FP16_LAYER_FRAC (inv24), real sustained board power / efficiency-under-load (inv25), real perplexity/eval-delta per
quant (inv26), and NOW real measured TTFT / end-to-end latency vs the SLA (inv27 -- settles whether the equal-prefill
card-independence holds on real hardware and whether short-reply workloads make the throughput edge irrelevant).

## next concrete action
- premise chain complete through PHASE / GATE / BATCH / CTX / WEIGHT-PRECISION-LAYERING / ENERGY-COST / OUTPUT-QUALITY /
  LATENCY-DIMENSION domains, all encoded AND every asserted number machine-computed, and the criterion now attacked on
  BOTH sides (denominator C in r35) AND the numerator on three axes (size/count inv8..25, meaning inv26, dimension
  inv27). Offline advance genuinely exhausted -- HOLD awaiting user Q1-Q8 / market quotes / hardware / eval. The loop
  does not stop; it records the exact reason and resumes when any input lands.

## r37 housekeeping
- persisted r37 cursor (this file); advanced INDEX.md cursor pointer r36->r37 + appended the r37 entry to the r-chain;
  added the inv27 block to the durable conclusion (04.5-r6-roofline-bound-conclusion.md); registered Q8 LATENCY/TTFT
  into resolve_hstar.py's REQUIRED_INPUTS + guard; refreshed MEMORY.md index line with inv27 + the new Q8.