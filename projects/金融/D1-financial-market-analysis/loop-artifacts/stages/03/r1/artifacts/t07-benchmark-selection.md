# origin: ai

# T07 — 基线选择设计文档（03-r1 节点）

**任务**：DAG 节点 T07（基线选择，orthogonal_key=benchmark-selection，parallel_group G2）。设计基线对比集 + 公平对比协议 + 04 执行接口。
**输入**：`t04-signal-spec.md`（§(a) 信号清单 / §(b) PIT / §(c) regime 窗口 / §(d) 多重检验 / §(e) 贡献）、`public-benchmarks.md`（02-r1，19 个 arXiv URL）、`stability-criteria.md`（02-r1，C1-C10 判据）。
**生成**：T07 research-worker，主机日期 2026-10-17（Asia/Shanghai）。
**confidence = 0.80**（合成理由见 §7.1）。

---

## 0. 摘要（关键结论速览）

1. **文献核验分层（P1 修正点）**：02 阶段记录 19 个 arXiv URL = 13 个 abs 直验（A 层）+ 6 个仅列表级（B 层）。T07 逐条 `curl export.arxiv.org/abs/<id>` 复核（2026-10-17）：**13 个 A 层维持 A；6 个 B 层全部升级为 A**（均 HTTP 200 + 标题匹配）。**更新后状态：19/19 = A 层，0 B 层，0 uncertain**（见 §1 逐条表）。
2. **2603.19380 定性修正**：该文是**股票指数**（印度 NIFTY Smallcap 250 小盘指数）幸存者偏差量化（survivor-only 高估年化 +4.94pp / 23.3%），**不是 crypto**。crypto 端幸存者偏差专门量化仍是**公开缺口**——不得把股票端数字挪用为 crypto 证据（§2）。
3. **基线清单**：5 条 pre-registered 基线 = buy-and-hold / momentum-12-1 / RSI-14 / trend-MA(50/200) / funding 朴素规则（§3）。每条标验证层级（A / uncertain）。
4. **公平对比协议**：三同 = 同 T04 §(c) 锁定窗口（5 年度 OOS × 3 regime）+ 同 T05 §成本参数（接口引用，不另定义）+ 同 T04 §(d) 45 检验家族（**基线也计入 trial count**，扩展为 120 起，§4）。
5. **未核验文献**：Harvey-Liu-Zhu 2016 等 11 条期刊/书文献全标 "uncertain ref"，**独立成节**（§5），不混入已核验清单。
6. **04 执行接口**：5 条基线实现规格（参数 + 数据源 + T04 §(b) PIT 引用），统一走 Binance data.binance.vision + T04 §(b) 全套 PIT 规则（§6）。

---

## 1. 文献核验分层（P1 修正点 — 本节最重要）

### 1.1 分层标准定义

| 层级 | 定义 | 证据要求 |
|------|------|----------|
| **A 层** | abs 页面直验 | `curl export.arxiv.org/abs/<id>` 返回 HTTP 200 **且** 页面标题与 02 记录标题匹配 |
| **B 层** | 仅列表级核验 | 标题/主题匹配，但 abs 页**未直验**（02 阶段只搜到列表/引用，未打开 abs 页） |
| **uncertain** | 未核验 | 不可达（429/403/000）/ 标题不匹配 / 期刊书籍无 arXiv 来源 |

**为什么必须分层而非笼统写"19 个已核验"**：分层是诚实声明——A 层 = 我有直验证据（HTTP 200 + 标题匹配）；B 层 = 我只有列表级线索（未亲自打开 abs 页确认）；uncertain = 我没有。02 阶段曾把 6 个论文标 B 层，T07 的 P1 修正点就是**逐条复核并把分层更新为可复核状态**，不得含糊。

### 1.2 19 个 URL 逐条复核结果（T07 直验，2026-10-17，`export.arxiv.org/abs/<id>`，`--max-time 30`，429 重试 1 次即 skip）

**原 A 层 13 个 — 全部维持 A**：

| # | arXiv id | 02 记录标题 | HTTP | 直验标题匹配 | 新层 | 角色（04 用途） |
|---|----------|-----------|------|:---:|:---:|----------------|
| 1 | 1912.03270 | BitMEX Funding Correlation with Bitcoin Exchange Rate | 200 | ✓ | **A** | funding 信号可预测性实证锚（同信号） |
| 2 | 2212.06888 | Fundamentals of Perpetual Futures | 200 | ✓ | **A** | 永续定价/套利 + 成本框架 |
| 3 | 2506.08573 | Designing funding rates (perp, crypto) | 200 | ✓ | **A** | funding 机制设计 |
| 4 | 2310.14973 | Reconciling Open Interest with Traded Volume | 200 | ✓ | **A** | OI 口径 |
| 5 | 1809.05961 | Optimal Dynamic Basis Trading | 200 | ✓ | **A** | basis 交易学术经典（非 crypto） |
| 6 | 2501.09404 | Agent-Based Simulation of a Perpetual Futures Market | 200 | ✓ | **A** | 微观结构仿真 |
| 7 | 1904.00890 | Momentum and liquidity in cryptocurrencies | 200 | ✓ | **A** | crypto 动量（**截面**，非时序） |
| 8 | 2112.15321 | Evolutionary correlation, regime switching... | 200 | ✓ | **A** | regime / 整体-Sharpe 非首要 |
| 9 | 2307.06400 | Quantile & expectile copula HMM (crypto) | 200 | ✓ | **A** | regime 分解 |
| 10 | 2607.04958 | Look-Ahead-Freedom as Temporal Non-Interference | 200 | ✓ | **A** | PIT 形式化 |
| 11 | 2609.20554 | Does Training on Future Data Pay? | 200 | ✓ | **A** | look-ahead 实证 |
| 12 | 2603.19380 | Survivorship Bias in EM Small-Cap (India NIFTY 250) | 200 | ✓ | **A** | 幸存者偏差（**股票**，非 crypto） |
| 13 | 2209.05559 | DRL Crypto Trading: backtest overfitting | 200 | ✓ | **A** | 过拟合=假设检验（crypto 实践最近） |

**原 B 层 6 个 — 全部升级为 A**：

| # | arXiv id | 02 记录标题 | HTTP | 直验标题匹配 | 02 层 | 新层 |
|---|----------|-----------|------|:---:|:---:|:---:|
| 14 | 2601.10812 | Optimal Liquidation of Perpetual Contracts | 200 | ✓ | B | **A ↑** |
| 15 | 2605.05089 | Dynamic Collateral Control... Spot Perpetual Basis | 200 | ✓ | B | **A ↑** |
| 16 | 2602.11708 | Systematic Trend-Following Adaptive Portfolio (crypto) | 200 | ✓ | B | **A ↑** |
| 17 | 1905.05023 | Avoiding Backtesting Overfitting by Covariance-Penalties | 200 | ✓ | B | **A ↑** |
| 18 | 2209.13623 | Publication Bias in Asset Pricing Research | 200 | ✓ | B | **A ↑** |
| 19 | 2309.06711 | Epps Effect and Signature of Short-Term Momentum | 200 | ✓ | B | **A ↑** |

### 1.3 分层更新结论

- **更新后：19/19 = A 层，0 = B 层，0 = uncertain（arXiv 来源内）**。
- 原 6 个 B 层论文**全部可达且标题匹配**，故全部升级 A。这是逐条 `curl` 直验的**实际结果**，不是推测。
- **诚实边界**：(1) 本次直验 = 2026-10-17 本环境单次结果；arXiv 限流（429）或网络波动可能影响**未来重跑**——按任务纪律（429 重试 1 次即 skip），若未来重跑某条 skip，该条降回 B 层并标注"重跑降级"，不假装仍 A。(2) 本层级 = **abs 页标题级**直验，与 02 同层级；**未做 PDF 正文级**核验（正文级仅 T01 对 2608.27734 做过）。(3) **11 条期刊/书文献**不在 arXiv 来源内，不进入本 19 条表，单独在 §5 标 uncertain ref。

### 1.4 分层对结论的支撑（P1 动机闭环）

02 阶段的"13 abs 直验 + 6 列表级"是**保守下界**（6 个 B 层只是"搜到了但没打开 abs"）。T07 直验把 6 个 B 层全部坐实为 A，因此**所有 19 个 arXiv 锚点现在都有 abs 直验证据**，基线清单（§3）引用的每个 arXiv 锚都可指回 §1.2 的直验行。这把"基线选择"的文献基础从"部分直验"提升到"全量直验"，是 P1 修正点（实际问题优先 + 可验证结果）的直接落地。

---

## 2. 2603.19380 定性修正（不得挪用）

### 2.1 该文是什么（直验标题级）

- **直验标题**（2026-10-17）：*Survivorship Bias in Emerging Market Small-Cap Indices: Evidence from India's NIFTY Smallcap 250*（作者 Ranse）。
- **场景 = 股票指数**（印度 NIFTY Smallcap 250 小盘指数），**不是 crypto**。样本 1437 只股票、2016–2025 共 9 年。
- **量化结果**（02 已摘录，本节点保留）：survivor-only 回测**高估年化收益 +4.94pp（相对 +23.3%）**、Sharpe **+0.097（+9.1%）**；成分换手率 82.5%（退市 16.1% / 升级 33.1% / 降级 33.2%）；bhavcopy 数据（**含退市股**）可 100% 复现当时时点成分。
- **机制**：survivor-only = 只用"活到最后"的成分做回测 → 系统性高估（退市/降级股被丢）。

### 2.2 定性修正（关键纪律 — 不得挪用为 crypto 证据）

1. **该文是股票端**幸存者偏差量化，**不是 crypto**。
2. **crypto 端**幸存者偏差的**专门量化论文 = 公开缺口**（02 `public-benchmarks.md` 总体缺口判断 #3 已确认；本节点 19 条直验中无一 crypto 幸存者量化）。
3. **本项目不得把 4.94pp / 23.3% 股票端数字当作 crypto 端证据**。把它写进结论当"crypto 幸存者偏差约 X%"= 虚构/挪用，违反诚实红线。
4. **正确用法**：4.94pp / 23.3% 仅作**"机制同构 + 量级参考"**（02 口径），且每次引用必须明确标注 **"股票端量级，crypto 无直接量化公开基准"**。

### 2.3 本项目 S1 的幸存者处理（预注册口径）

- **S1 = BTCUSDT 单标的**（长期存续，非成分轮换指数）→ **幸存者风险低**，预注册注明"单一长期存续标的，幸存者偏差已控制/不适用"。
- **机制同构声明**（保留 02 口径，但量化不可挪用）：加密市场"仅用当前在市交易对"回测 与 2603.19380 的 survivor-only **机制同构**（都丢已退市/下架标的）；若未来 S1 扩展为多交易对，**必须用当时时点成分（含已退市/下架对）**——但**偏差幅度无 crypto 已量化公开基准**，不得引用 4.94pp 当 crypto 数。
- **结论**：S1 单标的场景下幸存者偏差不是主要风险；但**预注册中必须写明**"若扩展多标的则需 point-in-time 成分，且 crypto 端偏差幅度属公开缺口"——这正是 02 判定的"gap 而非 finding"。

---

## 3. 基线清单（每条标验证层级）

### 3.0 基线选型原则

- **目的**：检验 funding 信号是否 **beat 朴素基准**。T04 §(e) 已定调：本项目贡献**不是**"发现 funding 有效"，而是"在严格 PIT + 预注册条件下对 funding 信号做**正式验证**"。基线集是验证的必要对照——没有基线对照，"beat"无从谈起。
- **原则**：(1) 每条基线 = 一个**公开可复现**的朴素策略 + **明确参数**（不糊弄）+ 验证层级标注；(2) **机制正交完备**（无择时 / 动量 / 均值回归 / 趋势 / 同信号朴素 五类机制各占一条）；(3) **不新建复杂基线**（复杂基线会与 funding 信号本身混淆贡献，且违反"朴素对照"初衷）；(4) 参数**先验圆整**（非样本内挑选，T04 §(d) 口径，04 不事后调）。
- **角色分工**：buy-hold = 首要对照（funding 必须 beat 它才算有 timing edge）；funding 朴素规则 = 最关键对照（隔离"信号本身"vs"严格验证栈"哪个贡献了绩效）。

### 3.1 基线 1 — Buy-and-Hold BTCUSDT

- **规格**：全期 +1 仓位持有 BTCUSDT，不择时、不加杠杆、不 rebalance。
- **参数**：无（期初 100% 仓位，期末不卖出）。
- **数据源**：Binance BTCUSDT 日线 kline（`data.binance.vision/.../daily/klines/BTCUSDT/1d/`）。
- **PIT 规则**：T04 §(b) B4 规则 3 —— **禁用未定版末根 K 线**；日线文件按 T+1 发布后可用（B4 bulk_daily）。
- **验证层级**：**行业标准实践，无需文献引用**（02 `public-benchmarks.md` #9 口径："buy & hold 为行业标准实践，无需引用"）。层级标 = *N/A（industry standard，无 ref 需求）*。
- **角色**：**首要对照**。funding 信号若不能 beat buy-hold（同期 OOS 超额收益为正且通过 C5 判据），则无 timing edge 可言。

### 3.2 基线 2 — Momentum 12-1（经典规格，crypto 时序适配）

- **规格**：经典 **12-1 动量**（Jegadeesh-Titman 12-1 的**时序单标的**适配——本项目 S1 是单标的 timing，非多标的截面排序）。
- **参数**（先验圆整，04 不事后调）：
  - 回看期 **L = 252 交易日**（≈1 年）
  - 跳过期 **S = 21 交易日**（≈1 月，跳过最近 1 月以避免短期反转污染，12-1 经典设计）
  - **t 时刻信号 = sign( P_{t−S} / P_{t−L} − 1 )**
  - 仓位：信号 > 0 → **+1（long BTCUSDT）**；信号 ≤ 0 → **0（flat）**
  - 再平衡：每日
- **crypto 短周期变体（敏感性，04 可选）**：7 / 30 日收益符号（02 `public-benchmarks.md` §建议1 口径"朴素动量如 7/30 日收益符号"）。**若 04 搜索这些 lookback，每个配置计入 trial count**（§4.3）。
- **数据源**：Binance BTCUSDT 日线 kline。
- **PIT 规则**：T04 §(b) B4 规则 3（仅已收盘 bar）。
- **验证层级**：**A**（crypto 锚 = arXiv:1904.00890，§1.2 #7 直验；**但该文为截面多币种动量，非时序单标的**——04 实现时须注明此区别，见 §3.7）+ **uncertain ref**（股票经典 Jegadeesh & Titman 1993 JF，§5）。
- **注意**：02 #8 明确指出 1904.00890 是**截面**（多币种排序），本项目 S1 是**时序**（单标的）——基线构造时保留此区别声明，不假装 crypto 动量文献直接覆盖时序单标的。

### 3.3 基线 3 — RSI-14（经典 Wilder 规格）

- **规格**：经典 **Wilder RSI** 均值回归择时（与动量/趋势的"顺势"机制正交，提供"逆势"机制对照）。
- **参数**（先验圆整）：
  - 周期 **N = 14**（Wilder 标准）
  - 平滑：**Wilder 平滑**（EMA 变体，alpha = 1/14）
  - **超卖 RSI < 30 → 入场 long BTCUSDT**
  - **超买 RSI > 70 → 离场 flat**
  - 中性（30 ≤ RSI ≤ 70）→ 维持现仓位
- **变体（敏感性，04 可选）**：趋势过滤 RSI > 50 → uptrend / RSI < 50 → downtrend。**若 04 搜索阈值，计入 trial count**。
- **数据源**：Binance BTCUSDT 日线 kline。
- **PIT 规则**：T04 §(b) B4 规则 3（仅已收盘 bar）。
- **验证层级**：**uncertain ref**（RSI 原始定义 = J. Welles Wilder Jr.《New Concepts in Technical Trading Systems》1978，**书籍**，无 arXiv 来源，无法 abs 直验 → 列入 §5）。层级标 = *uncertain ref*。
- **角色**：**均值回归对照**（funding 若呈动量/趋势特征，RSI 提供反向机制对照，分离"方向性择时"vs"震荡择时"）。

### 3.4 基线 4 — Trend-Following / Moving-Average（50/200 双均线）

- **规格**：经典**双均线趋势跟随**（金叉做多 / 死叉离场）。
- **参数**（先验圆整）：
  - 短期均线 **L_short = 50 日**
  - 长期均线 **L_long = 200 日**
  - **金叉**（50 日上穿 200 日）→ **long BTCUSDT**；**死叉**（50 日下穿 200 日）→ **flat**
- **变体（敏感性，04 可选）**：单均线 200 日（价在 200 日线上方 → long，否则 flat）。
- **数据源**：Binance BTCUSDT 日线 kline。
- **PIT 规则**：T04 §(b) B4 规则 3（仅已收盘 bar）。
- **验证层级**：**A**（crypto 锚 = arXiv:2602.11708 §1.2 #16 直验，Bui & Nguyen 趋势跟随；+ arXiv:2501.09404 §1.2 #6 直验机制仿真）+ **uncertain ref**（股票经典 Lo/Mamaysky/Wang 2000 JFE，§5）。

### 3.5 基线 5 — Funding 朴素规则（同信号对照 — 最关键）

- **规格**：用 funding rate 构造的**最朴素**规则，目的是**隔离"信号本身"vs"严格 PIT + 预注册验证栈"**哪个贡献了绩效（呼应 T04 §(e) 贡献定调）。
- **参数**（先验圆整，04 不事后调）：
  - t 时刻 funding = **latest_settled_funding**（T04 §(b) B2：最近一笔 settled 且 ts_norm ≤ t）
  - **规则 A（极端分位反向）**：funding < 低分位（25%）→ **long**（拥挤多头反向）；funding > 高分位（75%）→ **flat**（拥挤空头不追）；中间 → flat
  - **规则 B（符号跟随）**：funding > 0 → **持仓**（多头情绪）；funding < 0 → **flat**
  - 分位数阈值 = **先验圆整值**（04 前写死，非样本内挑选，T04 §(d) 口径）
- **数据源**：Binance fundingRate 月度 bulk（206 文件，`data.binance.vision/.../monthly/fundingRate/BTCUSDT/`）。
- **PIT 规则**：T04 §(b) B2（settled only）+ B4 规则 1（funding_settled lag）+ B0 规则 3（8h 逐 symbol 可变，不套硬网格）。
- **验证层级**：**A**（同信号锚 = arXiv:1912.03270 §1.2 #1 直验，Nimmagadda & Ammanamanchi funding 可预测性 GARCH 实证）。
- **角色**：**最关键对照** —— 它与主 funding 信号用**同一数据、同一 PIT 规则**，仅"择时规则"不同（朴素分位/符号 vs 严格验证栈选出的规则）。若两者 OOS 绩效差异不大 → 贡献主要来自"信号本身"；若差异大 → 严格验证栈（PIT + 多重检验 deflation）才是绩效来源。

### 3.6 基线集汇总

| 基线 | 机制类型 | 核心参数 | 数据源 | 验证层级 |
|------|---------|---------|--------|:---:|
| buy-and-hold | 无择时 | 全期 +1 | BTCUSDT 日线 | N/A（industry standard） |
| momentum-12-1 | 动量 | L=252, S=21, 日再平衡 | BTCUSDT 日线 | **A** (1904.00890, 截面≠时序) + uncertain (J-T 1993) |
| RSI-14 | 均值回归 | N=14, <30 入 / >70 出 | BTCUSDT 日线 | uncertain (Wilder 1978 书) |
| trend-MA(50/200) | 趋势 | 50/200 金叉死叉 | BTCUSDT 日线 | **A** (2602.11708/2501.09404) + uncertain (LMW 2000) |
| funding 朴素 | 同信号 | 分位 25/75 或符号 | fundingRate bulk | **A** (1912.03270) |

### 3.7 为什么是这 5 条（边界说明）

- **纳入 5 条覆盖五类正交机制**：无择时（buy-hold）/ 动量（12-1）/ 均值回归（RSI）/ 趋势（MA）/ 同信号朴素（funding）—— 机制完备，任何一类择时逻辑都有对应对照。
- **不纳入 HMM 制度分解作为"基线策略"**：regime 分解（arXiv:2307.06400 / 2112.15321）是**评估维度**（按 bull/bear/range 分解 OOS 绩效），不是独立择时策略——它是 T04 §(c) 的**共同评估要求**，作用于所有基线，不作为第 6 条基线。
- **不纳入 OI 基线**：OI 是 T04 §(a) 的**辅信号**，其增量价值由 04 决定（决策 A/B/C 降级链），不在基线集内混入（避免与 funding 主信号混淆贡献）。
- **不纳入复杂机器学习基线**：朴素对照原则（§3.0）；复杂基线会与 funding 信号本身混淆，且参数搜索会大幅膨胀 trial count 偏离"朴素"初衷。

---

## 4. 公平对比协议（三同）

> 本节是 T07 对 04 执行层的**接口契约**：funding 主信号与 5 条基线必须在三个维度**严格对齐**，否则"beat 基线"的结论无效。

### 4.1 同窗口（引用 T04 §(c) regime 日历锁定窗口）

- **5 个年度 OOS 窗口**：2021 / 2022 / 2023 / 2024 / 2025（2020 作**首窗扩展训练段**，2022 熊市**强制入 OOS**——T04 §(c) 方向一致性判据 C4 天然要求）。
- **regime 日历**（T04 §(c) 锁定，`regime_locked=true`，pre-04 冻结，**禁止自适应重估**）：
  - bull：2020-01-01 → 2021-12-31
  - bear：2022-01-01 → 2022-12-31
  - range：2023-01-01 → 2023-12-31
  - bull：2024-01-01 → 2025-12-31
- **基线约束**：5 条基线必须跑在这**相同**的 5 窗口 × 3 regime 网格上，**不得另开窗口**、不得用月度窗（02 C2：月度窗在文献中零出现且会加重 deflation）。

### 4.2 同成本模型（引用 T05 §成本参数，本节点不另定义）

- **接口约定**：基线与 funding 主信号使用**同一**成本模型——T05（`t05-data-pipeline-design.md`）**§4 成本参数（本节点唯一 owner）** 定义的 taker 手续费 + 滑点 + funding 结算归属。**本节点不定义、不复制任何成本参数**（T05 职责，02.5/03 已确认 DAG 唯一 owner）。
- **T05 §4 已知值**（仅引用，不改）：spot taker 0.1000% / USD-M futures taker 0.0500% / maker 0.0200%（**uncertain**，费率页本环境不可达，last-known 2026-10-17）；滑点 base 0.01%/side、stress 0.02%/side、taker 成交（pre-registered）。
- **理由（防不公平）**：若基线免成本而 funding 扣成本，"beat 基线"的超额是**成本差异**而非信号差异——02 `public-benchmarks.md` F5 已识别"成本低估"为最常见失败模式之一。三同中的"同成本"直接堵住这个漏洞。
- **04 依赖项**：T05 已声明成本参数 = uncertain + last-known；若 04 费率页可达则一手核验 + 刷新 + 标记受影响回测重跑（T05 §4.2 纪律）。**基线与 funding 必须用刷新后的同一版本**（不能 funding 用新费率、基线用旧费率）。

### 4.3 同检验流程（引用 T04 §(d) 45 检验家族 — 基线计入 trial count）

- **检验家族**：3 regime × 3 funding 阈值 × 5 窗口 = **45 个 OOS 检验**（T04 §(d) 预注册）。主方法 = **BH-FDR**（多重检验主防线）+ **DSR trial-count deflation**（第二层，Gençay 2608.27734 方法）；**弃 Bonferroni**（T04 §(d) 理由：45 检验高正相关，Bonferroni 过保守误杀真阳性）。
- **基线计入 trial count（本节点关键扩展）**：
  - T04 §(d) 原 trial count = 45（funding）+ 04 额外搜索。**T07 扩展**：每条基线策略-spec 也是独立 trial，**计入 DSR/PBO trial count**（不仅 funding 的 45）。
  - **计数约定**：采用与 T04 §(d) **一致的 cell 计数**（每 (spec × 窗口 × regime) = 1 trial）。T04 把 funding 的 3 阈值 × 5 窗 × 3 regime 计为 45，同理基线 = 5 spec × 5 窗 × 3 regime = **75 cell**。
  - **扩展 trial count（最小，pre-04 搜索前）= 45（funding）+ 75（基线 cell）= 120**。
  - **保守方向说明**：cell 计数是**上限（保守）**方向——它避免 under-deflation（少计 trial → DSR 过松 → 误报显著）。若 04 采用更严格的"只计搜索 spec"解释（buy-hold 等固定 spec 计 1 而非 15），计数会降到 45 + 5 = 50 起；**本节点采用保守的 120** 作为 DSR deflation 基准，与本项目"严格抗过拟合"定位一致。
  - **04 落地**：若 04 搜索基线参数（momentum lookback ∈ {7,30,90}、RSI 阈值变体、MA 参数变体），**每个配置逐项累加**进 trial count（T04 §(d) "04 中任何额外的阈值/窗口搜索次数，全记录"口径），触发 DSR 加严。**禁止"跑一个不过就换一个"**（T04 §(d) 红线）。
  - **精确数在 04 冻结基线集后最终确定**；120 是预注册最小基准。
- **通过判据**（T04 §(d) + 02 C5 最严显式集合）：每窗口 OOS **净收益 T≥2.0** + 每窗口 **≥30 笔** + **扣费后净正** + **全部测试年方向一致（C4）** + **permutation p<0.001** + **PSR>0.95**（参考）；**阈值基于超额收益**（非绝对，避免 02 C7 绝对收益 gate 误杀真信号）。基线与 funding **同一套判据**，无豁免。

### 4.4 公平性自检清单（04 逐条核对，任一 ✗ 则对比无效）

| 维度 | funding 主信号 | 5 条基线 | 是否对齐 |
|------|--------------|---------|:---:|
| 窗口 | 5 年度 OOS（T04 §(c)） | 同 5 年度 OOS | ✓ |
| regime | 3（bull/bear/range） | 同 3 | ✓ |
| 成本模型 | T05 §4（同版本） | T05 §4（同版本） | ✓ |
| trial count | 45（T04 §(d)） | 75 cell（计入 DSR） | ✓（全计入） |
| PIT 规则 | T04 §(b) B0-B6 | T04 §(b) B0-B6 | ✓ |
| 通过判据 | C5 集合（超额收益） | 同 C5 集合 | ✓ |
| 2022 熊市 | 强制入 OOS | 强制入 OOS | ✓ |

---

## 5. 未核验文献处理（独立成节，全标 uncertain ref）

### 5.1 处理原则

- 期刊/书籍文献（SSRN / Wiley / Elsevier / Oxford / AMS）**本环境不可直验**（SSRN curl 000、AMS 403、deprado.com 不可达）→ 全部标 **"uncertain ref"**。
- **本节与 §1（已核验 19 条）严格分离，不得混入**。引用时保留"未核验"不确定性，**不把它当已验证证据**。
- **补查纪律**：若 02.5/04 前补到 URL 并 abs 直验成功，走 §1.2 分层流程升级 A；补到前维持 uncertain ref。

### 5.2 未核验文献清单（12 条，全 uncertain ref）

| # | 文献 | 类型 | 用途（本项目） | 状态 |
|---|------|------|--------------|:---:|
| 1 | Harvey, Liu, Zhu《Backtesting》(JF 2016) | 期刊 | 多重检验 t>3.0 惯例（参考，T04 弃 Bonferroni 不用硬 t 门槛） | uncertain ref |
| 2 | Bailey, Borwein, López de Prado, Zhu《Pseudo-Mathematics and Financial Charlatanism》(Notices AMS 61(5):678-687, 2014) | 期刊 | 回测过拟合经典（项目定位背书） | uncertain ref（**⚠️ arXiv ID 1308.3655 经验证是错的**——那是粒子物理中微子质量论文，**绝不引用**） |
| 3 | Bailey et al.《The Deflated Sharpe Ratio》(JCF 2014) | 期刊 | DSR 原始定义（T04 §(d) 第二层方法） | uncertain ref |
| 4 | Bailey et al.《The Probability of Backtest Overfitting》(working paper) | 工作论文 | PBO 原始定义 | uncertain ref |
| 5 | López de Prado《Advances in Financial Machine Learning》(Wiley/Oxford, 2018) | 书籍 | purged K-fold / CPCV / 幸存者偏差章节（02 C9） | uncertain ref |
| 6 | White《A Reality Check for Data Snooping》(Econometrica 2000) | 期刊 | data snooping 经典 | uncertain ref |
| 7 | Hamilton (1989, Econometrica) | 期刊 | Markov 制度切换起源（regime 方法源） | uncertain ref |
| 8 | Jegadeesh & Titman (1993, JF) | 期刊 | 动量 12-1 经典（**股票端**，基线 2 的规格来源） | uncertain ref |
| 9 | Lo, Mamaysky, Wang (2000, JFE) | 期刊 | 技术分析/均线经典（基线 4 的规格来源） | uncertain ref |
| 10 | Koijen, Moskowitz, Pedersen, Vrugt《Carry》(JFE 2018) | 期刊 | 跨资产 carry 经典（funding ≈ 加密 carry 的类比锚） | uncertain ref |
| 11 | McLean & Pontiff (JF 2016) 因子衰减 + Hou, Xue, Zhang《Replicating Anomalies》(RFS 2015) | 期刊 | 因子衰减 / 数据质量（多重检验动机） | uncertain ref |
| 12 | Wilder Jr.《New Concepts in Technical Trading Systems》(1978) | 书籍 | RSI 原始定义（基线 3 的规格来源） | uncertain ref |

### 5.3 补查建议（02.5 / 04 前）

- **SSRN 不可达**（curl 000）→ Harvey-Liu-Zhu 2016 等需人工/代理补 URL 后直验。
- **AMS 403 / deprado.com 不可达** → Bailey 系列 / López de Prado 的定义细节按**领域知识**引用，标注"未核验"，不作为已验证引文。
- **arXiv 1308.3655 误引警报**：02 记录 Pseudo-Mathematics 对应 arXiv ID 1308.3655，**T07 验证该 ID 实为粒子物理中微子质量论文**——本项目任何引用 Pseudo-Mathematics 的地方**不得带 1308.3655**。

---

## 6. 04 执行接口（基线实现规格清单）

### 6.1 数据源（统一）

- **主数据**：Binance **data.binance.vision**（归档 CDN，**本环境可达**——T04 §Lead 批注确认 live API 不可达但 CDN 可达）：
  - BTCUSDT 日线 kline：`data.binance.vision/data/futures/um/daily/klines/BTCUSDT/1d/BTCUSDT-1d-<date>.zip`
  - fundingRate 月度 bulk：`data.binance.vision/data/futures/um/monthly/fundingRate/BTCUSDT/BTCUSDT-fundingRate-<YYYY-MM>.zip`（206 文件 2020-01→2026-09）
  - 日线文件 **T+1 迟报** / 月线**当月第一周一**（T04 §(b) B4）。
- **OI 源**（若 04 启用 OI）：T04 §(a) 决策 B（Bybit 主 + Binance 30d 交叉验证）；**本环境 live API 不可达 → 04 从 A（funding-only）起步**（T04 §Lead 批注 #1，记录降级事件）。**基线集不含 OI 基线**（§3.7）。

### 6.2 PIT 规则（引用 T04 §(b)，基线与 funding 信号同套）

- **B0 五条硬规则**：UTC 毫秒归一 / funding 只用 settled（predicted 物理隔离）/ 8h 逐 symbol 可变（不套硬网格）/ 数据 lag 与决策对齐（ts ≠ available）/ OI bar 起点语义。
- **B2 latest_settled_funding**：funding 朴素基线（§3.5）用。
- **B4 LAG_RULES**：
  - bulk_daily（日线 T+1）→ 4 条价格基线（buy-hold / momentum / RSI / trend-MA）用。
  - 规则 3 **禁用未定版末根 K 线** → 所有价格基线。
- **B6 PIT 违规检查清单**（8 项）：04 逐条自检，**任一违反即回测无效**（T04 §(b)）。
- **关键**：基线与 funding 信号**同一套 B0-B6**，不得为基线放宽任何 PIT 规则（否则对比不公平）。

### 6.3 各基线实现规格（参数 + 数据源 + PIT 引用）

| 基线 | 信号计算（04 实现） | 数据源 | PIT 规则引用 |
|------|--------------------|--------|-------------|
| buy-hold | 期初建仓 100%，不 rebalance | BTCUSDT 日线 | T04 §(b) B4(3) |
| momentum-12-1 | sign(P_{t−21}/P_{t−252} − 1)；>0 long 否则 flat；日再平衡 | BTCUSDT 日线 | T04 §(b) B4(3) |
| RSI-14 | Wilder RSI(14)；<30 入 long / >70 出 flat | BTCUSDT 日线 | T04 §(b) B4(3) |
| trend-MA(50/200) | 50 日 EMA 上穿 200 日 EMA → long；下穿 → flat | BTCUSDT 日线 | T04 §(b) B4(3) |
| funding 朴素 | latest_settled_funding；分位 25/75 或符号 → 仓位 | fundingRate bulk | T04 §(b) B2 + B4(1) |

### 6.4 评估输出（04 按 regime 分解，基线与 funding 同网格同指标）

- **每基线 × 每窗口 × 每 regime**：OOS 净收益 / T 统计量 / 交易笔数 / 方向一致性 / MDD / Sharpe / PSR。
- **与 funding 信号同网格同指标对比**（T04 §(d) + 02 C6：MDD 跨窗一致性无标准阈值，作参考项不作 gate）。
- **整体 Sharpe 不作首要指标**（02 #6，文献依据 arXiv:2112.15321 / 2307.06400——整体 Sharpe 会被 regime 混合掩盖）。
- **regime-wise 呈现是所有基线的共同要求**：bull / bear / range 各分解一次，2022 熊市单列（C4 方向一致性在此体现）。

---

## 7. 置信度与局限

### 7.1 合成置信度（confidence = 0.80）

- **抬高因素**：
  - (1) **19/19 arXiv URL 直验成功**（A 层证据完整，0 跳过）——"基线选择"的文献基础从 02 的"13 直验 + 6 列表级"提升到"全量直验"，核验不确定维度显著降低。
  - (2) **基线集机制正交完备**（5 类机制各占一条，无遗漏、无冗余）。
  - (3) **公平对比协议三同**（同窗口/同成本/同检验）严格对齐 T04 §(c)/(d) + T05 §4，无另定义成本/另开窗口。
  - (4) **2603.19380 定性修正**消除"股票端数字挪用为 crypto 证据"的虚构风险。
  - (5) **trial count 扩展**（45→120 保守 cell 计数）堵住"基线不计入 deflation"的 under-deflation 漏洞。
- **压低因素**：
  - (1) **RSI 基线无 arXiv 锚**（Wilder 1978 书籍，uncertain ref）——基线 3 的文献锚最弱。
  - (2) **momentum 12-1 股票经典 uncertain ref**（Jegadeesh-Titman 1993），且 crypto 锚 1904.00890 为**截面非时序**——基线 2 的文献锚有口径差。
  - (3) **T05 成本模型未一手核验**（本节点按接口引用，04 依赖 T05 落地；费率页不可达 → uncertain + last-known）。
  - (4) **19 直验 = 本环境 2026-10-17 单次**，arXiv 限流/网络波动可能影响未来重跑（已按"429 重试 1 次即 skip"规则处理，降级有预案）。
  - (5) **trial count = 120 是预注册最小基准**，04 实际搜索次数落地后需更新（精确数未定）。
- **取 0.80**：核验证据链强（19/19）压低"核验不确定"，但基线文献锚（RSI/momentum）+ 成本接口依赖（T05）两处残余不确定压低综合。比 T04（0.72）略高，因 T07 的核验比 02 更完整；但**不做 0.85+**，因两处文献锚不确定 + T05 成本依赖是真实存在、04 才能收敛的。

### 7.2 局限

1. **本节点只做"基线选择 + 协议设计"，不实现回测**（04 职责）。参数是**先验圆整**的预注册值，04 若调整须计入 trial count（§4.3）。
2. **19 直验 = 本环境 2026-10-17 单次、abs 页标题级**（与 02 同层级）；**未做 PDF 正文级**核验（正文级仅 T01 对 2608.27734 做过）。
3. **trial count 公式为预注册最小值（120）**，04 实际搜索落地后更新；精确数依赖 04 冻结的基线集 + 参数搜索次数。
4. **T05 成本模型缺失时的风险**：若 04 费率页仍不可达，成本参数维持 uncertain + last-known（spot 0.1000% / futures 0.0500% / maker 0.0200% / 滑点 base 0.01%）；**基线与 funding 必须用同一版本**（§4.2），不得 funding 用新费率、基线用旧费率。
5. **crypto 端幸存者偏差量化 = 公开缺口**（§2），S1 单标的不触发，但**预注册必须写明**多标的扩展时的 point-in-time 成分要求 + crypto 偏差幅度属缺口。

### 7.3 输出 schema 自检（对齐任务 output_schema）

- **anchors**：19 个 arXiv id（`verified=true`，`role` 见 §1.2 表）+ 12 条 uncertain ref（§5，`verified=false`）。
- **baselines**：5 条（`name`/`parameters`/`rationale` 见 §3）。
- **comparison_protocol**：三同（同 T04 §(c) 窗口 / 同 T05 §4 成本 / 同 T04 §(d) 45 家族，基线计入 trial count → 120 起）见 §4。

---

## §v2 核验补遗 (v2=827782bf 协同实例)

> 本节为按任务协同协议**分支①**在文末追加的只读核验补遗；原正文与任务 JSON 均不修改。核验方=T07 v2 协同实例（827782bf），核验日期 2026-10-17（host 本地时间 CST/UTC+8）。

### v2.0 协同状态记录（状态竞态，如实汇报）
- v2 初查（18:16 本地）：artifact 不存在（ls: No such file or directory）+ 任务 JSON status="ready" → 当时判定分支②（正常路径），v2 独立完成设计 draft 与 6 个 B 层候选的 curl 复核。
- v2 复核（18:33 后）：artifact 已在盘（32556 字节，mtime 18:21 = 原派发实例 7b69050c 写入）+ 任务 JSON status="completed"（updated_at=2026-10-17T10:33:29+00:00 即 18:33 本地；output/evidence 均已回填）→ **转分支①**：只读核验 + 本补遗。v2 独立 draft 作废（未落盘），任务 JSON 不修改（原实例已回填）。
- 时序自洽：artifact mtime（18:21）< JSON 回填（18:33），与"先写 artifact 再回填 JSON"的正常顺序一致，原实例判定为已走完全流程。

### v2.1 六点核验结论（全部通过）

| # | 必备内容点 | 结论 | 证据 |
|---|---|---|---|
| 1 | 文献核验分层（P1） | ✅ 通过 | §1 定义 A/B/uncertain 标准 + §1.2 19 个 URL 逐条直验列表（逐条状态，非笼统"19 个已核验"）；最终 19/19 全 A，v2 独立复核确认（见 v2.2） |
| 2 | 2603.19380 定性修正 | ✅ 通过 | §2 明确其为**股票指数**（印度 NIFTY Smallcap 250，1437 股，2016-2025，+4.94pp/23.3%，Sharpe +0.097/9.1%）**非 crypto**；§2.2 明示"不得挪用为 crypto 端证据"；crypto 端量化如实标为公开缺口 |
| 3 | 基线清单（含参数+验证层级） | ✅ 通过 | §3：buy-and-hold / momentum-12-1（L=252、S=21 交易日、日再平衡）/ RSI-14（Wilder N=14，<30 入场、>70 离场）/ trend-MA(50/200 EMA 金叉死叉) / funding 朴素（25/75 分位反向+符号跟随）；每条标 A/B/uncertain 层级（buy-and-hold=N/A industry standard） |
| 4 | 公平对比协议（三同） | ✅ 通过 | §4.1 同窗口=引用 T04 §(c) regime 日历锁定（5 年度 OOS 2021-2025、2022 熊强制 OOS、regime_locked=true）；§4.2 同成本=接口约定引用 T05 §4 不另定义（T05 已落盘且 §4 存在）；§4.3 同检验流程=引用 T04 §(d) 45 检验家族，**基线计入 trial count**（扩展至 120） |
| 5 | 未核验文献处理 | ✅ 通过 | §5 独立成节，12 条全标 "uncertain ref"（含 Harvey-Liu-Zhu 2016），未混入 §1 已核验清单；另含 arXiv 1308.3655 误引警报（实为粒子物理中微子论文） |
| 6 | 04 执行接口 | ✅ 通过 | §6：数据源（data.binance.vision 日线 klines + 月度 fundingRate 具体路径）+ PIT（引用 T04 §(b) B0-B6，基线与 funding 同一套不放宽）+ 各基线实现规格表 + 每窗口×每 regime 评估输出（2022 熊单列） |

### v2.2 6 个 B 层候选独立复核（v2 自测 curl，与原正文无矛盾）
v2 独立 curl 复核原 §1.2 升级 B→A 的 6 个候选（export.arxiv.org/abs/<id>，--max-time 30，2026-10-17）：

| ID | v2 实测 HTTP | v2 实测标题 | 原 §1.2 记录 | 结论 |
|---|---|---|---|---|
| 2601.10812 | 200 | Optimal Liquidation of Perpetual Contracts | 200 ✓ | 一致 |
| 2605.05089 | 200 | Dynamic Collateral Control for Permissionless Spot Perpetual Basis Trading | 200 ✓ | 一致 |
| 2602.11708 | 200 | Systematic Trend-Following with Adaptive Portfolio Construction: Enhancing Risk-Adjusted Alpha in Cryptocurrency Markets | 200 ✓（主标题） | 一致（v2 取含副标题全文） |
| 1905.05023 | 200 | Avoiding Backtesting Overfitting by Covariance-Penalties: an empirical investigation of the ordinary and total least squares cases | 200 ✓（主标题） | 一致（v2 取含副标题全文） |
| 2209.13623 | 200 | Publication Bias in Asset Pricing Research | 200 ✓ | 一致 |
| 2309.06711 | 200 | Epps Effect and the Signature of Short-Term Momentum Traders | 200 ✓ | 一致 |

- **6/6 HTTP 200 + 标题匹配**，与原正文 §1.2 及 Lead 预检情报均无矛盾；6 个 B 层候选的最终 A 层定性经 v2 独立复核确认。
- 范围说明：原 13 个 A 层条目 v2 未重新 curl（任务复核范围限于 6 个 B 候选）；v2 沿用 02/public-benchmarks.md 与原实例记录，不对该 13 条作独立复核声明。

### v2.3 观察项（设计差异/次要，均非矛盾）
1. **trial count 口径**：原正文取 120（45 + 5 spec×5 窗×3 regime=75 cell 上限保守计数）；v2 独立 draft 估计 ~55-60。两者均满足"基线计入 trial count"，原正文 120 在保守（上限）方向，与任务"保守防 under-deflation"意图一致，v2 判定更稳妥。
2. **基线条数**：原正文 5 条（7/30d 短周期动量并入动量变体；HMM 制度分解作评估维度而非第 6 条基线）；v2 draft 为 7 条。5 条方案完整覆盖任务要求的 buy-and-hold/动量/RSI+已核验公开基准，机制正交覆盖完备，非矛盾。
3. **JSON status 字面值**：任务协议写"JSON status=done"，盘上实值为 "completed"（output/evidence 已回填、postcondition 自证满足）；v2 按完成态处理（分支①），未改 JSON。
4. **momentum 锚点证据层级**：§3.2 如实标注 1904.00890 为**截面**动量、与本项目单标的**时序**用法不同（04 须注明）——恰当披露，属诚实加分而非缺陷。
5. **2603.19380 细节数字**：§2.1 的 1437 股/82.5% 换手/16.1%-33.1%-33.2% 分解比任务规格（4.94pp/23.3%）更细；核心两数 4.94pp/23.3% 经 v2 独立读 public-benchmarks.md 确认一致，其余细节 v2 未独立核验（未见矛盾）。

### v2.4 最终核验结论
- 原 artifact **六点必备内容全部通过**，与 v2 独立实测（6 B 层 curl 复核）及 Lead 预检情报**无矛盾**。
- 最终分层 **19/19 全 A** 经 v2 独立复核确认（就 6 个 B 层候选而言）。
- v2 未修改原正文，未修改任务 JSON（原实例已回填，status=completed）。
