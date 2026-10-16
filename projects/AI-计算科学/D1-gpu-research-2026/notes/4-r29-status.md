origin: ai
time: 2026-09-28T02:10+08:00
stage: 04 / round: r29 / status: DONE (IMPLEMENTATION: encode the WORKLOAD AXIS into the EXECUTABLE tree resolve_hstar.py -- r28's inv20 proved the $1735 break-even is DECODE-DOMINANT and prefill-heavy RAISES it to ~$1995, but the r17 tree HARDCODED decode-dominant be=$1735 with NO workload axis -> WRONG for any refurb quote in the ($1735,$1995) band. Fixed: resolve() now takes workload='decode'|'prefill', computes BE_A100_PREFILL from the roofline source (rv.total_rate at G=1), branches the server leaf on it. The band is where the two regimes DISAGREE; teeth-proven that the axis BITES.)

# cursor: 04/r29 = the deliverable tree was DECODE-only -- encoded the workload axis so a prefill-heavy quote in ($1735,$1995) resolves to A100-40, not 5090

## ground-truth (re-confirm, honest-first)
- stop-hook "持久状态" (stage 02 / Ego Lite / partition-cover / well-founded μ) = GLOBAL formal-methods cursor, NOT this project.
- real cursor = notes/4-r28-status.md -> advanced to r29 here. Stayed GPU thread, did not restart.
- guardrail satisfied: r28 was mostly ANALYSIS + a CORRECTION; r29 is IMPLEMENTATION (encode the axis into code).

## the genuine deliverable defect this round fixed
r17 collapsed the H* tree to `resolve(form_factor, a100_quote, rtx4090_quote)`. The server leaf compared the quote to
BE_A100=$1735 -- a DECODE-DOMINANT number (derived from the bw/bytes DECODE roofline). But inv20 (r28) showed the
TRUE break-even depends on the WORKLOAD: decode-dominant -> $1735, prefill-heavy -> ~$1995. So the tree was WRONG for
any quote in the ($1735,$1995) band: it returned 5090 there, but under a prefill-heavy workload the A100-40 actually
wins. At $1200 the tree was already correct (robust under both regimes); the defect was ONLY inside the band.

## done this round (implementation + verification)
- resolve() gains `workload="decode"` (default -> backward-compatible, all 9 prior cases unchanged).
- BE_A100_PREFILL computed from the roofline SOURCE (not hardcoded): `round(CARDS["RTX_5090"]["price"] *
  rv.total_rate("A100-40",1024,1) / rv.total_rate("RTX_5090",1024,1))` = $1995 (inv20's prefill-dominant be_short).
- server leaf: `be = BE_A100_PREFILL if workload=="prefill" else BE_A100` -> the leaf resolves on the RIGHT be.
- 4 new self-test cases pin the band: $1800 decode->5090, $1800 prefill->A100-40 (THE FLIP), $1200 prefill->A100-40
  (robust), $2000 prefill->5090 (above even the raised be).

## teeth-proven
- inv20 teeth (in-code): at $1800 decode and prefill MUST disagree (axis load-bearing). Normal: decode->5090,
  prefill->A100-40 -> they DISAGREE -> passes.
- [B] canary: `sed` the leaf to `be = BE_A100` (ignore workload axis) -> the $1800-prefill case FAILS (wrongly
  returns 5090 instead of A100-40) AND the teeth check fires ("axis is decorative") -> RED exit1 ✓. Both bite the SAME
  real threat (a tree that silently drops the workload axis). Restored -> green exit0.
- [C] full gate: run_all.py 3 suites ALL GREEN exit0 (roofline_verify + test_hstar_rule + resolve_hstar).

## why this matters (advance, not restate)
- r28 CORRECTED the direction (prefill-heavy makes the A100 MORE competitive, not less) but left the DELIVERABLE
  unchanged -- the tree still hardcoded the decode be. r29 closes that gap IN CODE: the executable H* resolver now
  carries the workload axis, so a refurb A100-40 quote anywhere in [$1200,$1995] resolves to A100-40 (decode up to
  $1735, prefill-heavy up to $1995), and only above $1995 does the 5090 win. This makes the deliverable correct across
  the whole price range, not just the decode point. Honest-first: the band width ($1735..$1995) is a roofline-model
  estimate (一手✓ arithmetic), the exact crossover needs a measured prefill/decode wall-clock ratio (ENV-BLOCKED).

## honest boundary (NOT loosened)
- BE_A100_PREFILL=$1995 is a roofline-model figure at the (P=1024,G=1) prefill-dominant point (一手✓ arithmetic on
  the model); the true crossover depends on the real prefill/decode wall-clock ratio -> ENV-BLOCKED (no CUDA/vLLM).
- the workload axis is a BINARY (decode|prefill); real workloads sit on a continuum -> the tree gives the two regime
  endpoints; a mid-band quote needs the user's actual prompt/gen profile (NEW required input, USER).
- A100-40 bw 一手✓ BLOCKED (社区R); 5090/4090 branches 一手✓ grounded (inv8).

## precise blocking (deliverable advances ONLY on these; this round made the tree workload-aware)
1. form-factor = USER (Q1). 2. refurb A100-40 quote vs $1735(decode)/$1995(prefill) = USER/market (Q2) -- AND if it
lands in ($1735,$1995), ALSO the workload profile (decode-heavy vs prefill-heavy) to pick the right be. 3. refurb
RTX 4090 quote vs $1124 = USER/market (Q3). 4. first-hand single-stream vLLM = ENV (no CUDA) -- settles eta (inv13),
KV dtype (inv19), AND the prefill/decode ratio (inv20) which pins the exact be.

## next concrete action
- premise chain complete through the PHASE boundary AND now ENCODED in the deliverable tree: regime (inv10) + traffic
  (inv11/inv15) + cache (inv16) + sparsity (inv17) + quant-meta (inv18) + KV-precision (inv19) + PHASE-domain
  (inv20, now in resolve()) + eta (inv13) + constants (inv8/inv14) + cross-file (inv12) + tree (r17/inv9). Every
  remaining unknown is ENV/USER-gated. Offline advance genuinely exhausted -- HOLD awaiting user/market/hardware.

## r29 housekeeping DONE (post-correction consistency sweep)
- FIXED stale MEMORY.md index line 3: was "prefill-heavy flips to 5090" (the OLD, directionally-WRONG r28-draft
  wording) -> now "prefill-heavy RAISES be $1735->~$1996, WIDENS A100 win-band [$1200,$1996], NO flip at $1200,
  flip ONLY in ($1735,$1996) band" -> matches the corrected durable memory + corrected r28/r29 cursors + INDEX. All
  persistence layers (MEMORY.md / durable memory / r28 cursor / r29 cursor / INDEX) now AGREE on the flip direction.
- re-ran run_all.py -> EXIT=0 (3 suites ALL GREEN), confirming the well-characterized resting state is intact after
  the edit. No invariant invented this round (offline advance genuinely exhausted); the only genuine pending action was
  this stale-index reconciliation, now closed.