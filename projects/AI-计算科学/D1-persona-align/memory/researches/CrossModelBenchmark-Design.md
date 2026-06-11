# Cross-Model Persona-V3 Benchmarking Design

**Phase**: planner
**Task**: A2 — Cross-model benchmark (GPT/Claude/Qwen) for persona alignment
**Date**: 2026-06-03
**Version**: v1.0

---

## 1. Objective

Evaluate whether persona-v3 alignment transfers across models. The core hypothesis is that a persona prompt works by priming model behavior through explicit conceptual anchors. Different model architectures have varying receptive fields for those anchors. This benchmark measures the transfer function:

$$\alpha(M, P) = \text{alignment}(M, P, \text{task})$$

where M = model, P = persona-v3 prompt, task = specific reasoning challenge, and alignment is quantified by the alignment_checker (6 dimensions + ReportBench + behavioral constraints).

---

## 2. Candidate Models

| Model | Provider | Context Window | Notes |
|-------|----------|---------------|-------|
| GPT-4o | OpenAI API | 128K | Best available GPT for persona tasks |
| Claude Sonnet (Opus for gold) | Anthropic API | 200K | Strong instruction following, possibly better for persona |
| Qwen3 / Qwen-Max | Alibaba / Aliyun Bailian | 128K | Strong Chinese, open-weights |
| (optional) Llama 3.1 70B | HuggingFace / self-host | 128K | Fully local evaluation possible |

**Priority**: GPT-4o > Claude > Qwen (standard coverage). Llama only if local testing needed.

**API requirement**: All three require API keys. Currently unknown if keys are available in environment.

---

## 3. Representative Persona File Selection

From 52 idea files in `memory/`, select 8 files covering:
- **Quality spectrum** (well-constructed to poor)
- **Domain diversity** (AI, social, abstract, concrete)
- **Persona-dimension richness** (activate many vs few dimensions)

### Selected Files (8 representatives)

| # | File | Quality | Domain | Primary Persona Dimensions Activated | Selection Rationale |
|---|------|---------|--------|-------------------------------------|-------------------|
| 1 | `idea-01-ai训练数据是否是层级化的-粗到细-rag外挂呢-以及内部检.md` | Excellent | AI/data theory | 精度, 探索, 感知, 自我, 投影 + 贝叶斯 + 跨域 | Most complete analysis. Shows rate-distortion, information theory, cross-domain analogies (CNN, cortex, cache). |
| 2 | `idea-07-cot-redundancy-information-theory.md` | Good | Theory | 精度, 探索, 先验 | Core theory — relevant to benchmark target. |
| 3 | `idea-04-如果让你当agent-例如coding和启动本地clicod.md` | Poor (stub) | Agent/task | (weak) | Worst-case test: minimal persona depth, mostly stubs. |
| 4 | `idea-102-self-centered-law-derivation.md` | Unknown | Philosophy | 自我, 先验, 投影 | "Self" dimension test. |
| 5 | `idea-09-安全-长期守则-硬编码不被压缩和遗忘.md` | Unknown | Safety/memorability | 探索, 先验, 精度 | Domain diversity: AI safety & self-preservation. |
| 6 | `idea-20-adaptive-token-information-density.md` | Good | AI/technical | 精度, 探索 | Core concept directly related to adaptive precision. |
| 7 | `idea-08-小说idea-ai视角下的诞生与进化-主要从长记忆开始因为有.md` | Unknown | Narrative/AI | 投影, 自我 | Cross-domain/creative reasoning test. |
| 8 | `idea-32-homology-groups-geometric-intuition.md` | Unknown | Math/topology | 投影, 精度 | Math rigor test — high projection demand. |

**Selection methodology**: First rank files by persona dimension keyword density (using the alignment checker). Then cluster by domain. Pick best representative per cluster. The final set ensures at least 2 high-quality, 2 medium-quality, and 2-4 low-quality files, plus domain diversity across AI theory, social science, mathematics, and creative reasoning.

---

## 4. Evaluation Methodology

### 4.1 Standardized Prompt Assembly

For each selected file, construct a unified prompt:

```
=== persona-v3 Prompt ===
{persona-v3-prompt.txt full text}

=== Task ===
Based on the following original thought/question, produce a detailed analysis
using the persona-v3 framework. Apply all 6 adaptive dimensions, use
cross-domain analogies, Bayesian reasoning, and the iterative追问 mechanism.

=== Original Input ===
{extracted "原始表述" section from the idea file}

=== Requirements ===
1. Apply persona-v3 adaptive framework (6 dimensions)
2. Include at least one cross-domain analogy
3. Include Bayesian analysis
4. Include iterative追问 (gap detection + follow-up questions + self-answer)
5. Be specific with concrete examples and evidence
```

**Baseline prompt**: Remove all persona-v3 scaffolding — provide ONLY the original input. This establishes the "without persona" baseline.

### 4.2 Response Generation

For each of the 8 selected files:
- Generate responses from each model (GPT-4o, Claude, Qwen) using the standardised prompt above.
- Use the SAME temperature and settings across models (recommend temperature=0.7, max_tokens=4096).
- Store all responses in `responses/cross_model_benchmark/<model>/` with consistent filenames.
- Also generate responses from a baseline prompt (no persona) for comparison.

### 4.3 Alignment Evaluation

Run the alignment checker on every generated response:

```bash
python3 scripts/persona_v3_alignment_checker.py \
    <response_file> \
    --json \
    --baseline <baseline_file_without_persona>  # optional drift detection
```

**Metrics collected per response:**
1. **Overall alignment score** (0-100) from alignment_checker
2. **Per-dimension scores**: adaptive_precision, adaptive_exploration, adaptive_perception, adaptive_prior, adaptive_self, adaptive_projection
3. **ReportBench metrics**: citation_relevance, factual_faithfulness
4. **Verification pattern coverage**: which of 33 patterns matched
5. **Behavioral constraint compliance**: concise/direct, no over-explanation, progress-oriented
6. **General info theory coverage**
7. **Persona drift** (vs baseline without persona)

### 4.4 Additional Evaluation Dimensions (beyond alignment_checker)

The alignment_checker primarily uses **keyword matching**, which is a known limitation (the evaluation base already notes "关键词匹配假阴性"). Supplement with:

**Human-labeled sanity check (20% sample):** Manually evaluate 2 of 8 files (~16 responses) for:
- Semantic coherence with persona intent (not just keyword presence)
- Quality of cross-domain analogies
- Quality of iterative追问
- Correct use of Bayesian reasoning

**Direct prompt evaluation:** Also evaluate the persona-v3 prompt itself:
```bash
python3 scripts/unified_eval.py --prompt --semantic
```

### 4.5 Comparative Framework

All results are compared along these axes:

| Comparison | Question | Metric |
|------------|----------|--------|
| M1 vs M2 | Model difference | $\Delta \alpha = \alpha(M1) - \alpha(M2)$ |
| P_quality | Prompt quality sensitivity | $\alpha$ vs input quality rank |
| Model vs Baseline | Persona added value | $\alpha(M) - \alpha(M, \text{no persona})$ |
| Dimension profile | Which dimensions vary by model | Per-dimension delta |
| Behavioral compliance | Which models best match behavioral constraints | Behavioral score |

---

## 5. Success Criteria

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| All 3 models score $\geq$ 50 on overall alignment | Yes | Above the 52-file evaluation baseline (avg 0.9741 keyword, ~50 semantic) |
| Consistency across models (stddev of model scores) $\leq$ 10 points | Yes | Tests generalizability of persona prompt |
| Persona prompt adds $\geq$ 15 points over baseline (no persona) | Yes | Demonstrates persona effectiveness |
| At least 4 of 6 dimensions score $>$ 0.3 for top model | Yes | Tests multi-dimensional coverage |
| Best model beats persona-v3 prompt own score by $\geq$ 5 points | Optional | Tests if model+persona > prompt alone |

**Accept/Reject**: If two models score below threshold but one passes, the failure is likely model-specific (not prompt-specific). If all three fail, the prompt needs revision.

---

## 6. Practical Constraints

### API Access
- **GPT-4o**: Requires OpenAI API key with GPT-4o model access
- **Claude Sonnet**: Requires Anthropic API key
- **Qwen3/Qwen-Max**: Requires Aliyun Bailian API or local model deployment

If no API keys are available, local open-weight models (Llama 3.1 70B, Mixtral) are the fallback, but local deployment requires sufficient GPU memory (~140GB for 70B at FP16) or quantized inference (~35-40GB for 4-bit Qwen3 72B).

### SSL/MITM Block
MITM SSL interception blocks pip package installation (see TASKS.md). Workaround: use existing virtualenv or system packages.

### Output Storage
Each model generates 8 responses + 8 baseline responses = 16 files per model. 3 models = 48 response files. ~50-200KB each = 2.4-9.6 MB total. Plan to store in `responses/cross_model_benchmark/`.

### Cost Estimates
| Model | Per response | 8 responses |
|-------|-------------|-------------|
| GPT-4o | ~$0.03 | ~$0.24 |
| Claude Sonnet | ~$0.01 | ~$0.08 |
| Qwen-Max | ~$0.005 | ~$0.04 |

Total estimated cost: <$1.00

---

## 7. Execution Plan

### Phase 1: File Selection and Verification (30 min)
1. Use alignment_checker on all 52 files to rank by dimension coverage and keyword density
2. Cluster files by domain (AI, social, math, creative, etc.)
3. Finalize 8-file selection, verify format, extract "原始表述" sections

### Phase 2: Prompt Assembly (30 min)
1. Create standardized prompt template using persona-v3-prompt.txt
2. Create baseline prompt (no persona)
3. Generate full prompts for all 8 files × 2 prompt types = 16 prompts

### Phase 3: Response Generation (1-2 hours, mostly network latency)
1. Call each model's API with all 16 prompts
2. Save responses to disk immediately
3. Monitor for failures/API rate limits

### Phase 4: Evaluation (30 min)
1. Run alignment_checker on all 48 responses + 16 baselines = 64 files
2. Collect JSON output for all
3. Compute per-model aggregate statistics

### Phase 5: Analysis and Reporting (1 hour)
1. Cross-model comparison tables and charts
2. Identify best model for persona tasks
3. Identify which dimensions are most sensitive to model choice
4. Produce recommendations for prompt refinement

---

## 8. Artifact Ownership

| Artifact | Location | Owner |
|----------|----------|-------|
| Selection criteria | This document (Section 3) | planner |
| Standardized prompts | `scripts/gen_cross_model_prompts.py` | executor |
| Responses | `responses/cross_model_benchmark/` | executor |
| Evaluation results | `eval_results/cross_model_benchmark/` | executor |
| Final report | `researches/CrossModelBenchmark-Results.md` | verifier |
| Script for automated generation | `scripts/cross_model_benchmark.py` | executor |

---

## 9. Next Steps

1. **Confirm API key availability** — check `.env` files and keychain for OpenAI, Anthropic, and Aliyun credentials.
2. **Rank all 52 idea files** — run `persona_v3_alignment_checker.py --json --show-sources` on each file to get objective ranking.
3. **Build `gen_cross_model_prompts.py`** — automate prompt assembly from template + idea file content.
4. **Build `cross_model_benchmark.py`** — end-to-end orchestration (generate responses, evaluate, aggregate).
5. **Execute benchmark** — once API access confirmed and scripts are built.

---

*Design approved by planner. Ready for executor implementation.*
