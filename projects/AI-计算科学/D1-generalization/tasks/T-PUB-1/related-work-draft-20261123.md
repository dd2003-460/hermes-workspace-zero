# §3 Related Work 初稿（T-PUB-1, ICML 2027）
# origin: ai · 2026-11-23 · W3 交付
# 素材: research/related-work-survey-20261123.md (6 篇撞车核验 conf 0.9 + 4 条 arXiv 线)
# 定位: 差异化三支柱 (a) format reliability (b) 机制归因 (c) 防 hack 理论

## §3 Related Work（目标 800-1000 词，初稿 ~700 词）

### 3.1 LLM-as-a-judge reliability

LLM-as-a-judge has become the default scalable evaluation mechanism (Zheng et al. 2023), and a rapidly growing literature — 600+ papers in 2026 alone — has documented its unreliability. The established failure modes are *verdict-accuracy* biases: position bias, verbosity bias, self-preference, and instruction sensitivity. The closest prior work to ours operates on the reliability axis rather than the bias axis:

- **Judge Reliability Harness (Dev et al. 2026, arXiv:2603.05399).** Measures a judge's robustness to *input* perturbations — formatting changes, paraphrasing, verbosity, label flips — via a perturbation test battery. The "format" in JRH is the judge's *input*; we measure the judge's *output* format reliability — the rate at which it fails to emit a parseable verdict at all. The two "formats" point in opposite directions: JRH perturbs the input and asks whether the verdict stays stable; we hold the input fixed and ask whether a verdict is emitted at all. JRH does not instrument the output-format failure mode.

- **Arena-Hard (arXiv:2610.30512).** Measures verdict drift across instruction combinations (21.2% prompt-flip rate), using repeated-run consistency as ground truth. No output-format reliability metric, no mechanism attribution, no anti-guess guarantee.

- **Consistency / Judge's Verdict / Metric Match / VERA (arXiv:2609.13824, 2510.09738, 2606.15029, 2610.05452).** Measure consistency against human annotation (Cohen's κ), reliability-metric estimation, or hidden-activation-based verdict reliability. All use *human annotation or perturbation tests* as the reference; none use a mechanical exact reference on the formalizable core.

**Our distinction (three pillars).** (a) *Format reliability as a first-class metric*: the prior literature measures verdict accuracy *given that a verdict was emitted*; we measure the prerequisite failure — the judge emitting no parseable verdict at all — which the above six papers do not instrument. (b) *Mechanism attribution*: where the reliability literature reports correlations ("reliability varies with X"), we attribute failures to actionable mechanisms with direct engine evidence (`finish_reason=length`, output-tail inspection) and separate truncation-recoverable from convergence-failure behavior classes. (c) *Anti-guess guarantee*: no prior work provides a guarantee that high scores are not guessable; we give a model-agnostic analytic bound (§Theory).

### 3.2 Mechanical / symbolic verification

The mechanical judge we use — SymPy symbolic comparison for numeric checkpoints, spec-driven regex for boolean ones — is a standard exact verifier. Its use as a *reference* for evaluating LLM judges is the novel element: prior LLM-judge work uses human annotation or perturbation tests as ground truth, which are themselves noisy and expensive. On the formalizable core (numeric/boolean checkpoints with known gold), a mechanical reference is exact, free, and reproducible by construction — making it the natural ground truth against which to measure judge reliability. This is analogous to using unit tests as the reference for evaluating a code-reviewer, rather than asking humans whether the review is correct.

### 3.3 Positioning summary

| Dimension | Reliability literature (JRH, Arena-Hard, etc.) | This work |
|---|---|---|
| Question | Is the emitted verdict accurate/robust? | Is a verdict emitted at all, and is the high score guessable? |
| "Format" | Input perturbation (JRH) | Output parseability (ours) |
| Ground truth | Human annotation / perturbation / repeated runs | Mechanical exact reference (formalizable core) |
| Mechanism | Correlation ("varies with X") | Attribution (truncation vs convergence, engine evidence) |
| Anti-guess | — | Analytic bound (model-agnostic given the guess model; conservative — see §Theory) |
| Judge-model dependent? | Yes (measures a specific judge) | Bound is model-agnostic; rates are per-judge |

The implication is not that LLM judges are useless — they remain appropriate for the non-formalizable residual (explanation quality, argument structure) where no mechanical reference exists. The implication is that on the formalizable core, the mechanical judge should be the default: it is exact, free, reproducible, and its failure mode (none) is known by construction.
