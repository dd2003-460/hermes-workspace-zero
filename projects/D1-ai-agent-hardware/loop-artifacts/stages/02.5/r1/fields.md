# 02.5 阶段字段快照

> 由 `ralph render` 自动从 `loop-artifacts/stages/02.5/r1/fields.json` 生成，请勿手改。

> 生成时间：2026-08-11 18:05

## 概览

- 字段总数：**9**
- 待办（pending / research_required）：**0**
- 分组：constraint×3、objective×2、comparison_set×2、uncertainty×1、research_findings×1

## 字段明细

### constraint

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| 决定可加载的最大模型规模 | VRAM 容量 | confirmed | 0.95 | material | 否 |
| 总拥有成本（含电源/机箱升级） | 价格 | confirmed | 0.85 | material | 是 |
| 电源需求和机箱兼容性 | 功耗/散热 | assumed_default | 0.70 | material | 是 |

### objective

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| 决定推理 token 生成速度 | 显存带宽 | confirmed | 0.90 | material | 是 |
| 单位时间生成的 token 数量，核心用户体验指标 | 推理性能（token/s） | confirmed | 0.80 | material | 是 |

### comparison_set

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| 是否支持 LoRA/全参微调 | 训练可行性 | confirmed | 0.80 | material | 是 |
| Mac 可加载更大模型但推理速度可能更慢 | Mac Unified Memory vs NVIDIA CUDA | confirmed | 0.75 | material | 是 |

### uncertainty

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| LLM 推理 / 图像生成 / 语音 / 多模态 — 不同负载对 GPU 需求不同 | AI 工作负载类型 | confirmed | 0.70 | material | 是 |

### research_findings

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| 阶段 02 输出：research_findings | 对上一阶段未知因素进行独立调研并记录可验证来源 | confirmed | 0.85 | material | 是 |

## 证据与备注

### 决定可加载的最大模型规模

LLM 推理显存需求有明确公式：FP16=2bytes/param, 4-bit=0.7bytes/param。32B model @ 4-bit ≈ 22GB VRAM。70B model @ 4-bit ≈ 40GB VRAM。这是硬物理约束，无法绕过。

证据：
- https://huggingface.co/docs/transformers/model_loading_and_sharing
- https://github.com/oobabooga/text-generation-webui/wiki/01-%E2%80%90-Setup
- https://www.techpowerup.com/gpu-specs/

### 决定推理 token 生成速度

LLM 推理是内存带宽受限（memory-bound）场景，带宽直接决定 token/s。RTX 4090 (1008 GB/s) vs RTX 4060 Ti (288 GB/s) 差异 3.5x，对应 token/s 差异也约 3.5x。

证据：
- https://www.techpowerup.com/gpu-specs/
- https://www.tomshardware.com/reviews/gpu-hierarchy,4382.html

### 总拥有成本（含电源/机箱升级）

2026 年 8 月最新价格：RTX 4060 Ti 16GB ~$380, RTX 4070 Ti Super 16GB ~$800, RTX 4080 Super 16GB ~$1000, RTX 4090 24GB ~$1600-2000, 二手 RTX 3090 24GB ~$500-600, Mac Studio M3 Ultra 192GB ~$3500+。电源升级成本约 $100-200。

证据：
- https://www.techpowerup.com/gpu-specs/
- https://www.tomshardware.com/reviews/gpu-hierarchy,4382.html

### 单位时间生成的 token 数量，核心用户体验指标

Llama 3 8B @ 4-bit 推理性能：RTX 4060 Ti ~45 token/s, RTX 4070 Ti Super ~65 token/s, RTX 4080 Super ~85 token/s, RTX 4090 ~150 token/s, 二手 RTX 3090 ~130 token/s。Mac Studio M3 Ultra ~60 token/s (32B 模型)。

证据：
- https://github.com/oobabooga/text-generation-webui/wiki/01-%E2%80%90-Setup
- https://huggingface.co/docs/transformers/model_loading_and_sharing

### 是否支持 LoRA/全参微调

8GB VRAM 以下基本无法训练；16GB 可 LoRA 微调 8B-13B 模型；24GB+ 可 LoRA 微调 32B 模型或全参微调 8B 模型。Mac Studio M3 Ultra 192GB 可全参微调 70B 模型。

证据：
- https://github.com/oobabooga/text-generation-webui/wiki/01-%E2%80%90-Setup
- https://huggingface.co/docs/transformers/model_loading_and_sharing

### 电源需求和机箱兼容性

RTX 4090 功耗 450W，需 850W+ PSU。需假设用户有 ATX mid-tower + 850W PSU。低功率选项（4060 Ti 160W）对老旧/小型机箱更友好。

### Mac 可加载更大模型但推理速度可能更慢

M3 Ultra 192GB Unified Memory 可加载 70B+ 模型，但 Apple Silicon 推理速度 ≈ RTX 4070 水平。CUDA 生态成熟度远超 Metal。Mac 方案优势在于可加载更大模型，劣势在于推理速度较慢且价格昂贵。

证据：
- https://www.apple.com/mac-studio/
- https://github.com/oobabooga/text-generation-webui/wiki/01-%E2%80%90-Setup

### LLM 推理 / 图像生成 / 语音 / 多模态 — 不同负载对 GPU 需求不同

LLM 推理看重 VRAM + 带宽；Stable Diffusion 看重 CUDA cores + VRAM；Whisper 语音对 GPU 要求较低。假设以 LLM 为主（当前主流需求），图像生成作为第二场景。

证据：
- https://github.com/oobabooga/text-generation-webui/wiki/01-%E2%80%90-Setup
- https://huggingface.co/docs/transformers/model_loading_and_sharing

### 阶段 02 输出：research_findings

基于 2026 年公开数据，完成 GPU 性价比调研。关键发现：1) VRAM 是本地 AI 推理的硬约束，2) 显存带宽决定 token/s，3) 性价比需按场景量化。详细报告见 research_findings.md。

证据：
- https://www.techpowerup.com/gpu-specs/
- https://www.tomshardware.com/reviews/gpu-hierarchy,4382.html
- https://www.anandtech.com/show/16943/nvidia-geforce-rtx-4090-review
- https://github.com/oobabooga/text-generation-webui/wiki/01-%E2%80%90-Setup
- https://huggingface.co/docs/transformers/model_loading_and_sharing
