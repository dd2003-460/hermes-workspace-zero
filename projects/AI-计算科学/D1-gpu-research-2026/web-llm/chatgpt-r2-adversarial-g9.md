origin: ai
输入路径: 反方结论包(04.5) → ChatGPT
观察时间: 2026-09-25T16:05+08:00 (Asia/Shanghai)
URL: https://chatgpt.com/c/6ab62d9e-2738-83e8-908c-0a2e00e855d0
回执: web-llm/chatgpt-r2-adversarial-g9.png
type: adversarial-review
condition: 反方核验, 仅已验证口径结论

# ChatGPT 反方回执（04.5 反方核验 #2）

## 反方 verdict（一句话）
原候选集合的"大方向"可保留，但原版排序式结论需降级为"规格矩阵 + 场景条件"，尤其应删除未经价格/benchmark 支撑的性价比判断。最稳妥决策框架不是"哪张卡最好"，而是先按 模型容量 → 精度 → 单卡/多卡/机柜 → 软件栈 → workload benchmark → 实际价格 逐层筛选。

## 反方风险等级表（逐项）
| 原结论 | 反方判断 | 来源 |
|---|---|---|
| H200 = 141GB / 4.8TB/s | ✅ 成立 | NVIDIA |
| B200 = 180GB / 8TB/s | ✅ 成立 | NVIDIA Docs |
| MI300X = 192GB / ~5.3TB/s | ✅ 成立 | AMD |
| MI350X = 288GB / 8TB/s | ✅ 成立 | AMD |
| MI300X ≈ B200 | ⚠️ 需限定"≈"维度(192 vs 180GB 差6.7%; 带宽差更明显) | — |
| B300 规格尚未核验 | ❌ 已可核验: 288GB HBM3e / up to 8TB/s, 8GPU/node 2.30TB | NVIDIA Docs |
| MI325X 只是边界项 | ⚠️ 应正式进入候选: 256GB HBM3e / ~6TB/s | AMD |
| MI355X 应进入候选 | ✅ 合理, 与 MI350X 同 288GB/8TB/s 级 | AMD ROCm |
| GB200/GB300 是 GPU SKU | ❌ 形态层级混淆 | — |
| GB200/GB300 是 rack-scale 候选 | ✅ 成立 | NVIDIA |
| vLLM 可部署 | ⚠️ 改"官方硬件支持", 不能自动推出生产就绪 | vLLM |
| 显存 ≈ 模型可服务尺寸 | ❌ 逻辑错误 | — |
| Groq/Cerebras 属于专用推理候选 | ✅ 成立 | — |
| Groq/Cerebras 可与 GPU 按 VRAM 直接比较 | ❌ 指标体系错误(SRAM vs HBM 不同体系) | — |
| H200/B200/MI350X 性价比排序 | ❌ 证据不足, 应删除 | — |

## 显/带宽 修正（审计友好写法, 两维度分开）
按单 GPU 显存容量: B300 ≈ MI350X ≈ MI355X (288GB) > MI325X (256GB) > MI300X (192GB) > B200 (180GB) > H200 (141GB) > H100 (80GB)。
按显存带宽: B200/B300/MI350X/MI355X ≈ 8TB/s > MI325X ≈ 6TB/s > MI300X ≈ 5.3TB/s > H200 4.8TB/s > H100 ~3.35TB/s。

## 形态修正
GB200 NVL72 = 36 Grace + 72 Blackwell GPU rack-scale system; 不应拿"GB200=某单卡显存"与 H200/B200 同层级。
Groq LPU / Cerebras WSE = 专用 inference accelerator, 进入"专用候选集合"但 NOT "GPU SKU 横向比较表"; 比较维度 = programmability/model coverage/quantization/custom model/API compat/latency/tokens/s/batch scaling/price/token/deployment control, NOT VRAM/bandwidth。
Cerebras: 2026 已宣布 AWS 部署 CS-3 并通过 Bedrock; "可获取"应写"云/API/专用系统可获取" ≠ 采购一张 card。

## 显存≠可服务尺寸 修正
删除"288GB GPU ≈ 可服务 288GB 模型"。改: GPU VRAM 仅容量上限的一部分; 可服务模型规模需同时考虑权重精度/量化、KV cache、context length、concurrency、runtime overhead、TP/PP、serving engine。NVIDIA NIM 文档将"每 GPU VRAM"/"verified GPU"/"模型 profile fit"分开。

## 性价比修正
删除"H200 中 / B200 高 / MI350X 高"。改: 当前没有足够统一价格+同 workload benchmark 数据支持稳定性价比排序; 应以具体模型/精度/输入输出长度/并发/TP/利用率/采购租赁价格计算 cost/token 或 cost/(useful tokens/s)。

## 候选遗漏
MI350P (144GB) 若定义="所有当前数据中心 Instinct 推理 GPU"则遗漏; 若定义="flagship/large-memory accelerator SKUs"则合理。→ 需先定义 candidate universe 才有可审计标准。

## 来源
NVIDIA Docs, AMD, AMD ROCm, vLLM, NVIDIA NIM, Cerebras。