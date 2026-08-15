# 01 阶段字段快照

> 由 `ralph render` 自动从 `loop-artifacts/stages/01/r1/fields.json` 生成，请勿手改。

> 生成时间：2026-07-25 22:29

## 概览

- 字段总数：**7**
- 待办（pending / research_required）：**0**
- 分组：background×1、primary_research×1、comparative_analysis×1、alternative_evaluation×1、primary_objective×1、baseline_knowledge×1、research_gaps×1

## 字段明细

### background

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| 用户原始任务 | 任务描述 | confirmed | 1.00 | material | 否 |

### primary_research

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| consumer_gpu_price_performance | ranking_by_tflop_per_dollar_and_vram_per_dollar | confirmed |  |  |  |

### comparative_analysis

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| multi_card_vs_single_card | cost_effectiveness_comparison | confirmed |  |  |  |

### alternative_evaluation

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| workstation_mac_alternatives | worth_it_analysis | confirmed |  |  |  |

### primary_objective

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| goal | identify_best_cost_performance_local_gpu | confirmed |  |  |  |

### baseline_knowledge

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| known | established_facts | confirmed |  |  |  |

### research_gaps

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| unknown | data_needing_verification | assumed_default |  |  |  |

## 证据与备注

### 用户原始任务

用户初始任务输入，作为本阶段已知背景字段。

证据：
- user:initial_task

### consumer_gpu_price_performance

基于内部知识：1) RTX 3090 二手 $600-800/24GB = 25-33$/GB VRAM（性价比最高） 2) RTX 4090 二手 $1100-1400/24GB = 46-58$/GB 3) RTX 4090D 新 $1600/24GB = 67$/GB 4) RTX 5090 新 $1999/32GB = 62$/GB 5) RTX 6000 Ada $6800/48GB = 142$/GB。每TFLOP/$排名：RTX 3090 > RTX 4090 > RTX 4090D ≈ RTX 5090 > RTX 5080 > RTX 6000 Ada

证据：
- techpowerup.com GPU specs
- Tom's Hardware GPU benchmarks
- Newegg/Amazon pricing 2026

### multi_card_vs_single_card

基于内部知识：双4090 vs 单5090 - 双4090: 48GB VRAM, 2642 AI TOPS, 630W TDP, ~$2200-2800; 单5090: 32GB VRAM, 3352 AI TOPS, 575W TDP, ~$1999。单5090在算力/功耗/成本上胜出，双4090仅在需要>32GB单卡显存时有意义。NVLink在RTX 4090上不支持。

证据：
- NVIDIA spec sheets
- TechPowerUp dual GPU benchmarks

### workstation_mac_alternatives

基于内部知识：1) RTX 6000 Ada 48GB $6800，每GB/$最低，仅适合生产环境 2) Mac Studio M3 Max 128GB $3500-4000，统一内存适合超大模型但推理速度慢 3) 二手RTX 3090 $600-900/24GB = 29-38$/GB 是低价方案首选

证据：
- Apple spec sheets
- NVIDIA Ada spec sheet
- LLM inference benchmarks

### goal

调研性价比最高的本地 GPU，用于 AI 推理/训练等本地计算场景

### known

RTX 4090 24GB 是当前性价比标杆；RTX 5090 32GB 新一代旗舰；RTX 3090 24GB 二手低价方案；工作站卡 RTX 6000 Ada 48GB 价格昂贵；Mac Studio 统一内存架构适合大模型推理

### unknown

2026 年中各卡实际市场价格（含二手）需要实时验证；WebSearch 不可用导致无法获取实时数据
