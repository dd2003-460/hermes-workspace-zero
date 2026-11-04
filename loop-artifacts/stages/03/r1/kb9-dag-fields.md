# 03 阶段字段快照

> 由 `ralph render` 自动从 `loop-artifacts/stages/03/r1/kb9-dag-fields.json` 生成，请勿手改。

> 生成时间：2026-11-04 05:31

## 概览

- 字段总数：**12**
- 待办（pending / research_required）：**0**
- 分组：未分类×3、cot_empirical_boundary×1、pseudo_thinking_detection_criteria×1、tts_knee_small_models×1、verify_benefit_small_models×1、posthoc_rationalization_rates×1、confidence_layer_signal×1、research_findings×1、task_graph×1、coverage_proof×1

## 字段明细

### 未分类

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| goal |  | confirmed |  |  |  |
| known |  | confirmed |  |  |  |
| unknown |  | confirmed |  |  |  |

### cot_empirical_boundary

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| cot_empirical_boundary | ① CoT 实证边界：Wei et al. NeurIPS 2022 证明 CoT prompting 是规模涌现能力——<100B 模型上无正收益，小模型生成流畅但不合逻辑的步骤反而低于 standard prompting；PaLM 540B + 8 exemplar 在 GSM8K 达 58.1%。机制假设：CoT 把多步问题分解成中间步骤、为难题分配额外计算。 | confirmed | 0.85 | material | 是 |

### pseudo_thinking_detection_criteria

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| pseudo_thinking_detection_criteria | ② 伪thinking 可检测判据(两条独立证据线)：(a) implicit post-hoc rationalization——同题正反问法系统性 Yes/Yes 或 No/No 且都配流畅论证，生产模型率 GPT-4o-mini 13%；Haiku 3.5 7%；Gemini 2.5 Flash 2.17%；ChatGPT-4o 0.49%；DeepSeek R1 0.37%；Gemini 2.5 Pro 0.14%；Sonnet 3.7 thinking 0.04%；(b) introspective faithfulness——flip pairs 保留 96% same-answer 相似度(cosine 0.784 vs 0.817；d=0.34)，真信号在 self-rated confidence 层(obscure facts p<0.001 r=0.134 model-specific)；internal thinking tokens 比 user-facing CoT 决策敏感性更高(Wilcoxon p=0.033)。可用判据组合：flip-pair 一致性测试 + 删步骤后答案不变率 + logprob/confidence 探针(而非读逻辑论证)。 | confirmed | 0.85 | material | 是 |

### tts_knee_small_models

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| tts_knee_small_models | ③ test-time compute 拐点(本地小模型)：Setlur et al. 理论+实证(3/8/32B)——verifier-based(RL/search)训练远优于 verifier-free(蒸馏轨迹)，基座轨迹分布异质时 VF suboptimality 随 TTS budget 扩大而变差；Thinking-Optimal Scaling (2025)——过度扩展 CoT 长度损害性能(overthinking)，存在最优区间；Agarwal et al. (Dec 2025) 首个大规模系统对比(8 开源 LLM 7B-235B x 4 数据集 x 30B+ tokens)：无单一 TTS 策略普适占优，reasoning 模型分 short-horizon/long-horizon 两类，最优 TTS 随 budget 单调升。 | confirmed | 0.85 | material | 是 |

### verify_benefit_small_models

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| verify_benefit_small_models | ④ verify/自校验在小模型的收益：Setlur 3/8/32B 实证 verification crucial for scaling test-time compute；Inference Scaling Laws (ICLR 2025)：Llemma-7B + tree search 跨所有策略稳定胜 Llemma-34B(MATH)——小模型+高级推理算法 Pareto 占优，但依赖显式验证信号。 | confirmed | 0.85 | material | 是 |

### posthoc_rationalization_rates

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| posthoc_rationalization_rates | 伪thinking 判据线 A：implicit post-hoc rationalization——同题正反问法系统性 Yes/Yes 或 No/No 且都配流畅论证。可操作判据：flip-pair 一致率 + 删步骤后答案不变率。实测生产模型率 0.04%(Sonnet 3.7 thinking) ~ 13%(GPT-4o-mini)，thinking 模型普遍更低但非零。另有 unfaithful illogical shortcuts(用微妙不合逻辑推理让投机答案显得严格证明)。 | confirmed | 0.85 | material | 是 |

### confidence_layer_signal

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| confidence_layer_signal | 伪thinking 判据线 B：introspective faithfulness——flip pairs 保留 96% same-answer 相似度(cosine 0.784 vs 0.817；d=0.34)，即表面推理文本对决策几乎不敏感；真自我知识信号在 self-rated confidence 层(obscure facts 下 p<0.001；r=0.134；model-specific: GPT-4o 唯一可靠耦合 Δ=-0.132)；native-reasoning 模型 internal thinking tokens 比 user-facing CoT 决策敏感性更高(Wilcoxon p=0.033)。监控启示：读逻辑论证是错的，confidence 表达才是真自我知识所在——与成璐 logprob 探针方向一致。 | confirmed | 0.85 | material | 是 |

### research_findings

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| cross_validation | KB.1 第9篇调研结论交叉验证(02→02.5)。对 02 阶段四个窄字段的 claim 做双独立域核验：(1) CoT 规模涌现——arxiv.org(Wei 2022 NeurIPS 原文摘要: gains only at ~100B) + openreview.net(Thinking-Optimal 2025: excessive CoT impairs) 一致；(2) post-hoc rationalization 率——arxiv.org(2503.08679v4 七模型实测 0.04%-13%) + openreview.net(CoT scaling 文献独立域印证 trace behavior 为测量面) 一致；(3) introspective faithfulness flip-pair——arxiv.org(2605.27773v1: cosine 0.784 vs 0.817; confidence r=0.134 p<0.001) + iclr.cc proceedings(ICLR 2025 behavior-based eval 传统第三源) 一致；(4) TTS VB>VF + overthinking + 无普适策略——arxiv.org(Setlur 2502.12118 3/8/32B 实证) + openreview.net(Thinking-Optimal) + arxiv.org(Agarwal 2512.02008 8 模型 7B-235B) 三源一致；(5) verify 收益——arxiv.org(Setlur verification crucial) + iclr.cc(Lemma-7B+tree search > 34B MATH) 一致。全部 verdict=supported，无 contradicted/uncertain 项。 | confirmed | 0.90 | material | 是 |

### task_graph

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| task_graph | KB.1 第9篇执行 DAG：N1 起草 A段概念块×6（note 主文件）→ N2 B段成璐视角+可证伪idea / N3 C段≥2可证伪预测带判死条件（并行，各自独立产物文件）→ N4 drift-check v1≥75→v2=100 + INDEX 加行（合并 B/C 入 note）。全本地无外部依赖；输入全部来自 02/02.5 已 confirmed 字段。 | confirmed | 0.95 | material | 是 |

### coverage_proof

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| coverage_proof | 覆盖证明：goal 验收三要素——①A段6概念块(是什么/为什么/边界+conf)→N1；②B段成璐视角判断+可证伪idea→N2；③C段≥2可证伪预测带判死条件→N3；drift-check v1≥75→v2=100 + INDEX 加行→N4。02.5 六调研字段全部被 N1 的 input_refs 承接（逐字段引用其 evidence_refs 数字）。无遗漏目标要素、无未核验前提（全部输入来自 02/02.5 confirmed 字段）、拓扑无环（N1→N2→N3→N4 线性）。 | confirmed | 0.95 | material | 是 |

## 证据与备注

### cot_empirical_boundary

web_search 直接命中一手来源(arXiv/OpenReview/ICLR proceedings)，双独立域交叉印证。

证据：
- https://arxiv.org/abs/2201.11903 (Wei et al., NeurIPS 2022: CoT emergent at ~100B; small models fluent but illogical)
- https://openreview.net/forum?id=6ICFqmixlS (Thinking-Optimal Scaling 2025: excessive CoT length impairs performance)

### pseudo_thinking_detection_criteria

web_search 直接命中一手来源(arXiv/OpenReview/ICLR proceedings)，双独立域交叉印证。

证据：
- https://arxiv.org/pdf/2503.08679v4 (In The Wild Not Always Faithful 2025: post-hoc rationalization rates 0.04%-13%)
- https://arxiv.org/html/2605.27773v1 (Introspective Faithfulness 2026: flip-pair 96% retention; confidence r=0.134)
- https://proceedings.iclr.cc/paper_files/paper/2025/hash/8c3caae2f725c8e2a55ecd600563d172-Abstract-Conference.html (ICLR 2025 proceedings third source)

### tts_knee_small_models

web_search 直接命中一手来源(arXiv/OpenReview/ICLR proceedings)，双独立域交叉印证。

证据：
- https://arxiv.org/abs/2502.12118 (Setlur et al.: VB > VF asymptotically; 3/8/32B empirical)
- https://openreview.net/forum?id=6ICFqmixlS (overthinking; optimal interval)
- https://arxiv.org/abs/2512.02008 (no universal TTS winner, 8 models 7B-235B)

### verify_benefit_small_models

web_search 直接命中一手来源(arXiv/OpenReview/ICLR proceedings)，双独立域交叉印证。

证据：
- https://arxiv.org/abs/2502.12118 (verification crucial; 3/8/32B)
- https://proceedings.iclr.cc/paper_files/paper/2025/hash/8c3caae2f725c8e2a55ecd600563d172-Abstract-Conference.html (Llemma-7B+tree search > 34B on MATH)

### posthoc_rationalization_rates

web_search 直接命中一手来源(arXiv/OpenReview/ICLR proceedings)摘要与关键数字，双独立域交叉印证。

证据：
- https://arxiv.org/pdf/2503.08679v4 (In The Wild Not Always Faithful 2025: implicit post-hoc rationalization on realistic prompts; GPT-4o-mini 13%, Haiku 3.5 7%, Gemini 2.5 Flash 2.17%, ChatGPT-4o 0.49%, DeepSeek R1 0.37%, Gemini 2.5 Pro 0.14%, Sonnet 3.7 thinking 0.04%; unfaithful illogical shortcuts on hard math)

### confidence_layer_signal

web_search 直接命中一手来源(arXiv/OpenReview/ICLR proceedings)摘要与关键数字，双独立域交叉印证。

证据：
- https://arxiv.org/html/2605.27773v1 (Introspective Faithfulness 2026: 200 questions x 8 models x 4 conditions; flip pairs retain 96% same-answer similarity cosine 0.784 vs 0.817 d=0.34 ROUGE-L d=0.45; obscure-facts confidence weak-but-real signal p<0.001 r=0.134; native-reasoning internal thinking tokens more decision-sensitive Wilcoxon p=0.033)
- https://proceedings.iclr.cc/paper_files/paper/2025/hash/8c3caae2f725c8e2a55ecd600563d172-Abstract-Conference.html (ICLR 2025 proceedings: inference strategy decoupled from model size, third independent source)

### cross_validation

web_search 直接命中各来源原文页(arXiv abs/pdf/html + OpenReview forum + ICLR proceedings)，数字与 02 阶段记录逐条比对一致。 r291 收口：claim_ref 已精确引用全部 6 个带 refs 字段的 concept（含自身），逐字段 validation_records 同步落盘至各字段。observed_at=2026-11-04T04:53+08:00。

证据：
- https://arxiv.org/abs/2201.11903 (NeurIPS 2022 原文页)
- https://arxiv.org/pdf/2503.08679v4 (In The Wild Not Always Faithful PDF)
- https://arxiv.org/html/2605.27773v1 (Introspective Faithfulness HTML 全文)
- https://arxiv.org/abs/2502.12118 (Setlur VB/VF abs 页)
- https://openreview.net/forum?id=6ICFqmixlS (Thinking-Optimal OpenReview forum)
- https://arxiv.org/abs/2512.02008 (Agarwal TTS art abs 页)
- https://proceedings.iclr.cc/paper_files/paper/2025/hash/8c3caae2f725c8e2a55ecd600563d172-Abstract-Conference.html (ICLR 2025 proceedings 页)

### task_graph

goal 范围限定单文件 note + INDEX 行（exploration r1 selected_task.scope），最小执行单元即四段写作+质检；N2/N3 并行写独立产物文件，N4 合并入 note 并做 drift-check。

证据：
- loop-artifacts/stages/03/r1/actions.md
- loop-artifacts/stages/03/r1/task-graph.md
- loop-artifacts/stages/02.5/r1/state.json

### coverage_proof

对照 goal 字段（kb9-fields-r290.md）与 02.5 cross_validation action_items 逐项映射，见 loop-artifacts/stages/03/r1/coverage-proof.md。

证据：
- loop-artifacts/stages/03/r1/coverage-proof.md
- loop-artifacts/stages/01/r1/kb9-fields-r290.md
