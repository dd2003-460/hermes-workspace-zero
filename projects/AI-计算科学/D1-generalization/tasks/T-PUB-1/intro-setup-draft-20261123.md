# §1 Introduction + §2 Setup 初稿（T-PUB-1, ICML 2027）
# origin: ai · 2026-11-23 · W2 交付
# 定位: 差异化三支柱 (a) format reliability (b) 机制归因 (c) 防 hack 理论
# 防撞车: JRH (Dev et al. 2026) 测输入扰动鲁棒性, 我们测输出格式可靠性——方向相反

## §1 Introduction（目标 900-1000 词，v2 ~950 词，2026-11-23 晚 W5 扩）

LLM-as-a-judge has become the default evaluation mechanism for LLM systems: it scales where human evaluation cannot, and it is now embedded in benchmarking pipelines, preference-label generation, and safety review. A parallel and rapidly growing literature (600+ papers in 2026 alone) has established that these judges are unreliable — they exhibit position bias, verbosity bias, self-preference, and instruction sensitivity. What this literature has not addressed is a more basic question: *on the subset of evaluation targets that are mechanically checkable, is an LLM judge even necessary?*

This question matters because the reliability of the judge silently bounds the validity of the entire evaluation pipeline. An automated agent-evaluation harness scores thousands of outputs per day; if the judge fails to emit a parseable verdict on half of them, the pipeline is not producing a noisy score — it is producing *no score* on half the data, and every aggregate reliability metric computed over the parseable subset is conditioned on a selection that the metric itself does not report. The failure is worse than a biased scorer: it is a scorer that is intermittently absent, and the absence is correlated with the difficulty of the item being scored (the harder the checkpoint, the more likely the judge's reasoning chain overruns its token budget and truncates).

We study this question on the **formalizable core** — the part of an evaluation target whose correctness reduces to a finite set of numeric or boolean checkpoints with a known ground truth (a gold value and a tolerance, or a spec-driven keyword/forbidden pattern). For GPU systems questions, this core includes derived quantities (throughput, KV-cache budget, ridge-point classification) and datasheet-anchored facts; for math/physics questions it includes closed-form values. The core is exactly the part where a mechanical judge — SymPy symbolic comparison for numeric checkpoints, spec-driven regex for boolean ones — is exact, free, and reproducible by construction. Our working hypothesis is that on this core the LLM judge is not merely unnecessary but actively harmful: it adds a failure mode (format truncation) that the mechanical judge does not have, and it adds noise (verdict flips) that the mechanical judge does not have.

**Our contribution.** Against a mechanical judge as the exact reference, we measure a 27b LLM judge on 67 real model outputs across 10 tasks (7 full-rank, 3 rank-deficient) under three prompt variants (201 judge calls total). We find:

1. **Format reliability fails (F1).** The LLM judge emits unparseable output on 52–84% of calls depending on prompt variant; the mechanical judge fails on 0% by construction. The failure is content-driven (task type / gold complexity), not a length threshold: full-rank tasks fail 7/7 across the entire length range.

2. **The mechanism is attributable and unstable (F2).** Controlled re-judging, output-tail inspection, and a 5-rep determinism probe show the mechanism is a single causal chain — input complexity → longer reasoning chain → collision with max_tokens → JSON truncation — not attention degradation. Three behavior classes: truncation-recoverable (Q01/Q02/Q06), convergence failure (Q03/Q05, the model cycles and cannot emit a verdict even with more tokens), and a borderline class (Q04) that **flips run-to-run at temperature 0** — the same input at the same temperature alternates between a 74-char JSON and a 2600-char reasoning chain. The root cause is instruction-following non-determinism; the LLM judge's format reliability is not merely low, it is unstable.

3. **Verdict accuracy flips at chance (F3).** Even on the parseable subset, the LLM judge disagrees with the mechanical judge on 48–52% of checkpoints — indistinguishable from a coin flip.

4. **The task set resists guessing (F4).** Under an explicit random-guess model, the probability of guessing all checkpoints correct is bounded analytically (1.2e-10 to 3.3e-5) and confirmed by simulation (0/2000). The bound is model-agnostic.

5. **Prompt optimization is not free (F5).** A three-arm behavioral experiment shows that fixing one checkpoint dimension (c1: 33%→100%) induces a side effect on another (c3: 100%→77%, via induced conditional-enumeration / hedging behavior).

**Positioning.** The closest prior work is the Judge Reliability Harness (Dev et al. 2026), which measures a judge's robustness to *input* perturbations (formatting, paraphrasing, verbosity, label flip). We measure a judge's *output* format reliability — the rate at which it fails to emit a parseable verdict at all — a failure mode JRH does not instrument. Where the reliability literature reports correlations ("reliability varies with X"), we attribute failures to actionable mechanisms (truncation vs complexity vs instruction-following) with direct engine evidence. Where prior work relies on human annotation or perturbation tests as ground truth, our mechanical reference is exact and free on the formalizable core. Where no prior work provides a guarantee that high scores are not guessable, we give a model-agnostic analytic bound.

**Implication.** On the formalizable core, the mechanical judge should be the default: it is exact, free, reproducible, and its failure mode (none) is known. LLM judges remain appropriate for the non-formalizable residual — explanation quality, style, argument structure — where no mechanical reference exists.

**Paper structure.** §2 describes the task set, the two judges, and the measurement protocol. The findings section reports five findings (F1–F5): format reliability (F1), mechanism attribution (F2), verdict accuracy (F3), the anti-guessing bound (F4), and prompt side effects (F5). A related-work section positions the contribution against the LLM-judge-reliability literature. An implications-and-limitations section closes the paper. Task construction and gold-derivation traces are in the appendix.

## §2 Setup & Method（目标 1200-1500 词，v2 ~1150 词，2026-11-23 晚 W5 扩）

### 2.1 Task set

Ten tasks: 7 full-rank (Q01–Q07) and 3 rank-deficient (Q08–Q10). Domains: GPU systems (7), math (1), physics (1). Each task carries 4–5 checkpoints (47 total).

**Full-rank tasks** are self-contained: the prompt provides all information needed to derive every checkpoint's gold value. Gold values are derived symbolically (SymPy 1.14.0) from the prompt's given quantities, or anchored to public datasheets (NVIDIA H100/H200 specs). Checkpoint types: `calc` (numeric, tolerance 2% or exact-integer), `fact` (numeric or textual, datasheet-anchored), `bool` (spec-driven keyword/forbidden-pattern). A representative example (Q01): a 32B FP8 model served on a single H100 SXM (80 GB HBM3, 3.35 TB/s) at batch 16 and context 12288 — five checkpoints form a dependency chain: c1 the H100 datasheet TDP (700 W), c2 the KV-cache bytes per token (64·8·128·2, tolerance 2%), c3 the bytes moved per decode step (weights + batch·ctx·kv_per_token, depends on c2), c4 the aggregate decode throughput at 85% of HBM bandwidth (depends on c3), c5 the joules per generated token (depends on c1 + c4). The chain makes the task internally consistent: each downstream checkpoint is only derivable if the upstream one is correct, which gives the mechanical judge a non-trivial dependency structure to check.

**Rank-deficient tasks** deliberately withhold information: Q08 omits the per-GPU HBM capacity (the model must either commit to a value from memory or flag the gap); Q09's retrieved spec excerpt is missing a row the question requires; Q10 presents two contradictory sources (vendor datasheet 3.35 TB/s vs blog 2.0 TB/s). These probe whether the model *knows what it doesn't know* — the rank-deficient axis. The prompt constrains the allowed source ("the only source you are allowed to use is this retrieved spec excerpt"), so supplementing with external facts is a scored violation, not a recovery. The correct behavior on a rank-deficient task is a two-part answer: (i) name the missing quantity (textual-gold checkpoint), and (ii) still compute the quantities that are derivable from the given information (calc checkpoints). This design makes the rank-deficient tasks a calibration probe: a model that fabricates the missing value fails the textual checkpoint; a model that refuses to compute anything fails the calc checkpoints; only a model that separates "what I know" from "what I don't" passes both.

**Task construction and gold verification.** Every gold value is derived by a SymPy expression at construction time and self-checked (the expression must evaluate to the stated gold within tolerance before the task is accepted). This makes the mechanical reference exact by construction: there is no human annotation step, no tolerance negotiation, and no "close enough" judgment. The full gold-derivation trace for all 47 checkpoints is in Appendix A.

### 2.2 Judges

**Mechanical judge.** Each checkpoint is evaluated deterministically:
- `calc` (tol > 0): SymPy evaluates the gold expression; the model's extracted value passes iff |v−g|/|g| < tol.
- `calc` (tol = 0, integer): exact match after SymPy evaluation.
- `fact` (numeric): same as calc with the fact's tolerance.
- `fact` (textual): spec-driven keyword match.
- `bool`: spec-driven `keywords` (any present → pass) and `forbidden_numbers`/`forbidden_patterns` (any present → fail). Supports "pass-by-absence" checkpoints (e.g., "must not output tok/s").

The mechanical judge is exact by construction: its only failure mode is a bug in the spec, which is caught by a SymPy self-check at task-construction time (Appendix A). One scope caveat, reported separately throughout: on the rank-deficient *textual-gold* checkpoints (naming a missing quantity), the mechanical reference is a regex heuristic, not an exact symbolic check. We flag every result that depends on this heuristic (F3 scope note) and show that the core coin-flip claim rests on the calc-gold checkpoints, where the reference is exact.

**LLM judge.** A 27b model (Qwen3-27B, local vLLM deployment, temperature 0) is prompted to judge each checkpoint and emit a JSON verdict `{"c1": true/false, ...}`. The judge is the same model family as the model being evaluated (27b judging 27b), which is the realistic deployment configuration for a cost-constrained evaluation pipeline and makes the result directly applicable to that setting. Three prompt variants:
- **V1_strict**: "You are a strict numeric grader. Judge each checkpoint right/wrong. tolerance=0.02 checkpoints: within 2% of gold = right; tolerance=0 (integer): must equal gold exactly, off-by-one = wrong. Output JSON only: {\"checkpoint_id\": true/false}. No explanation."
- **V2_loose**: relaxed tolerance phrasing + "be lenient on rounding".
- **V3_engineer**: structured engineering rubric + "show your check before the JSON".

The three variants span the prompt-design space a practitioner would realistically use: a strict contract (V1), a lenient phrasing (V2), and a structured rubric that asks the judge to show its work (V3). The variant is the only thing that changes between the three measurement arms; the model, temperature, and task set are held fixed.

Default `max_tokens=500` (the deployment default; the truncation mechanism in F2 is measured at this budget). The choice is deliberate: 500 is a common production default for judge calls (it bounds cost and latency), and the truncation mechanism we measure is precisely the failure mode that this budget induces.

### 2.3 Measurement protocol

- **Format reliability** = fraction of judge calls emitting unparseable output (no valid JSON verdict object).
- **Flip rate** = on parseable calls, fraction of checkpoints where LLM verdict ≠ mechanical verdict.
- **Mechanism attribution**: (i) max_tokens 500→2000 re-judging of failure cases (truncation recovery rate); (ii) engine `finish_reason` and `completion_tokens` (direct truncation evidence); (iii) partial correlation of input length vs failure controlling for output length (independent complexity effect); (iv) within-checkpoint-count stratification (gold-complexity vs checkpoint-count attribution).
- **Guessing bound**: explicit random-guess model (continuous: U[0.5g, 2g], hit prob 2·tol/1.5; integer: U[g±50], hit prob 1/101; textual: 1/100 conservative), analytic product bound + Monte Carlo (N=2000, seed=42).
- **Three-arm behavioral experiment** (rank-deficient only, n=10/arm): A_baseline (no reminder), B_remind (commitment reminder), B'_remind (commitment + conditional-enumeration inducement). c3 scored under two criteria: strict (commit to a single value; conditional enumeration = miss) and lenient (hedging-word exemption per sentence window).

### 2.4 Deployment

27b model served via vLLM at a local endpoint; no weight updates. All judge calls at temperature 0. Task construction and gold verification use SymPy 1.14.0; the full gold-derivation trace is in Appendix A. The judge and the evaluated model run on the same deployment, so the measurement is a within-system comparison: the only difference between the two "judges" is the verifier (mechanical vs LLM), not the model or the serving stack.
