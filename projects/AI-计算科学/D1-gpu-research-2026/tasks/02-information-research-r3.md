origin: ai
输入路径: 反方异议(04.5-r2 O1-O5) → 一手核验回02
观察时间: 2026-09-25T16:30+08:00 (Asia/Shanghai)

# 阶段 02 r3 工件：一手核验反方-flagged 规格（回02 repair）

## 触发
04.5-r2 Reviewer=revise→回02: 两独立反方LLM(Perplexity+ChatGPT)一致确认 B300/MI350X/MI355X/vLLM版本已在官方页可一手核验, 原"未核验"过度保守→显排序"仅MI350X领先"materially wrong。

## 一手核验结果（Ego Lite 浏览器, 官方页）

| 事实 | 一手来源(URL) | 一手原文/数值 | 状态 |
|---|---|---|---|
| B300 单GPU显 | nvidia.com GB300 NVL72 | "72 Blackwell Ultra GPUs... GPU Memory 20TB" → 20TB/72≈288GB/GPU; "1.5x larger HBM3E" vs Blackwell(192×1.5=288✓) | 一手✓(推算) |
| B300 带宽 | nvidia.com GB300 NVL72 | "GPU Bandwidth Up to 576 TB/s" → 576/72=8TB/s/GPU | 一手✓(推算) |
| B300 形态 | nvidia.com GB300 NVL72 | "rack-scale... 72 GPU + 36 Grace, NVLink 130TB/s, 17TB LPDDR5X" | 一手✓(rack非单卡) |
| HGX B300 显(冲突) | nvidia.com HGX | "Total Memory 2.1TB"(8GPU)→262.5GB/GPU | ⚠️与GB300 288GB冲突→边界 |
| MI350X/MI355X 显 | rocm.docs.amd mi350.html | "8 stacks of 12-Hi HBM3E... 288GB total (36GB/stack)" | 一手✓ |
| MI350X/MI355X 带宽 | rocm.docs.amd mi350.html | "HBM3E at 8 Gbps, up to 8 TB/s peak" | 一手✓ |
| MI350P 显/带宽 | rocm.docs.amd mi350.html | "4 HBM3E stacks, 144GB, up to 4 TB/s" | 一手✓ |
| MI350X/355X TDP | rocm.docs.amd mi350.html | MI350X 1000W air / MI355X 1400W liquid / MI350P 600W PCIe | 一手✓ |
| MI300X 带宽 | rocm.docs.amd mi300.html | "peak memory bandwidth 5.3 TB/s" | 一手✓ |
| MI325X 支持 | rocm.docs.amd compat-matrix | "MI325X (gfx942)" supported | 一手✓(存在) |
| MI325X 显/带宽 | — | AMD产品页404(bot-blocked), 仅LLM口径256GB/~6TB/s | ❌未一手→边界 |
| vLLM 版本 | docs.vllm.ai | "v0.30.0"(latest) | 一手✓(LLM怀疑错, 0.30.0正确) |
| vLLM Blackwell CUDA | docs.vllm.ai gpu.html | "Blackwell(B200,GB200) require min CUDA 12.8"; default CUDA 12.9 | 一手✓ |
| vLLM 厂商支持 | docs.vllm.ai | "NVIDIA GPUs, AMD GPUs, x86/ARM/PowerPC CPUs" | 一手✓ |
| vLLM per-GPU(MI325X/350X/355X/B300) | — | 安装页仅"compute cap≥7.5(e.g. H100,B200)", 不枚举 | ❌未一手→边界 |

## 一手修正结论（仅一手✓）
- 显排序(单GPU HBM, 一手): MI350X/MI355X(288GB) ≈ B300(288GB, GB300推算) > MI325X(256GB, 未一手) > MI300X(192GB) > B200(180GB) > H200(141GB) > H100(80GB)。
- 带宽排序(一手): MI350X/MI355X/B300(8TB/s) > MI300X(5.3TB/s) > H200(4.8TB/s) > H100(3.35TB/s); B200 8TB/s(官方页口径)。
- 反方"仅MI350X领先"修正: B300同288GB/8TB/s tier(一手GB300推算) → 排序需含B300。
- vLLM: 0.30.0一手✓(反方怀疑错); Blackwell需CUDA≥12.8一手✓; 厂商支持一手✓; per-GPU枚举未一手→边界。

## 边界（未一手, 不补造）
- B300 单GPU显: GB300推算288GB vs HGX 262.5GB 冲突→需NVIDIA B300 datasheet(未一手)。
- MI325X 256GB/~6TB/s: AMD产品页bot-blocked→仅LLM口径, 未一手。
- vLLM per-GPU(MI325X/MI350X/MI355X/B300): 安装页不枚举→边界。

## 证据协议
一手URL+原文+时间(2026-09-25 16:30+08); 一手✓项≥1一手官方页; 未一手留边界不补造。

## Reviewer 判定
`review: 02-r3 | first-hand-verify | pass | 反方-flagged B300/MI350X/MI355X/vLLM版本一手核验完成(nvidia GB300+rocm mi350+docs.vllm); 一手✓修正排序含B300同tier(B300一手推算, GB300 rack一手fetched); 未一手(MI325X精确/vLLM per-GPU/B300单GPU显冲突)留边界不补造; 一手URL+原文+时间列 | 修复阶段: 无(本维度通过; 边界属后续一手需)`