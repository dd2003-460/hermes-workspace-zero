# Step 6 — 直接核查（executor-045-c）

- 执行时间：2026-09-18（+08:00），ego-browser v2，task space `gpu-llm-cross-verify 04.5`，页面 `p2`
- 约束：≤3 项核查 × 各 ≤2 次尝试 × 20s 超时；检索走 bing.com（DDG 全变体网络不通）；
  记录到 **域名+日期+摘要** 级别；Bing 结果链接为 `ck/a` base64 跳转、多数解码失败 →
  **只记录成功解码的精确 URL，绝不编造 URL**
- 顺序按 增补 B：第 1 顺位 V100（委托人异议 B 直查）；Groq 官方规格页降为第 2 顺位；H100 2040 佐证不变顺位
- 状态说明：本文件随每步完成增量写盘；`[进行中]` 项在完成后回填

---

## 核查 1（第 1 顺位，增补 B 指定）：8× V100 32GB SXM2 NVLink 8 卡服务器 二手价格

- **查询 1A（EN）**：`8x V100 32GB SXM2 NVLink 8-GPU server used price 2026` → **found**（第 1 次尝试成功）
- **查询 1B（ZH）**：`V100 32G 八卡服务器 二手 价格` → **found**（第 1 次尝试成功）

EN 结果（域名+日期+摘要，节选）：

| # | 域名 | 日期（页面标注） | 摘要 |
|---|------|------------------|------|
| 1 | eBay.com | 2026-09-06 | "AI Deep Learning NVIDIA V100 8x 32GB SXM2 GPU Server" — 在售 listing，"We have hundreds of servers in our eBay…"（在售活跃） |
| 2 | eBay.com | 2026-08-14 | "DEEPSEEK 70B 671B AI Server 8 Way GPU 8x Nvidia V100 32GB SXM2 GPU (with NVLink cluster capabilities). 100% Good and Working" — 8 卡 NVLink 服务器，二手良好状态 |
| 3 | unixsurplus.com | 未标 | "2U Deep Learning AI Server 8 Way GPU 8x V100 32GB … Inspur NF5288M5 — featuring 8x NVIDIA Tesla V100 32GB SXM2 GPUs"（整机商在贩） |
| 4 | unixsurplus.com | 未标 | "Inspur NF5288M5 GPU Server 8x Nvidia V100 32GB SXM2 … high-speed NVLink interconnects, dual Intel …"（整机商在贩） |
| 5 | zhihu（专栏） | 未标 | "NVIDIA Tesla V100 32GB 价格演变研究（2017—2026）" — 系统梳理 V100 32GB 2017 发布至 2026-04 完整价格轨迹的研究文章（中文二手价走势一手综述） |
| 6 | servers.com | 未标 | "Nvidia DGX-1 - 8x Volta V100 HMB2 GPU NVLink Server" — "Servers are tested and benchmarked by us prior to shipping"（DGX-1 原厂形态 8 卡 NVLink 服务器，翻新测试在贩） |
| 7 | taobao.com | 2026-09 更新 | "v100卡32g - Top 100件" 淘宝热卖清单（中文二手单卡生态活跃） |
| 8 | ubrcental.com | 未标 | "Used DEEPSEEK 70B 671B AI Server 8 Way GPU 8x …"（海外二手整机） |

ZH 结果（域名+日期+摘要，节选）：

| # | 域名 | 日期（页面标注） | 摘要 |
|---|------|------------------|------|
| 1 | taobao.com | 未标 | "NVIDIA Tesla V100 SXM2 32G 计算卡，二手原装拆机卡"（SXM2 单卡二手） |
| 2 | zhihu（专栏） | 未标 | 同 EN#5 价格演变研究（2017—2026 完整轨迹） |
| 3 | ebay.com (cn) | 未标 | NVIDIA Tesla v100 全品项（全新/二手） |
| 4 | v2ex.com | 2025-07-10 | "低价出 tesla v100 32g pcie" — 出 13 片 V100 32G，"定制版那种，sxm3 改 pcie 的"（**魔改卡梯队直接信号**） |
| 5 | 台世风/二手指南站 | 2026-07-03 | "2026 Tesla V100 32GB 二手顯卡避坑指南：價格分析、散熱…" — 依据 2026 Q1–Q2 台湾二手论坛及拍卖平台的合理价区间分析 |
| 6 | taobao.com | 未标 | "浪潮NF5468M5 V100 32G SXM2 … 8卡GPU服务器"（8 卡整机在售） |
| 7 | ebay.com | 未标 | "Tesla V100 32GB for sale"（eBay 汇总） |
| 8 | goofish（闲鱼） | 未标 | 闲鱼二手平台（单卡 C2C 生态） |

**核查 1 结论：found。** 委托人异议 B ①②（V100 SXM2 8 卡 NVLink 多卡服务器 + 魔改/二手梯队）
**经直查确认在二手/翻新市场真实存在且 2026 年仍活跃在售**：eBay（2026-08-14 / 2026-09-06 活跃 listing）、
servers.com（DGX-1 原厂 8 卡 NVLink 翻新）、unixsurplus.com（Inspur NF5288M5 整机）、
中文生态（淘宝/闲鱼/V2EX 魔改卡/8 卡整机）+ 中文价格轨迹综述（知乎，2017—2026）。
→ **支持"候选池不完整"异议成立方向**，维持路由『回退 02.5（补证据调研）/ 05（扩池决策）』；
本轮不扩池、不改矩阵。注：Bing 摘要级不含具体成交价（价格在各 listing 页内，超出本步"域名+日期+摘要"级别），
具体价格带收集归入 02.5。

---

## 核查 2（第 2 顺位，原 Groq 官方规格页）：groq.com 官方 LPU 规格

- 尝试 1：`groq.com` @ domcontentloaded → 页面 SPA 未在提取时刻渲染正文，innerText 提取为空对象（**未获得官方口径数字**）
- 尝试 2：`groq.com` @ load + 轮询 → 浏览器 CDP 轮次挂起（进程 CPU≈0，超过 12 分钟未返回），终止进程
- 尝试 2 重跑（计入同一尝试顺位，全有界 20s/13s）：再次挂起，终止进程
- **结论：未完成（未执行到可提取状态）**。groq.com 对当前 ego CDP 会话持续挂起，超出"各 ≤2 次尝试"预算；
  不在本步再开新尝试，也不改用其它途径替代（禁 WebFetch/其它 API）。
- 处置：矩阵 Groq 行 96/20000 **维持 frozen**，两腿 LLM 官方口径反例（230 MB SRAM + up to 80 TB/s，
  GroqChip Product Brief v1.7）继续挂 `llm_counter_evidence` 标记，裁决归 05。本步未新增任何 Groq 数值证据，未改任何值。

## 核查 3（第 3 顺位，H100 2040 第二佐证）：Bing `NVIDIA H100 PCIe 80GB HBM3 memory bandwidth 2040 GB/s`

- 结果：**found（部分）— 二级来源簇存在，但摘要级无与 2040 精确相等的独立确认**（第 1 次尝试成功）

| # | 域名 | 日期（页面标注） | 摘要（要点） |
|---|------|------------------|--------------|
| 1 | runpod.io | 未标（"2026" 专题） | "NVIDIA H100 GPU: Specs, VRAM, Price & Benchmarks (2026)" — 80GB HBM3, SXM vs PCIe 规格汇总（摘要未显式带宽数字） |
| 2 | spheron.network | 2026-05-20 | "NVIDIA H100 Specs (2026): 80GB HBM3, 3,958 TFLOPS … **3,350 GB/s** memory bandwidth, 989 FP16 …" — **注意：3,350 GB/s 为 SXM 口径**（H100 SXM 通约 3,350–3,352），该站未分 PCIe/SXM 口径，不可作为 PCIe 2040 佐证 |
| 3 | h100higher.com（HKG 零售商） | 未标 | "NVIDIA H100 GPU PCIe Display Card 80GB"（Hopper 架构，PCIe 形态产品页，摘要无带宽数字） |
| 4 | itctshop.com | 未标 | "NVIDIA H100 80GB | Overview and Key Specifications" — Transformer Engine/FP8 概述，摘要无 PCIe 带宽数字 |
| 5 | techpowerup.com（GPU Database） | 2022-03-23 | "NVIDIA H100 PCIe 80 GB Specs … 80 GB **HBM2e** … connected using a **5120-bit** memory interface" — 数据库级第二来源：PCIe=HBM2e+5120-bit（与 ~2,040–2,048 GB/s 量级相容），**摘要未显示精确 GB/s 数** |
| 6 | nvidia.com（官方产品页） | 未标 | "For LLMs up to 70B (Llama 2 70B), the PCIe-based NVIDIA H100 NVL with NVLink bridge…" — 官方页强调 H100 **NVL**（2-GPU NVLink bridge）变体 |
| 7 | hyperscalers.com | 未标 | "Accelerated servers with H100 … 3 terabytes per second (TB/s)" — 系统级营销口径（整机聚合），非单卡 |
| 8 | baike.baidu.com | 未标 | H100/H200 百科条目（Hopper 两代概述，摘要无 PCIe 精确带宽） |

**核查 3 结论：** 二级来源确认 H100 **PCIe 形态 = HBM2e + 5120-bit**（TechPowerUp），数值上落在
2,000（官方 brief 口径）— 2,040（ICPE 2026）— ~2,048（数据库惯例）的同一区间，**但没有在摘要级独立读出
精确 "2040"**；Spheron 的 3,350 GB/s 是 SXM 口径、不可用于 D2 佐证。→ **D2 硬矛盾（2040 vs 2000）在本步
维持未裁决**，矩阵 H100 PCIe bandwidth=2040 保持 + low_confidence 保留，归 05 裁决。

---

## Step 6 总结

| 核查 | 顺位（增补 B） | 状态 | 对结论的影响 |
|------|----------------|------|--------------|
| V100 8 卡 SXM2 服务器二手（EN+ZH） | 第 1 | **found** | 委托人异议 B 直查成立方向 → 维持路由回退 02.5/05，本轮不扩池 |
| Groq 官方规格页 | 第 2 | 未完成（CDP 挂起，超预算，已如实记录） | 无新证据；Groq 96/20000 frozen，llm_counter_evidence 标记维持 → 05 |
| H100 PCIe 2040 第二佐证 | 第 3 | found（部分，无精确 2040 独立确认） | D2 维持未裁决 → 05 |

- 第 4 槽（MI300X ~$15k 佐证）**未使用**：3 槽已满且前 3 项为增补 B 指定顺序。
- 全部 URL 仅记录 `ck/a` 成功解码到的域名（eBay/unixsurplus/servers/techpowerup/runpod/spheron/nvidia/taobao/v2ex/baike 等）+ 日期 + 摘要；解码失败的未列精确 URL；**无编造 URL**。
- 全程仅用 p2；p1（ChatGPT）只读未动；无 ChatGPT 重新提交。
- 下一步：`task.finish({keep: ["p1"]})` 收尾（保留 ChatGPT 对话页可见）。
