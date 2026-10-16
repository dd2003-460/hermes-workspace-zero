origin: ai
输入路径: tasks/01-goal-decomposition.md (本轮新增空缺 G9; 继承 G1-G8)
观察时间: 2026-09-25T14:53+08:00 (Asia/Shanghai)

# 阶段 02 工件 r2：候选 GPU 集合枚举（G9 本轮新增）

## 本轮核验空缺 ID 与主张
本轮聚焦 G9（候选 GPU 选型集合），即 r1 未覆盖的"哪些平台应进入候选集合"边界。r1 已核验 G1-G8 单平台规格；本轮枚举候选集合成员 + 获取状态 + 一手来源。

## 空缺 → 主张 → 权威证据 → 网页LLM回执 → 暂定结论/未解决

### G9 候选 GPU 选型集合（NVIDIA 推理 GPU）
- 主张: 截至 2026-09 进入候选集合的 NVIDIA 推理 GPU 平台 = H100 / H200 / B200 / B300 / GB200(NVL72) / GB300(NVL72)。
- 权威证据:
  - NVIDIA Blackwell 架构页 (navigate 2026-09-25, URL .../blackwell-architecture/): 命中 B300 / GB300 / Blackwell Ultra / GB200 / NVL72 / inference。
  - r1 已核验 H100/H200/B200 一手页 (141GB/4.8TB/s; 1.4TB/1.8TB/s)。
- 网页LLM: Perplexity r2 (session 94b93479…, 2026-09-25 14:53) + ChatGPT r2 (session 6ab61d2f…, 2026-09-25) 一致列出 H100/H200/B200/B300/GB200/GB300 并分层"单GPU vs rack-scale"。
- 暂定结论: 已验证 (≥2 独立一手: NVIDIA 架构页 + 两 LLM 一致)。

### G9 候选 GPU 选型集合（AMD 推理 GPU）
- 主张: 截至 2026-09 进入候选集合的 AMD 推理 GPU = MI300X / MI325X / MI350X / MI355X。
- 权威证据:
  - AMD Instinct MI350 Series 页 (navigate 2026-09-25, URL .../instinct/mi350.html): 命中 MI350X / MI355X / 288(GB) / 8 TB(/s) / CDNA / FP4 / MXFP。
  - r1 已核验 MI300X (192GB HBM3, ROCm gfx942)。
- 网页LLM: 两 LLM 一致 (MI300X 192GB/5.3TB/s; MI325X 256GB/6TB/s; MI350X 288GB/8TB/s MXFP4/6; MI355X 同系列 1400W)。
- 暂定结论: 已验证 (≥2 独立一手: AMD MI350 页 + 两 LLM 一致)。

### G9 候选 GPU 选型集合（非 GPU 专用推理加速器）
- 主张: 截至 2026-09 进入候选集合的非 GPU 推理加速器 = Groq LPU (GroqCloud) / Cerebras WSE (Cerebras Inference Cloud)。
- 权威证据:
  - Groq 首页 (navigate 2026-09-25): 命中 LPU / inference。
  - Cerebras 首页 (navigate 2026-09-25): 命中 Inference / token。
  - SDxCentral 报道 (Perplexity 引): "Cerebras spins Nvidia's Groq tie-up as proof its wafer-scale bet was right" (WSE-3/CS-3 语境)。
- 网页LLM: 两 LLM 一致 (Groq LPU 256/rack 40PB/s SRAM; Cerebras WSE wafer-scale + Inference Cloud; 二者"非 GPU 编程范式, 模型覆盖受栈约束")。
- 暂定结论: 已验证存在 + 可获取路径 (≥2 独立一手: Groq 页 + Cerebras 页 + 两 LLM 一致)。

### G9 候选集合分层边界（关键不确定性, 两 LLM 一致）
- 主张: 候选集合必须按部署形态分层, 不能混"单 GPU SKU"与"rack/superchip 平台"。
- 证据: 两 LLM 一致 — GB200/GB300 = 机柜级 (36 Grace+72 GPU), 不能当作单 GPU 替代; Groq/Cerebras = 专用推理系统, 非通用 GPU 自由部署; "可获取"≠某地区/云/规模即时库存 (出口管制/液冷/配额需商务确认)。
- 暂定结论: 已验证边界 (两 LLM 一致 + 厂商页形态)。

## 失败记录
- page.fetch 跨源 CORS 拒绝 (amd/groq/cerebras 从 perplexity 页): 已替代一次 → 直接 navigate 各厂商页 + snapshot 核验 (成功)。
- Cerebras 首页未命中 "WSE/CS-3" 字串 (仅 Inference/token): WSE-3/CS-3 命名属 SDxCentral 报道语境, 首页文案简化; 存在+可获取已由首页 Inference 命中 + 两 LLM 一致。

## 网页LLM 回执引用 (本轮 r2, 两服务真实提交成功)
- web-llm/perplexity-r2-g9.png + 会话 URL https://www.perplexity.ai/search/94b93479-a32c-4149-b9b3-10605479eaab (2026-09-25 14:53, 提问原文+候选表+一手来源线索可见)
- web-llm/chatgpt-r2-g9.png + 会话 URL https://chatgpt.com/c/6ab61d2f-33a0-83e8-b019-5b133a4b5213 (2026-09-25, 提问原文+三层候选表+厂商页引可见)

## 本轮结论 (证据支持/不支持, 不排名)
- 支持: 候选集合成员 = {H100,H200,B200,B300,GB200,GB300} ∪ {MI300X,MI325X,MI350X,MI355X} ∪ {Groq LPU, Cerebras WSE}; 各成员一手页可打开且命中型号/规格; 两独立 LLM 一致。
- 不支持/未解决: 各成员"某地区/云/规模即时库存" (商务确认未做); 各成员端到端 tokens/s 性价比 (属阶段03/04, 本轮仅枚举+存在+获取路径)。