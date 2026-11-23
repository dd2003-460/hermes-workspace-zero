# §4 Findings 初稿（T-PUB-1, ICML 2027）
# origin: ai · 2026-11-23 · W1 交付
# 数据源: tasks/T-PUB-1/paper-data-table-20261123.md（全部数字可回溯）
# 状态: 初稿，逻辑 + 数字就位，待 W2 扩写论证 + W5 补 CI

## F1. LLM judges fail format reliability on the formalizable core

We measure format reliability as the rate at which an LLM judge emits unparseable output on inputs where a mechanical judge succeeds by construction. On 67 real 27b outputs across 10 tasks (7 full-rank, 3 rank-deficient), three prompt variants (V1_strict, V2_loose, V3_engineer) yield format failure rates of 77.6% (52/67), 83.6% (56/67), and 52.2% (35/67) respectively. The mechanical judge, which evaluates each checkpoint by SymPy symbolic comparison or spec-driven regex, fails on 0/67 (0%) by construction.

The failure rate is not uniform: it exhibits a threshold, not a gradient. Sorting outputs by length, the 10 shortest (385–604 chars) fail at 1/10 (10%) while the 57 longer (604–7210 chars) fail at 51/57 (89.5%). The 604-char threshold coincides with the point at which the model's reasoning chain collides with the default max_tokens=500 budget. This is a step function, inconsistent with a smooth attention-dilution mechanism and consistent with a hard truncation boundary.

**Claim.** No prompt phrasing brings a 27b LLM judge to usable format reliability on the formalizable core: even the best variant (V3) fails 52% of the time, versus 0% for the mechanical judge.

## F2. Mechanism attribution: truncation is the dominant driver, input complexity an independent factor, instruction-following a minority

We attribute format failures to three candidate mechanisms and separate them with controlled re-judging and partial correlation.

**Truncation (dominant, 83%).** Re-judging the six V1 failure cases with max_tokens raised from 500 to 2000 recovers 5/6 (83%): the model, given sufficient budget, emits clean JSON (raw_len 62–78 chars, no reasoning chain). Direct engine evidence: all six mt500 failure cases report `finish_reason=length` with `completion_tokens=500` — the vLLM engine itself reports the output was cut at the max_tokens ceiling. Truncation is not inferred; it is engine-reported.

**Input complexity (independent, partial r=0.436).** The raw correlation between input length (checkpoint count + gold complexity) and format failure is 0.483, stronger than output length's 0.273. Critically, the *partial* correlation controlling for output length remains 0.436 — input complexity has an effect independent of output truncation. Stratifying within the 4-checkpoint group (n=60): low gold-complexity outputs fail 65%, high-complexity 95%. The effect is driven by gold complexity (long formulas / textual gold), not checkpoint count (the 5-cp group, n=7, is too small to adjudicate). Residual ambiguity: the gold-complexity effect could be attention dilution (long formulas disperse attention) or task complexity (complex gold is harder to judge); both are functions of gold complexity and current data cannot separate them. A controlled experiment varying formula length at fixed complexity is a follow-up.

**Instruction-following (minority, 17%).** The single non-recovered case (Q03) emits a 3190-char reasoning chain even at max_tokens=2000 and never produces the requested JSON (`finish_reason=stop`, JSON absent). This is an instruction-following failure, independent of truncation.

**Claim.** Format failure = truncation (dominant, threshold-type) × input complexity (independent additive) × instruction-following (minority). A pure-attention-dilution account is ruled out by the threshold shape; a truncation-only account is ruled out by the partial correlation.

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

## 综合 claim（§4 收尾）

LLM judges are unreliable on the formalizable core along two independent dimensions — format reliability (52–84% failure, F1) and verdict accuracy (≈50% flip, F3) — and the dominant mechanism is output-length × max_tokens truncation interaction (F2), not prompt phrasing. The task set resists guessing (F4), and prompt modification trades dimensions (F5). The mechanical judge is exact on both dimensions by construction and is the appropriate default for the formalizable core.
