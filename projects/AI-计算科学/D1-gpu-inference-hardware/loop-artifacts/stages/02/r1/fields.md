# 02 阶段字段快照

> 由 `ralph render` 自动从 `loop-artifacts/stages/02/r1/fields.json` 生成，请勿手改。

> 生成时间：2026-08-17 15:22

## 概览

- 字段总数：**12**
- 待办（pending / research_required）：**0**
- 分组：background×1、primary_objective×1、baseline_knowledge×1、research_gaps×1、research_findings×8

## 字段明细

### background

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| 用户原始任务 | 任务描述 | confirmed | 1.00 | material | 否 |

### primary_objective

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| goal | systematic_gpu_research_for_local_llm_inference | confirmed | 1.00 | material | 否 |

### baseline_knowledge

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| known | established_facts | confirmed | 0.90 | material | 否 |

### research_gaps

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| unknown | data_needing_verification | confirmed | 0.00 | material | 否 |

### research_findings

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| RTX 5090官方规格和售价 | Blackwell消费级旗舰规格与价格 | confirmed | 0.95 | material | 是 |
| AMD MI300X规格和推理性能 | AMD数据中心GPU规格与LLM推理基准 | confirmed | 0.90 | material | 是 |
| H200规格和定价 | NVIDIA HBM3e高端GPU规格与价格 | confirmed | 0.90 | material | 是 |
| A100二手市场价格 | 退役A100 80GB二手成交价 | confirmed | 0.85 | material | 是 |
| RTX 4090D中国版规格差异 | RTX 4090D与RTX 4090规格对比 | confirmed | 0.90 | material | 是 |
| LLM推理性能基准数据 | 各GPU运行LLM的tokens/s基准 | confirmed | 0.85 | material | 是 |
| 新兴架构Groq Cerebras SambaNova | 非GPU专用推理架构评估 | confirmed | 0.80 | medium | 是 |
| 边缘方案Jetson Apple Silicon | 边缘设备LLM推理能力边界 | confirmed | 0.80 | medium | 是 |

## 证据与备注

### 用户原始任务

用户初始任务输入，作为本阶段已知背景字段。

证据：
- user:initial_task

### goal

系统性GPU调研：覆盖主流数据中心GPU、消费级GPU、新兴架构、边缘方案，为本地LLM推理选型提供决策依据

证据：
- user:initial_task

### known

已有项目知识：NVLink Gen5 ~900GB/s, PCIe 4.0 x16 ~32GB/s, RTX 4090 24GB GDDR6X, H100 80GB HBM3, KV cache是主要内存瓶颈, 量化可降低显存需求

证据：
- /Users/a1-6/Desktop/workspace/projects/D1-ai-agent-hardware/loop-artifacts/research-pci-e-llm-inference.md
- /Users/a1-6/Desktop/workspace/projects/D1-gpu-inference-hardware/tasks/TASKS.md
- /Users/a1-6/Desktop/workspace/D1-gpu-inference-hardware/loop-artifacts/stages/02/r1/web-llm-request-4.json

### unknown

已确认以下8项为待调研空缺（将在阶段02逐个派发subagent调研）：RTX 5090官方规格和售价、AMD MI300X规格和推理性能、H200规格和定价、A100二手市场价格、RTX 4090D中国版规格差异、LLM推理性能基准数据、Groq/Cerebras/SambaNova新兴架构、Jetson/Apple Silicon边缘方案能力

### RTX 5090官方规格和售价

从TechPowerUp权威数据库获取完整规格

证据：
- https://www.techpowerup.com/gpu-specs/geforce-rtx-5090.c4216
- https://www.google.com/search?q=NVIDIA+RTX+5090+specs+GB202

### AMD MI300X规格和推理性能

从Google搜索结果获取详细规格和推理基准

证据：
- https://www.google.com/search?q=AMD+MI300X+specs+HBM3+LLM+inference+benchmark
- https://rocm.blogs.amd.com/artificial-intelligence/LLM_Inference/README.html

### H200规格和定价

从Google AI Overview获取(来源: together.ai, thundercompute.com)

证据：
- https://www.together.ai/gpu/nvidia-h200
- https://www.thundercompute.com/blog/nvidia-h200-pricing
- https://www.google.com/search?q=NVIDIA+H200+specs+HBM3e+memory+bandwidth+price+leasing

### A100二手市场价格

从Google搜索结果(eBay/服务器经销商)获取二手市场价格

证据：
- https://www.ebay.com/shop/a100-gpu-80gb
- https://www.ebay.co.uk/shop/a100-80gb
- https://www.google.com/search?q=A100+80GB+used+price+eBay+server+dealer+2025+2026

### RTX 4090D中国版规格差异

从Google搜索结果获取规格对比

证据：
- https://overclock3d.net/news/gpu-displays/nvidia-launches-their-rtx-4090d-graphics-card-and-confirms-it-specifications/
- https://www.runpod.io/articles/guides/nvidia-rtx-4090
- https://www.google.com/search?q=RTX+4090D+vs+RTX+4090+CUDA+cores+14592+vs+16384

### LLM推理性能基准数据

从Google搜索结果获取多GPU LLM推理基准对比

证据：
- https://github.com/vllm-project/vllm
- https://computeprices.com/blog/best-gpus-for-ai-inference-performance-vs-price
- https://slyd.com/guides/inference-gpu-guide
- https://www.google.com/search?q=LLM+inference+benchmark+tokens+per+second+H100+MI300X+H200+A100+RTX+4090

### 新兴架构Groq Cerebras SambaNova

从Google搜索结果获取新兴推理架构性能数据

证据：
- https://groq.com/platform
- https://sambanova.ai/
- https://www.cerebras.ai/
- https://introl.com/blog/groq-lpu-infrastructure-ultra-low-latency-inference-guide-2025
- https://memu.pro/blog/groq-lpu-fast-inference-agent-memory
- https://www.google.com/search?q=Groq+LPU+Cerebras+WSE-3+SambaNova+DataScale+LLM+inference

### 边缘方案Jetson Apple Silicon

从Google搜索结果获取边缘设备LLM推理性能数据

证据：
- https://www.navyaai.com/blog/jetson-orin-nano-llm-benchmark
- https://www.google.com/search?q=Jetson+Orin+Apple+M3+M4+LLM+inference+benchmark+tokens+per+second+memory+limit
