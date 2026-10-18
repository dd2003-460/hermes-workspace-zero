# origin: ai

# T03 — Funding Rate 作为主择时/市场状态信号的负检索协议 (Negative Search Protocol)

> 本文件把 02 阶段 `public-benchmarks.md` #7 的缺口声明
> **「公开检索未找到以 funding rate 为主择时信号 / 市场状态信号的已发表回测」**
> 固化为可复现协议并执行核心检索。所有结果均为 curl 实际返回，未做任何虚构；空结果如实记录。

## 0. 结论速览 (TL;DR)

- **gap_confidence = 0.75**（缺口在 arXiv 公开预印本内强成立，但存在真实残留风险：付费金融期刊 + SSRN 不可搜 + 术语歧义）。
- 检索组数：**6 组**（≥ 任务要求的 5 组）。
- 双通道（arXiv HTML 宽松词匹配 + arXiv export API 严格短语匹配）**均无一条反例**：没有任何已发表论文以**加密货币永续合约 funding rate 为主择时信号/市场状态信号**并给出回测。
- 最接近的已发表邻接工作：arXiv:2608.25348（BTC 永续 PIT 审计 + 负结果，非 funding 择时策略）、arXiv:2506.08573（funding rate 设计/设定，非择时）、arXiv:2601.10812（最优清算控制，funding 仅作为成本项）。

---

## 1. 协议 (Protocol — 可复现)

### 1.1 检索日期
- **主机日期: 2026-10-17**（Sat Oct 17 2026，CST/Asia/Shanghai）。
- arXiv API feed 时间戳: `2026-10-17T06:56:33Z`。
- ISO date: **2026-10-17**

### 1.2 数据库 (Databases)
| 数据库 | 通道 | 状态 |
|--------|------|------|
| **arXiv (export.arxiv.org API)** | `bash curl`，任务指定格式 | ✅ 可达但**间歇 429** "Rate exceeded."（需 15s 间隔/重试）；重试后 200 |
| **arXiv (HTML search, arxiv.org/search/)** | `bash curl` | ✅ 稳定 200，宽松词匹配；连续过快请求偶发 14 字节 "Rate exceeded."，15–25s 间隔可靠 |
| **SSRN** | `bash curl` | ❌ 沙箱不可达（curl 000）— 列为局限 |
| **Google Scholar** | 无公开 API | ❌ 不可用 — 列为局限 |
| **付费金融期刊** (JFE/JBF/JFM 等) | 付费墙 | ❌ 沙箱不可搜 — 列为局限 |

> 说明: 本沙箱 `web_search` 工具无 API key 不可用，全程仅用 `bash curl`。`export.arxiv.org` 比 `arxiv.org` API 稳定。

### 1.3 检索词 (≥5 组，实际 6 组)
任务给定示例 + 优化后的 6 组：
1. `funding rate backtest`
2. `funding rate market regime`
3. `perpetual funding signal timing`
4. `funding rate momentum crypto`
5. `perpetual futures funding rate trading strategy`
6. `funding rate trading strategy`

### 1.4 可复现步骤
两条通道检索**同一 arXiv 库**，互为交叉验证（严格短语匹配是宽松词匹配的子集，双通道一致无命中 → 负结论更强）。

**通道 A — arXiv export API（任务指定格式）**，逐条执行（间隔 15s 防 429）：
```bash
# 多词用 + 连接，短语用 %22 引号
curl -sL "https://export.arxiv.org/api/query?search_query=<QUERY>&max_results=10&sortBy=relevance" -o out.xml
# 6 组 QUERY:
# Q1: all:%22funding+rate%22+AND+all:backtest
# Q2: all:%22funding+rate%22+AND+all:%22market+regime%22
# Q3: all:perpetual+AND+all:funding+AND+all:timing
# Q4: all:%22funding+rate%22+AND+all:momentum+AND+all:crypto
# Q5: all:%22perpetual+futures%22+AND+all:%22funding+rate%22+AND+all:%22trading+strategy%22
# Q6: all:%22funding+rate%22+AND+all:%22trading+strategy%22
```

**通道 B — arXiv HTML search（宽松词匹配）**：
```bash
curl -sL "https://arxiv.org/search/?query=<terms with + for spaces>&searchtype=all&start=0" -o out.html
# 例: https://arxiv.org/search/?query=funding+rate+backtest&searchtype=all&start=0
# 注意: 短语+AND 形式(%22...%22+AND+...) 解析异常/空；纯多词(funding+rate+backtest) 解析可靠。
```

**解析**:
- API: Atom `<entry>` 块 → id/title/published/summary（`parse_api.py`）。
- HTML: `<li class="arxiv-result">` 块 → id/title/date/abstract（`parse_html.py`/`extract_full.py`）。
- 每条 top hit 人工判读其摘要，判定**是否以 funding rate 为主择时信号**，并记录为何不是反例。

> 原始文件保存在 `/tmp/t03-search/`：`html-1..6.html`、`api-1..6.xml`、解析脚本 `parse_html.py`/`extract_full.py`/`parse_api.py`。（临时目录，非交付物。）

---

## 2. 逐 query 结果表

> 对每组给出：API（严格短语）结果、HTML（宽松词）结果、top hit（标题 + arXiv id）、**为何不是反例**。
> “反例”定义: 一篇已发表工作，其**主择时/市场状态信号 = 加密货币永续 funding rate**，并给出策略回测。

### Q1 — `funding rate backtest`
| 通道 | 命中数 | Top hit |
|------|--------|---------|
| API (短语 "funding rate" AND backtest) | **0** | （无） |
| HTML (宽松词) | 1 | arXiv:1706.10059 *A Deep Reinforcement Learning Framework for the Financial Portfolio Management Problem* (2017) |

- **为何不是反例**: 1706.10059 的核心是 **DRL 组合管理框架**（EIIE/PVM/OSBL + CNN/RNN/LSTM），在 30 分钟交易周期的加密货币市场做回测。"funding"/"rate" 仅作为成本/费率类词面出现，**信号源是 DRL 模型而非 funding rate**；API 严格短语 "funding rate" 甚至 0 命中，证明该词非其核心概念。
- **负结论**: 无 funding rate 择时回测。

### Q2 — `funding rate market regime`
| 通道 | 命中数 | Top hit |
|------|--------|---------|
| API (短语 "funding rate" AND 短语 "market regime") | **0** | （无） |
| HTML (宽松词) | 5 | arXiv:2607.11888 *Optimal Adaptive Market Making: … Perpetual Futures Markets* |

- **为何不是反例**: 2607.11888 是**做市（流动性提供）最优控制理论框架**；funding rate 仅作为 PnL 分解中的 "funding rate exposure" 与跨所对冲的 "funding rate dynamics" 出现，是**微观结构/做市问题**，不是以 funding rate 为主择时/市场状态信号的回测。HTML 宽松命中的其余（2604.08825 *Is Bitcoin A Hedge…*, 2604.01431 *Do Prediction Markets Forecast Cryptocurrency Volatility?*）中 "funding rate" 实为 **Federal Funds Rate**（宏观货币政策），信号源分别是 LLM 货币政策预期指数、Kalshi 预测市场概率——**均非加密 funding rate 择时**。
- **负结论**: API 严格匹配 0 命中，强化负结论。

### Q3 — `perpetual funding signal timing`
| 通道 | 命中数 | Top hit |
|------|--------|---------|
| API (perpetual AND funding AND timing) | 10 | arXiv:2506.08573 *Designing funding rates for perpetual futures in cryptocurrency markets* (2025) |
| HTML (宽松词) | 3 | arXiv:2609.04917 *AI in Equity and Crypto Markets: Progress, Profitability Evidence…* |

- **为何不是反例**:
  - 2506.08573: 研究 **funding rate 的"设计/设定"**（发行人如何设 funding rate 以维持永续价格对齐），是**机制设计**，不是择时信号回测。
  - 2609.04917: **AI 交易状态综述**，明确结论 "no general AI architecture is shown to deliver persistent, cross-regime, capacity-aware net alpha"——**本身支持缺口**，且非 funding 择时回测。
  - 其余 API top（2209.03307 *A primer on perpetuals*、2310.11771 *Perpetual Futures Pricing*、2212.06888 *Fundamentals of Perpetual Futures*、2609.05433 *Perpetual Futures for Stocks: The SpaceX Pre-IPO Market*）均为**定价/无套利/理论**。
  - **最接近邻接工作**: HTML 命中的 **arXiv:2608.25348** *Point-in-Time Audit Before Alpha: … Negative Matched-Budget Study on BTC Perpetual Futures* — 数据设定最接近本项目（Binance BTCUSDT USD-M 永续，含 trade/mark/index/funding/OI 流，PIT 审计），但它是**数据可用性审计 + 自适应 agent 负结果研究**（"all evaluated runs had positive IC but negative net Sharpe"），**不是以 funding rate 为主择时信号的策略回测**。
- **负结论**: 10 条 API 命中全部为理论/定价/机制设计/综述，无一条 funding 择时回测。

### Q4 — `funding rate momentum crypto`
| 通道 | 命中数 | Top hit |
|------|--------|---------|
| API (短语 "funding rate" AND momentum AND crypto) | **0** | （无） |
| HTML (宽松词) | **0**（arXiv 原文 "Sorry, your query for all: funding rate momentum crypto produced no results."） | （无） |

- **为何不是反例**: 双通道均 **0 结果**（HTML 为 arXiv 官方 "produced no results" 页，非 curl 失败）——如实记录。
- **负结论**: 无任何 funding rate 动量加密回测。

### Q5 — `perpetual futures funding rate trading strategy`
| 通道 | 命中数 | Top hit |
|------|--------|---------|
| API (短语 "perpetual futures" AND 短语 "funding rate" AND 短语 "trading strategy") | **0** | （无） |
| HTML (宽松词) | 2 | arXiv:2605.11263 *Optimal Control of the Ethena Yield-Bearing Stablecoin* |

- **为何不是反例**:
  - 2605.11263: **Ethena DeFi 协议的随机控制**（stETH 多头 + ETH 永续空头，delta 中性 carry 策略）。funding rate 是 carry 的**一个收入来源**（"funding-rate payments received from long perpetual holders"），核心是**基差/carry 套利的最优执行控制**，不是以 funding rate 为主择时/市场状态信号。
  - 2212.06888 *Fundamentals of Perpetual Futures*: **定价/无套利理论** + 隐含套利策略（基差套利），02 阶段已列为"最接近锚点但属定价/套利视角，非 funding 市场状态择时回测"。
- **负结论**: API 严格短语 0 命中；HTML 两条均为 carry/基差/定价，非 funding 择时。

### Q6 — `funding rate trading strategy`
| 通道 | 命中数 | Top hit |
|------|--------|---------|
| API (短语 "funding rate" AND 短语 "trading strategy") | 2 | arXiv:2601.10812 *Optimal Liquidation of Perpetual Contracts* (2026) |
| HTML (宽松词) | 22 | arXiv:2609.14859 *Gate Design and Stage-Dependent Incentives in Retail Proprietary-Trading Evaluations* |

- **为何不是反例**:
  - **API #1 2601.10812**: **最优清算（退出）控制问题**——"managing transaction costs, inventory risk, **and funding rate payments**"，funding 是**清算成本项**，求解的是给定持仓下的最优**退出**策略，**不是以 funding rate 为主入场/择时信号**。
  - **API #2 2506.22763** *Can We Reliably Predict the Fed's Next Move?* — "funding rate" 实为 **Federal Funds Rate**（美联储政策预测），**错误同名词**，与加密 funding rate 无关。
  - **HTML top 2609.14859** 为零售自营交易**门/激励设计**；2609.05663 *What LLM Trading Agents Actually Do in Production* 为 LLM 交易 agent 生产记录（funding 仅词面出现）；2603.10092 *Execution Is the New Attack Surface* 为**执行层安全/生存性**（funding 仅作数据字段）。**均非 funding rate 择时回测**。
- **负结论**: 严格短语 2 条均为清算控制/宏观误同名，宽松 22 条无一以 funding 为主择时信号。

---

## 3. 局限 (Limitations — 显式)

1. **仅覆盖 arXiv 公开预印本**。本沙箱 `web_search` 无 API key、SSRN 不可达（curl 000）、Google Scholar 无 API、付费金融期刊（JFE / Journal of Banking & Finance / Journal of Futures Markets 等）不可搜。**一篇以 funding rate 为主择时信号的回测完全可能只发表于付费金融期刊而非 arXiv。**
2. **arXiv 术语歧义**: "funding rate" 在宏观金融中 = **Federal Funds Rate**（2506.22763、2604.08825、2604.01431 均为 Fed 利率），在加密中 = 永续 funding rate。同名词污染使纯文本检索难以精确区分；**加密 funding 择时论文可能用 "perp carry" / "funding carry" / "basis signal" 等未覆盖术语**。
3. **检索词有限（6 组）**: 穷举所有可能措辞不可能；存在未覆盖的同义/邻接表述。
4. **arXiv 限流**: export API 间歇 429、HTML 连续请求偶发 "Rate exceeded."，需 15–25s 间隔；本检索在限流下完成，未做分页深翻页（max_results=10 / 首页），极冷门深排结果可能漏检。
5. **未检索非 arXiv 学术平台**: SSRN（金融论文主阵地）、RePEc、NBER、工作论文系列均不可达。

---

## 4. gap_confidence 与残留风险

### gap_confidence = **0.75**

**评级理由**:
- **+** arXiv（唯一可全量检索的公开库）内 **强成立**: API 严格短语匹配 Q1/Q2/Q4/Q5 = **0 命中**；Q3 = 10 条全部理论/定价/机制/综述；Q6 = 2 条（清算控制 + 宏观误同名）。双通道（宽松 + 严格）一致无反例。
- **+** 与 02 阶段已锚定的最接近文献一致: 1912.03270（funding 可预测性/Granger，单所，**无策略回测**）、2212.06888（定价/套利，非择时）、2025-26 机制/做市/基差系列——均非 funding 主择时回测。
- **−** 付费金融期刊 + SSRN 不可搜（真实可能藏反例）。
- **−** 术语歧义 + 6 组词有限 + 未深翻页。

> 口径说明: gap_confidence 度量的是**「以 funding rate 为主择时/市场状态信号的已发表回测不存在」**这一缺口陈述的置信度（而非「本次公开检索确实没找到」——后者置信度 ≈0.9+）。

### 残留风险 (Residual Risk)

1. **付费期刊黑箱（最高风险）**: 若反例存在于 JFE/JBF/JFM 等付费金融期刊或 SSRN，本检索无法发现 → 缺口可能被推翻。**缓解**: 后续节点若有期刊数据库访问权限，应补一轮付费库检索；当前 0.75 已对该风险打折。
2. **术语漂移**: 加密 funding 择时研究若以 "perp carry" / "funding carry" / "basis signal" / "basis trade" 表述，6 组词可能全部漏检。**缓解**: 协议可复现，后续可按需扩充检索词（carry/basis 族）再跑一轮。
3. **浅翻页**: 仅首页/前 10，极冷门排序的命中可能漏。**缓解**: 如需，可对 Q3/Q6 追加 `start=10,20…` 深翻页。
4. **双通道差异已记录但属预期**: HTML 宽松词匹配命中数 > API 严格短语匹配（如 Q1: HTML 1 vs API 0），差异源于词面匹配 vs 短语匹配，**两通道一致无反例**，不削弱负结论。

### 对下游 (03 阶段其他节点) 的含义
- 缺口陈述 **"公开检索未找到以 funding rate 为主择时信号的已发表回测" 在 arXiv 范围内成立（0.75 置信）**，可作为本项目"以 funding rate 为主择时/市场状态信号"之**新颖性声明**的支撑，但**必须**在最终论文中把该新颖性限定为"公开可检索预印本范围内"，并披露 SSRN/付费库未覆盖这一局限（本文件 §3 可直接引用）。

---
*生成: T03 node worker | 主机日期 2026-10-17 | 通道: arXiv export API + arXiv HTML search | 原始件: /tmp/t03-search/{html-1..6.html, api-1..6.xml}*

---

## 5. v2 独立交叉验证 (T03 v2 补派, 主机日期 2026-10-17)

> 本节为 **v2 补派轮次** 的独立复现，不改动上文 v1 结论；用于交叉验证并补齐任务 JSON 回填。
> 说明: v2 复跑前发现本 artifact 已由 v1 轮次写出(15:14)，且为更完备的双通道协议；v1 引用件已逐一核验为真实文献，故 v2 **不覆盖** v1，仅追加独立验证。

### 5.1 v2 独立复跑 (arXiv export API 单通道, 6 组, 全部真实 HTTP 200)

检索日期 **2026-10-17**；`https://export.arxiv.org/api/query`，`all:`(标题+摘要)字段，`max_results=10`，`sortBy=relevance`。执行中遇 arXiv 限流(429 "Rate exceeded")，采用 90s 冷却 + 12s 组间隔 + 单组 8s 一次重试后全部取得真实 HTTP 200 数据（非 429 污染）。

| # | 查询串 (search_query) | HTTP | totalResults | 与 v1 一致性 |
|---|---|---|---|---|
| Q1 | `all:"funding rate" AND all:"backtest"` | 200 | **0** | 一致 (v1 Q1 API=0) |
| Q2 | `all:"funding rate" AND all:"market regime"` | 200 | **0** | 一致 (v1 Q2 API=0) |
| Q3 | `all:"perpetual" AND all:"funding rate" AND all:"timing"` | 200 | **6** | 一致 (v1 Q3 理论/定价/机制族；命中 2506.08573 / 2212.06888 / 2209.03307 / 2601.10812 / 2609.05433 / 2310.14973，均非择时回测) |
| Q4 | `all:"funding rate" AND all:"momentum" AND all:"crypto"` | 200 | **0** | 一致 (v1 Q4 双通道=0) |
| Q5 | `all:"funding rate" AND all:"trading strategy" AND all:"perpetual"` | 200 | **1** | 一致 (2601.10812 最优清算, funding=成本项, 非择时信号) |
| Q6 | `all:"funding rate" AND all:"timing signal"` | 200 | **0** | 一致 (v1 无直接同名组, v2 增补, 0 命中强化负结论) |

**v2 逐条判定**: 4 组 0 命中；2 组命中(Q3×6, Q5×1)经标题+摘要判读**全部非反例**(机制设计 / 定价理论 / 教学 / 清算执行 / 股票 pre-IPO / OI 对账)。**结论与 v1 完全一致: 缺口在 arXiv 范围内成立。**

### 5.2 v1 关键引用件真实性核验 (v2 curl 确认)

- **arXiv:2608.25348** — v2 用 `id_list=2608.25348` 单独核验 → **真实文献**: *"Point-in-Time Audit Before Alpha: Public-Archive Availability and a Negative Matched-Budget Study on BTC Perpetual Futures"* (2026-08-26, Binance BTCUSDT USD-M 永续, 数据可用性 PIT 审计 + 80 模板负结果匹配预算研究)。属**数据可用性审计 + 负结果**，**非** funding rate 主择时信号回测 → **不是反例**，v1 引用**未虚构**，且为本项目最接近邻接锚(数据设定高度重合)。
- 2506.08573 / 2601.10812 / 2212.06888 — v2 在 Q3/Q5 复跑中独立再次命中，标题/摘要与 v1 描述一致。

### 5.3 v2 结论与 gap_confidence 裁定

- **gap 成立** (arXiv 全库, 标题+摘要, 2026-10-17): 双轮次(v1 双通道 + v2 独立 API)一致无反例。
- **gap_confidence 裁定**: v2 独立单通道复算得 0.85；**采纳 v1 的 0.75 为权威值**——v1 覆盖双通道(严格短语+宽松词)并更完整地计入付费期刊/SSRN 盲区、术语歧义(Federal Funds Rate 同名污染)、浅翻页等残留风险，口径更保守、更审慎。最终 **gap_confidence = 0.75**。
- **残留风险**: 与 v1 §4 一致(付费期刊/SSRN 黑箱为最高风险；术语漂移 carry/basis 族；浅翻页)；v2 新增确认: 最接近邻接锚 **2608.25348** 为负结果研究，**进一步支持**"funding 作主择时信号的回测尚未发表"的缺口陈述。

*v2 补派验证 | 主机日期 2026-10-17 | 通道: arXiv export API (6 组, 独立复跑) | 原始件: /tmp/t03_arxiv/{Q*_v3.xml, Q1_clean.xml, Q3_clean.xml, chk25348.xml, results3.txt}*
