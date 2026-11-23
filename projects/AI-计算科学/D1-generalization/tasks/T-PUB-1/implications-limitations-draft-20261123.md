# §5 Implications + §6 Limitations 初稿（T-PUB-1, ICML 2027）
# origin: ai · 2026-11-23 · W4 交付
# 数据源: findings-draft-20261123.md (F1-F5) + paper-data-table-20261123.md
# 状态: 初稿，逻辑 + 数字就位，待 W5 扩写 + 通读

## §5. Implications

### 5.1 For evaluation practice: the mechanical judge is the default on the formalizable core

The central practical consequence of F1–F4 is that on any task where the correct answer is *formalizable* — a numeric value with a tolerance, a spec-constrained quantity, a boolean checkpoint — a mechanical judge (symbolic comparison or spec-driven regex) is the appropriate default. Against the LLM judge it dominates on every axis we measured: format reliability (0% vs 52–84% failure, F1), verdict stability (0% vs ≈50% flip, F3), cost (zero inference calls vs one LLM call per checkpoint), and reproducibility (deterministic vs run-to-run variance even at temperature 0, F2). The LLM judge's known failure modes are not a reason to abandon it; they are a reason to *scope* it. The appropriate division of labor is:

- **Formalizable core** (numeric/spec checkpoints): mechanical judge. Exact, free, reproducible.
- **Non-formalizable residual** (explanation quality, reasoning style, open-ended correctness): LLM judge or human. The core is where the LLM judge is *least* defensible, not most.

This is a scoping claim, not a dismissal. A benchmark that mixes both kinds of checkpoints should grade the core mechanically and reserve LLM judgment for the residual, rather than letting a single LLM judge grade everything and inherit its format failures into the score.

### 5.2 For harness design: max_tokens is a correctness parameter, not just a cost parameter

F2 shows the dominant failure mechanism is token-budget exhaustion by the reasoning chain: the model reasons correctly but spends its `max_tokens` budget on the chain before it can emit the verdict. Two design consequences:

1. **`max_tokens` must be set above the P99 of the output-length distribution for the target model and task class**, not at a nominal default. Our default (500) truncated 6/6 hard cases; raising it to 2000 recovered the three recoverable cases. A harness that does not measure the length distribution is silently discarding correct answers.
2. **Constrain the output format (JSON-only decoding, or a structured-output constraint)** so the model cannot spend the budget on a free-form reasoning chain that displaces the verdict. The instruction-following non-determinism we observed (F2, Q04) — the same input at temperature 0 sometimes emits a 74-char JSON and sometimes a 2600-char chain — is exactly what a structured-output constraint removes.

### 5.3 For benchmark design: gold complexity, not checkpoint count, is the anti-hack lever

F4 (the guessing bound) and F5 (the trade-off) together argue against a common benchmark-design intuition. Adding more checkpoints does not by itself make a benchmark harder to game: a judge that flips at chance (F3) or a model that can guess the answer class (F4) defeats it regardless of checkpoint count. What resists guessing is *gold-value complexity* — answers that cannot be recovered from the answer distribution alone (our rank-deficient tasks, where the model must either report the gap or fabricate, F5). A benchmark's anti-hack property should be certified by the guessing bound (theory section), not assumed from its size.

### 5.4 For the LLM-judge literature: a mechanical reference changes what can be claimed

The LLM-judge-reliability literature (related work) establishes that LLM judges are unreliable, but its ground truth is human annotation or perturbation tests — both expensive and themselves noisy. On the formalizable core, a mechanical judge is an *exact* reference, which lets the field make claims it could not before: the failure is not just "the LLM judge disagrees with humans" (correlation, confounded by human noise) but "the LLM judge disagrees with an exact answer at a quantified rate, with a certified mechanism (truncation vs non-convergence vs instruction-following)." The mechanical reference is the contribution that turns reliability from a measured correlation into a measured deviation from ground truth.

## §6. Limitations

**Single model, single task set.** All measurements are on one model (27b) and one task set (10 tasks: 7 full-rank, 3 rank-deficient). The 52–84% format-failure rate and ≈50% flip rate are properties of *this* model on *this* core; cross-model generalization is untested. The guessing bound (theory section) is model-agnostic and provides the fallback: it certifies the task set resists guessing regardless of which judge or model is used, so the anti-hack claim does not rest on the single-model measurements. (A cross-model subset is the natural upgrade; see the task plan.)

**Default `max_tokens`.** The 500-token budget is a common default, not a production-tuned value. Production harnesses may use larger budgets, which would shift the F1 rates downward (more recoverable cases) — but F2 shows the shift is bounded: the convergence-failure cases (Q03/Q05) fail even at 2000, so a non-zero failure floor remains. The *mechanism* (reasoning-chain exhaustion) is the robust claim; the exact rates are budget-dependent.

**Small rank-deficient subset.** Only 3 of 10 tasks are rank-deficient (the class where the model must report a gap rather than fabricate). F5's trade-off is measured on this subset (n=10/arm). The trade-off is a real but small-n effect; the gray zone (7/30) is the measurable signal but its CI is wide.

**Gold provenance.** The fact-based gold values are sourced to spec-page level (e.g., "H100 SXM: 3.35 TB/s") but were not each verified against the primary PDF at the digit level. A gold error would silently corrupt the mechanical reference for that checkpoint. This is a known follow-up (followups.md #1) and does not affect the *mechanism* findings (which are about the judge, not the gold) but does bound the precision of the absolute rates.

**Single-run point estimates.** The F1/F3 rates are single-run estimates. F2 shows that on borderline cases the underlying quantity is a distribution (run-to-run flip at temperature 0), so the point estimates carry unmodeled variance. This *strengthens* the qualitative claim (the LLM judge is unstable) but means the exact rates should be read as order-of-magnitude, not calibrated.
