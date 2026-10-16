origin: ai
输入路径: 反方结论包(04.5) → Perplexity
观察时间: 2026-09-25T15:55+08:00 (Asia/Shanghai)
URL: https://www.perplexity.ai/search/a7efdf85-5a06-4845-a43b-fdeed7c94f5f
回执: web-llm/perplexity-r2-adversarial-g9.png
type: adversarial-review
condition: 反方核验, 仅已验证口径结论

# Perplexity 反方回执（04.5 反方核验 #1）

## 反方判定（一句话）
原结论可作为"规格初筛"，但尚不足以成为"推理硬件选型结论"；其中 B300/MI325X 定位遗漏或弱化、B200 规格与排序过度简化、GB200/GB300 形态混淆、vLLM 支持的版本与生产含义不清、未把专业推理服务的模型覆盖和部署约束纳入筛选，都可能改变最终推荐。

## 会改变结论的硬错误/缺口（逐项）
1. B200 显不稳定 180GB：Blackwell 单设备 HBM 最高 192GB；HGX B200 180GB 按 SKU/平台；B200 峰值带宽最高 8TB/s（原结论 180GB 过度简化）。
2. B300/Blackwell Ultra 遗漏：B300 = 288GB HBM3e ~8TB/s，与 MI350X 同显/带宽 tier → 原"仅 MI350X 领先"排序错误。
3. 显排序修正(单设备 HBM 维度): MI350X/MI355X/B300 288GB > MI325X 256GB > MI300X 192GB ≈ B200 180–192GB(按SKU) > H200 141GB > H100 80/94GB。
4. MI350X 不能无差别替代 MI355X：两者 288GB/8TB/s，但 MI355X 强调 MXFP6/MXFP4；ROCm/框架/量化/容器针对 MI300X/MI325X 需兼容+性能回归。
5. GB200/GB300 形态混淆：GB300 NVL72 = 72-GPU 单 NVLink 域, 130TB/s 总 NVLink, ~20TB GPU HBM, 17TB CPU LPDDR5X, 液冷/机柜级 AI factory；不应作为"可买到一张 GPU"等价物；应列为"整机/机柜项目"。
6. H100 过度简化：80GB/3.35TB/s vs 94GB/3.9TB/s；PCIe vs SXM 区分。
7. vLLM 0.30.0 版本可疑：Blackwell 需 CUDA 12.8；recipes 列 H100/H200/B200/MI300X/MI325X/MI355X；第三方列 B300/GB200/GB300/MI350X/MI355X；Blackwell INT8 kernel 限制需 FP8/NVFP4。
8. 显存容量 ≠ servable model size：未把显容量→可服务模型尺寸维度纳入筛选。
9. Groq/Cerebras 描述过宽：Groq=专用推理硬件+服务栈, 不是通用 CUDA/ROCm 替代; GroqCloud 目录仅列指定模型(Llama 3.1 8B/3.3 70B, GPT-OSS 20B/120B, Qwen 3.8 27B, Whisper 等)有模型级 token/s/价格/上下文/限额; 自定义权重/任意 HF 架构/特殊量化/多模态/自掌控数据面 ≠ 默认。Cerebras CS-4/WSE-3 Turbo 机柜级晶圆级专用; 托管模型 GPT-OSS 120B/Qwen 3.8 27B; 不能把"可部署硬件"/API/专用 endpoint 同一采购对象。
10. 三层分类修订: 单卡/8-GPU 通用节点(H100/H200/B200/B300/MI300X/MI325X/MI350X/MI355X) | NVLink 机柜级平台(GB200/GB300 NVL72 + HGX/DGX 8-GPU) | 专用推理系统/托管 API(Groq LPU/GroqCloud, Cerebras CS-4/WSE-3 Turbo/Cerebras Inference)。

## 反方"更稳健修订结论"
截至 2026-09, LLM 推理硬件不能按"GPU 型号单榜"选型。先按部署形态(单卡/8-GPU 通用节点 | NVLink 机柜级平台 | 专用推理系统/托管 API); 再在给定模型/精度/上下文/并发/SLO/地域/数据治理/交付周期/成本边界下比较。

## 反方"需补充核验清单"
目标模型清单(架构/参/稠密或MoE/权重精度/KV精度/最大上下文/多模态/LoRA/spec-decode); 真实流量画像(输入输出token比/并发/突发/P50-95-99 TTFT/ITL/端到端tokens/s/排队时延); 软件资格测试(指定 vLLM/SGLang/TensorRT-LLM/ROCm 版本, 加载/量化/KV cache/chunked prefill/TP-PP-EP/故障恢复/可观测); 同基准口径性能(同模型/量化/上下文/输出/并发/SLA, 分 prefill/decode/TTFT/ITL/总吞吐/利用率/P99); 成本口径(卡价+服务器+CPU/内存+NIC+交换机+存储+液冷+电力+机房改造+软件支持+运维+预留+折旧); 可获得性(日本/东京交付区域/云配额/OEM 交付期/保修/备件/液冷条件); 专用平台可移植性(目标模型是否已列入目录/私权重/context/数据驻留/限流/保留容量)。

## 来源
45 个来源(含 nvidia, rocm.docs.amd, console.groq, inference-docs.cerebras)。