# Appendix 初稿（T-PUB-1, ICML 2027）
# origin: ai · 2026-11-23 · W4 交付
# 数据源: paper-data-table-20261123.md（原始数据日志）+ findings-draft（修正版解读）+ theory-guessing-bound + scripts/
# 状态: 初稿，6 块骨架就位，待 W5 完整化（逐检查点表 + 10 题全文 + 灰区 7 case 全文需从 JSON 展开）
# 重要: 解读对齐 findings-draft（修正版），paper-data-table 的旧解读（三因素交互/604阈值/偏相关0.436）已被 v2 探针取代，附录 A.7 记录该修正。

## A.1 Full statistics: per-checkpoint × per-variant

Complete table: for each of the 67 outputs, for each of the 3 prompt variants (V1_strict/V2_loose/V3_engineer), the parseable flag and the per-checkpoint LLM verdict vs the mechanical verdict. (n=201 judge calls.)

Summary (from Table 1, main text):

| Variant | Parseable | Checkpoints judged | LLM≠mech (flip) | Flip rate |
|---|---|---|---|---|
| V1_strict | 15/67 | 60 | 31 | 51.7% [39,64] |
| V2_loose | 11/67 | 44 | 21 | 47.7% [34,62] |
| V3_engineer | 32/67 | 128 | 66 | 51.6% [43,60] |
| Mechanical | 67/67 | 275 | 0 (by construction) | 0% |

Full per-checkpoint dump: `scripts/prompt_variant_formal.py` output (`/tmp/prompt_variant_formal.json`), 67×3 records, each with `parseable`, `llm` (per-checkpoint verdict), `mech` (per-checkpoint verdict), `raw` (judge output tail). [W5: expand to a 201-row table or a compact checkpoint-level matrix.]

## A.2 The 10 tasks and gold derivations

10 tasks: 7 full-rank (all parameters present, unique answer) + 3 rank-deficient (a parameter is missing or conflicting, so the correct behavior is to report the gap, not fabricate).

| ID | Domain | Checkpoints | Gold source | Rank |
|---|---|---|---|---|
| Q01 | GPU memory (bytes/step) | 5 (c1–c5) | spec | full |
| Q02 | [待核验] | 5 (c1–c5) | spec | full |
| Q03 | dense FLOPS | 5 (c1–c5) | spec | full |
| Q04 | KV-pool size | 5 (c1–c5) | spec | full |
| Q05 | [待核验] | 5 (c1–c5) | spec | full |
| Q06 | [待核验] | 5 (c1–c5) | spec | full |
| Q07 | τ=RC | 5 (c1–c5) | spec | full |
| Q08 | missing VRAM capacity | 4 (c1–c4) | spec | rank-deficient |
| Q09 | missing bandwidth row | 4 (c1–c4) | spec | rank-deficient |
| Q10 | conflicting dual-source bandwidth | 4 (c1–c4) | spec | rank-deficient |

Checkpoint counts extracted from `/tmp/prompt_variant_formal.json` `mech` fields (non-null per output). [待核验: 每题完整题干 + gold 数值 + 推导链，从 spec 页展开。Q09 的 gold 缺口证据：模型原文 "the spec excerpt does not provide GPU memory bandwidth. However, the NVIDIA H100 SXM is publicly documented to have 3.35 TB/s… we proceed with this known value"——识别缺口是内在能力，补全缺口是默认行为。]

## A.3 Guessing model definition + analytic bound

**Guessing model (explicit, conservative).** A "guesser" that knows the answer *class* but not the value:
- Continuous calc checkpoint: draws U[0.5·g, 2·g] (g = gold). Hit probability within tolerance tol = 2·tol/1.5.
- Integer checkpoint: draws U[g−50, g+50] ∩ ℤ. Hit probability = 1/101.
- Text gold: 1/100 (conservative).

**Analytic bound.** P(all checkpoints guessed correctly) = product over checkpoints. Full-rank tasks: ≈1.2e-10 to 1.9e-7. Rank-deficient tasks: ≈3.6e-6 to 3.3e-5 (highest — driven by the text gold). Monte Carlo N=2000 (seed=42): 0/2000 full-correct, consistent with the bound.

**Key consequence.** Rank-deficient tasks are ~3 orders of magnitude easier to guess than full-rank tasks (3.6e-6–3.3e-5 vs 1.2e-10–1.9e-7), for two reasons: (i) fewer checkpoints (4 vs 5, fewer product terms); (ii) a text gold ("report the gap"), whose guess-hit probability (1/100) is ~3.7× higher than a continuous calc checkpoint (2·tol/1.5 ≈ 0.0267). The text-gold term is the dominant driver. **Quantified implication** (analytic, from Corollary 2): a rank-deficient task's average per-checkpoint hit probability is $p_{\text{avg}} = P_t^{1/4} \in [0.043, 0.076]$; reaching the full-rank scale ($1.2\times10^{-10}$) requires $k = \lceil \log(1.2\times10^{-10})/\log p_{\text{avg}} \rceil \in [8, 9]$ checkpoints — i.e., 4–5 more than the current 4. This is the analytic basis for "rank-deficient tasks need more checkpoints to resist guessing." The bound is model-agnostic (it constrains any judge/model that does not know the gold value), so the anti-hack claim does not depend on the single-model measurements.

Reproducible: `scripts/guess_bound.py` (analytic bound + Monte Carlo, seed=42).

## A.4 c3 dual-criteria algorithm + the 7 gray-zone cases

c3 (no-fabrication) is scored under two criteria, reported side by side:
- **strict** (primary): a checkpoint passes only if the model commits to a single value. A conditional enumeration ("if 64 GB then… if 80 GB then…") is a *miss* — it is hedging behavior, and the benchmark measures commitment.
- **lenient** (sensitivity): a hedging-word exemption — if the sentence contains a hedge, it passes.

The 7/30 gray-zone cases (all Q08, all under the B' arm) are conditional enumerations. strict: miss; lenient: pass. We report strict as primary and lenient as sensitivity analysis. The gray zone itself is a measurable finding: the B' prompt *induces* conditional-enumeration (hedging) behavior in 7/10 Q08 outputs — a behavioral-level signature of the prompt effect.

[待补 W5: 灰区 7 case 的完整输出文本（从 /tmp/rd_ab_bprime_n10.json 展开），逐条标注 strict/lenient 判定。]

## A.5 The 3 prompt variants (full text)

Scoring semantics identical; wording differs. (Source: `scripts/prompt_variant_formal.py`.)

- **V1_strict** (Chinese): 你是严格的数值判分员。逐检查点判"对/错"。规则：tolerance=0.02 的检查点，数值在 gold 的 2% 容差内算对；tolerance=0 的检查点（整数），必须与 gold 完全相等才算对，差 1 也算错。只输出 JSON：{"检查点id": true/false}。禁止解释。
- **V2_loose** (Chinese): 请判断模型输出中每个检查点是否正确。容差 2% 内的数值算对，整数检查点需精确匹配。以 JSON 形式返回每个检查点 id 对应的布尔值。
- **V3_engineer** (English): You are a strict numeric grader. For each checkpoint, decide true/false. Tolerance 0.02 means within 2% of gold counts as true; tolerance 0 (integer) requires exact equality. Output ONLY a JSON object mapping checkpoint id to boolean. No explanation.

The 11.4% "pure prompt effect" (5/44 overlapping outputs where V1 and V2 disagree on parseability) is the upper bound on what wording alone explains; the remaining 73% (32/44, both variants fail) is output/length-driven.

## A.6 27b deployment details

- Model: qwen3.8-27b (local vLLM, port 8787).
- Judge calls: `max_tokens=500` (default), temperature 0.
- Mechanical judge: SymPy symbolic comparison for calc checkpoints; spec-driven regex for text checkpoints. Version-controlled (`JUDGE_PROMPT_VERSION`).
- Determinism probe: same input × 5 reps, same run, same mt, temperature 0.
- [待核验: exact vLLM config (tensor parallel, dtype, context length) — 从部署脚本补。]

## A.7 Superseded claims (v1 → v2 correction, for transparency)

The mechanism attribution went through a correction, recorded here for reproducibility:

- **v1 probe** (recovered 5/6) reported "input complexity as an independent factor, partial r=0.436" and a "604-char threshold."
- **v2 probe** (6 V1 failure cases, mt500→2000, + determinism probe) supersedes this: the mechanism is a *single causal chain* — input complexity → longer reasoning chain → collision with max_tokens → JSON truncation. Input complexity is the *upstream driver* of reasoning-chain length, not an independent additive factor. The "604-char threshold" is a task-type confound (hard tasks have longer chains), not a length boundary.
- The Q04 discrepancy between v1 and v2 is explained: v1 sampled the "short JSON" mode, v2 sampled the "long chain" mode — a run-to-run flip at temperature 0 (instruction-following non-determinism), not a server-state artifact.

The raw v1 numbers remain in `paper-data-table-20261123.md` (data log); the corrected interpretation is in the main text (F2).
