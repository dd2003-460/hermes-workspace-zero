origin: ai
time: 2026-09-28T01:40+08:00
stage: 04 / round: r28 / status: DONE+CORRECTED (inv20 PREFILL-vs-DECODE phase: inv10/11/15/18/19 all analyzed the DECODE phase only, but a REAL request = PREFILL (whole prompt in one forward pass, batch=prompt_len -> COMPUTE-bound, AI>>ridge) THEN DECODE. Two consequences: (1) the bw/bytes ceiling's DOMAIN is DECODE-ONLY -- prefill runs compute-bound ~14x faster, so total-request throughput CAN exceed the decode ceiling (NARROWS inv11/18/19's 'never exceeded' to the decode phase); (2) the $1735 break-even is DECODE-DOMINANT -> at short generations it MOVES UP toward a compute-based ~$1996, WIDENING the A100-40 win-band to [$1200,$1996]. CORRECTION to first draft: prefill-heavy does NOT flip H* at $1200 (A100-40 wins under BOTH regimes, 1200<1735 AND 1200<1996); the flip occurs ONLY for quotes in the ($1735,$1996) band where decode-dominant says 5090 but prefill-heavy says A100-40.)

# cursor: 04/r28 = the roofline bounds DECODE only; $1735 be is DECODE-DOMINANT -> prefill-heavy RAISES it to ~$1996, widening the A100 win-band (NO flip at $1200)

## ground-truth (re-confirm, honest-first)
- stop-hook "持久状态" (stage 02 / Ego Lite / partition-cover / well-founded μ) = GLOBAL formal-methods cursor, NOT this project.
- real cursor = notes/4-r27-status.md -> advanced to r28 here. Stayed GPU thread, did not restart.

## caught-and-corrected THIS round (honest-first: my first-draft r28 narrative was WRONG)
First draft claimed "prefill-heavy flips H* back to the 5090 / A100-40 LOSES prefill-heavy". That is FALSE. Recomputed:
the break-even p_be is the price where A100-40's cost-perf == 5090's; A100-40 wins when quote < p_be. Decode-dominant
p_be=$1735; prefill-heavy p_be=$1996 (HIGHER, because prefill-heavy makes the two cards' total-request rates nearly
EQUAL -- both dominated by the identical compute-bound prefill at the same peak -> the slower-card discount shrinks). At
$1200: 1200<$1735 (decode) AND 1200<$1996 (prefill-heavy) -> A100-40 wins under BOTH -> NO flip. The workload axis
matters ONLY for quotes in the ($1735,$1996) band: there decode-dominant returns 5090 but prefill-heavy returns A100-40.

## done this round (验证 + a genuinely NEW gap, not a restatement)
inv10 proved DECODE (batch=1, 1 token/step) is MEMORY-bound so bw/bytes bounds it. inv11/15/18/19 bounded the DECODE
bytes/token. But NONE considered the PREFILL phase. A real request = PREFILL (whole prompt in ONE forward pass,
batch=prompt_len -> COMPUTE-bound, high arithmetic intensity) THEN DECODE (steady-state). Consequences:
- (1) PREFILL IS COMPUTE-BOUND: AI_prefill = 2*params*P / weights_bytes = 2*P/bp (weights amortized over P tokens).
  P=1024 -> AI=2048 flops/byte >> ridge 27.9 (73x); P=4096 -> AI=8192 >> ridge (294x). So bw/bytes does NOT bound
  prefill -> the roofline ceiling's DOMAIN is DECODE-ONLY.
- (2) TOTAL-REQUEST RATE EXCEEDS THE DECODE ROOFLINE: total_rate(P=1024,G=1024)=124 tok/s > decode roofline=66 ->
  the bw/bytes ceiling bounds DECODE ONLY; prefill runs compute-bound ~14x faster. This NARROWS inv11/18/19's
  "never exceeded" claim to the decode phase (honest: their bound is a DECODE bound, not a whole-request bound).
- (3) $1735 BREAK-EVEN IS DECODE-DOMINANT -> MOVES UP with prefill-heavy: decode-dominant(G=16384) be=$1736 ~ $1735;
  prefill-dominant(G=1) be=$1996 -> drifts UP to the compute-based ~$1999 (both cards ~equal compute-bound throughput).
  Effect: WIDENS the A100-40 win-band from [$1200,$1735] to [$1200,$1996]. At $1200 NO flip (robust). Flip ONLY in
  ($1735,$1996): decode-dominant -> 5090, prefill-heavy -> A100-40.

## teeth-proven
- teeth(a) [in-code]: prefill-dominant be MUST move UP -> if be_short stayed ~be_dec (<$50 diff) -> RED (the
  decode-only assumption would be non-load-bearing). Normal: be_short=$1996, be_dec=$1735, diff=$261 > $50 -> passes.
- [B] canary: pretend prefill is memory-bound (prefill_rate -> roofline) -> BOTH inv20(2) AND inv20(3) bite the SAME
  real threat: total=66<=roofline (prefill not faster) AND long-gen be=$1748 far from $1735 (decode roofline not
  recovered) -> RED exit1 ✓. Restored -> green exit0.
- [C] full gate: run_all.py 3 suites ALL GREEN exit0.

## why this matters (advance, not restate)
- r23-r27 stacked four optimism layers on the BYTES side (KV traffic, attention flops, cache-cannot-absorb, quant
  metadata, KV precision) -- all about the DECODE phase's bytes/token, all pushing bytes UP so the ceiling is looser
  but never exceeded. inv20 is DIFFERENT in KIND: it attacks the PHASE ASSUMPTION itself -- that the whole request is
  decode. It shows the ceiling's DOMAIN is narrower than previously claimed (decode-only, not whole-request), and that
  the $1735 break-even is a DECODE-DOMINANT figure that MOVES UP at short generations. Honest-first correction: I first
  said it flips H* away from the A100-40; recomputation shows the OPPOSITE -- prefill-heavy makes the A100-40 MORE
  competitive (raises its break-even), so the deliverable's $1200 A100-win is ROBUST to workload, not conditional.
  The real actionable consequence is a NEW required input: a refurb quote in the ($1735,$1996) band needs the workload
  profile to resolve (decode -> 5090, prefill-heavy -> A100-40).

## honest boundary (NOT loosened)
- prefill/decode split is standard LLM inference (社区R, well-known); the ~14x prefill speedup is a roofline-model
  estimate (一手✓ arithmetic on the model), not a measured vLLM number.
- the ($1735,$1996) band width is a roofline-model estimate; the exact crossover depends on the real prefill/decode
  wall-clock ratio -- ENV-BLOCKED (no CUDA/vLLM). DIRECTION (prefill-heavy raises be) proven.
- A100-40 bw 一手✓ BLOCKED (not fabricated); 5090/4090 branches 一手✓ grounded (inv8).

## precise blocking (deliverable advances ONLY on these; this round narrowed the ceiling's domain + corrected the flip direction)
1. form-factor = USER (Q1). 2. refurb A100-40 quote vs $1735 (decode) / $1996 (prefill-heavy) = USER/market (Q2).
3. refurb RTX 4090 quote vs $1124 = USER/market (Q3). 4. first-hand single-stream vLLM = ENV (no CUDA) -- also answers
eta (inv13), KV dtype (inv19), AND the prefill/decode ratio (inv20) which sets the exact be for short generations.

## next concrete action
- premise chain now complete through the PHASE boundary: regime (inv10) + traffic terms (inv11/inv15) + cache-cannot-
  absorb (inv16) + sparsity-invariance (inv17) + quant-metadata (inv18) + KV-precision (inv19) + PHASE-domain (inv20)
  + eta (inv13) + constants (inv8/inv14) + cross-file (inv12) + tree (r17/inv9). NEXT: encode the workload axis into
  the EXECUTABLE tree resolve_hstar.py (it currently hardcodes decode-dominant be=$1735 -> WRONG for a quote in the
  ($1735,$1996) band + prefill-heavy). That is the genuine deliverable defect this round surfaced.