# 01 阶段字段快照

> 由 `ralph render` 自动从 `loop-artifacts/stages/01/r1/tasks/01-r1-field-consumer_gpu_price_performance-3daa8be5da.json` 生成，请勿手改。

> 生成时间：2026-07-25 22:00

## 概览

- 字段总数：**7**
- 待办（pending / research_required）：**3**
- 分组：background×1、primary_research×1、comparative_analysis×1、alternative_evaluation×1、primary_objective×1、baseline_knowledge×1、research_gaps×1

## 字段明细

### background

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| 用户原始任务 | 任务描述 | confirmed | 1.00 | material | 否 |

### primary_research

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| consumer_gpu_price_performance | ranking_by_tflop_per_dollar_and_vram_per_dollar | research_required |  |  |  |

### comparative_analysis

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| multi_card_vs_single_card | cost_effectiveness_comparison | research_required | 0.20 |  |  |

### alternative_evaluation

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| workstation_mac_alternatives | worth_it_analysis | research_required |  |  |  |

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

2026-07-25 调研失败总结：WebSearch 连续 3 次调用均返回空结果（searchCount=0），WebFetch 对 techpowerup.com 的 6 个 GPU 规格页面均被 hook 拦截。当前环境外部搜索工具不可用，无法获取 2026 年中 RTX 5090/5080/4090/4090D/3090/3090 Ti 的实际售价和性能数据。待补：(1) RTX 5090/5080 Blackwell FP16/FP8 TFLOP 官方规格；(2) 2026 年中各卡全新/二手市场价格（Amazon/Newegg/京东/闲鱼/eBay）；(3) 每 TFLOP/$ 和每 GB VRAM/$ 排名计算。建议后续通过 ralph field-apply 重新调度此任务，或改用本地已知数据源（techpowerup.com 离线缓存、NVIDIA 官方 spec sheet）重试。

### multi_card_vs_single_card

多卡 vs 单卡性价比调研 — 所有外部搜索工具（WebSearch、WebFetch、curl）均不可用，无法获取实时价格数据和实测基准。

【搜索失败记录】
- DuckDuckGo HTML: 返回 CAPTCHA 人机验证，无法获取搜索结果
- TechPowerUp GPU Specs (5090/4090): HTTP 403 Forbidden
- Tom's Hardware (5090/4090 reviews): HTTP 403 Access Denied
- WebFetch videocardz.com: HTTP 403 Forbidden
- WebFetch nvidia.com: HTTP 403 Forbidden

【已有规格数据（来自之前 WebFetch 成功获取的 videocardz.com 和 nvidia.com）】

RTX 4090 (Ada Lovelace):
- VRAM: 24 GB GDDR6X
- CUDA cores: 16,384
- Boost clock: 2.52 GHz
- TDP: 450W (gaming avg 315W)
- AI TOPS (Tensor): 1,321
- Shader TFLOPS: 83
- RT TFLOPS: 191
- MSRP: $1,599
- 二手市场: 约 $1,200-1,500

RTX 5090 (Blackwell):
- VRAM: 32 GB GDDR7, 512-bit bus
- Boost clock: 2.41 GHz
- TDP: 575W, 需 1000W PSU
- AI TOPS (Tensor): 3,352
- RT TFLOPS: 318
- 长度: 304mm
- MSRP: $1,999

【理论对比分析（未经验证）】

双 RTX 4090 vs 单 RTX 5090:

| 指标 | 双4090 | 单5090 | 优势方 |
|------|--------|--------|--------|
| 总VRAM | 48GB | 32GB | 双4090 (+50%) |
| 总AI TOPS | 2,642 | 3,352 | 单5090 (+27%) |
| 总TDP | 900W | 575W | 单5090 (-36%) |
| 总成本(全新) | $3,198 | $1,999 | 单5090 (-37%) |
| 总成本(二手4090) | $2,400-3,000 | $1,999 | 单5090 或 双4090(低价) |
| 功耗效率(TOPS/W) | 2.94 | 5.83 | 单5090 (+98%) |

【双卡方案额外成本】
- 1200W+ PSU: +$100-200
- 支持双全尺寸卡的大机箱: +$50-150
- PCIe x8/x8 带宽降速（消费级主板通常只支持 x16/x4 或 x8/x8）
- 无 NVLink 桥接（RTX 4090 已取消 NVLink 支持）

【关键未决问题 — 需外部数据验证】
1. 双4090在AI推理场景的实际加速比（通信开销导致通常<2x）
2. 消费级主板双x16或x8/x8对LLM推理的影响
3. 二手4090实际市场价格（影响性价比计算）
4. RTX 5090实际street price（可能高于MSRP）
5. 多卡LLM推理的显存可利用率（PCIe带宽瓶颈）

【初步推断（低置信度，未验证）】
- 纯算力/瓦特效率：单5090显著优于双4090
- 总VRAM容量：双4090有50%优势，适合需要大显存的场景
- 总成本：单5090可能更便宜（即使按MSRP）
- 性价比综合：取决于具体AI推理工作负载和VRAM需求
- 双4090的额外成本（PSU、机箱、散热）进一步降低其性价比

【下一步】
需要恢复外部搜索能力获取：实际市场价格、AI推理实测加速比数据、PCIe带宽影响基准测试。

### workstation_mac_alternatives

需要评估工作站级卡和 Apple Mac Studio GPU 的性价比

### goal

调研性价比最高的本地 GPU，用于 AI 推理/训练等本地计算场景

### known

RTX 4090 24GB 是当前性价比标杆；RTX 5090 32GB 新一代旗舰；RTX 3090 24GB 二手低价方案；工作站卡 RTX 6000 Ada 48GB 价格昂贵；Mac Studio 统一内存架构适合大模型推理

### unknown

2026 年中各卡实际市场价格（含二手）、RTX 5090 正式发布后的实际售价、WebSearch 不可用导致无法获取实时数据
