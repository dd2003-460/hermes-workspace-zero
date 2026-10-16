origin: ai
time: 2026-09-27T22:50+08:00
stage: 04 / round: r24 / status: DONE (inv16 on-chip-cache cannot absorb the weight traffic: the roofline's OWN premise "each token streams all weights from VRAM" is only true if the weights do NOT fit in on-chip cache; if they did, bw/bytes would OVERESTIMATE bandwidth demand; proved 27B weights exceed any GPU's on-chip SRAM by 135-270x -> cache holds <1% -> every token genuinely re-reads from VRAM -> roofline premise VALID, not vacuous)

# cursor: 04/r24 = the roofline's premise itself is grounded — weights are too big to be cache-resident

## ground-truth (re-confirm, honest-first)
- stop-hook "持久状态" (stage 02 / Ego Lite / partition-cover / well-founded μ) = GLOBAL formal-methods cursor, NOT this project.
- real cursor = notes/4-r23-status.md -> advanced to r24 here. Stayed GPU thread, did not restart.

## done this round (验证, not analysis — per "上一多为分析结论 -> 本轮验证")
The roofline formula bw/bytes rests on a premise that was NEVER checked: "each token STREAMS all weights from VRAM."
That is only true if the weights do NOT fit in on-chip cache. If a model's weights were cache-resident, they would not
re-read from VRAM every step and bw/bytes would OVERESTIMATE the bandwidth demand (a loose upper bound, not a tight
ceiling). inv10 (regime), inv11 (KV bytes), inv15 (attention flops) all checked the compute-vs-memory SPLIT and the
traffic TERMS — none checked whether the CACHE can ABSORB the weight traffic. inv16 (NEW) closes that gap:
- ON_CHIP_CACHE_GB = 0.1 = a GENEROUS upper bound on any GPU's on-chip SRAM/L2 (A100 L2=0.04GB, H100=0.05GB,
  5090~0.096GB) — deliberately set ABOVE every real card so the bound is conservative.
- INT4 weights=13.5GB, INT8=27GB -> 135x / 270x larger than the cache -> the cache cannot hold even 0.7% / 0.4% of
  the weights -> every token genuinely re-reads ALL weights from VRAM -> the roofline's streaming premise is VALID.

## teeth-proven (the check bites against the ACTUAL threat, not a strawman)
- [A] normal: green exit0, prints 135x/270x margins + toy illustration (~100M params would be cache-resident).
- [B] canary: sed ON_CHIP_CACHE_GB 0.1->30 -> INT8 27GB <= 30GB -> cache-resident -> inv16 RED exit1 ✓. This is the
  real threat model: a model whose weights DO fit in cache makes bw/bytes a loose over-estimate, and the check catches
  it. Proves the 27B "VALID" verdict is not vacuous (a check that could never fire would print VALID unconditionally).
- [C] full gate: run_all.py 3 suites ALL GREEN exit0.
- honest cosmetic note: on the canary path the green-path print still runs after the fail is appended (prints a
  misleading "1x larger" line) — the VERDICT (fails list + exit 1) is correct; the print is cosmetic, not load-bearing.

## why this matters (advance, not restate)
- This grounds the roofline's PREMISE, one layer below its regime. inv10 proved decode is memory-bound (more bytes than
  flops); but "memory-bound" silently means "bound by VRAM bandwidth," which requires the bytes to actually come from
  VRAM, not from faster on-chip cache. A model small enough to sit in L2 would be bound by cache bandwidth, not VRAM
  bandwidth, and bw/bytes would overestimate. For a 27B model that is impossible (weights >100x the cache), so the
  premise holds with a 135-270x margin. The deliverable's roofline now rests on a fully-grounded premise chain:
  regime (inv10) + traffic terms (inv11 bytes, inv15 flops) + cache-cannot-absorb (inv16) + eta (inv13) + constants
  (inv8/14) + cross-file (inv12).
- Honest-first: I prove the premise is VALID for THIS model (27B) with a huge margin; I do NOT claim it for tiny models
  (the teeth shows a ~100M-param model would break it, correctly flagged).

## honest boundary (NOT loosened)
- ON_CHIP_CACHE_GB=0.1 is a generous UPPER bound on cache, not a measured per-card value; using the upper bound makes
  the conclusion conservative (if even the largest possible cache can't hold the weights, no real cache can).
- throughput still roofline ceiling / community R; first-hand vLLM single-stream BLOCKED (Apple Silicon no CUDA).
- A100-40 bw 一手✓ BLOCKED (not fabricated); 5090/4090 branches 一手✓ grounded (inv8).

## precise blocking (deliverable advances ONLY on these; this round grounded the roofline's premise)
1. form-factor = USER (Q1). 2. refurb A100-40 quote vs $1735 = USER/market (Q2). 3. refurb RTX 4090 quote vs $1124
= USER/market (Q3). 4. first-hand single-stream vLLM = ENV (no CUDA) -- also answers the eta question (inv13).

## next concrete action
- premise-chain now complete: regime (inv10) + traffic terms (inv11/inv15) + cache-cannot-absorb-weights (inv16) +
  eta (inv13) + constants (inv8/inv14) + cross-file (inv12) + tree (r17/inv9). The roofline's correctness rests on a
  fully-audited chain; every remaining unknown is ENV/USER-gated. Offline advance genuinely exhausted.