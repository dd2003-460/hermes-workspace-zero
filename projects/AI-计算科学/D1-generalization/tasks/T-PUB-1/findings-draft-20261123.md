# §4 Findings 初稿（T-PUB-1, ICML 2027）
# origin: ai · 2026-11-23 · W1 交付
# 数据源: tasks/T-PUB-1/paper-data-table-20261123.md（全部数字可回溯）
# 状态: 初稿，逻辑 + 数字就位，待 W2 扩写论证 + W5 补 CI

## Table 1. Main results (formalizable core, n=67 outputs × 3 judge variants)

| Judge | Format failure (Wilson 95% CI) | Verdict flip vs mechanical (CI) | Parseable n |
|---|---|---|---|
| V1 strict | 77.6% (52/67, [66,86]) | 51.7% (31/60, [39,64]) | 15 |
| V2 loose | 83.6% (56/67, [73,91]) | 47.7% (21/44, [34,62]) | 11 |
| V3 engineer | 52.2% (35/67, [40,64]) | 51.6% (66/128, [43,60]) | 32 |
| Mechanical | 0% (0/67) | 0% (by construction) | 67 |

Flip denominator = parseable checkpoints where both judges rendered a verdict.

## F1. LLM judges fail format reliability on the formalizable core

We measure format reliability as the rate at which an LLM judge emits unparseable output on inputs where a mechanical judge succeeds by construction. On 67 real 27b outputs across 10 tasks (7 full-rank, 3 rank-deficient), three prompt variants (V1_strict, V2_loose, V3_engineer) yield format failure rates of 77.6% (52/67, Wilson 95% CI [0.663, 0.859]), 83.6% (56/67, CI [0.729, 0.906]), and 52.2% (35/67, CI [0.405, 0.637]) respectively. The mechanical judge, which evaluates each checkpoint by SymPy symbolic comparison or spec-driven regex, fails on 0/67 (0%) by construction.

The failure is not a smooth function of output length; it is **confounded with task type**. Full-rank tasks (Q01–Q07, complex symbolic gold) fail 7/7 across the full length range (385–7210 chars) — including the shortest output in the set (Q07, 385 chars). Rank-deficient tasks (Q08–Q10, where the model often emits a short "flag the gap" response) fail 45/60, with a genuine length effect *within* the group: Q09's nine 435-char outputs all parse, while its 1707–1848-char outputs mostly fail. An apparent "604-char threshold" in the pooled data is an artifact of this task-type confound (the two task types happen to occupy different length bands), not a hard length boundary. The mechanism is content-driven, not length-driven: complex gold values force the judge into a long reasoning chain that exhausts the token budget (F2), while short gap-flagging responses let the judge emit a verdict quickly.

**Claim.** No prompt phrasing brings a 27b LLM judge to usable format reliability on the formalizable core: even the best variant (V3) fails 52% of the time, versus 0% for the mechanical judge.

## F2. Mechanism attribution: a single causal chain — input complexity → reasoning chain → token exhaustion → JSON truncation

We attribute format failures with a controlled re-judging probe (max_tokens 500→2000) plus engine `finish_reason` and output-tail inspection. The probe (v2, 6 V1 failure cases) shows the mechanism is **not** attention degradation (which would make verdicts more *wrong*) but **token-budget exhaustion by the reasoning chain**.

**The causal chain (unified).** All six mt500 failure cases report `finish_reason=length`, and the output tail in every case is *reasoning text* — the JSON verdict never begins. At mt2000 the recovered cases (Q01/Q02/Q06) emit a long reasoning chain followed by clean JSON (raw_len 63–78 for the JSON alone); the model is reasoning *correctly*, just spending its budget on the chain before it can emit the verdict. This unifies what we previously reported as two separate factors ("truncation" and "input complexity") into one causal chain: **input complexity → longer reasoning chain → collision with max_tokens → JSON truncated**. Input complexity is not an independent additive factor; it is the *upstream driver* of the reasoning-chain length that causes truncation.

**Two sub-mechanisms within the chain.** The mt2000 re-judge plus the determinism probe (5 reps) separate the failure cases into three behavior classes:
- **Truncation-recoverable (Q01/Q02/Q06).** Reasoning is correct and converges; raising max_tokens recovers the JSON (Q01: 5/5 at mt2000). The dominant class.
- **Convergence failure (Q03/Q05).** Even at mt2000 the model fails deterministically (Q03: 0/5, all `finish_reason=length` at ~3160 chars): the output tail shows *cycling* — re-deriving the same quantity repeatedly ("258048 × 16384. 258048 × 16000 = …; 258048 × 384 = …"), re-interpreting which checkpoint c5 maps to. More tokens do not help. This is the precise sense in which "input complexity" matters: not attention dilution, but **reasoning non-convergence** on hard gold values.
- **Borderline / instruction-following flip (Q04).** At mt2000 the same input flips run-to-run at temperature 0 (3/5 parseable): passing runs emit a 74-char pure JSON, failing runs emit 2600+ char cycling chains. Q04 is neither cleanly recoverable nor cleanly non-convergent — it samples between the two modes.

**Superseded claim.** An earlier version of this finding (based on a v1 probe that recovered 5/6) reported "input complexity as an independent factor, partial r=0.436." The v2 probe supersedes this: the partial correlation captured the convergence-failure sub-mechanism, not an independent attention effect. (An earlier F1 claim of a "604-char threshold" was likewise superseded — see F1: it is a task-type confound, not a length boundary.)

**Open verification (run-to-run determinism) — resolved.** A determinism probe (same input × 5 reps, same run, same mt, temperature 0; /tmp/judge_determinism.json) shows the judge is **deterministic on easy cases but non-deterministic on hard ones**:
- Q01 (easy) at mt2000: 5/5 parseable (deterministic recovery); at mt500: 0/5 (deterministic truncation).
- Q03 (hard) at mt2000: 0/5 parseable, all `finish_reason=length` at ~3160 chars (deterministic convergence failure — the model cycles and never emits JSON even with full budget).
- **Q04 (borderline) at mt2000: 3/5 parseable — a run-to-run flip at temperature 0.** The 3 passing runs emit a 74-char pure JSON (no reasoning chain); the 2 failing runs emit 2600+ char cycling reasoning chains. Same input, same mt, same run.

The flip is in **whether the model obeys the "output JSON only, no explanation" instruction**: obeying → short output → parseable; disobeying → long reasoning chain → truncation (at mt500) or cycling (at mt2000). This re-frames the causal chain: the root cause is **instruction-following non-determinism at temperature 0**, and input complexity determines the *severity* once a chain is written (short chain → recoverable by raising mt; long/cycling chain → not recoverable). The v1/v2 probe discrepancy on Q04 is now explained: v1 sampled the "short JSON" mode, v2 sampled the "long chain" mode — not a server-state artifact.

**Implication for F1 rates.** The 52–84% failure rates are single-run point estimates. On borderline cases the parseable rate has run-to-run variance (Q04: 3/5 = 60% ± a wide CI at n=5), so the true failure rate on such cases is a distribution, not a number. This *strengthens* the paper's claim: the LLM judge's format reliability is not merely low, it is **unstable** — the same input at the same temperature flips between parseable and unparseable. A mechanical judge has no such variance by construction.

**Table 2. Mechanism probe (v2): 6 V1 failure cases re-judged at max_tokens 500 vs 2000.**

| Case | mt500: finish / chars / parse | mt2000: finish / chars / parse | Behavior class |
|---|---|---|---|
| Q01 | length / 650 / ✗ | stop / 74 / ✓ | recoverable |
| Q02 | length / 619 / ✗ | stop / 74 / ✓ | recoverable |
| Q03 | length / 654 / ✗ | length / 3167 / ✗ | convergence failure |
| Q04 | length / 681 / ✗ | length / 2602 / ✗ | borderline (flip) |
| Q05 | length / 698 / ✗ | length / 3212 / ✗ | convergence failure |
| Q06 | length / 673 / ✗ | stop / 63 / ✓ | recoverable |

All six mt500 cases hit `finish_reason=length` (token budget exhausted before the JSON verdict begins). The three mt2000 recoveries (Q01/Q02/Q06) emit short pure-JSON (63–74 chars); the three non-recoveries (Q03/Q04/Q05) emit 2600–3200-char reasoning chains. Recovery is determined by whether the reasoning chain converges, not by max_tokens itself.

## F3. Even when parseable, LLM judge verdicts flip at chance rate

On the parseable subset, we measure the flip rate: the fraction of checkpoints where the LLM judge's verdict disagrees with the mechanical judge. V1: 31/60 (51.7%, Wilson 95% CI [0.393, 0.638]), V2: 21/44 (47.7%, CI [0.338, 0.621]), V3: 66/128 (51.6%, CI [0.430, 0.600]). All three variants flip at ≈50% — indistinguishable from a coin flip: exact two-sided binomial test against p=0.5 gives p=0.90 (V1), p=0.79 (V3); every CI contains 0.5. The parseable subset is small (15/11/32 calls) because format failure (F1) dominates; the flip rate is measured on what survives.

**Scope of the reference.** The mechanical reference is exact on calc checkpoints (SymPy symbolic comparison) but is a spec-driven regex heuristic on the textual-gold checkpoints of the rank-deficient tasks (c2: "names the missing quantity correctly"), where it scores 0/60. On those checkpoints the flip direction skews toward LLM-correct / mechanical-false-negative, so we report them separately: excluding the rank-deficient c2 textual-gold checkpoints, the flip rate is V1 27/45 (60.0%), V2 17/33 (51.5%), V3 45/96 (46.9%) — still ≈50% on every variant. The coin-flip claim therefore rests on the calc-gold checkpoints, where the reference is exact.

**Claim.** Format reliability and verdict accuracy are distinct failure modes, and both fail: the LLM judge is unreliable both in *emitting* a verdict (F1) and in the *content* of the verdict it does emit (F3). The mechanical judge is exact on calc checkpoints by construction (0/67 format failures, symbolic gold); on textual-gold checkpoints it is a heuristic reference and is reported as such.

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
