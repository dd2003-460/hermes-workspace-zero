origin: ai
time: 2026-09-27T21:20+08:00
stage: 04 / round: r20 / status: DONE (inv12 cross-file CONSISTENCY: resolve_hstar's HARDCODED break-evens pinned to roofline_verify's COMPUTED ones; caught a bug in the NEW invariant itself — wrong quant in the 4090 ratio — fixed; teeth-proven)

# cursor: 04/r20 = the two files that encode H* must AGREE -- hardcoded tree constants vs computed roofline source

## ground-truth (re-confirm, honest-first)
- stop-hook "持久状态" (stage 02 / Ego Lite / partition-cover / well-founded μ) = GLOBAL formal-methods cursor, NOT this project.
- real cursor = notes/4-r19-status.md -> advanced to r20 here. Stayed GPU thread, did not restart.

## done this round (验证, not analysis — per "上一多为验证/分析 -> 本轮验证")
r17 collapsed the tree to EXECUTABLE code but HARDCODED BE_A100=1735 / BE_4090=1124. roofline_verify.py COMPUTES
those break-evens from CARDS(bw,price). Two sources of the same number = drift risk: if a bw/price fix lands in
roofline_verify and resolve_hstar is forgotten, the tree resolves H* on a STALE break-even -> WRONG answer. inv12
(NEW) recomputes p_be from rv.roofline()/rv.CARDS and pins the constants -> the two files are now provably consistent.

## BUG caught in the NEW invariant (test-the-test, same discipline as r18's units bug)
- First inv12 wrote ratio_4090 = roofline(4090,"INT4")/roofline(5090,"INT8") = 74.7/66.4 = 1.125 -> p_be 2248.9
  -> inv12 went RED against the correct BE_4090=1124. Diagnosed: NOT a CARDS drift — MY ratio used the WRONG quant
  on the 5090 side. BE_4090=1124 was originally derived (r13 dominance) comparing 4090 INT4 vs 5090 **INT4**
  (132.7), a QUALITY-COMPARABLE same-quant ratio (the clean cost-perf basis). Fixed to INT4/INT4 -> 74.7/132.7 =
  0.5629 -> p_be 1124.4 == 1124 ✓. The invariant was right to fire; my formula was the bug, not the constant.
- Lesson recorded: an invariant that flags a mismatch must first be checked for ITS OWN error before trusting it as
  a data-drift finding. Here it self-exposed via the exact mismatch it was built to catch.

## why this matters (advance, not restate)
- Before r20: the decision tree's break-even numbers were FREE-FLOATING constants with no link to the roofline that
  produced them. A future spec fix could silently desync the tree from the physics. Now: every tree constant is
  pinned to the computed roofline source -> single source of truth, machine-enforced.
- This closes the last structural seam: r17 made the tree RUN, r20 makes it run on numbers that CANNOT drift from
  the roofline. The deliverable is now internally consistent end-to-end (physics -> roofline -> break-even -> tree).

## honest boundary (unchanged, NOT loosened)
- p_be recomputed from CARDS whose bw/vram are 一手✓ for 3/4 cards (inv8); A100-40 bw still 社区R (一手✓ BLOCKED).
- throughput still roofline ceiling / community R; first-hand vLLM ENV-BLOCKED (Apple Silicon no CUDA).
- inv12 checks INTERNAL consistency only — it cannot validate the input specs (that's inv8's job).

## precise blocking (deliverable advances ONLY on these; this round closed an internal-consistency seam, not the answer)
1. form-factor = USER (Q1). 2. refurb A100-40 quote vs $1735 = USER/market (Q2). 3. refurb RTX 4090 quote vs
$1124 = USER/market (Q3). 4. first-hand single-stream vLLM = ENV (no CUDA).

## teeth-proven
- [A] normal: inv12 green (BE_A100 1735==computed 1734.6, BE_4090 1124==computed 1124.4), ALL PASS exit0.
- [B] canary: sed BE_A100 1735->1500 -> inv12 "BE_A100 1500 != computed 1734.6" -> FAIL exit1 ✓ (teeth).
- [C] full gate: 3 suites ALL GREEN exit0.

## next concrete action
- autonomous 一手✓ + logic/regime/ceiling-tightness/cross-file-consistency verification exhausted. Roofline now:
  inputs pinned (3/4), tree runs+tested (r17), regime proven (r18), ceiling valid+tight (r19), tree constants pinned
  to roofline (r20). No further offline advance without user Q1/Q2/Q3 or an NVIDIA box.
- resting state: deliverable = self-resolving tree, internally consistent end-to-end, ceiling proven tight.