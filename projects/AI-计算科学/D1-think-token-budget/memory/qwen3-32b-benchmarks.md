# origin: ai
# Qwen3-32B 官方 benchmark 数据（R3 参考基线）

来源：Qwen3 Technical Report（arXiv 2505.09388v1），§4.6 Post-training Evaluation，
Table 13（Qwen3-32B Thinking）/ Table 14（Qwen3-32B Non-thinking）。
从 https://arxiv.org/html/2505.09388v1 的 HTML 本地解析（/tmp/qwen3_report.html）。
用户本地模型 qwen3.8-27b-w8a16 属 27-32B dense 类 → Qwen3-32B 是最接近的官方基准。
HF 官网在本环境不可达（web_fetch/curl 均失败）；hf-mirror.com 可达。

## Table 13 — Qwen3-32B (Thinking)
| 基准 | 分数 |
|---|---|
| MMLU-Redux | 90.9 |
| GPQA-Diamond | 68.4 |
| C-Eval | 87.3 |
| LiveBench 2024-11-25 | 74.9 |
| IFEval strict prompt | 85.0 |
| Arena-Hard | 93.8 |
| AlignBench v1.1 | 8.72 |
| Creative Writing v3 | 81.0 |
| WritingBench | 7.90 |
| MATH-500 | 97.2 |
| AIME'24 | 81.4 |
| AIME'25 | 72.9 |
| ZebraLogic | 88.8 |
| AutoLogi | 87.3 |
| BFCL v3 | 70.3 |
| LiveCodeBench v5 | 65.7 |
| CodeForces | 1977 / 97.7% |
| Multi-IF | 73.0 |
| INCLUDE | 73.7 |
| MMMLU 14-lang | 80.6 |
| MT-AIME2024 | 75.0 |
| PolyMath | 47.4 |

同行对比：DeepSeek-R1-Distill-Llama-70B / QwQ-32B / o3-mini(medium)。

## Table 14 — Qwen3-32B (Non-thinking)
| 基准 | 分数 |
|---|---|
| MMLU-Redux | 85.7 |
| GPQA-Diamond | 54.6 |
| C-Eval | 83.3 |
| LiveBench 2024-11-25 | 59.8 |
| IFEval strict prompt | 83.2 |
| Arena-Hard | 92.8 |
| AlignBench v1.1 | 8.58 |
| Creative Writing v3 | 78.3 |
| WritingBench | 7.54 |
| MATH-500 | 88.6 |
| AIME'24 | 31.0 |
| AIME'25 | 20.2 |
| ZebraLogic | 29.2 |
| AutoLogi | 78.5 |
| BFCL v3 | 63.0 |
| LiveCodeBench v5 | 31.3 |
| CodeForces | 1353 / 71.0% |
| Multi-IF | 70.7 |
| INCLUDE | 70.9 |
| MMMLU 14-lang | 76.5 |
| MT-AIME2024 | 24.1 |
| PolyMath | 22.5 |

同行对比：GPT-4o-mini / LLaMA-4-Scout / Qwen2.5-72B-Instruct。

## Thinking vs Non-thinking 差距（decode 思考 token 承载的准确率）
| 基准 | thinking | non-thinking | gap |
|---|---|---|---|
| ZebraLogic | 88.8 | 29.2 | 59.6 |
| AIME'25 | 72.9 | 20.2 | 52.7 |
| MT-AIME2024 | 75.0 | 24.1 | 50.9 |
| AIME'24 | 81.4 | 31.0 | 50.4 |
| LiveCodeBench v5 | 65.7 | 31.3 | 34.4 |
| CodeForces | 1977 | 1353 | - |
| GPQA-Diamond | 68.4 | 54.6 | 13.8 |
| MATH-500 | 97.2 | 88.6 | 8.6 |

## R3 结论
- AIME 2025 是 P1（answer-only）压测首选：官方、公开、整数答案（易自动判分）、
  且 thinking/non-thinking gap 52.7 分 = 思考 token 承载准确率最多的官方基准之一。
- 次选：ZebraLogic（逻辑，gap 59.6）、GPQA-Diamond（知识，gap 13.8）。
- 预训练参考（Table 4, Qwen3-32B-Base）：MMLU 83.61 / MATH 61.62 / GSM8K 93.40 /
  GPQA 49.49 / BBH 87.38 / EvalPlus 72.05。
