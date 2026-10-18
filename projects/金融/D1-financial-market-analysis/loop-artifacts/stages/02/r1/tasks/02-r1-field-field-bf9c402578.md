# 02 阶段字段快照

> 由 `ralph render` 自动从 `loop-artifacts/stages/02/r1/tasks/02-r1-field-field-bf9c402578.json` 生成，请勿手改。

> 生成时间：2026-10-17 03:54

## 概览

- 字段总数：**7**
- 待办（pending / research_required）：**3**
- 分组：research_findings×7

## 字段明细

### research_findings

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| 研究未知因素：候选资产类别的公开行情数据历史深度与退市标的覆盖（幸存者偏差规避） | 验证并记录：候选资产类别的公开行情数据历史深度与退市标的覆盖（幸存者偏差规避） | research_required | 0.55 |  |  |
| 研究未知因素：可得数据跨度能否覆盖牛市 | 验证并记录：可得数据跨度能否覆盖牛市 | confirmed | 0.78 |  |  |
| 研究未知因素：熊市与震荡市状态 | 验证并记录：熊市与震荡市状态 | research_required | 0.70 |  |  |
| 研究未知因素：稳定性检验判据的时间窗口数量与通过阈值的具体定义 | 验证并记录：稳定性检验判据的时间窗口数量与通过阈值的具体定义 | confirmed | 0.80 |  |  |
| 研究未知因素：资金费率/OI 等替代交易信号的发布时刻与更新频率（交易时点是否已发布） | 验证并记录：资金费率/OI 等替代交易信号的发布时刻与更新频率（交易时点是否已发布） | confirmed | 0.75 |  |  |
| 研究未知因素：金融数据的修订与迟报机制（样本是否混入未来信息） | 验证并记录：金融数据的修订与迟报机制（样本是否混入未来信息） | research_required | 0.70 |  |  |
| 研究未知因素：同类时间戳信号回测的公开研究基准与常见失败模式 | 验证并记录：同类时间戳信号回测的公开研究基准与常见失败模式 | confirmed | 0.68 |  |  |

## 证据与备注

### 研究未知因素：候选资产类别的公开行情数据历史深度与退市标的覆盖（幸存者偏差规避）

加密永续：Coinglass API v4 文档确认提供 Funding Rate History(OHLC)、Price History(OHLC)、Open Interest 历史及显式 Delisted Pairs 接口，Binance 官方免费公共数据门户(data.binance.vision)与 GitHub 官方仓库均确认可访问，交易所原始逐日文件天然含历史退市对，5年OOS窗口(约2021-2026)加密端免费数据充足且可规避幸存者偏差；Binance 永续/funding 具体起始日期未从已抓页面确认(先验2019-08/09)。美股：Alpha Vantage 官方文档确认日线覆盖 25+ 年(自 2000-01)，但免费档仅 outputsize=compact(最近100根)、full 需付费，5年日线回测在免费档不可行；退市覆盖仅确认存在 Listing/Delisting Status 工具接口，其免费档可用性未验证；Stooq(stooq.com/db/)本次访问 403 未获数据。中国A股：Baostock 官网(www.baostock.com)可访问但为 JS 壳页，历史起点(先验1990)与退市股覆盖未获有效文本证据；AkShare/Tushare 本次未验证，免费退市覆盖暂不可确认。综合：5年窗口下加密类免费源可直接采用(首选且可规避幸存者偏差)；美股需另落实免费全历史源(Stooq 待验证)；A股需先落实免费退市覆盖，否则回退交易所原始文件或付费 CSMAR/Wind。待补证据：Binance 永续/funding 起始日期、Bybit/OKX 数据起点、Stooq 历史深度与退市覆盖、Baostock/AkShare 历史起点与退市股覆盖、AV Listing/Delisting 接口免费档可用性。
[observed_at补录: 子代理a829e197调研落盘时刻, 研究文件观察时间2026-10-17(CST)]

证据：
- https://docs.coinglass.com/reference/getting-started-with-your-api
- https://www.alphavantage.co/documentation/
- https://data.binance.vision/
- https://github.com/binance/binance-public-data

### 研究未知因素：可得数据跨度能否覆盖牛市

A股：AkShare日线从2004起(已验证)，完整覆盖2005-2007、2014-2015、2019-2021三轮牛市。美股：Yahoo/Stooq日线覆盖1993/1950起，完整覆盖2009-2020(11年)大牛市及2022末-2025。加密：Binance USDT-M期货2019.9上线，funding rate历史从此时起——可覆盖的完整牛市仅2019.9-2021.11一段(约26月)；2013/2016-2017牛市无funding rate。主场景S1(永续+funding rate)下，5年回测窗口=2019.9→2024.9+，含2019-2021牛+2022熊+2023-2024，满足A4牛熊震荡约束，但无法回测2019年前的完整牛市周期。

证据：
- https://akshare.akfamily.xyz/data/index/index.html
- https://akshare.akfamily.xyz/data/dc/dc.html

### 研究未知因素：熊市与震荡市状态

【子代理初判】本沙箱web工具受限（web_search无API key，Binance现货/fapi、Yahoo、Stooq被拦），原evidence_refs留空不编造。【2026-10-17主代理一手复核，本环境可达】①S1加密：data.binance.vision逐日文件节点直探 200-03-12崩盘底/2021-11-10牛顶/2022-01-10熊顶/2022-11-21熊底 均206（2018-12-15=404，早于免费起点2020-01，符合预期）→2020-2025窗口含2020-21牛+2022熊+2023震荡，A4满足（一手实证）。②S2美股：Yahoo chart API ^GSPC 节点直探 2002-10-09熊底(776.8)/2008-03-10(1273.4)/2022-10-13(3577.0) 均200→三大熊市日线实际存在（回溯起点不晚于2002-10，2000-01窗口失败待精确）。③S3 A股：Yahoo 000300.SS 返回400不支持；Baostock/AkShare免费退市覆盖未验证→仍research_required。关键判断不变：主场景2020-2025满足A4。

证据：
- https://data.binance.vision/data/futures/um/daily/klines/BTCUSDT/1h/BTCUSDT-1h-2020-03-12.zip
- https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?interval=1d

### 研究未知因素：稳定性检验判据的时间窗口数量与通过阈值的具体定义

16条arXiv来源HTTP 200实抓核验。窗口划分: 公开实践主流=3-5个互不重叠年度OOS窗口+expanding walk-forward(2605.04004三测试年/2608.24786四窗口+OOT/2602.00080 15年9splits); 月级窗口文献零出现; 理论守恒律α+β≤1+Λ(2609.29530)约束窗口数。通过阈值: 无普适标准; 最严格显式集合=每窗口OOS净收益T≥2.0+≥30笔+扣费净正+全测试年方向一致+permutation p<0.001(2605.04004五条原文); 替代=GT-Score四项复合; MDD跨窗口一致性无公开标准值(未解决,03设计)。验证栈: 结构性PIT是前提(2608.27734: Sharpe 35泄漏oracle完整通过DSR+PBO)→DSR/PBO/PSR按试验数deflate→标签重叠用CPCV/purged k-fold+embargo。校准警告: MinervaScore真实数据无前瞻力(ρ=0.013); 绝对收益门槛误杀真信号(2610.07701)。DSR/PBO原始定义(Bailey/López de Prado)本环境不可达,标未核验领域知识。详见research/stability-criteria.md(17.2KB)。

证据：
- https://arxiv.org/abs/1902.07855
- https://arxiv.org/abs/1905.05023
- https://arxiv.org/abs/1910.05555
- https://arxiv.org/abs/2008.09481
- https://arxiv.org/abs/2209.05559
- https://arxiv.org/abs/2407.17645
- https://arxiv.org/abs/2512.15720
- https://arxiv.org/abs/2601.08896
- https://arxiv.org/abs/2602.00080
- https://arxiv.org/abs/2604.15531
- https://arxiv.org/abs/2605.04004
- https://arxiv.org/abs/2605.17724
- https://arxiv.org/abs/2608.23808
- https://arxiv.org/abs/2608.24786
- https://arxiv.org/abs/2608.27734
- https://arxiv.org/abs/2609.29530
- https://arxiv.org/abs/2610.07701

### 研究未知因素：资金费率/OI 等替代交易信号的发布时刻与更新频率（交易时点是否已发布）

核心PIT语义经官方文档+官方SDK双渠道确认: t时刻可用集=已结算费率(fundingRateTimestamp≤t, Bybit官方原文latest=last settled)+bar_end≤t的OI bar(Bybit官方警示极端行情数据延迟, 回测须加缓冲)。Binance免费OI历史(openInterestHist)仅30天(binance-futures-connector 4.2.0原文Only the data of the latest 30 days is available.)→5年OI回测免费源仅Bybit(官方可查询上限为symbol上线时间); Coinglass OI/Funding历史单请求≤90天且付费。单位: Binance/Bybit/OKX毫秒, Coinglass秒→归一UTC ms为管道必做项。未解决: Binance文档字段语义/OKX OI深度/Coinglass定价档位/4h-1h funding对清单(本环境Binance/OKX文档站与交易所API不可达, 需可直连环境实测)。详见research/funding-rate-oi-timing.md。

证据：
- https://bybit-exchange.github.io/docs/v5/market/history-fund-rate
- https://bybit-exchange.github.io/docs/v5/market/open-interest
- https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History
- https://github.com/binance/binance-futures-connector-python
- https://pypi.org/project/binance-futures-connector/4.2.0/
- https://pypi.org/project/pybit/5.17.0/
- https://pypi.org/project/python-okx/0.4.4/

### 研究未知因素：金融数据的修订与迟报机制（样本是否混入未来信息）

加密端核心机制已一手官方源确认: data.binance.vision免费逐日文件官方承认可被历史修订(binance-public-data README CHECKSUM节: 2022-04-21 aggTrades、2022-08-08 klines两例已记录修订, 可审计)+日线T+1迟报+API末根K线未定版(收盘才冻结)。修订罕见/离散/可审计且已记录者均针对spot→S1 futures funding/OI样本影响大概率可忽略(未100%排除)→修订风险暂定=中。待补(决定中→低): futures归档文件是否在2022-08后或针对futures修订过; Coinglass修订行为(change log无修订条目); A股指数PIT(拟生效样本)与美股财报重述URL未核验。详见research/data-revision-latency.md。

证据：
- https://github.com/binance/binance-public-data/
- https://github.com/binance/binance-spot-api-docs/blob/master/CHANGELOG.md
- https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md
- https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Open-Interest
- https://docs.coinglass.com/reference/change-log
- https://www.csindex.com.cn/#/indices/family/detail?indexCode=000300
- https://www.spglobal.com/spdji/en/indices/equity/sp-500/

### 研究未知因素：同类时间戳信号回测的公开研究基准与常见失败模式

阶段 02 字段调研完成（观察日期 2026-10-17，web_search 不可用，主通道 = arXiv HTML 搜索 + curl 直取 abs 页）。Q1 公开基准与 Q2 失败模式均取得公开一手来源：前 13 个 evidence_refs 的 arXiv abs 页已直接抓取验证（全部 HTTP 200，5 要素完整记录）；后 6 个为列表级引用（ID/标题/日期来自 arXiv 官方搜索页，abs 未抓取）。完整记录: research/public-benchmarks.md。核心结论: (1) 'funding rate 作为市场状态/择时信号的已发表回测'未找到——本项目属填补缺口，对标基线需自建朴素基准（buy&hold/动量/趋势）+ 引用 arXiv:1912.03270（funding 可预测性实证）、arXiv:2212.06888（永续定价/基差理论）、arXiv:1904.00890（crypto 动量）等公开锚；(2) 失败模式均有已验证出处：look-ahead（arXiv:2607.04958、2609.20554）、幸存者偏差量化（arXiv:2603.19380：高估年化 4.94pp/23.3%）、过拟合/数据窥探（crypto 专属 arXiv:2209.05559）、制度切换（arXiv:2112.15321、2307.06400）、成本边界（arXiv:2212.06888 含成本定价边界框架）；(3) 待补证据（confidence 未更高的原因）: 期刊经典文献（Bailey 2013/2014、Harvey-Liu-Zhu 2016 JF、White 2000、Hamilton 1989、Jegadeesh-Titman 1993、Lo-Mamaysky-Wang 2000、Koijen et al. 2018 JFE、McLean-Pontiff 2016、Hou-Xue-Zhang 2015、López de Prado 2018 书）均为未核验领域知识——ssrn.com 沙箱不可达（curl 000）无法 URL 核验，待 02.5 交叉验证补；crypto 端幸存者/清算级联量化文献为公开缺口；Binance USDT-M 费率未核验（developers.binance.com 不可达）。另: 记忆中 Bailey 2013 的 arXiv ID 1308.3655 经验证是错误 ID（实为粒子物理论文），未引用。

证据：
- https://arxiv.org/abs/1912.03270
- https://arxiv.org/abs/2212.06888
- https://arxiv.org/abs/2506.08573
- https://arxiv.org/abs/2310.14973
- https://arxiv.org/abs/2501.09404
- https://arxiv.org/abs/1809.05961
- https://arxiv.org/abs/1904.00890
- https://arxiv.org/abs/2112.15321
- https://arxiv.org/abs/2307.06400
- https://arxiv.org/abs/2209.05559
- https://arxiv.org/abs/2609.20554
- https://arxiv.org/abs/2607.04958
- https://arxiv.org/abs/2603.19380
- https://arxiv.org/abs/2601.10812
- https://arxiv.org/abs/2605.05089
- https://arxiv.org/abs/2602.11708
- https://arxiv.org/abs/1905.05023
- https://arxiv.org/abs/2209.13623
- https://arxiv.org/abs/2309.06711
