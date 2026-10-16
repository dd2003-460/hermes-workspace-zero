origin: ai

# 阶段 04.5 最终复核 — 网页 LLM 交叉验证交接工件（D1-gpu-inference-hardware / 04.5-r1）

- **执行角色**：最终复核执行 subagent（executor-045-c，第 3 位执行者；前两位因 API 中断退出）。按阶段文件（`/Users/a1-6/Desktop/workspace/loop/1-loop/main-8.7-loop/04.5-final-review.md`，已全文读并对齐）：站在反方检查从原始任务到阶段 04 的完整证据链；不掩盖问题，不自行推进状态。
- **generated_at**: 2026-09-18T07:52:13+08:00（Asia/Shanghai）
- **输入路径（全部已读取并核对）**：
  - 任务契约：`/Users/a1-6/Desktop/workspace/loop/1-loop/main-8.7-loop/04.5-final-review.md`（**全量阶段 prompt 已读并对齐 = 是**）
  - 字段任务：`loop-artifacts/stages/04.5/r1/tasks/04.5-r1-field-01-cross_validation_out-6b42d6e860.json`
  - 两腿提交包：`loop-artifacts/stages/04.5/r1/web-llm/submission-package.txt`（4333 B，ChatGPT / Gemini 逐字一致提交）
  - ChatGPT 回执：`loop-artifacts/stages/04.5/r1/web-llm/chatgpt-receipt.json`（24948 B，8 项齐全）；规范证据 `/Users/a1-6/workspace/project/2026-09-16-gpu-045-chatgpt.txt`（20280 B，观察时间 2026-09-17T13:07:29+08:00，模型 gpt-5.5 Instant xhigh）
  - Gemini 回执：`loop-artifacts/stages/04.5/r1/web-llm/gemini-receipt.json`（21747 B，8 项齐全）；规范证据 `/Users/a1-6/workspace/project/2026-09-16-gpu-045-gemini.txt`（10101 B，观察时间 2026-09-17T23:10:24+08:00，模型 gemini-3.1-pro-preview，Thinking High，Grounded Search ON）
  - 逐 claim 裁定记录：`loop-artifacts/stages/04.5/r1/web-llm/claim-validation.md`（两腿最终版）
  - 历史 0/3 失败回执（对照用）：`loop-artifacts/stages/04.5/r1/web-llm/09a5f82306c1dcea.json`
  - 阶段 03 矩阵：`loop-artifacts/stages/03/r1/artifacts/hardware-comparison-matrix.json`；阶段 04 验证报告：`loop-artifacts/stages/04/r1/evidence/stage04-verification-report-r1.md`
- **观察时间汇总**：ChatGPT 2026-09-17T13:07:29+08:00；Gemini 2026-09-17T23:10:24+08:00。回执 2/2。
- **留痕声明**：本次访问运行在用户已登录的可见浏览器（ego task space 继承登录态），两条对话均已持久化到用户账号历史（ChatGPT `chatgpt.com/chat` 侧栏、Gemini AI Studio `/library` "Created by you"），凭回执中的最终 URL 可随时打开复核。这是可追溯特性，不是匿名/无痕。

## 1. 原始任务逐项回应

原始任务（阶段 01 字段 `systematic_gpu_research_for_local_llm_inference`）：**系统性 GPU 调研——覆盖主流数据中心 GPU、消费级 GPU、新兴架构、边缘方案，为本地 LLM（7B/70B）推理选型提供决策依据**；背景事实（established_facts：NVLink Gen5 ~900 GB/s、PCIe 4.0 x16 ~32 GB/s、RTX 4090 24 GB GDDR6X、H100 80 GB HBM3、KV cache 是主要内存瓶颈、量化可降显存）；阶段 01 另列 8 项 data_needing_verification。

逐项回应：

1. **原始目标（系统性调研→选型决策依据）**：部分达成。15 卡矩阵覆盖数据中心/消费级/新兴架构/边缘四类（NVIDIA 8 卡 + AMD MI300X + Apple M4/M4 Max + Groq LPU + Cerebras WSE-3 + SambaNova SN3000）；阶段 04 验证报告 L4 外部复核当时 3/15、来源可追溯性 FAIL（全项目 0 HTTPS）。本轮两腿核验：8 项待核 claim 中 **4 项实质关闭**（#1 RTX 6000 Ada 960 GB/s、#3 Cerebras WSE-3 4T/900K/5nm、#6 MI300X ~$15k 三方一致估计口径、#7 M4 Max "up to" 546 GB/s）、**2 项标签分歧但实质一致**（#5 5090 市价、#8 Groq）、**2 项硬数值矛盾未解**（#2 A100 PCIe FP16：156 密集 vs 312/156=TF32；#4 H100 PCIe 带宽：2040 vs 2000），并记录 1 项 Gemini 单边新信号（D5，MI300X OAM 机箱）与**用户 2026-09-17 候选池缺口异议 B**。即：LLM 对抗审查发现的新问题如实登记并路由，不掩盖、不自行裁定。
2. **背景事实（established_facts）**：两腿证据未与其直接矛盾；唯 A100 "NVLink" 语义需收窄——PCIe 卡是 NVLink **Bridge**（≤2 卡），SXM/HGX 才是 600 GB/s fabric，两腿同向修正，已作 03 口径注记（见第 3 节可追溯表 A100 行）。
3. **8 项 data_needing_verification**：状态见 `claim-validation.md` §A（8/8 已逐腿核查）；其中 H100/A100 数值矛盾、SambaNova SN3000（两腿未新增独立核验）、RTX 4090D 区域价差仍属未解/未覆盖，全部进入第 5 节未完成项。
4. **用户（委托人）2026-09-17 异议 B（候选池完备性，实质）**：15 卡矩阵缺 ① V100 SXM2 8 卡 NVLink 多卡服务器（DGX-1 代、二手/退役价）② 魔改/二手卡梯队（P40 24G 魔改、V100 32G 二手、3090/4090 魔改）——对"本地部署 7B/70B 性价比"（尤其 70B 多卡）高度相关。**已按契约写入 `claim-validation.md` §E 异议映射表（末行）与本文件第 4/5/6 节 → 路由"回退 02.5（补证据调研）/ 05"**；04.5 为复核阶段，不现场扩池、不改写矩阵候选范围、不试图在本轮证明现有池已完备。先行直查（浏览器内 Bing）结果见 `web-llm/step6-direct-checks.md`。
5. **网页 LLM 门禁（Ego Lite 真实浏览器、≥2 独立服务、真实回执、逐字一致文本）**：满足 2/2——ChatGPT（chatgpt.com，对话页 `6aaa79ee-e968-83e8-8f52-709f43ec44c3`）+ Gemini AI Studio（`prompts/1tXyPz9SOPALLQM_sxQ4MK60KOKBSQU0l`，library 持久化已验证）。未使用 API/WebSearch/WebFetch/`ralph ... web-llm`/模型记忆替代；本轮及 step-6 直查的检索一律走浏览器内 Bing（DDG 在此网络不通，WebSearch 在本环境会幻觉）。
6. **协议纠正（契约增补 A）落地**：role = 最终复核执行 subagent；本文件头 = `origin: ai` + 输入路径 + 观察时间；六节按"最终交接工件"指定顺序；两份回执逐条对齐 8 个可审计回执项（服务 / 最终 URL / 时间与时区 / 准确提交内容 / 可见回答或失败原文 / Ego 观察或截图引用 / 提出的反例 / 采纳与拒绝理由）；收尾动作 `task.finish({keep: ["p1"]})`（保留 ChatGPT 对话页可见）。

## 2. 最终结论及其适用边界

**立场（非"最终通过"）**：15 卡矩阵在"规格速查 + 口径标注"层级可作本地 7B/70B 推理选型的决策输入；**截至本轮，其中 2 项规格数值存在两腿直接矛盾、1 项（Groq LPU）两腿均给出官方口径反证但未改值**。按阶段文件"LLM 回复是对抗审查信号，不是权威事实源"，未解决的矛盾保持 `low_confidence` / `llm_counter_evidence` 标注并路由 05，不由复核阶段强行闭合。

**阶段 04 分工作负载三推荐的本轮复核风险**（04 报告：L1 $/tok 重算 22/22 PASS；L2 排名一致性 FAIL；L3 加权框架 FAIL；L4 3/15 PARTIAL；Overall Confidence 0.72；Go/No-Go = **CONDITIONAL GO**，4 项前置条件）：
- **7B 最佳 → RTX 5090**：本轮两腿均确认 5090 实际成交价远超 $1,999 MSRP（ChatGPT：typical ~$5k–6k、listing 可达 $7k+；Gemini：US 中位 $4.7–6.5k、极端 >$9k），且 Gemini 腿提出 **4090 二手 $1.6–1.8k 与 6000 Ada ~$6.8k 对 5090 的"反杀"论点**（未裁定，登记为对抗信号）。best_overall 价格敏感度高风险仍在。
- **70B 多 GPU 最佳 → H200**：H100 PCIe 带宽 2040 vs 2000 矛盾外溢到 Hopper 谱系口径（D2）；H200 本体本轮未新增数值争议，但 04 报告 L3（权重和 0.90、9/11 total 不可复现、H200 65.75 > 5090 62.5 翻转 best_overall）未修复前，任何 best_overall 都不可复现。
- **70B 单 GPU 最佳 → MI300X**：**D5（Gemini 腿）指出 MI300X 为 OAM 形态、无标准 PCIe，需 8 卡 HGX/OAM 机箱（系统成本 >$30k）→ "单卡 ~$15k" 的 $/tok 分母不成立**；$15k 本身三来源一致但均为估计/ASP 口径非 MSRP（TrendForce/Silicon Analysts $10–15k、Samsung Securities ASP $15,000）。已作 03 口径注记 + 05 补全研究项，未改矩阵值。

**字段处置（`cross_validation_out`）**：`research_required` → **`inferred`**，confidence 0.5 → **0.65**。依据见第 5 节。**绝不**记为 `confirmed` / "最终通过"。

**适用边界（本结论只支持以下用法）**：
- 支持：15 卡内规格/价格/性价比的相对层级速查与口径对照；02.5/03/05 后续阶段可直接引用本工件的口径注记。
- 不支持 / 不得引用为定论：① Groq LPU 矩阵值（20 TB/s + 96 GB）——两腿官方口径均为 **230 MB SRAM + up to 80 TB/s on-die**（GroqChip Product Brief v1.7），矩阵值存疑、已标 `llm_counter_evidence`、值未改（冻结至 05）；② A100 PCIe FP16 定值（156 密集 vs 312 稀疏/156=TF32，D1，待 05 官方 datasheet 裁决）；③ H100 PCIe 带宽定值（2040 [ICPE 2026] vs 2000 [官方 brief]，D2，保持 low_confidence）；④ MI300X "单卡 $/tok"（OAM 机箱口径未闭合，D5）；⑤ 候选池外任何卡（含异议 B 的 V100 8 卡服务器、魔改/二手梯队）——属**未调研**，不是"证据显示其不适用"。

## 3. 结论 → 阶段 02/02.5 证据 → 阶段 03 节点 → 阶段 04 实际结果的可追溯表

路径前缀 `P = /Users/a1-6/Desktop/workspace/projects/D1-gpu-inference-hardware/loop-artifacts/stages`；"实际结果"取自 `P/04/r1/evidence/stage04-verification-report-r1.md`（2026-09-09）。

| 结论簇（本工件立场） | 阶段 02 证据 | 阶段 02.5 证据 | 阶段 03 节点 | 阶段 04 实际结果 → 04.5 状态 |
|---|---|---|---|---|
| C1 规格表（bandwidth/显存/精度）含 A100、H100、RTX 6000 Ada、Cerebras WSE-3 | `P/02/r1/fields.json` + `P/02/r1/web-llm-request-1..8.json`（per-device 任务文件） | `P/02.5/r1/cross-validation.json` + `P/02.5/r1/web-llm/d3f72cc11c2b5be5.json` | `P/03/r1/artifacts/hardware-comparison-matrix.json`（15 卡） | 04：外部复核 3/15 PARTIAL → 04.5 两腿确认并回填 6 处官方口径修正（RTX 6000 Ada 960 GB/s、A100 SXM4 FP16-T 312 / 带宽 2039、A100 PCIe FP16 156 / 带宽 1935 / 移除 NVLink-fabric）；**残余 D1（A100 PCIe 156 身份）、D2（H100 2040 vs 2000）未解 → 05** |
| C2 消费级市价（5090 溢价、4090/4090D） | 同 C1（RTX-5090、RTX-4090D 任务文件） | `P/02.5/r1/cross-validation.json`（summary：RTX 5090 规格确认、价格=零售溢价 MSRP $1,999 vs $4,700+，confidence 0.95→0.90） | 矩阵 `NVIDIA RTX 5090 / 4090 / 4090D` + `cost-performance-analysis.json` | 04：L4 记"5090 溢价"未解决 → 04.5 D3（两腿标签分歧、实质一致：区间 $4.7–6.5k 中位、可达 $7k+、极端 >$9k）+ Gemini 4090/6000-Ada 反杀论点登记 |
| C3 定价类（MI300X $15k）与 OAM 形态 | `P/02/r1/web-llm-request-3.json`（AMD-MI300X 任务） | `P/02.5/r1/cross-validation.json`（MI300X 规格确认） | 矩阵 `AMD MI300X`（本轮新增 OAM 形态/系统成本口径注记） | 04："$15k 无来源"列入未解决 → 04.5 #6 关闭为**三方一致独立估计口径**（非 MSRP）+ **D5 OAM 机箱 >$30k → "单卡 $/tok" 分母存疑 → 05 research_required** |
| C4 新兴/超算路线（Groq、Cerebras、SambaNova） | `P/02/r1/web-llm-request-4.json`（Groq-Cerebras-SambaNova 任务） | 未单列 | 矩阵 `Groq LPU / Cerebras WSE-3 / SambaNova SN3000`（本轮新增 Groq 两腿 `llm_counter_evidence` 注记） | 04：Cerebras 未核 → 04.5 #3 两腿关闭（官方硬件页 404 退役，二级源 4T/900K/5nm）；**#8 Groq 两腿均反证矩阵值（230MB/80TB/s，Product Brief v1.7）→ 标记、值冻结**；SN3000 两腿未新增核验 → 仍开放 |
| C5 苹果/边缘（M4、M4 Max、Jetson） | `P/02/r1/web-llm-request-6.json`（Jetson-Apple-Silicon 任务） | 未单列 | 矩阵 `Apple M4 Max / Apple M4` + `edge-solution-boundaries.md` | 04：边缘未核 → 04.5 #7 两腿确认 "up to" 546 GB/s（apple.com 芯片页 404 退役，Mac Studio 规格页现仅列 M5 Max 460 GB/s） |
| C6 基准口径与 LLM 推理基准 | —（阶段 01 established_facts 已给方法论事实） | `P/02.5/r1/web-llm/cross-check-synthetic.json` | `P/03/r1/artifacts/benchmark-methodology.md` + `cost-performance-analysis.json` | 04：L4 未解决"7B tok/s 5841 单源"、基准方法论 10–70x 差异 → 04.5 两腿同向复述：5841 tok/s 是 **prefill** 口径，decode ~140–317，$/tok 最敏感单一参数 → 保留 02.5/05 优先级 |
| C7 成本模型与 final recommendations（L1 输入） | 各 price web-llm-request | `P/02.5/r1/cross-validation.json`（summary 价格侧） | `cost-performance-analysis.json` + `decision-framework.json` + `coverage-proof.json` | 04：L1 22/22 PASS / **L2 排名一致性 FAIL / L3 加权框架 FAIL（best_overall=5090 不稳健，H200 65.75>62.5）** → 04.5 结论：L3 修复前 best_overall 不可复现，CONDITIONAL GO 4 项前置条件原样保留、本轮不代为修复 |

## 4. 两个以上 Ego Lite 网页 LLM 回执和异议处置表

### 4.1 回执（2/2，逐项对齐阶段文件 8 项可审计字段）

| # | 服务 | 最终 URL（对话页，用户可打开复核） | 时间与时区 | 准确提交内容 | 可见回答 / 失败原文 | Ego 观察 / 截图引用 | 提出的反例 | 采纳 / 拒绝理由（摘） |
|---|------|------|------|------|------|------|------|------|
| 1 | **ChatGPT**（chatgpt.com，账号 璐 lu，免费档） | `https://chatgpt.com/c/6aaa79ee-e968-83e8-8f52-709f43ec44c3`（p1 保留可见） | 2026-09-17T13:07:29+08:00（Asia/Shanghai）；模型 gpt-5.5 Instant xhigh | `submission-package.txt` 4333 B 逐字（`_chatgpt-user.txt` 4340 B 含提交壳记录） | 14284 B 全文（`_chatgpt-answer.txt`；规范证据 20280 B 含页头元数据），无失败原文 | Ego 观察：登录态确认→提交→轮询至响应稳定；截图 `web-llm/chatgpt-p1-prompt-submitted.png`（111792 B，prompt 已入框）；历史页 `chatgpt.com/chat` 侧栏标题出现 = 持久化已验证 | 7 项（详见回执 `counter_examples`）：A100 156=dense/312=sparse 修正、H100 2040=ICPE 2026 实测源、5090 市价区间、Groq 官方 230MB/80TB/s、5090 "基本消失"表述的保留、OAM 机箱论点（Gemini 侧同向）、Mi500/MI500U 256GB 前瞻性信息（仅记录） | 采纳 4（#1 #3 #6 #7 对应佐证 + Groq 反证登记）；拒绝 0 条关键值修改；A100/H100 数值矛盾**不裁定**，双向记录（D1/D2）→ 05 |
| 2 | **Gemini (AI Studio)**（aistudio.google.com，账号 高殷巷 yinxianggao1@gmail.com） | `https://aistudio.google.com/prompts/1tXyPz9SOPALLQM_sxQ4MK60KOKBSQU0l` | 2026-09-17T23:10:24+08:00（Asia/Shanghai）；模型 gemini-3.1-pro-preview，Thinking High，Grounded Search ON | 同文（逐字一致，`_gemini-user.txt` 记录） | body 5831 字符 / 8641 B（规范证据 10101 B 含页头元数据）；**截图不可用**（AI Studio 页 `page.screenshot` CDP 超时，按协议以 URL + 文本文件为正式证据） | Ego 观察：登录态确认→提交→轮询完成；library 持久化已验证（"GPU硬件选型与指标校验 \| Created by you" 出现于 `aistudio.google.com/library`） | 7 项（回执 `counter_examples`）：A100 PCIe FP16=312/156=TF32（**与 ChatGPT 腿冲突，D1**）、H100 2000 GB/s 官方 brief（**D2**）、5090 US 中位 $4.7–6.5k + 极端 >$9k + 4090/6000-Ada 反杀（D3 标签分歧）、Groq 96GB 疑误挂 AWS Trainium2 96GB HBM（#8 两腿同实质反证）、OAM 8 卡 HGX >$30k 系统成本（D5）、MI300X 5 来源定价表、未引源 "Groq 3 LPU 500MB/150TB/s"（仅记录不采纳） | 采纳 5（#1 #3 #6 #7 佐证 + #8 反证登记 + OAM 口径注记）；拒绝 3（"A100 FP16=312" 不单独采纳——与另一腿矛盾；未引源 Groq 3 声明不采纳；Mi500 前瞻数据仅记录） |

两腿分歧登记（对抗信号，**不自行裁定**，完整字段见两份回执 `two_leg_disagreements` 与 `claim-validation.md` §D）：**D1** A100 PCIe FP16（156 密集 vs 312/156-TF32）｜**D2** H100 PCIe 带宽（2040 vs 2000，保 2040 + low_confidence）｜**D3** 5090 市价标签（部分确认 vs 确认，实质区间重叠）｜**D4** Groq 标签分裂（"官方否定" vs "疑似 AI 幻觉/证据不足"——实质同为矩阵值被官方口径推翻，按 05 `llm_counter_evidence` 标记、**96/20000 数值冻结**）｜**D5** MI300X OAM 机箱（Gemini 单边，03 口径注记 + 05）。

### 4.2 异议处置表（LLM 腿异议 10 条 + 用户异议 1 条；全文与理由见 `claim-validation.md` §E）

| 异议（来源腿） | 处置路由 | 一句话理由 |
|---|---|---|
| A100 SXM FP16 应为 19.5 疑传抄（ChatGPT） | **回退 03 口径注记**（已记 03：19.5=FP64-Tensor、1950/195 TF32、312 dense FP16） | 两腿一致认定 312 正确；04.5 只记录不擅改 03 |
| A100 SXM NVLink 600 GB/s = 双向 fabric 口径（Gemini） | **回退 03 口径注记** | 数值不矛盾，补 fabric/die-to-die 语义 |
| A100 PCIe FP16 = 312 / 156 实为 TF32（Gemini）↔ 156=dense（ChatGPT） | **D1 双向记录 → 05 官方 datasheet 裁决** | 两腿硬冲突，04.5 不裁定 |
| A100 PCIe 带宽 1935 实为 fabric 总量、非 2000/2039（Gemini） | **回退 03 口径注记 + 05** | 记录 fabric 总量解释，不覆盖现值 |
| Groq 官方 230 MB SRAM + up to 80 TB/s on-die（两腿，Product Brief v1.7） | **03 `llm_counter_evidence` 标记，值冻结至 05** | 两腿同实质反证矩阵 96 GB/20 TB/s；改值属 05 决策 |
| 5090 美国第三方零售基本消失 / 中位 $4.7–6.5k / 极端 >$9k / 4090-6000Ada 反杀（Gemini） | **登记对抗信号 → 02.5 交叉价格口径** | 与 ChatGPT 腿区间重叠（D3 标签分歧）；影响 best_overall 价格敏感性 |
| "Groq 3 LPU 500MB/150TB/s (Rubin-2026)" 未引源子声明（Gemini） | **仅记录，不采纳** | 无两腿可核验来源，本身即 LLM 断言 |
| MI300X OAM、无标准 PCIe、8 卡 HGX >$30k、"单卡 $15k" $/tok 分母不成立（Gemini，D5） | **03 形态/系统成本口径注记 + 05 research_required** | 单边新信号，机制上合理，不否认 ~$15k 卡片估计值本身 |
| Mi500/MI500U 256 GB 前瞻性条目（ChatGPT） | **仅记录，不采纳入矩阵** | 2026-09-17 时刻尚未 GA/在售 |
| **用户（委托人）2026-09-17 异议 B：候选池缺口 ① V100 SXM2 8 卡 NVLink 多卡服务器（DGX-1 代、二手/退役价）② 魔改/二手卡梯队（P40 24G 魔改、V100 32G 二手、3090/4090 魔改）** | **回退 02.5（补证据调研）/ 05（扩池决策）；04.5 不现场扩池** | 对本地 7B/70B 性价比（70B 多卡）高度相关；本轮只登记不扩池；Reviewer 若判"候选池缺口"，revise→02.5 是**预期正确结果**，本轮不证明现有池完备。① 先行直查见 `web-llm/step6-direct-checks.md`（found/not-found 如实） |

## 5. 薄弱点、未完成项、残余风险、置信度及其依据

**薄弱点（本证据链自身）**：
1. **D1（A100 PCIe FP16）与 D2（H100 PCIe 带宽）为硬数值矛盾且本轮无官方 datasheet 级一手裁定**——两腿是 LLM 信号，方向相反（或同向但溯源不同：ICPE 2026 论文 vs 官方 brief）。2040 的解释本身也存疑（可能是 fabric/bus 合成值或 A100 SXM 2039 混淆），2000 可能是官方舍入口径。**保留 low_confidence 是正确的弱态，不是拖延**。
2. **Groq 矩阵值（96 GB / 20 TB/s）与两腿官方口径（230 MB / 80 TB/s）数量级冲突但值未改**——按契约冻结至 05；在此之前该卡的任何推理类结论（tok/s、$/tok）均不可用。
3. **基准可比性是 $/tok 的最敏感单一参数**：5841（prefill）vs 140–317（decode）跨 10–70×，两腿同向复述；03 `benchmark-methodology.md` 已记，但 04 L3 框架 FAIL（权重和 0.90、9/11 total 不可复现、best_overall 翻转风险）未修复，**best_overall=5090 当前不可复现**。
4. **Gemini 腿截图不可用**（CDP 超时，AI Studio 已知坑）——正式证据为对话 URL + 规范文本文件 + library 持久化验证，接受该降级并如实记录。
5. **LLM 腿的"确认"仍是信号**：除直接给出官方/一手源 URL 的条目外，两腿一致本身不构成 confirmed（例如 5090 区间、MI300X 定价三方均为媒体/渠道估计）。

**未完成项（进入 05 / 回退 02.5 的清单）**：
- A100 PCIe FP16 身份（156 密集 vs TF32/稀疏口径）——05 官方 datasheet 直接核验。
- H100 PCIe 带宽 2040 vs 2000——05 双源并列保留或裁定。
- Groq 值改判（230 MB / 80 TB/s 口径）——05。
- MI300X OAM 系统成本口径（> $30k 机箱）与 $/tok 重算——05（research_required 挂起）。
- SambaNova SN3000 规格（两腿未新增独立核验；官方规格页缺失）——维持 research_required。
- RTX 4090D 区域价（$1,600 vs CN ~$1,835）——05 区域价格条目。
- **异议 B：V100 SXM2 8 卡 NVLink 多卡服务器（DGX-1 代）二手/退役价 + 魔改/二手卡梯队（P40 24G 魔改、V100 32G 二手、3090/4090 魔改）的完整证据链**——回退 02.5 补证据调研（step-6 已先行直查 V100 英文/中文源，见 `step6-direct-checks.md`），扩池与否由 05 决策。

**残余风险**：价格/ASP 数据点时滞 1–2 个月（2026-08/09 渠道口径）；4090 二手与 6000 Ada 的"反杀"若成立将动摇 7B 最佳推荐，但该论点是 LLM 单边信号、未进入任何矩阵计算；候选池缺口（异议 B）意味着**当前矩阵对"极致性价比本地 70B 多卡"这一最痛场景可能系统性高估新机路线成本**。

**置信度及其依据**：字段处置 `research_required → inferred`，**0.5 → 0.65**。
- 比 0.65 高不了的缘故：2 项硬数值矛盾未解（D1/D2）+ 1 项官方口径反证未改值（Groq）+ 1 项候选池完备性质疑（异议 B）+ best_overall 框架不稳健（继承 04）。
- 高于 0.5（旧 research_required）的缘由：门禁从 0/3 回执升至 **2/2 真实浏览器回执**（8 项字段齐全、留痕可复核）；8 项 claim 中 4 项实质关闭 + 2 项标签分歧实质一致并拿到可核查 URL；03 已落 6 处口径修正与本轮新增注记；失败模式（旧 0/3 因 prompt box 不可用）已定位且绕过。
- 与 04 自报 0.72 的关系：0.72 针对"本地重算层 + 分工作负载推荐（3/3 成立 0.75）"，本复核**不推翻**之；但对外交接的整体置信度降为 0.65——复核阶段暴露的矛盾优先级高于此前自评。

## 6. 最有价值的下一步和需要回退的真实阶段（如有）

**需要回退的真实阶段：`02.5`（补证据调研）与 `05`（裁决/改值）。** 按契约增补 B：**若 Reviewer 判"结论超出证据 / 候选池缺口"，`revise`→02.5 是预期正确结果；04.5 为复核阶段，不现场扩池、不改写矩阵候选范围、不试图在本轮证明现有池已完备。**

最有价值的下一步（按价值排序）：
1. **回退 02.5：补齐异议 B 证据**——① V100 SXM2 8 卡 NVLink 多卡服务器（DGX-1 代）二手/退役价（step-6 先行直查已执行，`web-llm/step6-direct-checks.md` 记录 found/not-found）；② 魔改/二手卡梯队（P40 24G 魔改、V100 32G 二手、3090/4090 魔改）的价位 + 70B 实测吞吐/功耗/多卡互联（NVLink Bridge 语义限制须一并调研）。此项对"本地部署 7B/70B 性价比"决策价值最高：DGX-1 代 8 卡 V100 32G 二手（~$256 GB HBM2 聚合）若单价低于新机路线，70B 多卡推荐可能整体改向。
2. **回退 05：数值裁决与改值**——A100 PCIe FP16 官方 datasheet 裁决（D1）；H100 2040/2000 双源处理（D2）；Groq 值改判（230 MB/80 TB/s，D4）；MI300X OAM 系统成本口径与 $/tok 重算（D5）；SN3000 官方规格或显式剔除；4090D 区域价条目。
3. **回退 02.5 + 03 修复联动**（04 报告 CONDITIONAL GO 前置条件 ①–④ 原样有效）：decision_framework 权重归一（否则 best_overall 可能翻 H200）；rankings_7b + score_percentile 自洽；12 设备补 HTTPS 来源或显式降 low_confidence（本轮已为其中多项提供可核查 URL，见 `claim-validation.md` §A）；MI300X 定价来源/剔除。
4. **05 前完成 5090 价格交叉口径收口**（"typical $5k–6k" ∩ "中位 $4.7–6.5k，listing 可达 $7k+，极端 >$9k"），并重估 best_overall 价格敏感性（含 4090 二手 / 6000 Ada 反杀情景，作为 What-if 而非结论）。

**收尾动作**：本工件 + 全部留痕写盘完成后，ego task space 以 `task.finish({keep: ["p1"]})` 关闭（保留 ChatGPT 对话页 p1 可见供用户复核；p2 已释放）。本阶段**不写"最终通过"**，字段最终状态 `inferred / 0.65` 由主 Agent 通过 `ralph field-apply` 合并（执行者不运行 ralph 命令）。
