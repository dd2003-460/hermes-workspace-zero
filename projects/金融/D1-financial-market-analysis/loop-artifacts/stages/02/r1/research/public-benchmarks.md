# 同类时间戳信号回测的公开研究基准与常见失败模式

**disposition**: confirmed（Q1 公开基准与 Q2 失败模式均有已验证一手来源；核心 arXiv 来源 13 篇 abs 页直接抓取验证 + 6 篇列表级引用；期刊经典文献为未核验领域知识，待 02.5 补 URL）
**观察时间**: 2026-10-17（子代理调研；web_search 不可用；主通道 = arXiv HTML 搜索 + curl 直取 abs 页，全部 HTTP 200）

## 工具可用性（如实记录，失败≠证据）

- `web_search` 不可用：`DeepSeek search has no API key for DEEPSEEK_API_KEY`（与项目先前记录一致）。
- arXiv Atom API（export.arxiv.org）：限流（429/503/30s timeout，多次重试失败）→ 弃用。
- arXiv HTML 搜索（`https://arxiv.org/search/?query=...&searchtype=all`）+ abs 页直取：curl 稳定 200、无限流 → 本次主通道；已验证 13 个 abs 页全 200。
- Semantic Scholar API：429 限流，不可用。
- SSRN（ssrn.com）：沙箱不可达（curl 000）→ Harvey/Hou/López de Prado 等 SSRN 托管期刊文献本次无法直接 URL 核验（标"未核验领域知识"）。
- chainalysis.com/reports/：可达（200）但未抓取（预算）→ 行业报告《State of Perpetual Futures》未核验。
- 重要教训：记忆中 Bailey et al.《Pseudo-Mathematics and Financial Charlatanism》的 arXiv ID 1308.3655 经 fetch 验证**是错的**（实为粒子物理论文《Models with radiative neutrino masses...》Restrepo/Zapata/Yaguna 2013）→ 不引用；引用前必须 fetch 验证，已执行。

## 关键主张与来源

### Q1 公开研究基准

#### A. funding rate / 永续（perps）专项研究（与 S1 主场景直接可比）

**1. funding rate 可预测性的直接实证（2019，最早公开实证之一）**
- 来源标题: BitMEX Funding Correlation with Bitcoin Exchange Rate（Nimmagadda & Ammanamanchi）
- URL: https://arxiv.org/abs/1912.03270
- 发布日期: 2019-11-26；观察日期: 2026-10-17
- 实际观察: 证明 funding rate 的异方差性；Granger 因果：funding rate ↔ Bitcoin 反向永续互换（双向）；用最佳拟合 GARCH 模型建立 funding rate 预测模型；摘要结论：结果对"用 funding rate 做市场趋势预测工具有意义"。
- 对本项目的含义: funding rate 有方向性预测力是**已存在的公开主张**；但该研究仅单所（BitMEX）、单币（BTC）、2021 前样本 → 本项目 2020-01→2025-01+ 窗口（含牛/熊/震荡/牛）是样本与制度覆盖的直接升级，可与其同信号（funding rate）对标。
- 不确定性: arXiv 预印本，未见期刊版；Granger 因果 ≠ 策略可盈利（该文未做策略回测）。

**2. 永续基差/funding 的套利理论框架（funding 信号为何存在）**
- 来源标题: Fundamentals of Perpetual Futures（He, Manela, Ross, von Wachter）
- URL: https://arxiv.org/abs/2212.06888
- 发布日期: 2022-12-13；观察日期: 2026-10-17
- 实际观察: 无摩擦市场永续无套利定价 + 含交易成本的定价边界；实证：crypto 永续相对标的的偏离**大于传统货币市场**、跨币种共动、随时间衰减；提出隐含套利策略。
- 对本项目的含义: funding 本质是"瞬时偏离的价格"（carry/basis 成分）——funding 信号有理论锚；但该文是定价/套利视角，**不是"用 funding 做市场状态择时"的回测**（最接近的公开锚，直接可对标基准仍未找到）。

**3. funding rate 设计与复制组合（2025，机制侧）**
- 来源标题: Designing funding rates for perpetual futures in cryptocurrency markets（Kim & Park）
- URL: https://arxiv.org/abs/2506.08573
- 发布日期: 2025-06-10；观察日期: 2026-10-17
- 实际观察: 通过适当设计 funding rate 可使永续价格锚定目标价值；开发永续期货复制组合供发行方对冲；讨论路径依赖 funding rate 替代方案。
- 对本项目的含义: funding 是可调节的设计参数而非固定利率——信号构造时"不同 funding 规则下信号含义不同"的机制参考。

**4. OI 指标与 funding 的关系（S1 次级信号 OI 的学术定位）**
- 来源标题: Reconciling Open Interest with Traded Volume in Perpetual Swaps（Giagkiozis & Said）
- URL: https://arxiv.org/abs/2310.14973
- 发布日期: 2023-10-23；观察日期: 2026-10-17
- 实际观察: funding rate 经套利者将永续锚定标的；OI 是永续市场核心指标（活动度/情绪/流动性）；由 OI 与成交量估计抵押品下界。
- 对本项目的含义: "OI 作为状态指标"有公开学术定位可用（阶段 03 的 OI 增补论证），但免费 5 年 OI 历史已实证不可得（见 data-history-depth.md）→ OI 只能作辅助验证。

**5. 清算（liquidation）端——清算级联问题**
- 来源标题: Optimal Liquidation of Perpetual Contracts（**列表级引用**：标题/ID/日期来自 arXiv 搜索页，abs 未抓取）
- URL: https://arxiv.org/abs/2601.10812
- 发布日期: 2026-01-15；观察日期: 2026-10-17
- 实际观察: 搜索页标题级信息；清算理论方向的永续论文。
- 对本项目的含义: "清算级联"的**公开实证基准 = 缺**（本次未找到专门实证清算级联的加密论文）；行业报告（Chainalysis，未核验）是仅有的公开侧补充。

**6. 基差交易（basis trade / cash-and-carry）基准**
- 来源标题（学术经典，非 crypto）: Optimal Dynamic Basis Trading（Angoshtari & Leung）
- URL: https://arxiv.org/abs/1809.05961
- 发布日期: 2018-09-16；观察日期: 2026-10-17
- 实际观察: 随机基差下期货+标的动态交易（基差建模为 stopped scaled Brownian bridge，允许到期不收敛）；HARA 效用；HJB 方程精确解条件 + 数值算例。
- 来源标题（crypto，**列表级引用**）: Dynamic Collateral Control for Permissionless Spot Perpetual Basis Trading
- URL: https://arxiv.org/abs/2605.05089（发布日期: 2026-05-06；观察日期: 2026-10-17；搜索页级：permissionless 场景 spot-perp 基差交易的动态抵押控制）
- 对本项目的含义: carry/基差是标准策略类，"funding 作为 carry 信号"的公开对标线存在；但 crypto 专项基差交易论文 2026 年才出现 → 该细分领域年轻，直接可复制的 crypto 回测基准少。
- 未核验领域知识（待补URL）: Koijen, Moskowitz, Pedersen, Vrugt《Carry》(JFE 2018)——跨资产 carry 经典。

**7. 永续市场微观结构模拟（方法论基准）**
- 来源标题: Agent-Based Simulation of a Perpetual Futures Market（Rao）
- URL: https://arxiv.org/abs/2501.09404
- 发布日期: 2025-01-16；观察日期: 2026-10-17
- 实际观察: CLOB 限价订单簿上的 agent-based 模型（扩展 Chiarella et al. 2002 参数至永续环境），含方向性 + 基差交易 agent。
- 对本项目的含义: funding 由多空失衡/套利者生成——信号"机制侧"有公开仿真参考，可作稳健性检验（信号生成机制仿真 vs 历史回测交叉验证）。

#### B. 朴素基准（buy & hold / 动量 / 趋势）

**8. 动量（crypto 专项，abs 已验证）**
- 来源标题: Momentum and liquidity in cryptocurrencies（Begušić & Kostanjčar）
- URL: https://arxiv.org/abs/1904.00890
- 发布日期: 2019-04-01；观察日期: 2026-10-17
- 实际观察: 最流动 crypto 资产中动量效应强（支持羊群理论）；动量-流动性二元排序构建组合；两个 long-only 策略（illiquid losers / liquid winners）跑赢市值加权组合。
- 对本项目的含义: "动量择时"朴素基准在 crypto 文献中有公开锚；注意该文是**截面**（多币种排序），本项目 S1 是**时序**（BTCUSDT 单标的）——03 阶段用单标的 N 日动量构造基准时需注明此区别。
- 未核验领域知识（待补URL）: Jegadeesh & Titman (1993, JF) 动量经典（股票端）。

**9. 趋势跟随（crypto，列表级引用）**
- 来源标题: Systematic Trend-Following with Adaptive Portfolio Construction: Enhancing Risk-Adjusted Alpha in Cryptocurrency Markets（Bui & Nguyen，**列表级引用**）
- URL: https://arxiv.org/abs/2602.11708（发布日期: 2026-02-12；观察日期: 2026-10-17，搜索页级）
- 对本项目的含义: 最新 crypto 趋势跟随文献，可作"趋势跟随 vs funding 择时"的对标锚。
- 未核验领域知识（待补URL）: Lo, Mamaysky, Wang (2000, JFE) 技术分析/均线经典；buy & hold 为行业标准实践，无需引用。

#### C. 制度切换 / 非平稳（状态类信号必须处理的维度）

**10.** 来源标题: Evolutionary correlation, regime switching, spectral dynamics and optimal trading strategies for cryptocurrencies and equities（James）
- URL: https://arxiv.org/abs/2112.15321（v1 2021-12-31；搜索页显示后续版本 2022-03-13；观察日期: 2026-10-17，abs 已验证）
- 实际观察: 随机矩阵理论 + PCA 对比 crypto vs 股票相关矩阵特征谱差异；时变行业行为；regime switching 与最优交易策略。
**11.** 来源标题: Quantile and expectile copula-based hidden Markov regression models for the analysis of the cryptocurrency market（Foroni, Merlo, Petrella）
- URL: https://arxiv.org/abs/2307.06400（发布日期: 2023-07-12；观察日期: 2026-10-17，abs 已验证）
- 实际观察: 用 regime-switching copula 的 hidden Markov 回归模型联合估计 crypto 收益的 quantile 与 expectile。
- 对本项目的含义: "制度切换"是 crypto 文献成熟线（HMM/copula-HMM/RMT）；若 funding 信号定位"状态信号"，回测必须按制度分解评估（regime-wise），否则"整体 Sharpe"可能掩盖制度依赖。
- 未核验领域知识（待补URL）: Hamilton (1989, Econometrica) Markov 制度切换起源。

### Q2 常见失败模式（每条给公开出处）

**F1. 前视偏差 / look-ahead bias（PIT 泄露）— 本项目第一失败模式**
- 已验证来源 1: Look-Ahead-Freedom as Temporal Non-Interference: A Verifiable Correctness Property for Backtesting and Agentic Trading Pipelines（Fonseca）
  - URL: https://arxiv.org/abs/2607.04958（2026-07-06；观察日期 2026-10-17，abs 已验证）
  - 实际观察: 原文 "Look-ahead bias (using information from after a decision epoch to make the decision at that epoch) is the dominant way a backtest or a machine-learning evaluation flatters a system that will disappoint in deployment"；将 look-ahead-freedom 形式化为时间信息格上的 temporal non-interference；给出分离"数据可用性"与"参考时点"的 pipeline calculus。
- 已验证来源 2: Does Training on Future Data Pay? Look-Ahead Bias in Forecasting with Pretrained Models（Chen, Chen, Chen, Huang, Zhang）
  - URL: https://arxiv.org/abs/2609.20554（2026-09-17；观察日期 2026-10-17，abs 已验证）
  - 实际观察: post-origin 训练信息系统性夸大测量精度与经济价值；5 组时序基础模型 × 年度 vintage，14 个股票市场、4 个期限；以 origin-aligned PIT 基准（数值历史完全相同）对照。
- 对本项目的具体含义: funding 8h 结算 + 日线文件 T+1 发布（见 data-revision-latency.md 主张 3）→ 信号必须对齐"当时已知"时间戳（t 时点信号最早 t+1 日文件/下一 8h 结算后可用），否则整个回测无效。

**F2. 幸存者偏差 / survivorship bias**
- 已验证来源（量化）: Survivorship Bias in Emerging Market Small-Cap Indices: Evidence from India's NIFTY Smallcap 250（Ranse）
  - URL: https://arxiv.org/abs/2603.19380（2026-03-19；观察日期 2026-10-17，abs 已验证）
  - 实际观察: 1437 只股票、2016-2025 九年；survivor-only 回测**高估年化收益 4.94pp（23.3%）、Sharpe 0.097（9.1%）**；成分 82.5% 换手（退市 16.1% / 升级 33.1% / 降级 33.2%）；用含退市股数据（bhavcopy）重建可 100% 复现当时成分。
  - 独立性说明: 唯一已核验量化来源（股票指数场景，非 crypto）；机制与加密"仅用当前在市交易对"同构。
- 对本项目的具体含义: S1 若固定 BTCUSDT 单标的 → 幸存者风险低（长期存续标的），预注册中注明即可；若扩展到多交易对 → 必须用"当时时点成分清单（含已退市对）"，收益将被系统性高估（幅度参考 4.94pp/23.3% 量级，crypto 无直接量化）。
- 缺口: crypto 端幸存者偏差的专门量化论文本次未找到（公开基准缺口）。
- 未核验领域知识（待补URL）: López de Prado《Advances in Financial Machine Learning》(Wiley 2018) 幸存者偏差标准处理章节。

**F3. 回测过拟合 / 数据窥探 / 多重检验**
- 已验证来源（crypto 专属）: Deep Reinforcement Learning for Cryptocurrency Trading: Practical Approach to Address Backtest Overfitting（Gort, Liu, Sun, Gao, Chen, Wang）
  - URL: https://arxiv.org/abs/2209.05559（2022-09-12；观察日期 2026-10-17，abs 已验证）
  - 实际观察: 指出现有 DRL 回测"optimistically reported increased profits...may suffer from the false positive issue due to overfitting"；将 backtest overfitting 检测**形式化为假设检验**，估计过拟合概率并拒绝过拟合 agent；10 个 crypto 测试。
- 已验证来源（**列表级**）: Avoiding Backtesting Overfitting by Covariance-Penalties — URL: https://arxiv.org/abs/1905.05023（2019-05-01，搜索页级）
- 已验证来源（**列表级**，发表偏差相关）: Publication Bias in Asset Pricing Research — URL: https://arxiv.org/abs/2209.13623（2023-09-21，搜索页级；资产定价研究只发表显著结果 → 文献本身有选择偏差，读公开基准时需打折）
- 未核验领域知识（待补URL，SSRN 不可达）: Bailey, Borwein, López de Prado, Zhu《Pseudo-Mathematics and Financial Charlatanism》(2013, 回测过拟合经典；**注意 arXiv ID 1308.3655 经验证是错的粒子物理论文，未重新核实正确 ID，不引用**)；Bailey et al.《The Deflated Sharpe Ratio》(JCF 2014)；Harvey, Liu, Zhu《Backtesting》(JF 2016, 多重检验 t>3.0 惯例)；White《A Reality Check for Data Snooping》(Econometrica 2000)。
- 对本项目的具体含义: 预注册约束"滚动走步 OOS + 明确训练/验证/测试边界"正是对此的缓解；参数网格多时必须报告试验次数，理想用 DSR 类校正（DSR 具体 URL 待 02.5 补）；2209.05559 的"过拟合概率检验"方法可直接参考。

**F4. 非平稳 / 制度切换**
- 已验证来源: 见 Q1-C（arXiv:2112.15321 与 arXiv:2307.06400，两篇 abs 均已验证）——crypto 文献把非平稳/制度切换当常态处理。
- 对本项目的具体含义: 本项目窗口（2020-21 牛 / 2022 熊 / 2023 震荡 / 24-25 牛）天然覆盖多制度 → 回测结果必须按制度分解呈现（per-regime Sharpe/命中率），并检验"跨制度稳定性"（这是预注册稳定性判据的文献依据）。
- 未核验领域知识（待补URL）: Hamilton (1989)。

**F5. 成本 / 滑点低估**
- 已验证来源（间接但直接相关）: arXiv:2212.06888（主张 2）——"含交易成本的定价边界"是该文核心框架之一：成本直接改变永续无套利区域 → 对 perp 策略，成本模型是核心组件而非后加项。
- 未核验领域知识（待补URL）: 本次未找到 crypto 回测成本/滑点建模的专门公开论文；一般实践 = taker 手续费 + 滑点（按订单簿深度）+ 开平仓时点的 funding 结算归属；Binance USDT-M 当前费率数值**未核验**（developers.binance.com 沙箱不可达）。
- 对本项目的具体含义: funding 择时信号若触发频率低（日/周级），成本敏感性中等；若在 8h 结算边界高频进出，必须显式建模 funding 结算成本与滑点。

**F6. 数据修订 / PIT（与同目录文件交叉引用，不重复）**
- 机制与公开出处已在 data-revision-latency.md 确认（官方 mutable archive 承认 + 2 例历史修订 + T+1 迟报 + 末根 K 线未定版）。
- 对本项目的具体含义: 回测数据管线应"记录下载时点 + CHECKSUM"，并在预注册中声明"用的是截至下载时点的归档"；信号时间戳对齐规则（F1）与之联动。

**F7. 信号衰减 / 单周期过拟合 / 频率错配**
- 已验证来源（**列表级**）: Epps Effect and the Signature of Short-Term Momentum Traders — URL: https://arxiv.org/abs/2309.06711（2023-09-13，搜索页级；crypto 短期限动量结构（Epps 尺度）与低频信号不同 → 注意信号频率与数据频率匹配）。
- 未核验领域知识（待补URL）: McLean & Pontiff (JF 2016) 因子衰减；Hou, Xue, Zhang《Replicating Anomalies》(RFS 2015) 数据质量与异常衰减。
- 对本项目的具体含义: funding rate 定义本身在样本期内可能变化（结算间隔/cap 政策等，具体条目未核验）→ 回测中必须保留"当时时点的 funding 定义"（PIT 信号定义），避免用当前定义回溯。

## 公开基准的总体缺口判断（诚实记录）

1. **直接可对标回测稀缺**：未找到专门以"funding rate 作为市场状态/择时信号"的已发表回测（最接近 = 2019 funding 可预测性实证 arXiv:1912.03270 + 定价理论 arXiv:2212.06888 + 2025-26 机制/做市/基差交易论文群）。→ 本项目的定位是**填补缺口**；对照基线应自建朴素基准（buy & hold / 动量 / 趋势）+ 引用上列公开锚。
2. **失败模式经典文献全在期刊/书（SSRN/Wiley/Elsevier），沙箱 SSRN 不可达** → 全部标未核验领域知识（待补URL），02.5 交叉验证阶段补。
3. **crypto 端幸存者偏差、清算级联的量化公开基准 = 缺口**（幸存者量化仅有 2026 股票指数一篇；清算级联仅有理论清算论文 + 未核验行业报告）。
4. crypto 基差交易/趋势跟随的**专项**回测基准 2026 年才出现 → 领域年轻，直接可复制的公开回测少，自建基准的合理性高。

## 对阶段03的建议输入（只给建议输入，不写最终推荐）

1. **基准集（建议纳入对照）**：(a) buy & hold BTCUSDT；(b) 朴素动量（如 7/30 日收益符号）；(c) 趋势跟随/均线择时（对标锚 arXiv:2602.11708 / 未核验 Lo-Mamaysky-Wang 2000）；(d) funding 朴素规则（如 funding 极端分位 → 反向/跟随仓位，对标锚 arXiv:1912.03270 的 GARCH 预测思路）；(e) 制度分解评估（HMM 分解对标 arXiv:2307.06400 / 2112.15321）。
2. **PIT 检查清单（优先级最高）**：8h funding 结算时间戳 × T+1 日线文件（data-revision-latency.md 主张 3）→ 每个决策时点只允许用"当时已发布"的数据；实践上给每个数据点打"数据可用时间"与"参考时点"双时间戳（形式化框架参考 arXiv:2607.04958）。
3. **过拟合缓解**：滚动走步 OOS（预注册已有）+ 报告试验次数 + DSR 类校正（URL 待 02.5 补）；方法上可参考 arXiv:2209.05559 的过拟合概率检验。
4. **幸存者处理**：S1 固定 BTCUSDT → 预注册注明"单一长期存续标的，幸存者偏差不适用/已控制"；扩展多标的 → 必须含已退市对（机制量化参考 arXiv:2603.19380 的 4.94pp/23.3% 量级）。
5. **成本参数（待补）**：Binance USDT-M taker 费率 + 滑点模型 + 开平仓 funding 结算归属（官方费率页本次不可达，03 前需补一手来源）；成本-边界框架参考 arXiv:2212.06888。
6. **制度分解呈现**：回测结果按 2020-21 牛 / 2022 熊 / 2023 震荡 / 24-25 牛分段报告，"整体 Sharpe"不作为首要指标（文献依据 arXiv:2112.15321 / 2307.06400）。
7. **信号定义 PIT**：保留"当时时点的 funding rate 定义"（结算间隔/cap/结算时点），防止定义回溯。
8. **02.5 交叉验证待补清单**：(a) Bailey 2013（正确 arXiv ID）/ Bailey 2014 DSR / Harvey-Liu-Zhu 2016 JF / White 2000 / Hamilton 1989 / Jegadeesh-Titman 1993 / Lo-Mamaysky-Wang 2000 / Koijen et al. 2018 JFE / McLean-Pontiff 2016 / Hou-Xue-Zhang 2015 / López de Prado 2018 书的 URL；(b) Chainalysis《State of Perpetual Futures》报告 URL（chainalysis.com/reports 可达）；(c) crypto 端幸存者/清算级联量化文献；(d) Binance USDT-M 当前费率（官方页）。

**（本文件只提供建议输入 —— 基准集选型、PIT 实现方案、成本参数决策属 03/04 阶段）**
