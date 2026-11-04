# 02 阶段字段快照

> 由 `ralph render` 自动从 `loop-artifacts/stages/02/r1/subfields-r290.json` 生成，请勿手改。

> 生成时间：2026-11-04 04:40

## 概览

- 字段总数：**8**
- 待办（pending / research_required）：**0**
- 分组：未分类×3、research_findings×1、cot_empirical_boundary×1、pseudo_thinking_detection_criteria×1、tts_knee_small_models×1、verify_benefit_small_models×1

## 字段明细

### 未分类

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| goal |  | confirmed |  |  |  |
| known |  | confirmed |  |  |  |
| unknown |  | confirmed |  |  |  |

### research_findings

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| research_findings | KB.1 第9篇『伪thinking vs 真推理』调研回填(差额=01 阶段 unknown 四项，全部带回 evidence_refs)：<br><br>① CoT 实证边界(哪些任务真受益/表演性步骤)：Wei et al. NeurIPS 2022 证明 CoT prompting 是规模涌现能力——<100B 模型上无正收益，小模型生成流畅但不合逻辑的步骤反而低于 standard prompting；PaLM 540B + 8 exemplar 在 GSM8K 达 58.1%。机制假设：CoT 把多步问题分解成中间步骤、为难题分配额外计算。<br><br>② 伪thinking 可检测判据：两条独立证据线。(a) In The Wild Not Always Faithful (2025)：真实 prompt 上 implicit post-hoc rationalization——同题正反问法系统性 Yes/Yes 或 No/No 且都配流畅论证；生产模型率 GPT-4o-mini 13%, Haiku 3.5 7%, Gemini 2.5 Flash 2.17%, ChatGPT-4o 0.49%, DeepSeek R1 0.37%, Gemini 2.5 Pro 0.14%, Sonnet 3.7 thinking 0.04%。(b) Introspective Faithfulness (2026)：flip pairs 保留 96% same-answer 相似度(cosine 0.784 vs 0.817, d=0.34)——表面推理文本对决策几乎不敏感；真信号在 self-rated confidence 层(obscure facts 下 p<0.001, r=0.134, model-specific)；native-reasoning 模型 internal thinking tokens 比 user-facing CoT 决策敏感性更高(Wilcoxon p=0.033)。最接近的可用判据组合：flip-pair 一致性测试 + 删步骤后答案不变率 + logprob/confidence 探针(而非读逻辑论证)。<br><br>③ test-time compute 拐点(本地小模型)：Setlur et al. 理论+实证(3/8/32B)——verifier-based(RL/search)训练远优于 verifier-free(蒸馏轨迹)，基座轨迹分布异质时 VF suboptimality 随 TTS budget 扩大而变差；Thinking-Optimal Scaling (2025)——过度扩展 CoT 长度损害性能(overthinking)，存在最优区间；Agarwal et al. (Dec 2025) 首个大规模系统对比(8 开源 LLM 7B-235B x 4 数据集 x 30B+ tokens)：无单一 TTS 策略普适占优，reasoning 模型分 short-horizon/long-horizon 两类，最优 TTS 随 budget 单调升。<br><br>④ verify/自校验在小模型的收益：Setlur 3/8/32B 实证 verification crucial for scaling test-time compute；Inference Scaling Laws (ICLR 2025)：Llemma-7B + tree search 跨所有策略稳定胜 Llemma-34B(MATH)——小模型+高级推理算法 Pareto 占优，但依赖显式验证信号。<br><br>对 persona 工作的直接含义：成璐 S3 质疑的『伪thinking』有现成判据基础(flip-pair + confidence 探针)，且其研究方向(logprob 探针做优先级排序)与 introspective faithfulness 结论(confidence 表达才是真自我知识所在)方向一致；本地 27B 实验(T17 刚跑完 610 题链路健康)可做删步骤消融验证。 | confirmed | 0.85 | material | 是 |

### cot_empirical_boundary

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| cot_empirical_boundary | ① CoT 实证边界(哪些任务真受益/表演性步骤)：Wei et al. NeurIPS 2022 证明 CoT prompting 是规模涌现能力——<100B 模型上无正收益，小模型生成流畅但不合逻辑的步骤反而低于 standard prompting；PaLM 540B + 8 exemplar 在 GSM8K 达 58.1%。机制假设：CoT 把多步问题分解成中间步骤、为难题分配额外计算。 | confirmed | 0.85 | material | 是 |

### pseudo_thinking_detection_criteria

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| pseudo_thinking_detection_criteria | ② 伪thinking 可检测判据：两条独立证据线。(a) In The Wild Not Always Faithful (2025)：真实 prompt 上 implicit post-hoc rationalization——同题正反问法系统性 Yes/Yes 或 No/No 且都配流畅论证；生产模型率 GPT-4o-mini 13%, Haiku 3.5 7%, Gemini 2.5 Flash 2.17%, ChatGPT-4o 0.49%, DeepSeek R1 0.37%, Gemini 2.5 Pro 0.14%, Sonnet 3.7 thinking 0.04%。(b) Introspective Faithfulness (2026)：flip pairs 保留 96% same-answer 相似度(cosine 0.784 vs 0.817, d=0.34)——表面推理文本对决策几乎不敏感；真信号在 self-rated confidence 层(obscure facts 下 p<0.001, r=0.134, model-specific)；native-reasoning 模型 internal thinking tokens 比 user-facing CoT 决策敏感性更高(Wilcoxon p=0.033)。最接近的可用判据组合：flip-pair 一致性测试 + 删步骤后答案不变率 + logprob/confidence 探针(而非读逻辑论证)。 | confirmed | 0.85 | material | 是 |

### tts_knee_small_models

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| tts_knee_small_models | ③ test-time compute 拐点(本地小模型)：Setlur et al. 理论+实证(3/8/32B)——verifier-based(RL/search)训练远优于 verifier-free(蒸馏轨迹)，基座轨迹分布异质时 VF suboptimality 随 TTS budget 扩大而变差；Thinking-Optimal Scaling (2025)——过度扩展 CoT 长度损害性能(overthinking)，存在最优区间；Agarwal et al. (Dec 2025) 首个大规模系统对比(8 开源 LLM 7B-235B x 4 数据集 x 30B+ tokens)：无单一 TTS 策略普适占优，reasoning 模型分 short-horizon/long-horizon 两类，最优 TTS 随 budget 单调升。 | confirmed | 0.85 | material | 是 |

### verify_benefit_small_models

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| verify_benefit_small_models | ④ verify/自校验在小模型的收益：Setlur 3/8/32B 实证 verification crucial for scaling test-time compute；Inference Scaling Laws (ICLR 2025)：Llemma-7B + tree search 跨所有策略稳定胜 Llemma-34B(MATH)——小模型+高级推理算法 Pareto 占优，但依赖显式验证信号。 | confirmed | 0.85 | material | 是 |

## 证据与备注

### research_findings

web_search 三批查询(keenable/parallel 后端)直接命中 arXiv/OpenReview/ICLR proceedings 原文摘要与关键数字，全部为 2022-2026 一手来源。

证据：
- https://arxiv.org/abs/2201.11903 (Wei et al., Chain-of-Thought Prompting Elicits Reasoning, NeurIPS 2022)
- https://arxiv.org/pdf/2503.08679v4 (Chain-of-Thought Reasoning In The Wild Is Not Always Faithful, 2025)
- https://arxiv.org/html/2605.27773v1 (Do Models Know Why They Changed Their Mind? Introspective Faithfulness of CoT Under Knowledge Conflict, 2026)
- https://arxiv.org/abs/2502.12118 (Setlur et al., Scaling Test-Time Compute Without Verification or RL is Suboptimal, ICLR 2025)
- https://openreview.net/forum?id=6ICFqmixlS (Towards Thinking-Optimal Scaling of Test-Time Compute, 2025)
- https://arxiv.org/abs/2512.02008 (The Art of Scaling Test-Time Compute for LLMs, Dec 2025)
- https://proceedings.iclr.cc/paper_files/paper/2025/hash/8c3caae2f725c8e2a55ecd600563d172-Abstract-Conference.html (Inference Scaling Laws, ICLR 2025)

### cot_empirical_boundary

web_search 直接命中一手来源(arXiv/OpenReview/ICLR proceedings)摘要与关键数字，双独立域交叉印证。

证据：
- https://arxiv.org/abs/2201.11903 (Wei et al., NeurIPS 2022: CoT prompting emergent at ~100B scale; small models fluent but illogical chains -> lower than standard prompting; PaLM 540B GSM8K 58.1%)
- https://openreview.net/forum?id=6ICFqmixlS (Thinking-Optimal Scaling 2025: excessively scaling CoT length can impair reasoning performance in certain domains)

### pseudo_thinking_detection_criteria

web_search 直接命中一手来源(arXiv/OpenReview/ICLR proceedings)摘要与关键数字，双独立域交叉印证。

证据：
- https://arxiv.org/pdf/2503.08679v4 (In The Wild Not Always Faithful 2025: implicit post-hoc rationalization on realistic prompts; GPT-4o-mini 13%, Haiku 3.5 7%, Gemini 2.5 Flash 2.17%, ChatGPT-4o 0.49%, DeepSeek R1 0.37%, Gemini 2.5 Pro 0.14%, Sonnet 3.7 thinking 0.04%)
- https://arxiv.org/html/2605.27773v1 (Introspective Faithfulness 2026: flip pairs retain 96% same-answer similarity, cosine 0.784 vs 0.817 d=0.34; confidence layer weak-but-real signal r=0.134 p<0.001; internal thinking tokens more decision-sensitive than user-facing CoT Wilcoxon p=0.033)
- https://proceedings.iclr.cc/paper_files/paper/2025/hash/8c3caae2f725c8e2a55ecd600563d172-Abstract-Conference.html (ICLR 2025 proceedings: inference strategy decoupled from model size empirical tradition, third independent source)

### tts_knee_small_models

web_search 直接命中一手来源(arXiv/OpenReview/ICLR proceedings)摘要与关键数字，双独立域交叉印证。

证据：
- https://arxiv.org/abs/2502.12118 (Setlur et al. ICLR 2025: VB methods asymptotically superior to VF when base trace distribution heterogeneous; empirical on 3/8/32B pre-trained LLMs)
- https://openreview.net/forum?id=6ICFqmixlS (Thinking-Optimal Scaling 2025: overthinking — excessive CoT length harms accuracy on math tasks; optimal interval exists)
- https://arxiv.org/abs/2512.02008 (Agarwal et al. Dec 2025: first large-scale TTS comparison, 8 open-source LLMs 7B-235B x 4 datasets x 30B+ tokens; no single strategy universally dominates; short-horizon vs long-horizon reasoning models)

### verify_benefit_small_models

web_search 直接命中一手来源(arXiv/OpenReview/ICLR proceedings)摘要与关键数字，双独立域交叉印证。

证据：
- https://arxiv.org/abs/2502.12118 (Setlur et al.: verification crucial for scaling test-time compute; 3/8/32B empirical corroboration)
- https://proceedings.iclr.cc/paper_files/paper/2025/hash/8c3caae2f725c8e2a55ecd600563d172-Abstract-Conference.html (Inference Scaling Laws ICLR 2025: Llemma-7B + tree search consistently outperforms Llemma-34B across all tested strategies on MATH; smaller models + advanced inference = Pareto-optimal trade-offs)
