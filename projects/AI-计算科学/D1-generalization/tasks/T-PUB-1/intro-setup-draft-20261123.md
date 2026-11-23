# §1 Introduction + §2 Setup 初稿（T-PUB-1, ICML 2027）
# origin: ai · 2026-11-23 · W2 交付
# 定位: 差异化三支柱 (a) format reliability (b) 机制归因 (c) 防 hack 理论
# 防撞车: JRH (Dev et al. 2026) 测输入扰动鲁棒性, 我们测输出格式可靠性——方向相反

## §1 Introduction（目标 900-1000 词，初稿 ~750 词，W5 扩）

LLM-as-a-judge has become the default evaluation mechanism for LLM systems: it scales where human evaluation cannot, and it is now embedded in benchmarking pipelines, preference-label generation, and safety review. A parallel and rapidly growing literature (600+ papers in 2026 alone) has established that these judges are unreliable — they exhibit position bias, verbosity bias, self-preference, and instruction sensitivity. What this literature has not addressed is a more basic question: *on the subset of evaluation targets that are mechanically checkable, is an LLM judge even necessary?*

We study this question on the **formalizable core** — the part of an evaluation target whose correctness reduces to a finite set of numeric or boolean checkpoints with a known ground truth (a gold value and a tolerance, or a spec-driven keyword/forbidden pattern). For GPU systems questions, this core includes derived quantities (throughput, KV-cache budget, ridge-point classification) and datasheet-anchored facts; for math/physics questions it includes closed-form values. The core is exactly the part where a mechanical judge — SymPy symbolic comparison for numeric checkpoints, spec-driven regex for boolean ones — is exact, free, and reproducible by construction.

**Our contribution.** Against a mechanical judge as the exact reference, we measure a 27b LLM judge on 67 real model outputs across 10 tasks (7 full-rank, 3 rank-deficient) under three prompt variants (201 judge calls total). We find:

1. **Format reliability fails (F1).** The LLM judge emits unparseable output on 52–84% of calls depending on prompt variant; the mechanical judge fails on 0% by construction. The failure is content-driven (task type / gold complexity), not a length threshold: full-rank tasks fail 7/7 across the entire length range.

2. **The mechanism is attributable and unstable (F2).** Controlled re-judging, output-tail inspection, and a 5-rep determinism probe show the mechanism is a single causal chain — input complexity → longer reasoning chain → collision with max_tokens → JSON truncation — not attention degradation. Three behavior classes: truncation-recoverable (Q01/Q02/Q06), convergence failure (Q03/Q05, the model cycles and cannot emit a verdict even with more tokens), and a borderline class (Q04) that **flips run-to-run at temperature 0** — the same input at the same temperature alternates between a 74-char JSON and a 2600-char reasoning chain. The root cause is instruction-following non-determinism; the LLM judge's format reliability is not merely low, it is unstable.

3. **Verdict accuracy flips at chance (F3).** Even on the parseable subset, the LLM judge disagrees with the mechanical judge on 48–52% of checkpoints — indistinguishable from a coin flip.

4. **The task set resists guessing (F4).** Under an explicit random-guess model, the probability of guessing all checkpoints correct is bounded analytically (1.2e-10 to 3.3e-5) and confirmed by simulation (0/2000). The bound is model-agnostic.

5. **Prompt optimization is not free (F5).** A three-arm behavioral experiment shows that fixing one checkpoint dimension (c1: 33%→100%) induces a side effect on another (c3: 100%→77%, via induced conditional-enumeration / hedging behavior).

**Positioning.** The closest prior work is the Judge Reliability Harness (Dev et al. 2026), which measures a judge's robustness to *input* perturbations (formatting, paraphrasing, verbosity, label flip). We measure a judge's *output* format reliability — the rate at which it fails to emit a parseable verdict at all — a failure mode JRH does not instrument. Where the reliability literature reports correlations ("reliability varies with X"), we attribute failures to actionable mechanisms (truncation vs complexity vs instruction-following) with direct engine evidence. Where prior work relies on human annotation or perturbation tests as ground truth, our mechanical reference is exact and free on the formalizable core. Where no prior work provides a guarantee that high scores are not guessable, we give a model-agnostic analytic bound.

**Implication.** On the formalizable core, the mechanical judge should be the default: it is exact, free, reproducible, and its failure mode (none) is known. LLM judges remain appropriate for the non-formalizable residual — explanation quality, style, argument structure — where no mechanical reference exists.

## §2 Setup & Method（目标 1200-1500 词，初稿 ~600 词，W5 扩）

### 2.1 Task set

Ten tasks: 7 full-rank (Q01–Q07) and 3 rank-deficient (Q08–Q10). Domains: GPU systems (7), math (1), physics (1). Each task carries 4–5 checkpoints.

**Full-rank tasks** are self-contained: the prompt provides all information needed to derive every checkpoint's gold value. Gold values are derived symbolically (SymPy 1.14.0) from the prompt's given quantities, or anchored to public datasheets (NVIDIA H100/H200 specs). Checkpoint types: `calc` (numeric, tolerance 2% or exact-integer), `fact` (numeric or textual, datasheet-anchored), `bool` (spec-driven keyword/forbidden-pattern).

**Rank-deficient tasks** deliberately withhold information: Q08 omits the per-GPU HBM capacity (the model must either commit to a value from memory or flag the gap); Q09's retrieved spec excerpt is missing a row the question requires; Q10 presents two contradictory sources (vendor datasheet 3.35 TB/s vs blog 2.0 TB/s). These probe whether the model *knows what it doesn't know* — the rank-deficient axis. The prompt constrains the allowed source ("the only source you are allowed to use is this retrieved spec excerpt"), so supplementing with external facts is a scored violation, not a recovery.

### 2.2 Judges

**Mechanical judge.** Each checkpoint is evaluated deterministically:
- `calc` (tol > 0): SymPy evaluates the gold expression; the model's extracted value passes iff |v−g|/|g| < tol.
- `calc` (tol = 0, integer): exact match after SymPy evaluation.
- `fact` (numeric): same as calc with the fact's tolerance.
- `fact` (textual): spec-driven keyword match.
- `bool`: spec-driven `keywords` (any present → pass) and `forbidden_numbers`/`forbidden_patterns` (any present → fail). Supports "pass-by-absence" checkpoints (e.g., "must not output tok/s").

The mechanical judge is exact by construction: its only failure mode is a bug in the spec, which is caught by a SymPy self-check at task-construction time (Appendix A).

**LLM judge.** A 27b model (local vLLM deployment, temperature 0) is prompted to judge each checkpoint and emit a JSON verdict `{"c1": true/false, ...}`. Three prompt variants:
- **V1_strict**: "You are a strict numeric grader. Judge each checkpoint right/wrong. tolerance=0.02 checkpoints: within 2% of gold = right; tolerance=0 (integer): must equal gold exactly, off-by-one = wrong. Output JSON only: {\"checkpoint_id\": true/false}. No explanation."
- **V2_loose**: relaxed tolerance phrasing + "be lenient on rounding".
- **V3_engineer**: structured engineering rubric + "show your check before the JSON".

Default `max_tokens=500` (the deployment default; the truncation mechanism in F2 is measured at this budget).

### 2.3 Measurement protocol

- **Format reliability** = fraction of judge calls emitting unparseable output (no valid JSON verdict object).
- **Flip rate** = on parseable calls, fraction of checkpoints where LLM verdict ≠ mechanical verdict.
- **Mechanism attribution**: (i) max_tokens 500→2000 re-judging of failure cases (truncation recovery rate); (ii) engine `finish_reason` and `completion_tokens` (direct truncation evidence); (iii) partial correlation of input length vs failure controlling for output length (independent complexity effect); (iv) within-checkpoint-count stratification (gold-complexity vs checkpoint-count attribution).
- **Guessing bound**: explicit random-guess model (continuous: U[0.5g, 2g], hit prob 2·tol/1.5; integer: U[g±50], hit prob 1/101; textual: 1/100 conservative), analytic product bound + Monte Carlo (N=2000, seed=42).
- **Three-arm behavioral experiment** (rank-deficient only, n=10/arm): A_baseline (no reminder), B_remind (commitment reminder), B'_remind (commitment + conditional-enumeration inducement). c3 scored under two criteria: strict (commit to a single value; conditional enumeration = miss) and lenient (hedging-word exemption per sentence window).

### 2.4 Deployment

27b model served via vLLM at a local endpoint; no weight updates. All judge calls at temperature 0. Task construction and gold verification use SymPy 1.14.0; the full gold-derivation trace is in Appendix A.
