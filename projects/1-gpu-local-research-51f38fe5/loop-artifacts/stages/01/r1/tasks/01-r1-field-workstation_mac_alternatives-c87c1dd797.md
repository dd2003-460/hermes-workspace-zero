# 01 阶段字段快照

> 由 `ralph render` 自动从 `loop-artifacts/stages/01/r1/tasks/01-r1-field-workstation_mac_alternatives-c87c1dd797.json` 生成，请勿手改。

> 生成时间：2026-07-25 11:42

## 概览

- 字段总数：**4**
- 待办（pending / research_required）：**3**
- 分组：background×1、primary_research×1、comparative_analysis×1、alternative_evaluation×1

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
| multi_card_vs_single_card | cost_effectiveness_comparison | research_required | 0.30 |  |  |

### alternative_evaluation

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| workstation_mac_alternatives | worth_it_analysis | research_required |  |  |  |

## 证据与备注

### 用户原始任务

用户初始任务输入，作为本阶段已知背景字段。

证据：
- user:initial_task

### consumer_gpu_price_performance

2026-07-25 调研尝试：WebSearch 两次调用均返回空结果（searchCount=0），WebFetch 对 techpowerup.com 的 6 个 GPU 规格页面（RTX 5090/5080/4090/4090D/3090/3090 Ti）均被 hook 拦截标记为外部搜索连续失败。未能获取到任何可验证的价格或性能数据。待补：(1) RTX 5090/5080 Blackwell 架构 FP16/FP8 TFLOP 官方规格；(2) 2026 年中各卡全新/二手市场价格；(3) 每 TFLOP/$ 和每 GB VRAM/$ 排名计算。建议后续通过 ralph field-apply 重新调度此任务，或改用本地已知数据源（如 techpowerup.com 离线缓存、NVIDIA 官方 spec sheet）重试。

### multi_card_vs_single_card

多卡 vs 单卡性价比调研 — 部分数据已获取，但 WebSearch 全部失败，WebFetch 仅获取到基础规格，价格数据和实测数据缺失。

【已获取的规格对比】
RTX 4090 (Ada Lovelace):
- VRAM: 24 GB GDDR6X
- CUDA cores: 16,384
- Boost clock: 2.52 GHz
- TDP: 450W (gaming avg 315W)
- AI TOPS (Tensor): 1,321
- Shader TFLOPS: 83
- RT TFLOPS: 191

RTX 5090 (Blackwell):
- VRAM: 32 GB GDDR7, 512-bit bus
- Boost clock: 2.41 GHz
- TDP: 575W, 需 1000W PSU
- AI TOPS (Tensor): 3,352
- RT TFLOPS: 318
- 长度: 304mm

【待补的关键数据 — 因搜索工具不可用未能获取】
1. 双 RTX 4090 vs 单 RTX 5090 的总VRAM/总算力/价格对比
   - 双4090: 48GB VRAM, 2x 1,321 = 2,642 AI TOPS, 2x 450W = 900W TDP
   - 单5090: 32GB VRAM, 3,352 AI TOPS, 575W TDP
   - 价格: WebFetch 返回 $XXX.XX 占位符，未获取到实际售价
   - 双4090总VRAM多50%，但单5090 Tensor算力高27%

2. 双卡 PCIe 带宽瓶颈 (x16/x16 vs x8/x8)
   - 需要实测数据确认 PCIe 降速对 AI 推理的影响

3. 供电需求
   - 单4090: 450W, 推荐 850W PSU
   - 双4090: 900W GPU + 系统余量, 需 1200W+ PSU
   - 单5090: 575W, 需 1000W PSU

4. 主板/通道限制
   - 需要确认消费级主板支持双全尺寸 x16 的型号

5. NVLink 成本效益
   - RTX 4090 已取消 NVLink 桥接支持，需确认

6. AI 推理实测加速比
   - 需要 LLM serving / Stable Diffusion 等场景的多卡实测

7. 二手价格对比
   - 需要二手市场 4090 和 5090 的实时价格

【初步推断（未验证）】
- 纯算力角度：双4090总VRAM更大(48GB vs 32GB)，适合大模型；单5090单卡Tensor算力更强
- 性价比角度：取决于二手4090价格是否显著低于5090
- 双卡方案额外成本：1200W+ PSU (+$100-200)、更好的机箱(+$50-150)、可能的PCIe交换卡
- 双卡功耗翻倍但AI推理加速比通常低于2x（通信开销）

【下一步】
需要恢复 WebSearch 功能或使用 curl/wget 直接抓取硬件评测网站获取价格和实测数据。

证据：
- https://videocardz.com/newz/nvidia-geforce-rtx-5090-specs (WebFetch 2026-07-25)
- https://www.nvidia.com/en-us/geforce/graphics-cards/40-series/rtx-4090/ (WebFetch 2026-07-25)

### workstation_mac_alternatives

外部证据源（WebSearch/WebFetch）连续失败，无法获取实时价格和数据。待补证据项：1) RTX 6000 Ada Generation 当前价格（MSRP $6,800，需验证实际售价）和规格（48GB GDDR6，300W TDP，Ada Lovelace架构）；2) RTX 4090 vs 6000 Ada 每GB VRAM/$对比（4090约$1,600/24GB=67$/GB，6000 Ada约$6,800/48GB=142$/GB）；3) Mac Studio M3 Max/Ultra GPU benchmark数据（Metal性能框架，LLM推理tokens/sec）；4) Mac Studio统一内存架构 vs NVIDIA VRAM对比（M3 Max 128GB vs RTX 4090 24GB）；5) 二手RTX 3090性价比（二手约$700-900/24GB=29-38$/GB）；6) RTX 5090/5080定价（尚未正式发布）。结论：在缺乏实时数据的情况下无法完成性价比排名，需外部工具恢复后重新调研。
