# Workshop short paper draft (4 pages, ICLR 2027 workshop track)
# origin: ai · 2026-11-23 · Track B 保底轨（publication-strategy-20261122 §3 轨 B）
# 定位: 主会稿 (ICML 2027, 9 页) 的 4 页压缩子集 — 数据同源 (tasks/T-PUB-1/data/), 数字与主会稿精确一致
# 目标: ICLR 2027 workshop (2027-04-29~30, 论文截止 2027-02~03 随各 workshop CFP)
# 状态: 初稿 — 数据层完整 (F1/F3/F4 + 机制 + 自修复案例), 待 W6 arena 评审后统一修订

# Mechanical Verifiers as Objective Judges for Agent Reliability

## Abstract

LLM judges are the default scorer in automated agent evaluation, but their reliability on the formalizable core — where the correct answer is a numeric or spec-constrained quantity — has not been measured against an exact reference. We measure it. On 67 real outputs from a 27b model across 10 tasks, a 27b LLM judge under three prompt variants fails to emit a parseable verdict on 52–84% of checkpoints, and on the checkpoints it does parse, its verdicts disagree with a mechanical judge at ≈50% — indistinguishable from a coin flip (binomial p = 0.79–0.90). A mechanical judge (SymPy symbolic comparison or spec-driven regex) fails on 0/67 by construction. We isolate the mechanism: input complexity lengthens the judge's reasoning chain until it exhausts max_tokens and truncates the verdict; raising max_tokens recovers 3/6 truncated cases (the rest fail by chain non-convergence, not budget). We certify the task set against guessing via a model-agnostic bound (P(all-correct by guess) ≤ 3.3×10⁻⁵). On the formalizable core, a mechanical judge is exact, free, and reproducible — and should be the default there.

## 1. Setup

**Tasks.** 10 tasks (7 full-rank, 3 rank-deficient) over GPU systems and math/physics. Full-rank tasks have all parameters present and a unique answer; rank-deficient tasks omit or conflict a key parameter, so the correct behavior is to report the gap rather than fabricate. Each task carries 4–5 checkpoints (47 total): calc checkpoints with a symbolic gold value and tolerance, and fact checkpoints anchored to vendor datasheets. Gold values are verified by SymPy self-check at construction time.

**Judges.** (i) LLM judge: the same 27b model (Qwen3-27B, vLLM, temperature 0) asked to verify a candidate answer under three prompt variants — V1_strict (JSON contract, exact values), V2_loose (relaxed format), V3_engineer (engineering-style rubric). (ii) Mechanical judge: SymPy symbolic comparison for calc checkpoints, spec-driven regex for boolean/fact checkpoints. The mechanical judge is exact on calc checkpoints by construction; on textual-gold checkpoints (naming a missing quantity) it is a regex heuristic and we report those separately.

**Protocol.** 67 real 27b outputs (7 full-rank × 1 + 3 rank-deficient × 10 reps per arm) × 3 prompt variants = 201 judge calls. *Format reliability* = fraction of outputs the LLM judge fails to parse. *Flip rate* = fraction of checkpoints (on parseable outputs, both judges verdicted) where the LLM verdict disagrees with the mechanical verdict.

## 2. Findings

**F1: Format reliability fails at 52–84%.** V1: 77.6% (52/67, Wilson 95% CI [0.663, 0.859]); V2: 83.6% (56/67, [0.729, 0.906]); V3: 52.2% (35/67, [0.405, 0.637]). The mechanical judge: 0/67. No prompt phrasing brings the LLM judge to usable format reliability; the best variant still fails over half of checkpoints.

**F3: Parseable verdicts flip at chance.** V1: 31/60 (51.7%, CI [0.393, 0.638]); V2: 21/44 (47.7%, CI [0.338, 0.621]); V3: 66/128 (51.6%, CI [0.430, 0.600]). Exact two-sided binomial tests against p = 0.5 give p = 0.90 (V1) and p = 0.79 (V3); every CI contains 0.5. Scope: on the rank-deficient textual-gold checkpoints the mechanical reference is a heuristic (0/60), skewing flips toward LLM-correct; excluding them the flip rate is V1 27/45 (60.0%), V2 17/33 (51.5%), V3 45/96 (46.9%) — still ≈50% everywhere. The coin-flip claim rests on calc-gold checkpoints, where the reference is exact.

**F4: The task set is not guessable.** We define a random-guess model (independent sampling per checkpoint type: U[0.5g, 2g] for continuous calc, U{g±50} for integer-exact, 1/100 for textual gold) and derive an analytic upper bound on P(all checkpoints correct by guess): full-rank 1.2×10⁻¹⁰ to 1.9×10⁻⁷; rank-deficient 3.6×10⁻⁶ to 3.3×10⁻⁵ (highest: fewer checkpoints + textual gold). Monte Carlo (N=2000, seed=42): 0/2000 all-correct, consistent with the bound. The bound is an upper bound (conservative: independence assumption, 1/100 textual constant) — high scores on this set are not achievable by guessing.

## 3. Mechanism: truncation, and the self-repair case

All six mt500 format-failure cases in the mechanism probe hit `finish_reason=length` — the token budget is exhausted before the JSON verdict begins. Raising max_tokens 500→2000 recovers 3/6 cases (Q01/Q02/Q06 emit short pure-JSON verdicts, 63–74 chars); the three non-recoveries (Q03/Q04/Q05) emit 2600–3200-char reasoning chains that cycle without converging — recovery is determined by whether the reasoning chain converges, not by max_tokens itself. The same input at temperature 0 flips between parseable and unparseable across runs (Q04: 3/5), so format reliability is not merely low, it is *unstable*.

**Self-repair case.** Q01 at mt500: the judge's reasoning chain exhausts 500 tokens mid-derivation, no verdict emitted (unparseable, 0/5 runs). Same input at mt2000: the chain converges, the judge emits a 74-char pure-JSON verdict with all checkpoints correct (5/5 runs, deterministic). The failure is a budget artifact, not a capability gap — which is exactly why the mechanical reference (which has no reasoning chain to truncate) is the appropriate default on the formalizable core.

## 4. Implications and limitations

**Implications.** (i) On the formalizable core, use the mechanical judge: free, 100% reliable on calc checkpoints, reproducible. (ii) Reserve LLM judgment for the non-formalizable residual (explanation quality, argument structure). (iii) Harness design: max_tokens must exceed the P99 of the judge's output-length distribution, and JSON-only decoding removes the truncation failure mode. (iv) Benchmark design: checkpoint count is not the anti-guessing lever — gold complexity is (F4).

**Limitations.** Single model (27b), single task set (10 tasks); cross-model generalization untested. max_tokens=500 is the default configuration; production deployments may differ. Rank-deficient tasks number 3. The textual-gold checkpoints rely on a regex heuristic reference, reported separately (F3 scope note).

## References (core)

Dev et al. 2026, Judge Reliability Harness (arXiv:2603.05399); Arena-Hard judge (arXiv:2610.30512); Consistency ≠ Reliability (arXiv:2609.13824); The Judge's Verdict (arXiv:2510.09738); Metric Match (arXiv:2606.15029); VERA (arXiv:2610.05452); TRUST (arXiv:2611.10787, under review ICLR 2027). Full related-work comparison in the 9-page main-conference version.
