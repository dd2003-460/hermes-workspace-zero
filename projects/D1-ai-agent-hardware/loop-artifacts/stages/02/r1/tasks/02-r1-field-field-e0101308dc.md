# 02 阶段字段快照

> 由 `ralph render` 自动从 `loop-artifacts/stages/02/r1/tasks/02-r1-field-field-e0101308dc.json` 生成，请勿手改。

> 生成时间：2026-07-25 04:01

## 概览

- 字段总数：**8**
- 待办（pending / research_required）：**6**
- 分组：constraint×3、objective×2、comparison_set×2、uncertainty×1

## 字段明细

### constraint

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| 决定可加载的最大模型规模 | VRAM 容量 | research_required |  |  |  |
| 总拥有成本（含电源/机箱升级） | 价格 | research_required | 0.90 | material | 是 |
| 电源需求和机箱兼容性 | 功耗/散热 | assumed_default | 0.70 | material | 是 |

### objective

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| 决定推理 token 生成速度 | 显存带宽 | research_required | 0.90 | material | 是 |
| 单位时间生成的 token 数量，核心用户体验指标 | 推理性能（token/s） | research_required | 0.85 | material | 是 |

### comparison_set

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| 是否支持 LoRA/全参微调 | 训练可行性 | research_required | 0.80 | material | 是 |
| Mac 可加载更大模型但推理速度可能更慢 | Mac Unified Memory vs NVIDIA CUDA | research_required | 0.75 | material | 是 |

### uncertainty

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| LLM 推理 / 图像生成 / 语音 / 多模态 — 不同负载对 GPU 需求不同 | AI 工作负载类型 | assumed_default | 0.60 | material | 是 |

## 证据与备注

### 决定可加载的最大模型规模

LLM 推理显存需求有明确公式：FP16=2bytes/param, 4-bit=0.7bytes/param。32B model @ 4-bit ≈ 22GB。这是硬物理约束。

### 决定推理 token 生成速度

LLM 推理是内存带宽受限（memory-bound）场景，带宽直接决定 token/s。RTX 4090 (1008 GB/s) vs RTX 4060 Ti (288 GB/s) 差异 3.5x。

### 总拥有成本（含电源/机箱升级）

用户未给预算。需按 entry/mid/high 三档分别研究当前市场价格。电源升级成本需计入总拥有成本。

### 单位时间生成的 token 数量，核心用户体验指标

需针对典型模型（Llama 3 8B/70B, Qwen 7B/14B/32B）在 llama.cpp / vLLM 下测试或引用公开 benchmark。

### 是否支持 LoRA/全参微调

8GB VRAM 以下基本无法训练；16GB 可 LoRA 微调小模型；24GB+ 可微调 13B-32B。用户未明确是否需要训练。

### 电源需求和机箱兼容性

RTX 4090 功耗 450W，需 850W+ PSU。需假设用户有 ATX mid-tower + 850W PSU。低功率选项（4060 Ti 160W）对老旧/小型机箱更友好。

### Mac 可加载更大模型但推理速度可能更慢

M3 Ultra 192GB Unified Memory 可加载 70B+ 模型，但 Apple Silicon 推理速度 ≈ RTX 4070 水平。CUDA 生态成熟度远超 Metal。需量化对比。

### LLM 推理 / 图像生成 / 语音 / 多模态 — 不同负载对 GPU 需求不同

LLM 推理看重 VRAM + 带宽；Stable Diffusion 看重 CUDA cores + VRAM；Whisper 语音对 GPU 要求较低。假设以 LLM 为主（当前主流需求），图像生成作为第二场景。
