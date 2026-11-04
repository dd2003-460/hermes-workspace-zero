# F10-R5 / 阶段 02 — 资料搜集与网页 AI 交叉询问

# origin: ai (成璐 2026-11-05 r290 派发)
# 阶段: 02-information-research（`loop/prompt-first/02-information-research.md`）
# 观测日: 2026-11-05（UTC 17:45-17:58）| 分支: arena/f10-gas-dynamics-research

---

## 0. 通道状态（必须先记，否则等于伪造成交）

| 通道 | 状态 | 证据 |
|---|---|---|
| **ego-browser + 网页 LLM 交叉询问** | ❌ **不可用** | 本 runtime 无 `ralph` 可执行文件、无 `ego-browser`、无任何 LLM 站点登录态（`loop/ralph_runtime` 仅有 pyproject，无 runner）。按 02 §2 规定"通道未配置快速失败 → 记录完整失败原因后继续公开网页资料搜集，不得等待或循环重试" |
| `curl` / `wget` | ❌ **全部阻断** | 对 fred.stlouisfed.org / home.treasury.gov / stablecoins.llama.fi / api.coingecko.com 四个域各 1 次，均 `OpenSSL SSL_connect: SSL_ERROR_SYSCALL`，`http=000` |
| `fetch_page`（HTTP 直取） | ✅ 可用 | FRED CSV / Deribit JSON / CoinGecko JSON / DefiLlama JSON / Fed HTML 均成功取回 |
| `web_search` | ✅ 可用 | 用于 Q1 文献线索，结论一律回到出版方/机构页面直核 |

> **降级声明**：02 阶段的"网页 LLM 交叉询问"一步**未执行**，原因是通道不存在而非跳过。替代路径 = 每个关键主张取 ≥2 个**不同发布方**的一手页面（出版方/机构/arXiv），并在 02.5 做对抗核验。conf 全局降一级处理（任务书【失败降级】第 1 条允许）。

---

## 1. 空缺逐项回应

### G1 · macro 对 crypto 的**无条件**日频可预测性 → **弱**

- **S9**（2025, "A Comprehensive Look at Bitcoin Return Predictability"）：141 个变量中 67 个样本内显著，**仅 29 个**在至少一个 horizon 有 OOS 增益，**仅 4 个**在所有 horizon 胜过随机游走；按类别，"跑赢基准"的比例为 技术类 32.2% / 基本面 16.7% / 情绪 18.8% / **宏观 5.6%**。
- **S8**（UCLouvain 2026 硕士论文，510 次周频 OOS 预测）：宏观-金融块对已含 crypto-native 变量的模型**无增量**，在线性族中甚至**显著变差**；8 组配置**无一**击败历史均值。
- **S2**（Nakagawa & Sakemoto 2023, Applied Finance Letters 11:146-158）：从约 100 个宏观指标抽公共因子的动态因子模型，**季度**频率上公共因子与 crypto 预期收益强相关（1 SD 产出因子 → BTC −13.1%），**月度不显著**；单个宏观指标（通胀、货币供应）均不显著。
- **判定**：无条件日频大概率不可交易。**但** S2 提示"宏观信息存在，只是时间尺度在季度" —— 这与 F10 的 4h-24h 持有期差 2-3 个数量级，是 **horizon mismatch** 而非"宏观无信息"。

### G2 · **核心**：宏观状态下微观信号才有效的交互证据 → **几乎没有；最接近的一条，条件变量不是宏观**

- **S5 · Shek (2026) "Conditional Arbitrage Capacity: Evidence from Crypto Perpetual Funding Rates"（SSRN 7520320，2026-09-24）** ← 全文检索里唯一**正面**测"funding 反转是否条件有效"的论文
  - 样本：BTC/ETH/SOL，2021-2026，**274 次 funding 极端事件**（另覆盖 13 币）
  - 结果：**上涨日**的事件 24h 反转 **+1.88%**；**下跌日**的事件 24h **继续 −1.74%**
  - 差距 **+3.62pp**，block bootstrap 95% CI **[2.60, 4.67]**；扣除 funding 后 +3.59pp
  - 稳健性：围绕 7 次外生市场冲击，±30 天窗口内 7/7 为正（sign test **p=0.00781**），合并估计 **+6.47pp** [4.45, 8.86]；12 个"年×方向"格、13 币一致
  - **关键限定**：条件变量 = **当日价格方向**，不是任何宏观变量。作者提出的状态变量是"conditional arbitrage capacity"（资本水平 × 市场是否顺/逆套利资本）
  - conf：**中低**（单人 SSRN 预印本、未经同行评审；但效应量大、CI 窄、稳健性检验充分）
- **S13 · Pindza (2026) Digital Finance 8:48**（同行评审，开放获取）：CEX-DEX funding 套利按 **GARCH 波动率三分位**分层，funding spread 的持续性参数随 regime 变化；funding 风险 + 市场风险合计 >50% 的策略方差。
  - 只支持"regime 分层在 funding 上有结构"，**未测**"regime 使某个信号从无效变有效"
- **判定：G2 = 无直接先例。** 目前最强的交互证据（S5）成立，但其条件变量是**快变量（当日方向）**，不是慢变量（宏观）。这正是本调研最重要的单条发现。

### G3 · 宏观对 crypto **波动/成交量**（非方向）的预测力 → **有，且比方向强得多**

- **S3**（arXiv 2302.10252）：FOMC 2018-01→2022-12 事件研究，意外加息 1pp → BTC **−26.33%**、ETH **−30.28%**（5% 显著）；除两大币外的市场**不显著**；5 分钟波动在公告日**至少翻倍**。
- **S4**（FRL 2026, 41 次 FOMC 2021-01→2026-01，Coinbase 小时线）：公告后一小时 BTC 平均 |r| 0.66%→**1.25%**（Δ=**0.59pp**, t=**3.77**, p=0.00053），美元成交量 **2.54×**；ETH Δ=0.65pp、**2.81×**；matched-week 安慰剂后仍 Δ=0.44/0.50pp。
- **S6**（arXiv 2604.01431, Kalshi 宏观合约, 2023-01→2026-03）：Fed-dovish 信号预测 BTC **波动** 样本内 t=3.63（调整 R² 14.1%→15.5%），但**样本外 MSFE=1.009（失败）**；衰退风险信号 OOS **MSFE 0.979**（Clark-West p=0.020）；**渠道特异性**：BTC 对货币政策、altcoin 对 CPI 反应；作者明确诊断为 **regime dependence**（信号只覆盖 2024-2025 降息周期）。
- **判定**：把目标从"方向"改成"带宽/风控"有实证支撑（与 F10-R4 主判据弱 PASS 方向一致）；但 S6 表明**单 regime 集中会让 OOS 崩掉**，这与 F10-R4 的"增量 0.002-0.011 但方向 13-15%"同构。

### G4 · "条件效应"的载体是否必须为宏观 → **不必；价格/状态类条件已在加密上成立**

- **S11**（ACFR/AUT, TSMOM in crypto）：TSMOM 最优 28d lookback / 5d hold，Sharpe **1.51** vs 市场 0.84；**只在市场 bullish 时持多**；"bad state"下系数**始终不显著**；空头腿普遍亏损。
- **S12**（FRL 2025, "State transitions and momentum effect in cryptocurrency market"，经 S7 引用段获取）：crypto 动量**只在 UP–UP regime** 出现，其他状态转移会抑制；作者归于信念更新不对称。
- **S7**（Chang et al. 2023 FRL）：**VIX 水平不预测** crypto 动量溢价，**EPU 也不预测**，只有 **VIX premium**（VIX 期货隐含 − 现货）显著预测未来 1 与 3 个月动量溢价。
- **判定**：条件化本身有效，但**有效的条件变量都是"快变量或价格衍生量"**（当日方向、价格状态、波动率风险溢价），不是我们原本设想的 DGS10/DXY 慢变量。

### G5 · 事件效应的方向 vs 波动分解

- 方向：**S3** 给出显著负效应（对意外收紧）；但 2026 年后的复现研究（S4 引述的一段 FOMC 事件研究综述）指出"实际利率变动、政策方向类别、非对称幅度**都不能稳健解释**事件窗口收益，而 **VIX 变化**在多个窗口显著负相关"——即**方向效应主要来自风险情绪，不是利率决议本身**。
- 波动/量：**S3/S4** 双重确认（≥2 独立来源，不同数据源：NYXBT vs Coinbase）。
- **对 Q3 的含义**：H 假设若押"方向"，应押 **VIX/风险情绪** 而非 **利率意外**；若押"带宽"，S3/S4 已足够支撑，但那是 F10-R4 已试过的路。

### G6 · 链上 vs 宏观的冗余度 → **链上占主导，宏观增量接近零**

- **S8**：crypto-native（链上）变量在场时，宏观块**无增量且拖累线性模型**。
- **S-补充**（2026, "Bitcoin forecasting with machine learning and on-chain information", Southern African Journal 系）：SHAP/permutation importance 显示**链上变量占总贡献约 50%**，而 **VIX 等传统市场指标相关性有限**。
- **判定**：这正是 F7 的翻版风险（funding 与 basis ρ=−0.31~−0.39 → 无增量）。**加宏观很可能重蹈 F7。**

### G7 · 已在 2022-2025 窗口存活的宏观因子

- **S1**（Liu-Tsyvinski-Wu 2022, JF 77(2):1133-1177）：crypto 三因子 = **市场 + 规模 + 动量**；宏观因子**未进入**该模型。
- **S10**（IMF GFSR Note 2022/01 + GFSR 2023-01）：BTC 与 S&P500 相关性从 2017-19 的近 0 升至 2020-22 的 **≈0.4**（约 4 倍），股权→crypto 的波动溢出 **+16pp**；2023-2025 回落到中等且波动。
- **判定**：2022-2025 窗口里"存活的宏观对象"是**股票风险因子（beta）**而非利率/DXY 本身；且相关性**不是常数**（S10 自己说 2023-25 "no settled regime"）。
- **概念区分（重要）**：**相关性上升 ≠ 条件预测力上升**。S10 证明传导增强，S9/S8 证明可预测性未增强。二者不矛盾，但会误导设计。

### G8-G11 · 数据可得性（实测记录见 §2 表；完整机读版见 `macro-data-availability.json`）

### G12 / G14 · 留给阶段 03 与调研报告 Q3

---

## 2. 数据源实测记录（2026-11-05 UTC）

| # | 变量 | 端点 | 实测结果 | 覆盖 | 结论 |
|---|---|---|---|---|---|
| 1 | US 10Y 名义 | `fredgraph.csv?id=DGS10` | ✅ 返回 CSV，列 `observation_date,DGS10` | 1962-01-02 → **2026-11-02**（末端实测值 4.91） | 可用 |
| 2 | US 10Y 实际(TIPS) | `?id=DFII10` | ✅ | 末端 **2026-11-02**（2.62）；起始未本轮实测 | 可用 |
| 3 | VIX | `?id=VIXCLS` | ✅ | 末端 **2026-11-03**（20.83） | 可用 |
| 4 | 广义美元 | `?id=DTWEXBGS` | ✅ | 末端 **2026-10-30**（121.67） | 可用（**非 ICE DXY**，是 broad trade-weighted，需标 proxy） |
| 5 | S&P500 | `?id=SP500` | ✅ | **2016-11-07** → 2026-11-03（FRED 只留近 10 年） | 覆盖 2020+ ✓ |
| 6 | 美联储资产负债表 | `?id=WALCL` | ✅ | 周频，末端 **2026-10-28** | 可用 |
| 7 | 美国 M2 | `?id=M2SL` | ✅ | 月频，末端 **2026-09-01** | 可用（滞后 2-3 周） |
| 8 | TED spread | `?id=TEDRATE` | ⚠️ 有数据但**终止** | **止于 2022-01-21** | ❌ **序列已停更**，不可用 |
| 9 | Deribit BTC DVOL | `get_volatility_index_data?currency=BTC` | ✅ **活着** | **2021-03-24** → **2026-11-04** | 可用；**起点不满足 2020-01** |
| 10 | BTC dominance | CoinGecko `market_chart/range` | ❌ `error_code 10012`："limited to … past 365 days" | — | **免费不可得** |
| 11 | BTC dominance（备选源） | CoinPaprika `historical` | ❌ "before 2025-11-04 … is not allowed in this plan" | — | **免费不可得** |
| 12 | 稳定币供应 | `stablecoins.llama.fi/stablecoin/1` | ⚠️ 可用但响应极大（单次 **2760 chunks**，含全链逐日） | 2014→ | 可用，需自建切片 |
| 13 | Global M2 | — | ❌ 未找到免费整合源；仅有 US M2 + 部分 OECD | — | **不可得**（只能 proxy） |
| 14 | FOMC 日历 | `federalreserve.gov/monetarypolicy/fomccalendars.htm` | ✅ 2021-2027 完整，含声明 PDF/HTML 链接 | 2021→2027 | 可程序化抓取 |
| 15 | CPI 日历 | BLS 官网 | ⚠️ 未本轮实测 | — | 存在性断言-未核验 |
| 16 | Binance perp/funding | `data.binance.vision` | ⚠️ S3 目录页 JS 渲染，`fetch_page` 拿不到清单；`curl` 阻断 | 项目 r6 manifest 证明 2022-2025 曾成功下载 | 沿用仓库既有数据，本沙箱无法新增实测 |

### ⚠️ 与仓库既有结论冲突的一条（必须上报）

- 仓库 `r7/f10-r4-report.md` "诚实约束"第 3 条写：**"DVOL 缺席：R1 的最强温度源 (Deribit IV) API 已失效"**。
- 本轮实测：**该端点返回 2021-03-24 → 2026-11-04 的完整日频 OHLC，`continuation: null`，非空**。
- 结论：**"API 已失效"的表述至少在当前时点不成立**。可能原因是当时参数/时段问题，或端点曾临时故障后恢复。→ F10-R4 主判据弱增量的"DVOL 缺席"解释**需要重估**。这是本轮对既有产物的唯一实质性事实修正，已交 02.5 对抗核验。

---

## 3. 搜索/抓取失败记录（不伪装为证据）

| # | 动作 | 失败原因 | 处理 |
|---|---|---|---|
| 1 | `curl` 取 FRED/财政部/DefiLlama/CoinGecko | SSL_ERROR_SYSCALL（沙箱阻断非白名单域） | 改 `fetch_page`，4 域全部成功 |
| 2 | `data.binance.vision` S3 列表 | 纯 JS 渲染，返回空表 | 不重复抓；改用仓库 r6 manifest 作旁证 |
| 3 | CoinGecko / CoinPaprika 2020 年历史 | 免费层 365 天限制（返回明确错误文本） | 记为"免费不可得"，不换关键词重试（02 §7 规定最多换一次词；此为硬限制不是零结果） |
| 4 | ego-browser / 网页 LLM | 运行时不存在 | 见 §0 降级声明 |
| 5 | 大陆网络可达性 | 沙箱在境外，**无法实测** | 只记项目历史旁证（`tasks/TASKS.md` B1：Yahoo 403 / Stooq 403 / ifzq 空数组），标"未实测" |

---

## 4. 仍未解决（交给 02.5 与 Q3）

- **U1**：S5 的条件变量是"当日方向"——**当日方向本身是不是宏观的函数**？若是，宏观可能通过方向间接起作用；若不是，宏观与 S5 的机制正交。本轮未找到测此事的论文。
- **U2**：S6 显示"单 regime 集中 → OOS 崩"，但未给"如何事前判断当前是否处在信号有效的 regime"。这是 H_macro 的可执行性死角。
- **U3**：BTC dominance 无免费历史 → 若 Q3 需要它，只能改用"BTC 收益 − 山寨篮收益"自算（需 Binance 全市场数据，成本高）。
- **U4**：CPI 发布日历未实测；QT/QE 切换时点无标准定义（须自行构造）。
- **U5**：大陆可达性未实测，部署前必须由 Lead 在有大陆网络的环境补测（阻塞项，非本轮可解决）。

---

## 5. 本阶段未做的事（防止越界）

- 未写最终推荐（02 §9 规定）——推荐/裁决在 Q3 与阶段 03。
- 未做任何回测（任务书明确"不含回测"）。
- 未修改 F1-F10 任何既有产物；对 r7 报告的唯一动作是**在调研报告里标注冲突**，不改原文件。
