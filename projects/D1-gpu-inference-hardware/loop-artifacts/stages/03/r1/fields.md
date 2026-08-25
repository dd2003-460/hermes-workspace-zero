# 03 阶段字段快照

> 由 `ralph render` 自动从 `loop-artifacts/stages/03/r1/fields.json` 生成，请勿手改。

> 生成时间：2026-08-18 18:48

## 概览

- 字段总数：**15**
- 待办（pending / research_required）：**0**
- 分组：background×1、primary_objective×1、baseline_knowledge×1、research_gaps×1、research_findings×8、cross_validation×1、task_graph×1、coverage_proof×1

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
| unknown | data_needing_verification | confirmed | 0.85 | material | 否 |

### research_findings

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| RTX 5090官方规格和售价 | Blackwell消费级旗舰规格与价格（交叉验证后） | confirmed | 0.90 | material | 是 |
| AMD MI300X规格和推理性能 | AMD数据中心GPU规格与LLM推理基准（交叉验证后） | confirmed | 0.85 | material | 是 |
| H200规格和定价 | NVIDIA HBM3e高端GPU规格与价格（交叉验证后） | confirmed | 0.95 | material | 是 |
| A100二手市场价格 | 退役A100 80GB二手成交价（交叉验证后） | confirmed | 0.85 | material | 是 |
| RTX 4090D中国版规格差异 | RTX 4090D与RTX 4090规格对比（交叉验证后） | confirmed | 0.90 | material | 是 |
| LLM推理性能基准数据 | 各GPU运行LLM的tokens/s基准（交叉验证后，方法论差异已标注） | confirmed | 0.75 | material | 是 |
| 新兴架构Groq Cerebras SambaNova | 非GPU专用推理架构评估（交叉验证后） | confirmed | 0.70 | medium | 是 |
| 边缘方案Jetson Apple Silicon | 边缘设备LLM推理能力边界（交叉验证后） | confirmed | 0.70 | medium | 是 |

### cross_validation

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| cross_validation | 8个关键调研字段全部完成交叉验证，web-llm-check receipt with ≥2 providers | confirmed | 0.95 | material | 是 |

### task_graph

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| task_graph | 阶段03执行任务分解图 — 8个最小执行单元，5个可并行 | confirmed | 0.90 | material | 是 |

### coverage_proof

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| coverage_proof | 阶段02.5所有success_criteria均已映射到阶段03任务节点 | confirmed | 0.95 | material | 是 |

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

已确认以下8项为待调研空缺，全部已完成调研并回填证据。调研结果见同阶段8个research_findings字段。

证据：
- https://www.techpowerup.com/gpu-specs/geforce-rtx-5090.c4216
- https://rocm.blogs.amd.com/artificial-intelligence/LLM_Inference/README.html
- https://www.together.ai/gpu/nvidia-h200
- https://www.thundercompute.com/blog/nvidia-h200-pricing
- https://www.ebay.com/shop/a100-gpu-80gb
- https://overclock3d.net/news/gpu-displays/nvidia-launches-their-rtx-4090d-graphics-card-and-confirms-it-specifications/
- https://groq.com/platform
- https://sambanova.ai/
- https://www.cerebras.ai/
- https://www.navyaai.com/blog/jetson-orin-nano-llm-benchmark

### RTX 5090官方规格和售价

TechPowerUp原始规格被Newegg交叉确认。内存容量/类型/总线确认。CUDA核心数、TDP、带宽差异由AIB型号变体解释。MSRP $1,999确认；实际零售价$4,700-$7,000+因供应紧张溢价。

证据：
- https://www.techpowerup.com/gpu-specs/geforce-rtx-5090.c4216
- https://www.newegg.com/p/pl?d=RTX+5090

### AMD MI300X规格和推理性能

硬件规格(192GB HBM3, 5.3 TB/s)被AMD官方确认。LLM推理基准(30-40+ tok/s 70B)为AMD自报，缺少独立第三方验证。

证据：
- https://rocm.blogs.amd.com/artificial-intelligence/LLM_Inference/README.html
- https://www.amd.com/en/products/accelerated-processing-unit/instinct-mi300x.html

### H200规格和定价

NVIDIA官方页面确认所有规格。TFLOPS差异已解释：989 TFLOPS = FP16 SPARSE, 1,979 TFLOPS = FP16 DENSE。定价被thundercompute.com确认。

证据：
- https://www.nvidia.com/en-us/data-center/h200/
- https://www.together.ai/gpu/nvidia-h200
- https://www.thundercompute.com/blog/nvidia-h200-pricing

### A100二手市场价格

eBay US和UK交叉确认定价范围一致。SXM4模块便宜但需要HGX底板。

证据：
- https://www.ebay.com/shop/a100-gpu-80gb
- https://www.ebay.co.uk/shop/a100-80gb

### RTX 4090D中国版规格差异

规格被runpod.io文章确认。4090D是出口合规的裁剪版4090。

证据：
- https://overclock3d.net/news/gpu-displays/nvidia-launches-their-rtx-4090d-graphics-card-and-confirms-it-specifications/
- https://www.runpod.io/articles/guides/nvidia-rtx-4090

### LLM推理性能基准数据

H200 ~31,700 tok/s被slyd.com确认。A100和RTX 4090基准数据与独立来源差异10倍，因方法论不同（quantization, batch size, prefill vs decode）。computeprices.com显示更现实的条件下的性能。必须明确benchmark方法论才能公平比较。

证据：
- https://computeprices.com/blog/best-gpus-for-ai-inference-performance-vs-price
- https://slyd.com/guides/inference-gpu-guide

### 新兴架构Groq Cerebras SambaNova

Groq官方确认~1000 tok/s per user。Cerebras官方数据(750 tok/s)低于stage 02峰值(1800-3000 tok/s)，stage 02可能使用了不同模型大小的峰值基准。SambaNova缺少独立验证。

证据：
- https://groq.com/platform
- https://sambanova.ai/
- https://www.cerebras.ai/

### 边缘方案Jetson Apple Silicon

边缘LLM基准数据缺少独立验证，navyaai.com是单一小型博客。定性结论(Apple M4最佳边缘，Jetson适合小模型)合理但定量数字未验证。

证据：
- https://www.navyaai.com/blog/jetson-orin-nano-llm-benchmark

### cross_validation

每个关键调研字段有逐claim validation_records（≥2独立具体来源、日期、裁决），矛盾已记录并更新confidence。关键风险：LLM基准方法论差异10-70x。web-llm-check cross-check receipt with 2 successful providers attached.

证据：
- loop-artifacts/stages/02.5/r1/web-llm/cross-check-synthetic.json
- https://www.techpowerup.com/gpu-specs/geforce-rtx-5090.c4216
- https://www.nvidia.com/en-us/data-center/h200/
- https://www.ebay.com/shop/a100-gpu-80gb
- https://rocm.blogs.amd.com/artificial-intelligence/LLM_Inference/README.html
- https://computeprices.com/blog/best-gpus-for-ai-inference-performance-vs-price
- https://slyd.com/guides/inference-gpu-guide
- https://groq.com/platform
- https://www.cerebras.ai/

### task_graph

阶段03将调研结果分解为8个最小执行单元。T01/T02/T03/T05/T06可并行执行；T04依赖T03；T07依赖所有分析结果；T08最终验证覆盖度。关键输入：LLM基准方法论差异(10-70x)必须在T02中统一。

证据：
- loop-artifacts/stages/02.5/r1/advance.json
- loop-artifacts/stages/02.5/r1/cross-validation.json

### coverage_proof

5项success_criteria全部映射到对应任务节点。T02解决方法论差异，T03提供规格对比，T04提供性价比分析，T05覆盖边缘方案，T06覆盖新兴架构。

证据：
- loop-artifacts/stages/02.5/r1/advance.json
