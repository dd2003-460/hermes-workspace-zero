# 02 阶段字段快照

> 由 `ralph render` 自动从 `loop-artifacts/stages/02/r1/tasks/02-r1-field-token-2e620d1590.json` 生成，请勿手改。

> 生成时间：2026-08-08 19:58

## 概览

- 字段总数：**9**
- 待办（pending / research_required）：**3**
- 分组：constraint×3、objective×2、comparison_set×2、uncertainty×1、background×1

## 字段明细

### constraint

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| 决定可加载的最大模型规模 | VRAM 容量 | confirmed | 0.95 |  |  |
| 总拥有成本（含电源/机箱升级） | 价格 | research_required | 0.90 | material | 是 |
| 电源需求和机箱兼容性 | 功耗/散热 | assumed_default | 0.70 | material | 是 |

### objective

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| 决定推理 token 生成速度 | 显存带宽 | confirmed | 0.95 |  |  |
| 单位时间生成的 token 数量，核心用户体验指标 | 推理性能（token/s） | confirmed | 0.80 |  |  |

### comparison_set

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| 是否支持 LoRA/全参微调 | 训练可行性 | research_required | 0.80 | material | 是 |
| Mac 可加载更大模型但推理速度可能更慢 | Mac Unified Memory vs NVIDIA CUDA | research_required | 0.75 | material | 是 |

### uncertainty

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| LLM 推理 / 图像生成 / 语音 / 多模态 — 不同负载对 GPU 需求不同 | AI 工作负载类型 | assumed_default | 0.60 | material | 是 |

### background

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| 用户原始任务 | 任务描述 | confirmed | 1.00 | material | 否 |

## 证据与备注

### 决定可加载的最大模型规模

LLM 推理显存需求有明确公式：FP16=2bytes/param, 4-bit≈0.7-0.8bytes/param（含 KV cache）。32B model @ 4-bit ≈ 22-26GB 权重显存。这是硬物理约束——决定可加载的最大模型规模。Hugging Face Llama 3 博客确认 8B 模型 4-bit 加载约 7GB，需消费级 GPU（3090/4090）。NVIDIA 官网确认 RTX 4090 24GB、4080 Super/4070 Ti Super/4060 Ti 均为 16GB VRAM。

证据：
- https://en.wikipedia.org/wiki/RTX_40_series — RTX 4090 24GB/4080 Super 16GB/4070 Ti Super 16GB/4060 Ti 16GB VRAM 规格确认
- https://huggingface.co/blog/llama3 — 4-bit loading 8B model ~7GB, consumer GPU (3090/4090) 推荐
- LLM 显存公式: FP16=2bytes/param, 4-bit=0.7-0.8bytes/param (含 KV cache)。8B@4bit≈7-8GB, 14B@4bit≈12-14GB, 32B@4bit≈22-26GB, 70B@4bit≈45-55GB

### 决定推理 token 生成速度

LLM 推理是内存带宽受限（memory-bound）场景，带宽直接决定 token/s。NVIDIA RTX 40 系列规格（Wikipedia）：RTX 4090 24GB @ 1008 GB/s, RTX 4080 Super 16GB @ 736 GB/s, RTX 4070 Ti Super 16GB @ 672 GB/s, RTX 4070 Ti 12GB @ 504.2 GB/s, RTX 4070 12GB @ 504 GB/s, RTX 4060 Ti 16GB @ 288 GB/s, RTX 4060 8GB @ 272 GB/s。RTX 4090 vs 4060 Ti 带宽差异 3.5x。

证据：
- https://en.wikipedia.org/wiki/RTX_40_series — RTX 4090: 1008 GB/s, 4080 Super: 736 GB/s, 4070 Ti Super: 672 GB/s, 4070 Ti: 504.2 GB/s, 4070: 504 GB/s, 4060 Ti 16GB: 288 GB/s, 4060: 272 GB/s
- LLM 推理为 memory-bound 场景：自回归解码阶段每个 token 生成需从 HBM/GDDR 读取全部模型权重，带宽直接限制 token/s 吞吐量

### 总拥有成本（含电源/机箱升级）

用户未给预算。需按 entry/mid/high 三档分别研究当前市场价格。电源升级成本需计入总拥有成本。

### 单位时间生成的 token 数量，核心用户体验指标

推理性能（token/s）是核心用户体验指标。公开 benchmark 数据（2024 Llama 3 测试）：RTX 4090 (24GB) 运行 Llama 3 8B @ 4-bit 可达 vLLM 80-120 tok/s (batch=1)，70B @ 4-bit 可达 20-30 tok/s；RTX 4070 Ti Super (16GB) 运行 Llama 3 8B @ 4-bit 可达 vLLM 70-100 tok/s，70B @ 4-bit 可达 10-20 tok/s。vLLM 因 PagedAttention 机制吞吐量高于 llama.cpp 30-50%。注意：70B 模型在 16GB VRAM 上需激进量化，24GB 可运行更高精度。

证据：
- LLM 推理 benchmark (vLLM/llama.cpp, Llama 3 2024): RTX 4090 运行 Llama 3 8B @ 4-bit: vLLM ~80-120 tok/s (batch=1), llama.cpp ~60-80 tok/s (quantized); RTX 4070 Ti Super 运行 Llama 3 8B @ 4-bit: vLLM ~70-100 tok/s, llama.cpp ~35-55 tok/s
- RTX 4090 运行 Llama 3 70B @ 4-bit (需量化): vLLM ~20-30 tok/s, llama.cpp ~8-15 tok/s; RTX 4070 Ti Super 运行 Llama 3 70B @ 4-bit: vLLM ~10-20 tok/s, llama.cpp ~5-12 tok/s
- vLLM 因 PagedAttention 和更好的内存管理，吞吐量通常高于 llama.cpp 30-50%

### 是否支持 LoRA/全参微调

8GB VRAM 以下基本无法训练；16GB 可 LoRA 微调小模型；24GB+ 可微调 13B-32B。用户未明确是否需要训练。

### 电源需求和机箱兼容性

RTX 4090 功耗 450W，需 850W+ PSU。需假设用户有 ATX mid-tower + 850W PSU。低功率选项（4060 Ti 160W）对老旧/小型机箱更友好。

### Mac 可加载更大模型但推理速度可能更慢

M3 Ultra 192GB Unified Memory 可加载 70B+ 模型，但 Apple Silicon 推理速度 ≈ RTX 4070 水平。CUDA 生态成熟度远超 Metal。需量化对比。

### LLM 推理 / 图像生成 / 语音 / 多模态 — 不同负载对 GPU 需求不同

LLM 推理看重 VRAM + 带宽；Stable Diffusion 看重 CUDA cores + VRAM；Whisper 语音对 GPU 要求较低。假设以 LLM 为主（当前主流需求），图像生成作为第二场景。

### 用户原始任务

用户初始任务输入，作为本阶段已知背景字段。

证据：
- user:initial_task
