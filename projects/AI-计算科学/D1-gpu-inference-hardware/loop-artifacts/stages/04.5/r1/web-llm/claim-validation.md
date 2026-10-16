# Claim 交叉验证记录（04.5-r1）— 两腿 web-LLM（终版）

- 时间基准：ChatGPT 腿 observed_at 2026-09-17T13:07:29+08:00（模型 gpt-5.5 Instant, thinking xhigh）；Gemini 腿 observed_at 2026-09-17T23:10:24+08:00（模型 Gemini 3.1 Pro Preview / gemini-3.1-pro-preview, Thinking High, Grounded Search ON）。
- 提交口径：两腿提交**逐字相同**文本 `web-llm/submission-package.txt`（4333 B / 2728 chars），含 8 项 claim + 附件 A–E。
- 定位：LLM 回复 = **对抗审查信号**，不是权威事实源。两腿分歧 = 标记为对抗信号，**不自我裁决**。
- 本阶段允许的改动：标注 / 注记 / 口径收窄 / `llm_counter_evidence` 标记。**不静默改写 03 矩阵数值（Groq 严格不改数值）**。
- 证据链：`chatgpt-receipt.json` + `/Users/a1-6/workspace/project/2026-09-16-gpu-045-chatgpt.txt`；`gemini-receipt.json` + `/Users/a1-6/workspace/project/2026-09-16-gpu-045-gemini.txt`。回执 2/2。

## A. 逐项判定对照（8 项 claim × 两腿）

| # | Claim | ChatGPT 判定 | Gemini 判定 | 实质一致? | 处置方向 |
|---|-------|--------------|------------|-----------|----------|
| 1 | RTX 6000 Ada = 960 GB/s | 确认（NVIDIA 官方 PDF：48GB / 960 GB/s） | 确认（NVIDIA 官方 Datasheet [1]，48GB GDDR6 / 384-bit；ainery [2] 二手） | 是 | 关闭；03 加 source_ref（NVIDIA 官方） |
| 2 | A100 SXM4 FP16 Tensor 312；PCIe 156；2039/1935 GB/s；PCIe 无 NVLink | 数值基本确认：312/156 是 dense FP16（NVIDIA 页稀疏 624/312）；19.5=FP64 非 FP16；"PCIe 无 NVLink" 过绝对 → 应为 "NVLink Bridge ≤2 卡，非 SXM/HGX fabric" | 部分否定：SXM 312 / FP64 19.5 / 2039/1935 ✅，但判 **PCIe 版 FP16 Tensor 同为 312（156 是 TF32 值）**，且 PCIe 支持双卡 NVLink Bridge 600 GB/s | **否（数值直接矛盾）** | 03 加双腿分歧口径注记；两腿都认同的 NVLink 措辞修正采纳；156-dense 说法待 05 直接核验官方 datasheet |
| 3 | Cerebras WSE-3 = 4T transistors / 900K AI cores / 5nm | 确认（2024 官方发布资料 + 当前产品页）；须钉住名称 WSE-3/CS-3（WSE-3T/CS-4 已出现：250 PFLOPS / 43.2 PB/s） | 确认（官方 2024 发布会 [3] + TSMC 5nm [4]；附 44GB SRAM / 125 PFLOPS 当量） | 是 | 关闭；03 加 source_ref + 名称钉住注记 |
| 4 | H100 PCIe 80GB = 2040 GB/s（需第二来源） | 确认，第二来源 = ICPE 2026 论文 GPU spec table（"H100 PCIe — 80GB HBM2e — 2040 GB/s"）；2040≈2.04 TB/s，文献常取整 2.0 TB/s → source note 注明取整 | 否定：官方 H100 PCIe Product Brief 带宽 **2,000 GB/s (2 TB/s) HBM2e**；称 2040 系与 A100 SXM 2039 或其他规格混淆产生的错误值 | **否（数值直接矛盾）** | 维持 04.5 已记录的 **low_confidence**，不自我裁决；step 6 可选直接核验 + 05 复核 |
| 5 | RTX 5090 street price $4700–7000 | 部分确认：$4,700 证据强（TopCPU US median、StockX $4,001–6,999）；$7,000 仅高端/地区/第三方（StockX max、Tom's 3rd-party $6,500–9,500、PC Gamer ~$5,700、videocardprices 2026-09-15 $5,000）；**不构成统一"典型街价区间"**；矩阵单点保持 $5,000 | 确认：2026-09 第三方/黄牛**中位 $4,700–6,500**，极端 >$9,000（Tom's [7][10]、GPU Poet [8]）；"5090 基本从美国第三方零售消失"；反杀论：4090 二手 $1.6–1.8k、6000 Ada ~$6.8k 无黄牛溢价 | 部分（标签分歧：部分确认 vs 确认；中枢读数 $5.0k vs $4.7–6.5k） | 02.5 价格口径收窄："典型 $5k–6k，listing 可达 $7k+（US median 2026-09 已达 $4.7–6.5k）"；矩阵单点不变 $5,000 |
| 6 | MI300X ≈ $15k | 确认"约 $15k 有独立来源"，**非 AMD 官方 MSRP**（Citi 经 Tom's：大客户 ~$10k / 其他 ~$15k；Samsung Securities 2024 ASP $15,000；Moyan 2026 OAM $10k–15k indicative） | 确认：TrendForce / Silicon Analysts 2026-08 测算单芯片 $10,000–15,000（批量浮动）；AMD 不公开 MSRP；per-chip vs 8 卡板/双芯模块口径须分清 | 是 | 关闭为 "estimated street/ASP: ~$15k — non-official, independently reported estimate"；03 价格 source 标 estimate 型 |
| 7 | Apple M4 Max 546 GB/s | 确认（Apple 官方新闻稿 "up to 546GB/s"；芯片规格页下线不影响） | 确认（Apple 官方技术规格 [11]：满配 16C CPU/40C GPU = 546 GB/s；旧 32C-GPU SKU = 410 GB/s） | 是 | 关闭；口径 "up to 546 GB/s"；03 加 source_ref |
| 8 | Groq LPU = 20 TB/s + 96GB SRAM | **否定**：官方 GroqChip Product Brief v1.7 = 230 MB SRAM/chip + up to 80 TB/s on-die；Argonne workshop 同口径（230 MB / 80 TB/s / 750 TOP/s INT8 / 188 TFLOP/s FP16）；230MB≠230GB 差三个数量级 | **证据不足**（"高度疑似 AI 幻觉或拼接数值"；96GB 疑误挂 AWS Trainium2 的 96GB HBM；可核验官方口径同为 230 MB / 80 TB/s）。另含未引源子声明"Groq 3 LPU（Rubin-2026）500MB/150TB/s"——无来源，不采纳 | 标签分歧（否定 vs 证据不足）；**实质口径一致**（旧值 20TB/s+96GB 双双被判疑） | 03 矩阵 Groq 条目 `llm_counter_evidence` 标注（**不改 96 / 20000 数值**）→ 05 复核改值；未引源子声明仅记录 |

## B. ChatGPT 三处 [!] 修正指令 → 处置

1. A100 PCIe "无 NVLink" → "可通过 NVLink Bridge 双卡互连，但不具备 SXM/HGX 600 GB/s NVLink fabric" → **回退 03 矩阵加语义注记**（03 critical_notes；Gemini 腿同向佐证，采纳为注记而非数值改动）。
2. RTX 5090 $4700–7000 → "当前典型约 $5k–6k；历史/特殊 listing 可达 $7k+"；矩阵单点保持 $5,000 → **回退 02.5 证据口径收窄**（价格备注；单点数值不变）。
3. Groq 20TB/s+96GB → 删除旧值，改为 230MB SRAM + up to 80TB/s → **回退 03 矩阵：本阶段只 mark `llm_counter_evidence`（不改数值）**，数值改写留 05 复核（硬约束：不改 Groq 数值）。

## C. Gemini 腿：判定明细与 red-team（新增对抗信号）

### C.1 逐项判定（Gemini，引用标号 [1]–[12] 对应页脚来源）

1. RTX 6000 Ada 960 GB/s — **确认**：NVIDIA 官方 Datasheet PDF [1]（48GB GDDR6 / 384-bit，960 GB/s）；ainery.co.za [2] 二手印证。
2. A100 — **部分否定**：SXM4 FP16 312 ✅ / FP64 19.5 ✅ / 2039 & 1935 GB/s ✅；**错误点一**：声称 "A100 PCIe 版 FP16 Tensor 同样为 312 TFLOPS（无稀疏），156 实为 TF32 值"（引 [3][4] NVIDIA HPC 页）；**错误点二**：A100 PCIe 支持双卡 NVLink Bridge（600 GB/s），"无 NVLink" 表述错误。→ 与 ChatGPT 腿及 04 矩阵 156 值**数值级直接矛盾**（见 D1）。
3. Cerebras WSE-3 — **确认**：2024 官方发布会 [3]：4T transistors / 900K AI cores / TSMC 5nm [4] / 44GB on-chip SRAM（算力当量 ≈125 PFLOPS B200 口径）。
4. H100 PCIe 80GB — **否定**：官方 Datasheet [5] + H100 PCIe Product Brief [6] = HBM2e，带宽 2,000 GB/s (2 TB/s)；称 2040 为混淆值。→ 与 ChatGPT 腿（ICPE 2026 2040）**数值级直接矛盾**（见 D2）。
5. RTX 5090 街价 — **确认**（但自述口径更强）：2026-09 第三方/黄牛中位 **$4,700–6,500**，极端（特定 AIB 型号）**>$9,000**；成因：AIC 板卡断货 + 矿潮后遗症 + AI 需求挤占；"5090 基本从美国第三方零售消失"（Tom's [7][10]、GPU Poet [8]）。
6. MI300X ~$15k — **确认**：TrendForce / Silicon Analysts 2026-08 报告测算单芯片 $10,000–15,000（批量浮动），AMD 不公开 MSRP [9]；澄清 per-chip 口径 vs 双芯模块/8 卡板。
7. M4 Max 546 GB/s — **确认**：Apple 官方技术规格 [11]：满配 M4 Max（16C CPU / 40C GPU）= 546 GB/s；较早 32C-GPU SKU = 410 GB/s；MacBook Pro / Mac Studio 满配一致。
8. Groq 20TB/s+96GB — **证据不足（疑似 AI 幻觉/拼接）**：无官方/权威来源显示单卡 96GB SRAM；第一代 GroqChip 单卡 **230 MB SRAM（对应 80 TB/s on-die）**（引 [11][12] flopper/fitmyllm 转述）；"96GB" 疑误挂 **AWS Trainium2 96GB HBM** 容量。
   - **未核实子声明（仅记录，不采纳）**：本腿称 "最新 Groq 3 LPU（集成 2026 NVIDIA Rubin 平台版本）单片 500 MB SRAM / 150 TB/s" —— 无任何可核验来源（两腿均未独立支撑），本身即 LLM 断言。

### C.2 Gemini red-team 三点（vs ChatGPT 腿的差异标注）

- **①（新增，ChatGPT 腿未提）MI300X "70B 单卡最佳" = 物理性无效前提**：MI300X 为 **OAM 形态、无标准 PCIe**，必须 8 卡 HGX/OAM 专用机箱；"8 卡 MI300X + HGX 机箱整体采购成本远超 $15,000 单卡价…估算突破 $30,000 以上" → "单卡 ~$15k" 的 $/tok 分母**系统性忽略系统级附加成本**。Gemini 认为工作站内可跑的 70B 仅 Mac Studio M4 Max 128GB / 2×PCIe RTX 6000 Ada。→ 注：03 矩阵 MI300X 条目 form_factor 字段本身已标注 "OAM (8-GPU HGX / dual-SXM package)"，该信号与既有矩阵注记同向，但 $/tok 口径问题未在任何矩阵行解决 → 05 research_required。
- **②（与 ChatGPT 腿独立同向）RTX 5090 街价是 best_overall 翻转数字**：US 第三方 median $6,500+，$7,000 时 $/tok 塌陷；**RTX 4090 以 $1.6–1.8k 稳定二手价"彻底反杀"5090；RTX 6000 Ada（~$6.8k MSRP，无黄牛溢价）击败 $7,000 的 5090**。ChatGPT 腿的对应论点更温和（$4,700 证据强 / $7,000 非典型区间）。
- **③ H100 PCIe 带宽陷阱（新角度）**：H100 PCIe 仅 2,000 GB/s **< A100 SXM 2,039**，而 $25k vs A100 PCIe 二手 ~$8k ≈ 3× 价格、无带宽增益；decode 是 memory-bound → H200 4,800 GB/s 明确更优；H100 PCIe 作为 70B 多卡方案的疑问（跨节点 NVLink Bridge vs H200 NVL 的 NVSwitch）。→ 该论点同时依赖 D2 的 2000 GB/s 值（两腿矛盾点），一并带不确定性传递。

## D. 两腿分歧清单（对抗信号，不自我裁决）

| 编号 | Claim | 立场 A（ChatGPT） | 立场 B（Gemini） | 分歧性质 | 落点 |
|------|-------|-------------------|------------------|----------|------|
| D1 | #2 A100 PCIe FP16 Tensor | **156 TFLOPS = dense FP16**（稀疏 312；NVIDIA 页星号=sparsity，读法 dense 156/312） | **312 TFLOPS**（称无稀疏；156 实为 **TF32** 值；SXM/PCIe 的 TF32 均 156） | **数值级直接矛盾**（156 的身份：dense FP16 vs TF32） | 不裁决。03 加口径注记（两腿对 SXM 312 / FP64 19.5 / 2039&1935 / NVLink-Bridge≤2 卡 无分歧，均采纳为注记）；156 归属待 05 直接核验 A100 官方 datasheet 表格 |
| D2 | #4 H100 PCIe 80GB 带宽 | **2040 GB/s 确认**（第二来源 = ICPE 2026 论文 GPU spec table；NVIDIA 页常写 ~2.0 TB/s，2040 为资料表精确值） | **2000 GB/s 官方值**（NVIDIA H100 Datasheet + PCIe Product Brief），称 2040 为与 A100 SXM 2039 的混淆值 | **数值级直接矛盾**（2040 vs 2000） | 不裁决。矩阵维持 2040 + **low_confidence**（沿用 04.5 已有状态）；step 6 可选直接核验；05 复核；两腿来源均已记录在各自证据文件 |
| D3 | #5 RTX 5090 街价 | 部分确认；$4,700–7,000 **不是**统一典型区间；典型 ~$5k–6k，单点 $5,000 | 确认 $4,700–7,000 区间；US median 已达 $4,700–6,500，极端 >$9,000 | 标签 + 中枢读数分歧（方向一致：远离 MSRP $1,999） | 不裁决中枢值。02.5 采用双方交集口径："典型 $5k–6k，US median 2026-09 $4.7–6.5k，listing 可达 $7k+，极端 >$9k"；矩阵单点不变 $5,000；"4090/6000 Ada 反杀" 作为对抗信号记入 05 |
| D4 | #8 Groq 旧值 | **否定**（官方 Product Brief v1.7 230 MB + up to 80 TB/s） | **证据不足 / 疑似 AI 幻觉**（官方口径同为 230 MB / 80 TB/s） | 标签分歧，**实质口径一致**（旧值 20TB/s+96GB 均被判疑；官方口径两腿相同） | 03 矩阵 `llm_counter_evidence` 标注（双腿反证，标注强度最高的一项）；不改数值；05 复核改值 |
| D5 | MI300X "70B 单卡" 分母（Gemini 独有新增） | （未提出形态论）ChatGPT 腿的对应论点 = 容量 claim 高置信 + 吞吐 claim 需同口径 benchmark 复验 | MI300X = OAM、无标准 PCIe、需 8 卡 HGX/OAM 机箱 >$30k，"单卡 ~$15k" 分母不成立 | 单方新增对抗信号 | 03 MI300X 条目加 form-factor/机箱成本口径注记；05 research_required（按 "OAM 机箱口径" 重算 $/tok 分母） |

## E. 异议 → 处置映射表（objection mapping，终版）

| LLM 异议（腿） | 处置 | 理由 |
|----------------|------|------|
| Groq 20TB/s+96GB 规格否定（官方 230MB+80TB/s）（两腿，D4） | 回退 03 矩阵：`llm_counter_evidence` 标注（**不改数值**） | 官方 Product Brief v1.7 + Argonne 双口径一致（ChatGPT 腿）；Gemini 腿独立同向 + 疑点溯源（Trainium2 HBM 误挂）。反证强度两腿叠加最高；按流程 04.5 不静默改写 03 数值 |
| A100 dense(312/156) vs sparse(624/312) 口径（ChatGPT 腿）+ PCIe FP16=312/156=TF32（Gemini 腿，D1） | 回退 03 矩阵：加 dense/sparse/TF32 三列口径注记 + "156 身份两腿矛盾，待 05 官方 datasheet 直接核验" 标记 | 数值本身争议在列定义歧义；注记不动数值；矛盾照录 |
| A100 PCIe NVLink 表述过绝对（两腿同向） | 回退 03 矩阵：NVLink 字段语义注记（≤2 卡 NVLink Bridge 600 GB/s，非 SXM/HGX fabric） | 两腿独立同向，采纳为措辞注记 |
| H100 PCIe 2040 vs 2000（两腿矛盾，D2） | **维持 04.5 已记录 low_confidence，不改值**；step 6 可选直接核验 + 05 复核 | 两腿来源冲突且互指对方混淆；本环节不自我裁决 |
| RTX 5090 街价区间收窄 + 单点 $5,000（ChatGPT 腿）+ median $4.7–6.5k / 极端 >$9k + 4090/6000 Ada 反杀（Gemini 腿，D3） | 回退 02.5：价格备注收窄为交集口径，矩阵单点不变 $5,000；反杀论点记入 05 对抗信号 | 区间端点证据强度不均；单点值两腿不矛盾（$5,000 均有价格追踪支持） |
| MI300X OAM 形态 / 8 卡机箱 >$30k → "70B 单卡" 分母存疑（Gemini 独有，D5） | 回退 03：MI300X 条目加 form-factor/系统级成本口径注记 + **05 research_required**（按 OAM 机箱口径重算 $/tok 分母） | 单方新增但触及 03 矩阵已有 form_factor 注记；不裁决，05 复核 |
| 5841 / 140 / 317 tok/s 可比性（ChatGPT 腿） | Stage 05 research_required（统一 benchmark protocol 后重验：workload/batch/seq-len/quant/runtime/prefill-decode 定义） | $/tok 与单卡/多卡结论对 benchmark 口径敏感度高于对价格的敏感度；附件 D 已承认 prefill/decode 10–70× 差异 |
| best_overall=5090 不稳健（权重和 0.90、9/11 不可复现、重算 H200 65.75>5090 62.5）（ChatGPT 腿，与项目 04 自身审计一致） | 维持阶段 04 已记录的降级结论（UNRESOLVED / framework-sensitive） | 项目自身审计已发现，LLM 独立复证，不重复处置 |
| H100 PCIe "3× 价格无带宽增益 / decode memory-bound" 论点（Gemini 腿） | 随 D2 一并传递至 05（依赖 2000 值，带不确定性）；不在本环节单独处置 | 论点成立性依赖两腿矛盾中的带宽值 |
| "Groq 3 LPU 500MB/150TB/s (Rubin-2026)" 未引源子声明（Gemini 腿） | **仅记录，不采纳**（进入 05 时若被引用须先独立核验） | 无两腿可核验来源，本身即 LLM 断言 |
| **用户（委托人）2026-09-17 实质性异议：15 卡候选池缺口** — ① V100 SXM2 8 卡 NVLink 多卡服务器（DGX-1 代、二手/退役价）；② 魔改/二手卡梯队（P40 24G 魔改、V100 32G 二手、3090/4090 魔改等）——对"本地部署 7B/70B 性价比"高度相关（70B 多卡尤其） | **回退 02.5（补证据调研）/ 05（扩池决策）**；04.5 为复核阶段，**不现场扩池、不改写矩阵候选范围** | 用户异议属对候选池完备性的实质性异议，与 LLM 腿异质性不同：记录在册，不新增设备条目、不试图在本轮证明现有池已完备。Reviewer 若按阶段 prompt 判"结论超出证据/候选池缺口"，`revise`→02.5 是预期正确结果。① 的先行直查（浏览器内 Bing，非 WebSearch）结果见 `web-llm/step6-direct-checks.md`（found/not-found 如实记录） |

## F. 开放项状态更新（对应 submission-package 附件 E，截至本轮两腿核验）

- **H100 PCIe 2040 GB/s**：两腿直接矛盾（ChatGPT/ICPE-2026=2040 vs Gemini/NVIDIA-Brief=2000）→ **维持开放**（两源冲突不可在本环节裁决），low_confidence 沿用。
- **RTX 5090 街价**：收敛为交集口径 "典型 $5k–6k（US median 2026-09 $4.7–6.5k），listing 可达 $7k+，极端 >$9k"；矩阵单点 $5,000 不变。开放项 → 口径调整后视同收敛（单点值不冲突）。
- **MI300X ~$15k**：两腿一致（独立 estimate 存在、非 AMD MSRP）→ **关闭**，source type = estimate / reported ASP（TrendForce/Silicon Analysts 2026-08、Citi、Samsung Securities 2024）。
- **Groq 规格**：两腿实质一致反证 230 MB SRAM + up to 80 TB/s → **llm_counter_evidence 已标记**（03），数值改值留 05 复核。
- **Apple M4 Max 546 GB/s**：两腿一致（Apple 官方 "up to 546 GB/s"；满配 vs 旧 SKU 410 GB/s 已区分）→ **关闭**，口径 "up to"。
- **SambaNova SN3000**：两腿均未新核验（submission 附件 E 含、claim 1–8 未含）→ **维持 research_required**。
- **RTX 4090D 区域价差**：两腿未单独展开 → **维持开放**（附 Gemini 反杀论点中 4090 二手 $1.6–1.8k 作为输入，未验证不采纳为规格）。

## G. 处置与置信度建议（供 Step 5 字段更新引用）

- 回执：**2/2**（ChatGPT + Gemini，两腿逐字同文本）。
- 8 项 claim 汇总：实质一致关闭 4（#1 #3 #6 #7）；标签/口径分歧但实质一致 2（#5 #8）；数值级直接矛盾 2（#2 #4）+ 单方新增对抗信号 1（MI300X OAM 形态，D5）。
- 建议字段处置：`research_required` → **`inferred`**（已有两独立 LLM 腿证据 + 部分多源关闭项，但 #2/#4 矛盾未解、Groq 改值未做、MI300X 分母口径未定——不足以 confirmed，也不再缺证据到 research_required 程度）；置信度 0.5 → **0.65**。
- 依据逐条落点：#1/#3/#6/#7 → 03 source_refs；#2/#4 → 03 口径注记 + low_confidence 沿用 + 05；#5 → 02.5 口径收窄；#8 → 03 llm_counter_evidence（不改值）+ 05；D5/5841-140-317 tok/s → 05 research_required；best_overall → 维持 04 降级结论。
