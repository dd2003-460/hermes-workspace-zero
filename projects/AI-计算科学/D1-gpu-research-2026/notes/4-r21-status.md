origin: ai
time: 2026-09-27T21:35+08:00
stage: 04 / round: r21 / status: DONE (inv13 BW-efficiency eta: roofline uses THEORETICAL peak BW = implied eta=1; real GPUs hit ~70-85%; proved ceiling still valid under eta<1 AND that the break-even ratio silently assumes UNIFORM eta across cards -> H* CAN flip if the A100-40's single-stream efficiency is worse -> uniform-eta is LOAD-BEARING, honest open risk)

# cursor: 04/r21 = the roofline's hidden third optimism (imperfect BW utilization) bounded; uniform-eta flagged load-bearing

## ground-truth (re-confirm, honest-first)
- stop-hook "持久状态" (stage 02 / Ego Lite / partition-cover / well-founded μ) = GLOBAL formal-methods cursor, NOT this project.
- real cursor = notes/4-r20-status.md -> advanced to r21 here. Stayed GPU thread, did not restart.

## done this round (验证, not analysis — per "上一多为验证/分析 -> 本轮验证")
The roofline bw/bytes uses the SPEC PEAK bandwidth, which silently implies eta=1 (perfect utilization). No real GPU
saturates its memory subsystem at spec peak — achievable BW is ~70-85% (eta<1). inv13 (NEW) bounds this LAST major
silent optimism and separates what it does/doesn't threaten:
- (1) ceiling STILL valid: real = eta*peak <= peak for any eta in (0,1] -> the upper-bound property survives imperfect
  BW utilization. (This is the THIRD optimism layer accounted: r18 regime, r19 KV traffic, r21 BW-efficiency.)
- (2) the break-even RATIO p_be = price_5090*roof_A/roof_5090 cancels eta ONLY IF eta is UNIFORM across the two
  cards. If the A100-40's achievable-BW fraction is materially lower than the 5090's (datacenter card repurposed on
  a desktop board, no NVLink, weaker single-stream efficiency), the true ratio drops -> the true be DROPS -> H* FLIPS.
- quantified the flip: uniform be=$1735 (A100-40 wins @ $1200). With A100-40 eta 0.80->0.45 (worse than 5090's),
  true be=$976 -> $1200 > $976 -> 5090 wins -> H* FLIPS at a quote my uniform model called an A100 win.

## why this matters (advance, not restate)
- This is the FIRST time the deliverable's cost-perf ranking is shown to be CONDITIONAL on a physics assumption that
  cannot be checked offline: uniform achievable-BW efficiency. The H* = A100-40-refurb conclusion (server branch) is
  robust ONLY if the A100-40 sustains single-stream BW efficiency comparable to the 5090's. That is exactly what a
  first-hand vLLM benchmark (ENV-BLOCKED) would measure -> this round converts a hidden assumption into a NAMED,
  quantified open risk with a concrete falsifiable condition (A100-40 achievable-BW fraction < ~0.56 of 5090's flips it).
- Honest-first: I do NOT claim the A100-40 wins unconditionally. The server-branch H* now carries an explicit caveat:
  "assuming comparable single-stream BW efficiency; verify on a real box."

## honest boundary (NOT loosened — tightened)
- eta values (0.80 uniform, 0.45 bad) are illustrative bounds, NOT measured -> the FLOOR of the risk (does the flip
  actually happen?) is ENV-BLOCKED (no CUDA). What IS proven offline: the flip MECHANISM and its threshold (~0.56).
- throughput still roofline ceiling / community R; first-hand vLLM single-stream BLOCKED (Apple Silicon no CUDA).
- A100-40 bw 一手✓ BLOCKED (not fabricated); 5090/4090 branches 一手✓ grounded (inv8).

## precise blocking (deliverable advances ONLY on these; this round named+quantified a new load-bearing risk)
1. form-factor = USER (Q1). 2. refurb A100-40 quote vs $1735 = USER/market (Q2). 3. refurb RTX 4090 quote vs $1124
= USER/market (Q3). 4. first-hand single-stream vLLM = ENV (no CUDA) -- AND this round shows #4 now also answers the
eta question (measured achievable BW per card), so it is doubly load-bearing.

## teeth-proven
- [A] normal: inv13 green (real<=peak), teeth print be $1735->$976, @$1200 True->False (H* flips), ALL PASS exit0.
- [B] canary: sed eta_a_bad 0.45->0.80 (=uniform) -> be stays $1735, no flip -> teeth "H* didn't flip when eta
  dropped" -> FAIL exit1 ✓ (proves the check has teeth, not decorative).
- [C] full gate: 3 suites ALL GREEN exit0.

## next concrete action
- silent-assumption audit of the roofline conclusion now spans: inputs (inv8), tree-executable (r17)+monotone (inv9),
  regime/memory-bound (inv10), ceiling-tightness/KV (inv11), cross-file consistency (inv12), BW-efficiency (inv13).
- The remaining un-checked items are all ENV/USER-gated (measured eta, live quotes, form-factor). Offline advance is
  genuinely exhausted; resting state is honest and well-characterized.