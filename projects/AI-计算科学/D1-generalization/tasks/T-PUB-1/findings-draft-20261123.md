# §4 Findings 初稿（T-PUB-1, ICML 2027）
# origin: ai · 2026-11-23 · W1 交付
# 数据源: tasks/T-PUB-1/paper-data-table-20261123.md（全部数字可回溯）
# 状态: 初稿，逻辑 + 数字就位，待 W2 扩写论证 + W5 补 CI

## F1. LLM judges fail format reliability on the formalizable core

We measure format reliability as the rate at which an LLM judge emits unparseable output on inputs where a mechanical judge succeeds by construction. On 67 real 27b outputs across 10 tasks (7 full-rank, 3 rank-deficient), three prompt variants (V1_strict, V2_loose, V3_engineer) yield format failure rates of 77.6% (52/67), 83.6% (56/67), and 52.2% (35/67) respectively. The mechanical judge, which evaluates each checkpoint by SymPy symbolic comparison or spec-driven regex, fails on 0/67 (0%) by construction.

The failure is not a smooth function of output length; it is **confounded with task type**. Full-rank tasks (Q01–Q07, complex symbolic gold) fail 7/7 across the full length range (385–7210 chars) — including the shortest output in the set (Q07, 385 chars). Rank-deficient tasks (Q08–Q10, where the model often emits a short "flag the gap" response) fail 45/60, with a genuine length effect *within* the group: Q09's nine 435-char outputs all parse, while its 1707–1848-char outputs mostly fail. An apparent "604-char threshold" in the pooled data is an artifact of this task-type confound (the two task types happen to occupy different length bands), not a hard length boundary. The mechanism is content-driven, not length-driven: complex gold values force the judge into a long reasoning chain that exhausts the token budget (F2), while short gap-flagging responses let the judge emit a verdict quickly.

**Claim.** No prompt phrasing brings a 27b LLM judge to usable format reliability on the formalizable core: even the best variant (V3) fails 52% of the time, versus 0% for the mechanical judge.

## F2. Mechanism attribution: a single causal chain — input complexity → reasoning chain → token exhaustion → JSON truncation

We attribute format failures with a controlled re-judging probe (max_tokens 500→2000) plus engine `finish_reason` and output-tail inspection. The probe (v2, 6 V1 failure cases) shows the mechanism is **not** attention degradation (which would make verdicts more *wrong*) but **token-budget exhaustion by the reasoning chain**.

**The causal chain (unified).** All six mt500 failure cases report `finish_reason=length`, and the output tail in every case is *reasoning text* — the JSON verdict never begins. At mt2000 the recovered cases (Q01/Q02/Q06) emit a long reasoning chain followed by clean JSON (raw_len 63–78 for the JSON alone); the model is reasoning *correctly*, just spending its budget on the chain before it can emit the verdict. This unifies what we previously reported as two separate factors ("truncation" and "input complexity") into one causal chain: **input complexity → longer reasoning chain → collision with max_tokens → JSON truncated**. Input complexity is not an independent additive factor; it is the *upstream driver* of the reasoning-chain length that causes truncation.

**Two sub-mechanisms within the chain.** The mt2000 re-judge separates the failure cases into two sub-mechanisms:
- **Truncation-recoverable (Q01/Q02/Q06, 3/6).** Reasoning is correct and converges; raising max_tokens recovers the JSON. This is the dominant sub-mechanism.
- **Convergence failure (Q03/Q04/Q05, 3/6).** Even at mt2000 the model fails: the output tail shows *cycling* — re-deriving the same quantity repeatedly ("258048 × 16384. 258048 × 16000 = …; 258048 × 384 = …"), re-interpreting which checkpoint c5 maps to ("but maybe c5 corresponds to … but according to the model's answer it wrote Compute…"). These are cases where the model *cannot converge* on a verdict — more tokens do not help. This is the precise sense in which "input complexity" matters: not attention dilution, but **reasoning non-convergence** on hard gold values.

**Superseded claim.** An earlier version of this finding (based on a v1 probe that recovered 5/6) reported "input complexity as an independent factor, partial r=0.436." The v2 probe supersedes this: the partial correlation captured the convergence-failure sub-mechanism, not an independent attention effect. The threshold shape (F1) is consistent with the unified chain: short outputs (simple gold → short reasoning chain) fit under max_tokens and pass; long outputs (complex gold → long chain) exceed it and truncate.

**Open verification (run-to-run determinism).** The v1 and v2 probes, run on the same 6 cases with the same prompt at temperature 0, disagree on Q04 (v1: recovered, pure JSON; v2: failed, long cycling reasoning). This indicates the judge is **not deterministic at temperature 0** — the same input produces qualitatively different outputs across runs. A determinism probe (same input × 5 reps, same run) is in progress; its result determines whether all format-reliability rates in F1 must be reported with a run-to-run variance interval. Until it resolves, the 52–84% failure rates (F1) and the sub-mechanism split (F2) carry a determinism caveat.

## F3. Even when parseable, LLM judge verdicts flip at chance rate

On the parseable subset, we measure the flip rate: the fraction of checkpoints where the LLM judge's verdict disagrees with the mechanical judge. V1: 31/60 (51.7%), V2: 21/44 (47.7%), V3: 66/128 (51.6%). All three variants flip at ≈50% — indistinguishable from a coin flip.

**Claim.** Format reliability and verdict accuracy are distinct failure modes, and both fail: the LLM judge is unreliable both in *emitting* a verdict (F1) and in the *content* of the verdict it does emit (F3). The mechanical judge is exact on both by construction.

## F4. Guessing bound: the task set is not guessable

To rule out that high scores are achievable by guessing, we define an explicit random-guess model and derive an analytic upper bound on the probability of guessing all checkpoints correct.

Guess model: continuous calc checkpoints (tol 2%) — guess U[0.5g, 2g], hit probability 2·tol/1.5; integer-exact checkpoints (tol 0) — guess U[g±50], hit probability 1/101; textual gold — hit probability 1/100 (conservative). The probability of guessing all checkpoints correct is the product over checkpoints (independent-guess assumption).

Analytic bound: full-rank tasks P(all-correct by guess) ≈ 1.2e-10 to 1.9e-7; rank-deficient tasks ≈ 3.6e-6 to 3.3e-5 (highest, fewer checkpoints + textual gold). Simulation (N=2000, seed=42): 0/2000 all-correct, consistent with the bound.

Rank-deficient tasks are guessable ~3 orders of magnitude more easily than full-rank — a quantitative basis for "rank-deficient tasks need more checkpoints to resist guessing." The bound is model-agnostic (it depends only on the guess model and checkpoint structure, not on the judge).

**Claim.** The task set resists guessing: even the most guessable task (rank-deficient) has P(all-correct by guess) ≤ 3.3e-5, so observed scores cannot be attributed to chance.

## F5. Prompt modification trades one dimension for another

Three-arm behavioral experiment on rank-deficient tasks (n=10/arm): A_baseline (no reminder), B_remind (commitment reminder), B'_remind (commitment + conditional-enumeration inducement).

| arm | c1 | c3 (strict) | c3 (lenient) | c4 |
|---|---|---|---|---|
| A_baseline | 10/30 (33%) | 25/30 (83%) | — | 30/30 (100%) |
| B_remind | 30/30 (100%) | 30/30 (100%) | — | 21/30 (70%) |
| B'_remind | 30/30 (100%) | 23/30 (77%) | 30/30 (100%) | 30/30 (100%) |

B' fixes c1 (33%→100%) but degrades c3-strict (100%→77%): 7/30 outputs (all Q08) are conditional enumerations ("if 64 GB then… if 80 GB then…") — strict scoring marks these as miss (no single committed value), lenient (hedging-word exemption) marks them pass. B fixes c3 but degrades c4 (100%→70%). No arm is 100% on all dimensions.

**Claim.** Prompt optimization is not free: modifying the prompt to improve one checkpoint dimension induces side effects on another. The gray zone (7/30) is itself a measurable finding — B's prompt induces conditional-enumeration (hedging) behavior, a behavioral-level signature of the prompt effect.

## 综合 claim（§4 收尾，2026-11-23 related work 调研后修正）

LLM judges fail on the formalizable core along two independent dimensions — format reliability (52–84% failure, F1) and verdict accuracy (≈50% flip, F3) — with the dominant mechanism being output-length × max_tokens truncation (F2), not prompt phrasing; the task set resists guessing (F4) and prompt modification trades dimensions (F5). These failure modes are known in the LLM-judge-reliability literature, but that literature relies on human annotation or perturbation tests as ground truth. Our contribution is not the discovery of unreliability but the *reference*: on the formalizable core a mechanical judge is an exact, free, reproducible ground truth, and against it we (i) isolate the failure mechanism (truncation vs input complexity vs instruction-following, F2), (ii) certify the task set against guessing (F4), and (iii) show prompt optimization is not free (F5). The mechanical judge is the appropriate default for the formalizable core; LLM judges remain for the non-formalizable residual (explanation quality, style).
