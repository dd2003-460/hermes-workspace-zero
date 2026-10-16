origin: ai
time: 2026-09-27T20:20+08:00
input: 04-roofline-r5 + r13 feasible-quant dominance + r15/r16 一手✓ bw pinning + 显存门 + H* decision-rule (test_hstar_rule.py)
supersedes_form_of: 04-Hstar-collapse-r7.md, 04.5-final-review-r6.md (both predate the r13 4090-candidate + r15/r16 一手✓)

# 04 DELIVERABLE (final form): H* as a self-resolving decision tree

## 0. what this doc is
The original task asks for H* = the most cost-effective hardware SYSTEM to RUN (inference-deploy, not train) a
27B model (anchor Gemma-3-27B). Criterion R(H) = P(H)/C(H) = throughput ÷ price, subject to a VRAM feasibility
gate. This doc collapses H* into a TREE keyed on the user's own answers, so the answer resolves in one line the
moment those answers exist. No new derivation here — every number is 一手✓ computed + machine-checked upstream
(roofline_verify.py / test_hstar_rule.py, run_all.py green).

## 1. the three live candidates (r13 finding: NOT just A100-40-vs-5090)
| card | form | max quant it CAN load | roofline @ that quant | price (assumed) | R@roofline |
|---|---|---|---|---|---|
| A100-40 refurb | datacenter (2-slot, server airflow) | INT8 (40GB) | 58 tok/s | $1200 | 0.0480 |
| RTX 5090 | consumer tower | INT8 (32GB) | 66 tok/s | $1999 | 0.0332 |
| refurb RTX 4090 | consumer tower | INT4 ONLY (24GB, cannot load INT8=29.6GB) | 74.7 tok/s | <$1124? | (price-driven) |
- L40S excluded: break-even $963 << $7500 new -> never flips at realistic price (r13 inv6).
- The 4090 is a NEW 3rd candidate neither prior doc carried: at roofline it beats 5090 iff refurb price < $1124.
  Honest caveat: 4090 is INT4-only -> lower precision than the INT8 the other two run; quality is a constraint, not in R.

## 2. VRAM feasibility gate (一手✓, hybrid-KV; do NOT re-derive)
weights+KV(8K)+2GB: INT4=15.81 / INT8=29.61 / BF16=57.22 GB. Fits: INT4 all four; INT8 = {A100-40, L40S, 5090}
(4090 EXCLUDED at INT8); BF16 = none. -> each card compared only at its best FEASIBLE quant (r13 fix).

## 3. provenance of the load-bearing inputs (r15/r16 一手✓; inv8 pins 3/4)
- bw/vram 一手✓ (WebFetch, pinned by inv8): 5090=1792/32 (Wikipedia RTX 50), 4090=1008/24 (Wikipedia RTX 40),
  L40S=864/48 (NVIDIA L40S page). A100-40 bw=1555 = 社区R, 一手✓ BLOCKED (NVIDIA page only 80GB / TP403 /
  Wiki domain-blocked / datasheet PDF 80k>fetch-ctx) — NOT fabricated.
- price = 二手市场假设 (USER/market), NOT 一手✓ offline.
- throughput = roofline theoretical ceiling; community "single-stream" numbers ABOVE roofline = batched (r5).
  first-hand vLLM batch=1 = ENV-BLOCKED (Apple Silicon, no CUDA) -> the one remaining honesty gap.

## 4. THE DECISION TREE (self-resolving on the user's answers)
```
Q1: form-factor?
├─ SERVER / workstation you can cool properly + accept refurb-no-warranty
│    └─ Q2: live refurb A100-40 quote?
│         ├─ < $1735  -> H* = A100-40 refurb INT8   (best cost-perf 0.0480, INT8 quality, 40GB headroom)
│         └─ > $1735  -> H* = RTX 5090 INT8          (faster 66>58, price flips it)
└─ DESKTOP TOWER (consumer cooling, easy buy)
     └─ Q3: live refurb RTX 4090 quote?
          ├─ < $1124  -> H* = refurb RTX 4090 INT4   (cheapest, 74.7 tok/s, INT4-only quality caveat)
          └─ > $1124  -> H* = RTX 5090                (INT8-capable, faster, full consumer support)
```
- Break-even $1735 = 1999×(roof_A100/roof_5090)=1999×0.867 (quant-invariant, inv7).
- Break-even $1124 = 1999×(roof_4090_INT4/roof_5090_INT4)=1999×0.563 (quant-invariant, inv7).
- Machine-checked at $1200/$2000/$1735 boundaries by test_hstar_rule.py (independent runner, ALL PASS ✓).

## 5. honest boundary (what this deliverable is NOT)
- H* is NOT one number today. It is fully determined by the user's THREE one-line answers (form-factor, A100-40
  quote, 4090 quote). Until given, the tree is the deliverable — a parameterized answer, not a guess.
- All throughput is roofline ceiling / community R; first-hand vLLM pending a rented NVIDIA box (ENV).
- A100-40 bw is 社区R (blocked), so the A100-40 branch's roofline rests on an unverified-but-standard number; the
  5090 and 4090 branches are 一手✓ grounded.

## 6. status
- Harness: green + teeth-proven (run_all.py, canary-tested r14). Roofline inputs: 3/4 cards 一手✓ pinned (r16).
- Deliverable: decision tree COMPLETE and self-resolving; advances to a single H* on user answers Q1/Q2/Q3.

`review: 04-deliverable | Hstar-decision-tree | deliverable-form | consolidates roofline rank + r13 feasible-quant
4090-candidate (be $1124) + r15/r16 一手✓ bw pinning (3/4 cards) into a self-resolving tree keyed on user
answers Q1 form-factor / Q2 A100-40 quote vs $1735 / Q3 refurb-4090 quote vs $1124; supersedes form of r7/r6
(which lacked the 4090 3rd candidate + 一手✓ provenance); honest boundary: throughput=roofline/communityR,
first-hand vLLM ENV-blocked, A100-40 bw 一手✓ BLOCKED (not fabricated); next: user Q1/Q2/Q3 -> single H*`