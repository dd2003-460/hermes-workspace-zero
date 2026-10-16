origin: ai
time: 2026-09-27T21:50+08:00
stage: 04 / round: r22 / status: DONE (inv14 PARAMS-tolerance + PARAMS-invariance: '27B' is a MARKETING ROUND NUMBER never pinned to an exact dense count — the LAST free constant; proved every VRAM fit verdict survives +/-2% PARAMS error AND the H* DELIVERABLE (break-even) is PARAMS-invariant so the rounding cannot flip the decision)

# cursor: 04/r22 = the last free constant ('27B') is bounded — gates have tolerance, the decision is invariant to it

## ground-truth (re-confirm, honest-first)
- stop-hook "持久状态" (stage 02 / Ego Lite / partition-cover / well-founded μ) = GLOBAL formal-methods cursor, NOT this project.
- real cursor = notes/4-r21-status.md -> advanced to r22 here. Stayed GPU thread, did not restart.

## done this round (验证, not analysis — per "上一多为分析 -> 本轮验证")
PARAMS = 27.0e9 is a marketing round number ("27B"), never pinned to an exact dense-parameter count. It is the LAST
free constant the entire roofline rests on. Two questions, both machine-answered by inv14 (NEW):
- (1) VRAM-gate TOLERANCE: how far can PARAMS drift before a fit verdict flips? margin/bytes_per_param gives each
  fitting card's PARAMS-absorbing headroom as % of PARAMS. Tightest = INT8/5090 at 8.9% -> all fit verdicts survive
  the plausible +/-2% rounding band of "27B" with >4x margin. The rounding does NOT threaten any gate.
- (2) PARAMS-INVARIANCE of the DELIVERABLE: roofline ~ 1/PARAMS for EVERY card, so the break-even RATIO cancels
  PARAMS -> p_be must NOT move when PARAMS moves. Proved: be = $1735 at PARAMS and at 10x PARAMS (identical). The
  H* DECISION is invariant to the exact parameter count; only absolute tok/s and GB scale with it, not the choice.

## teeth-proven (both halves, not decorative)
- teeth(a) boundary REAL: INT8/5090 tolerance 8.9% -> at +9.9% total=32.27GB > 32GB -> OOMs. The tolerance is a
  genuine cliff, not a decorative margin.
- teeth(b) invariance test DETECTS leaks: a hypothetical leaky formula (PARAMS not cancelled) moves at 10x PARAMS
  -> the test would catch a future formula that wrongly lets the decision depend on PARAMS.
- canary: sed BAND 0.02->0.10 -> INT8/5090 tol 8.9% < 10% -> inv14(1) RED exit1 ✓ (proves the tolerance check bites).

## why this matters (advance, not restate)
- Completes the constant-by-constant audit of the roofline conclusion. Every input is now either pinned 一手✓ (bw/vram
  via inv8), or proven to have TOLERANCE/invariance so its imprecision cannot change the answer (regime inv10 has
  ~7x margin, ceiling inv11 tight, cross-file inv12 pinned, eta inv13 flagged load-bearing, PARAMS inv14 tolerant+
  invariant). The deliverable's correctness no longer depends on any single un-pinned number.
- Honest-first: I do NOT claim PARAMS=27.0e9 is exact. I prove EXACTNESS IS UNNECESSARY — the gates tolerate the
  rounding and the decision is invariant to it. That is the stronger, more honest statement.

## honest boundary (NOT loosened)
- PARAMS exact dense count not 一手✓ (not needed — decision is invariant, gates tolerant); "27B" band assumed +/-2%
  (illustrative; any band < 8.9% preserves every gate, proved for the actual tightest).
- throughput still roofline ceiling / community R; first-hand vLLM single-stream BLOCKED (Apple Silicon no CUDA).
- A100-40 bw 一手✓ BLOCKED (not fabricated); 5090/4090 branches 一手✓ grounded (inv8).

## precise blocking (deliverable advances ONLY on these; this round bounded the last free constant, not the answer)
1. form-factor = USER (Q1). 2. refurb A100-40 quote vs $1735 = USER/market (Q2). 3. refurb RTX 4090 quote vs $1124
= USER/market (Q3). 4. first-hand single-stream vLLM = ENV (no CUDA) -- also answers the eta question (inv13).

## next concrete action
- Constant audit exhausted: bw/vram (inv8), tree (r17/inv9), regime (inv10), KV-tightness (inv11), cross-file (inv12),
  eta (inv13), PARAMS (inv14). Every remaining unknown is ENV/USER-gated. Offline advance genuinely exhausted.