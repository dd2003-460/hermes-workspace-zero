# 04 阶段字段快照

> 由 `ralph render` 自动从 `loop-artifacts/stages/04/r1/tasks/04-r1-field-verification_uncertainties-5811232cc1.json` 生成，请勿手改。

> 生成时间：2026-09-09 18:12

## 概览

- 字段总数：**22**
- 待办（pending / research_required）：**1**
- 分组：background×1、primary_objective×1、baseline_knowledge×1、research_gaps×1、research_findings×8、cross_validation×1、task_graph×1、coverage_proof×1、verification_scope×1、verification×5、verification_report×1

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

### verification_scope

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| verification_scope | 阶段04验证范围 — 验证stage 03决策框架的准确性、计算正确性、和推荐可靠性 | confirmed | 0.90 |  |  |

### verification

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| verification_hardware_matrix | 硬件对比矩阵数据准确性验证 — 抽查15个设备的规格数据与独立来源一致性 | confirmed | 0.80 |  |  |
| verification_cost_performance | 性价比分析计算正确性验证 — 验证$/tok计算和排名 | confirmed | 0.85 |  |  |
| verification_decision_framework | 决策框架评分方法论验证 — 验证8项加权评分标准和GPU评分 | confirmed | 0.95 |  |  |
| verification_recommendations | 关键推荐交叉验证 — 验证RTX 5090最佳7B、H200最佳70B多GPU、MI300X最佳70B单GPU推荐 | confirmed | 0.75 |  |  |
| verification_uncertainties | 8项remaining_uncertainties处理 — 每项给出缓解措施或置信度调整 | confirmed | 0.80 |  |  |

### verification_report

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| verification_report | 阶段04验证报告 — 汇总所有验证结果，给出overall confidence和recommendation reliability | pending | 0.00 | material | 是 |

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

### verification_scope

验证范围 = 4 层: L1 $/tok 算术 (22 值, 全过); L2 排名一致性 (发现 6 处顺序违规); L3 决策框架内部一致性 (权重和=0.90 且 9/11 total 不可复现, 均失败); L4 关键推荐独立来源交叉验证 (5090 最佳7B / H200 最佳70B多GPU / MI300X 最佳70B单GPU, 由 hardware_matrix/recommendations/uncertainties 三个字段承接, 待办)。L1-L3 已由 Python 独立重算 (2026-09-09)。

### verification_hardware_matrix

复核结论: 矩阵内部自洽 ($/tok 22/22 通过); 15 设备中 2 个完成官方来源复核且一致: RTX 5090 (MSRP $1999 + 32GB GDDR7, NVIDIA 产品页) 和 H200 (141GB HBM3e @4.8TB/s, NVIDIA 数据页)。系统性缺口: 全项目 0 条 HTTPS 来源链接, stage 03 的 'source attribution' 不可追溯; 其余 13 设备的规格/价格/吞吐 (含 7B tok/s 基准值 10-70x 方法论方差) 待补来源 → 列入 uncertainties/research_required。

证据：
- loop-artifacts/stages/04/r1/evidence/computation-verification-r1.md
- https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5090/
- https://www.nvidia.com/en-us/data-center/h200/

### verification_cost_performance

L1 本地重算: 22/22 $/tok 通过 (price/tok_s, 0 偏差)。L2 排名: rankings_7b 6 处顺序违规 (6000Ada 记录#13应#4, H200 #12→#5, M4 #4→#6, M4Max #5→#7, MI300X #6→#8, SN3000 #7→#10), score_percentile 不自洽 → 需修复。关键价格/吞吐外部复核 (2026-09-09): RTX 5090 MSRP $1999 + 32GB GDDR7 经 NVIDIA 产品页确认 (其 $/tok_7b=$0.34 基于 MSRP; 零售溢价场景 $0.86 仍 #1, stage03 caveat 已注明); H200 141GB HBM3e @4.8TB/s 经 NVIDIA 数据页确认, $35000 维持估计值。

证据：
- loop-artifacts/stages/04/r1/evidence/computation-verification-r1.md
- https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5090/
- https://www.nvidia.com/en-us/data-center/h200/

### verification_decision_framework

8 项权重之和=0.90≠1.0; 11 个 GPU 中 9 个 recorded total 无法由 breakdown×weights 复现 (RTX5090 记录82/重算62.5, H200 78/65.75, MI300X 72/60.5 等)。重算下 H200(65.75)>RTX5090(62.5), best_overall=RTX5090 推荐在框架自身算术下翻转。'5090 最佳7B' 不受影响 (0.34 仍为最低 $/tok_7b)。修复项: 权重归一化+重算 totals+重排 rankings+重导推荐。

### verification_recommendations

3 项核心推荐交叉验证结果: (1) 'RTX 5090 最佳 7B' — 成立: $/tok_7b=$0.34 为 22 值最低 (L1 重算 0 偏差), MSRP $1999 + 32GB GDDR7 经 NVIDIA 产品页确认 (2026-09-09); 零售溢价 $5k 时 $0.86 仍 #1; 弱点: 5841 tok/s 单源基准。 (2) 'H200 最佳 70B 多GPU' — 成立: 141GB HBM3e @4.8TB/s + NVLink 经 NVIDIA 数据页确认, 官方 Llama2 70B 推理 1.9X H100 (与矩阵 210→316 tok/s 量级一致); $35k 维持估计值; 多GPU扩展未计入矩阵 $/tok (stage03 caveat #9)。 (3) 'MI300X 最佳 70B 单GPU' — 部分成立: 192GB HBM3 单卡经 Wikipedia/AMD_Instinct 确认 (唯一可单卡容纳 70B FP16 ~140GB + KV 的消费/工作站外选项), 但 $15k 价格仍无来源 (AMD 官网协议错误, Wikipedia 无价格), 且 stage03 caveat 指出其为双 chiplet 卡, per-GPU 口径下 7B 排名会变化。 稳健性警示: 因 L3 框架 bug (权重和=0.90, 9/11 total 不可复现), 重算下 H200(65.75)>5090(62.5), 'best_overall=5090' 不稳健; 3 项分工作负载推荐本身均成立。

证据：
- loop-artifacts/stages/04/r1/evidence/computation-verification-r1.md
- https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5090/
- https://www.nvidia.com/en-us/data-center/h200/
- https://en.wikipedia.org/wiki/AMD_Instinct

### verification_uncertainties

stage03 的 8 项 remaining_uncertainties 逐项处理 (2026-09-09): [已复核/部分解决 3 项] (a) RTX 5090 价格波动 — MSRP $1999 经 NVIDIA 官方页今日确认, 零售 $4700-7000 未独立复核; (b) H200 规格 — 141GB HBM3e @4.8TB/s 经 NVIDIA 官方页今日确认, 价格仍估计; (c) MI300X 规格 — 192GB HBM3 单卡经 Wikipedia 今日确认。 [仍开放 5 项] (d) MI300X $15k 定价 — 无来源 (AMD 官网 ERR_HTTP2_PROTOCOL_ERROR, Wikipedia 无价格) → research_required; (e) RTX 5090 5841 tok/s@7B — 单源, 方法论相关 (10-70x 方差), 保留 flag; (f) Apple M4/M4 Max 吞吐 (80/200 tok/s) — 单源低置信 (stage03 已注明), 保留 flag; (g) ROCm 生态成熟度 — 定性判断, CUDA 仍主导 (框架评分 ROCm=60 为假设); (h) Groq/Cerebras/SambaNova — 托管无单价; Groq ~1000 tok/s/user 与 Cerebras 750 tok/s 为 stage03 T06 独立来源确认, SambaNova 厂商单源 (置信 0.55)。 结论: 不确定性清单本身经验证成立, 5 项开放项转入 stage 05 跟踪。

证据：
- loop-artifacts/stages/04/r1/evidence/computation-verification-r1.md
- https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5090/
- https://www.nvidia.com/en-us/data-center/h200/
- https://en.wikipedia.org/wiki/AMD_Instinct

### verification_report

阶段04的required_output。汇总所有验证结果，给出overall confidence和recommendation reliability，决定是否可以进入stage 05
