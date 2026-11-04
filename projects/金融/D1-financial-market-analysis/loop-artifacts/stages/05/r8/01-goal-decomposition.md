# F10-R5 / 阶段 01 — 目标分解、已知与空缺条件

# origin: ai (成璐 2026-11-05 r290 派发)
# 任务书: `projects/金融/D1-financial-market-analysis/tasks/F10-r5-macro-regime-task.md`
# 阶段: 01-goal-decomposition（`loop/prompt-first/01-goal-decomposition.md`）
# 执行: arena agent mode | 观测日: 2026-11-05 | 分支: arena/f10-gas-dynamics-research @ 99c8a77

---

## 1. 目标到底要交付什么

**一句话目标**：判定"宏观 regime 条件能否把已 FAIL 的微观结构信号从无条件无效变成条件有效"这件事，**在文献与数据层面是否值得花回测算力**。

交付物（任务书【交付物】冻结）：
1. `f10-r5-macro-survey.md`（Q1 文献 + Q2 数据 + Q3 ≤3 个交互假设）
2. `macro-data-availability.json`（变量 × 源 × 状态矩阵）
3. 回执（repo + branch + commit_sha + 自报模型身份）

**验收判据**（来自任务书）：
- Q1 ≥5 个独立来源，每个带 URL + 一句话结论 + 关系（支持/反对/无关）+ conf
- Q2 每变量确认：频率 / 覆盖起止 / 源 URL / 是否需 key / 大陆可达性；最低要求 **日频 + 2020-01 起 + 无付费墙**
- Q3 ≤3 个假设，每个带理论依据（引 Q1 编号）+ 数据字段 + 8-gate 阈值 + 全 FAIL 的收束判据
- **本轮不含回测**

---

## 2. 顶层因素分解（正交三分，合起来覆盖目标）

目标 = 判定 H_macro 是否值得回测。三者互不重叠、合起来完整：

| 因素 | 边界 | 回答什么 |
|---|---|---|
| **F-E 证据层**（Q1） | 只管"别人测过没有/结果如何"，不管我们能否取数 | 文献里 macro×crypto 的**条件**（交互）效应是否被独立复现过 |
| **F-D 数据层**（Q2） | 只管"变量能不能拿到、够不够长、要不要钱" | 即便效应为真，我们有没有可执行的 PIT 数据 |
| **F-I 设计层**（Q3） | 只在 F-E 支持 且 F-D 可行 时才构造 | 若要做，怎么做才可证伪（阈值 + 收束） |

> 正交性自检：任一因素失败都不影响另两因素的结论（例：文献强但数据断 → 仍可判"不可执行"）。三者并集 = "值不值得做"，无遗漏维度（成本/算力不在本次调研范围，任务书已排除）。

---

## 3. 递归分解到叶子

### 3.1 F-E 证据层

- **F-E1 宏观变量对 crypto 的"无条件"预测力** → 叶子（已知负结果，只需补证）
  - 项目内已知：F8 DVOL 方向信号全 FAIL；F6/F7 funding/basis 全 FAIL
  - 待研究：学术上 macro 对 BTC 日线的无条件可预测性是否也弱 → **G1**
- **F-E2 "条件/交互"效应是否有独立复现** → 拆 3 个叶子
  - **F-E2a 宏观状态 × 微观信号**（正是 H_macro 本体）→ **G2**
  - **F-E2b 宏观 × 收益/波动本身**（不含微观信号）→ **G3**
  - **F-E2c 非宏观的"状态"条件**（价格方向、波动状态、事件窗口）——用于判断"条件"效应的载体是否必须是宏观 → **G4**
- **F-E3 事件研究（FOMC/CPI/QT 切换）** → 叶子 → **G5**
  - 子问题：(a) 是否有可交易的**方向**效应，(b) 是否只有**波动/成交量**效应
- **F-E4 冗余性**：宏观 vs 链上/crypto-native 是否信息重叠 → 叶子 → **G6**
  - 若重叠，加宏观 = 重蹈 F7（funding 与 basis ρ=−0.31~−0.39 的信息冗余）
- **F-E5 已发表 crypto×macro 因子模型里哪些因子在 2022-2025 存活** → 叶子 → **G7**

### 3.2 F-D 数据层

- **F-D1 传统宏观序列**（美债 10Y、实际利率、DXY、VIX、S&P500、美联储资产负债表、M2）→ 叶子 → **G8**
- **F-D2 事件日历**（FOMC 会期、CPI 发布日、QT/QE 切换时点）→ 叶子 → **G9**
- **F-D3 crypto-native 状态变量**（DVOL、BTC dominance、稳定币供应、资金费/OI）→ 叶子 → **G10**
  - 关键子问题：DVOL 是否真的如 r7 报告所称"API 已失效"（若是，最强的波动温度源永久缺席）
- **F-D4 覆盖度硬约束**：日频 + 2020-01 起 + 无付费墙 + PIT 可用 → 叶子（判据，不是研究对象）→ **G11**

### 3.3 F-I 设计层

- **F-I1 假设形式化**（[宏观条件] × [已有信号] × [指标] + 方向）→ **G12**
- **F-I2 判定阈值**：沿用 F6/F7/F8 的 8-gate 协议（t≥2 / n≥30 / net>0 / 跨窗≥3/4 / perm p<0.001 B=2000 / PSR>0.95 / BH-FDR / DSR>0）→ **G13**
  - 已从仓库取得原文口径（`f7-preregistration.md` 第 11 行 + Gate F1-F8 列表），**不算空缺**
- **F-I3 收束判据**（全 FAIL 时怎么办）→ **G12 的子项**
- **F-I4 PIT 时点语义**：宏观序列发布延迟（FRED 值可修订、DGS10 当日收盘即定、WALCH 周四发布、M2 月度滞后约 2-3 周）→ **G14**

---

## 4. 已知条件（不需要研究）

| # | 条件 | 来源 |
|---|---|---|
| K1 | 四条负结果线的结论与失败模式（F6 0/135、F7 ρ=−0.31~−0.39 全 FAIL、F8 DVOL 全 FAIL、F10-R4 主判据弱 PASS + 次判据 FAIL 方向正确率 13-15%） | `stages/05/r2/f6-crossmarket-report.md`、`r3/f7-report.md`、`r4/f8_report.md`、`r7/f10-r4-report.md`（r7 在 main，本分支无） |
| K2 | 8-gate 协议具体口径 | `r3/f7-preregistration.md:11` + Gate F1-F8 |
| K3 | 项目已有加密数据栈：Binance vision 1h/1d klines + funding（2020- 或 2022-）、Bybit OI（2022-）、Deribit DVOL（r4 缓存 1334 点，2022-04-08→2025-12-01） | `r6/data/manifest.json`、`r4/f8_report.md` |
| K4 | 失败模式诊断：无条件、全样本、日线频率；R4 的止损宽度 ∝ 30d σ 随温度同步膨胀 → 失效 | `r7/f10-r4-report.md` §2 |
| K5 | 交易成本口径：往返 0.14%（taker 0.05%×2 + slippage 0.02%×2） | `r6/f10_report.md` |
| K6 | 候选 C = 宏观/跨资产 regime 增强，是 F8 报告指定的剩余未试维度 | `r4/f8_report.md` §"下一步" |
| K7 | 本沙箱 `fetch_page` 可直连 FRED CSV / Deribit API / CoinGecko / DefiLlama；`curl` 被阻断 | **本轮实测**（见 02 阶段日志） |

---

## 5. 空缺清单（阶段 02 必须逐项回答）

| ID | 空缺（复合空缺已列子问题） | 阻塞哪个判断 | 优先级 |
|---|---|---|---|
| **G1** | macro 对 BTC **日频**收益的**无条件**可预测性有多强？子问题：1) 单变量 t/R² 量级 2) 多变量因子模型 OOS 是否胜过随机游走 | 若无条件本来就强，则"条件化"是无的放矢 | P0 |
| **G2** | **核心**：是否存在已发表的"宏观状态下微观信号才有效"的**交互**证据？子问题：1) crypto 领域有无 2) 股票/外汇领域的交互范式能否迁移 | 直接决定 H_macro 是否有先例 | **P0** |
| **G3** | 宏观变量对 crypto **波动/成交量**（而非收益方向）的预测力 | 判断该不该把目标从"方向"改成"带宽/风控" | P0 |
| **G4** | "条件效应"的成功载体是不是必须为宏观？子问题：1) 价格方向 2) 波动状态 3) 事件窗口 三类条件各自的效果 | 若微观条件已足够，加宏观是冗余 | **P0** |
| **G5** | FOMC/CPI 事件的效应分解：方向 vs 波动 vs 成交量；窗口长度 | Q3 H2 是否成立 | P1 |
| **G6** | 链上/crypto-native 与宏观的信息重叠度（R² / 增量） | 防 F7 式冗余 | P0 |
| **G7** | 已发表 crypto 因子模型中，哪些宏观因子在 **2022-2025** 窗口仍显著 | 样本期一致性 | P1 |
| **G8** | 传统宏观序列的免费源状态（频率/起止/URL/key） | Q2 交付 | P0 |
| **G9** | 事件日历免费源状态 | H2 可执行性 | P1 |
| **G10** | DVOL / BTC dominance / 稳定币供应 的真实可用性（含"DVOL API 是否已死"的复核） | Q2 + R1 最强温度源能否回归 | **P0** |
| **G11** | 各变量是否满足"日频 + 2020-01 起 + 无付费墙 + PIT" | 直接剔除不可用变量 | P0 |
| **G12** | 交互假设的具体形式 + 全 FAIL 的收束判据 | Q3 交付 | P1 |
| **G14** | 宏观序列的 PIT 延迟与修订风险 | 防前视 | P1 |

> **不列入空缺**（已由 K 条件覆盖）：8-gate 阈值口径（K2）、成本（K5）、已有数据栈（K3）。

---

## 6. 阶段 02 研究路径（写明目标站点/搜索词/字段/备用源，但**不在本阶段执行**）

| 空缺 | 目标来源类型 | 搜索词（英文为主） | 需抓字段 | 失败备用 |
|---|---|---|---|---|
| G1 | arXiv q-fin、JF/JFE/RFS | "Bitcoin return predictability" "out-of-sample R2" | OOS R²/MSFE vs RW | SSRN 摘要页 |
| G2 | arXiv、SSRN、期刊 | "conditional" "regime" "funding rate" "limits to arbitrage" "state-dependent momentum" | 交互项系数/分组差异 | 用股票/外汇的交互范式类推并显式降级 |
| G3 | 期刊 | "FOMC" "volatility" "cryptocurrency" event study | |r| 跳幅、成交量倍数 | 央行/NBER 工作论文 |
| G4 | 期刊 | "time-series momentum" "market state" crypto | 分状态 t 值 | 项目内 F10-R4 自身的分解 |
| G5 | 期刊/Fed | "FOMC announcement" bitcoin event study | 窗口、方向性显著性 | Fed 官网日历自建事件表 |
| G6 | 期刊/arXiv | "on-chain" "macro" "incremental" "SHAP" | 增量 R²/MSEE | 定性判断 + conf 降级 |
| G7 | arXiv/BIS | "crypto factor model" "macro factors" | 因子显著性 + 样本期 | BIS 工作论文库 |
| G8/G9/G10/G11 | FRED / Deribit / DefiLlama / Fed / BLS / data.binance.vision | 直接打 API/CSV 实测 | 起止日期、频率、HTTP 状态、错误文本 | 换同义代理并标 proxy |
| G12/G14 | 由 G1-G11 推导 | — | — | — |

**候选变量冻结集**（防漂移，后续阶段不得悄悄增删；增删须在此登记理由）：
`US10Y(DGS10)`、`US10Y_real(DFII10)`、`VIX(VIXCLS)`、`BroadUSD(DTWEXBGS)`、`SP500`、`WALCL`、`M2SL`、`TEDRATE`、`DVOL_BTC`、`BTC_dominance`、`stablecoin_supply`、`global_M2`、`FOMC_dates`、`CPI_dates`。
> 其中 `global_M2` 与 `BTC_dominance` 为**高怀疑项**（预期不可得），保留是为了让 02 阶段给出**否定证据**而不是静默删除。

---

## 7. 阶段判定

- 目标交付物：明确（3 项，已冻结）
- 主要因素：三正交层（证据/数据/设计），已递归到叶子（14 个空缺，含复合空缺的子问题）
- 已知条件：K1-K7，均带仓库内路径或本轮实测出处
- 关键空缺与阻塞：G2/G4/G10 为 P0 中的决定性项
- 阶段 02 第一批行动：已给出具体站点 + 搜索词 + 字段 + 备用源
- 未验证内容是否被伪装成已知：**否** —— 所有"可能有/应该有"的表述均落在 G 编号空缺内；本文件不含任何未标来源的事实断言

**判定：分解完成（pass）→ 进入阶段 02。**
