# 02.5 阶段字段快照

> 由 `ralph render` 自动从 `loop-artifacts/stages/02.5/r1/fields.json` 生成，请勿手改。

> 生成时间：2026-10-17 13:51

## 概览

- 字段总数：**8**
- 待办（pending / research_required）：**0**
- 分组：research_findings×7、cross_validation×1

## 字段明细

### research_findings

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| 研究未知因素：候选资产类别的公开行情数据历史深度与退市标的覆盖（幸存者偏差规避） | 验证并记录：候选资产类别的公开行情数据历史深度与退市标的覆盖（幸存者偏差规避） | confirmed | 0.82 | high | 是 |
| 研究未知因素：可得数据跨度能否覆盖牛市 | 验证并记录：可得数据跨度能否覆盖牛市 | confirmed | 0.80 | high | 是 |
| 研究未知因素：熊市与震荡市状态 | 验证并记录：熊市与震荡市状态 | confirmed | 0.85 | high | 是 |
| 研究未知因素：稳定性检验判据的时间窗口数量与通过阈值的具体定义 | 验证并记录：稳定性检验判据的时间窗口数量与通过阈值的具体定义 | confirmed | 0.85 | high | 是 |
| 研究未知因素：资金费率/OI 等替代交易信号的发布时刻与更新频率（交易时点是否已发布） | 验证并记录：资金费率/OI 等替代交易信号的发布时刻与更新频率（交易时点是否已发布） | confirmed | 0.80 | high | 是 |
| 研究未知因素：金融数据的修订与迟报机制（样本是否混入未来信息） | 验证并记录：金融数据的修订与迟报机制（样本是否混入未来信息） | confirmed | 0.85 | high | 是 |
| 研究未知因素：同类时间戳信号回测的公开研究基准与常见失败模式 | 验证并记录：同类时间戳信号回测的公开研究基准与常见失败模式 | confirmed | 0.72 | high | 是 |

### cross_validation

| 要素 (concept) | 属性 | 状态 | 置信度 | 影响 | 可逆 |
|---|---|---|---|---|---|
| cross_validation | 02.5交叉验证: 7个研究字段全部完成交叉验证(3字段直验HTTP re-probe + 4字段双LLM web-llm交叉核对) | confirmed | 0.85 | high | 是 |

## 证据与备注

### 研究未知因素：候选资产类别的公开行情数据历史深度与退市标的覆盖（幸存者偏差规避）

02.5直验C1-C6全confirm: Binance免费fundingRate月度2020-01起(2019各月404), OI文件不存在(404), 当月未归档; 修订风险低; 幸存者偏差规避附条件=Coinglass付费档(C6, $29/mo)。

证据：
- https://docs.coinglass.com/reference/getting-started-with-your-api
- https://www.alphavantage.co/documentation/
- https://data.binance.vision/
- https://github.com/binance/binance-public-data

### 研究未知因素：可得数据跨度能否覆盖牛市

02.5双LLM交叉确认核心窗口(2020-01→2025-01+覆盖2020-21牛/2022熊/2023震荡/24-25牛); 修正: 周期约5年非6年, "只有2020-21完整牛"软化为"2020-21为免费funding唯一完整大牛", A股2004/美股1993起点表述过度概括(Yahoo ^GSPC实际1927)。

证据：
- https://akshare.akfamily.xyz/data/index/index.html
- https://akshare.akfamily.xyz/data/dc/dc.html

### 研究未知因素：熊市与震荡市状态

02.5直验3/3 confirm: S1起点=2019-12-31(2018全段404), 2022熊+2023震荡覆盖成立; 矛盾1项(2022-10-13 Yahoo 3577.0 vs 新浪3669.91)判新浪正确采用3669.91; 0.85不给0.9因C1两源同Binance发布方。

证据：
- https://data.binance.vision/data/futures/um/daily/klines/BTCUSDT/1h/BTCUSDT-1h-2020-03-12.zip
- https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?interval=1d

### 研究未知因素：稳定性检验判据的时间窗口数量与通过阈值的具体定义

02.5双LLM交叉确认方法论核心(3-5个不重叠年度OOS窗口+expanding, 无普适阈值, PIT第一层前提, DSR/PBO无法防前视); "最严格显式判据集合"软化为候选集合(2026 arXiv:2608.27734编号LLM不可核验, 03直验)。

证据：
- https://arxiv.org/abs/1902.07855
- https://arxiv.org/abs/1905.05023
- https://arxiv.org/abs/1910.05555
- https://arxiv.org/abs/2008.09481
- https://arxiv.org/abs/2209.05559
- https://arxiv.org/abs/2407.17645
- https://arxiv.org/abs/2512.15720
- https://arxiv.org/abs/2601.08896

### 研究未知因素：资金费率/OI 等替代交易信号的发布时刻与更新频率（交易时点是否已发布）

02.5双LLM交叉确认PIT语义(t_available=max(bar_end,published,received)+δ, funding只用已结算值8h默认逐symbol可变, OI bar需bar_start+duration<=t+延迟缓冲, 单位逐字段归一); 驳回"仅Bybit可得5年免费OI"→OI三选项决策点路由03。

证据：
- https://bybit-exchange.github.io/docs/v5/market/history-fund-rate
- https://bybit-exchange.github.io/docs/v5/market/open-interest
- https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History
- https://github.com/binance/binance-futures-connector-python
- https://pypi.org/project/binance-futures-connector/4.2.0/
- https://pypi.org/project/pybit/5.17.0/
- https://pypi.org/project/python-okx/0.4.4/

### 研究未知因素：金融数据的修订与迟报机制（样本是否混入未来信息）

02.5直验C1/C2/C3/C6 confirm(官方updates/清单3文件全spot零futures→futures归档无记录修订, 风险中→低; 修订实为3例spot: 2022-04-21/2022-08-08/2022-10-04; 迟报=日线T+1/月线首周一); C4/C5 unresolved记录(Coinglass changelog无futures修订条目, CSI300"计划生效样本"PIT隐患)。

证据：
- https://github.com/binance/binance-public-data/
- https://github.com/binance/binance-spot-api-docs/blob/master/CHANGELOG.md
- https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md
- https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Open-Interest
- https://docs.coinglass.com/reference/change-log
- https://www.csindex.com.cn/#/indices/family/detail?indexCode=000300
- https://www.spglobal.com/spdji/en/indices/equity/sp-500/

### 研究未知因素：同类时间戳信号回测的公开研究基准与常见失败模式

02.5双LLM交叉确认研究缺口真实(截至2026-10公开检索未找到以funding rate作主择时信号的已发表回测), 表述修正"不存在"→"公开检索未找到"; "全部无arXiv全文"被驳; 2603.19380(4.94pp/23.3%)export.arxiv.org直验成立; 03须建可操作negative search协议。

证据：
- https://arxiv.org/abs/1912.03270
- https://arxiv.org/abs/2212.06888
- https://arxiv.org/abs/2506.08573
- https://arxiv.org/abs/2310.14973
- https://arxiv.org/abs/2501.09404
- https://arxiv.org/abs/1809.05961
- https://arxiv.org/abs/1904.00890
- https://arxiv.org/abs/2112.15321

### cross_validation

3字段(data-history/bear-range/data-revision)经02.5 direct HTTP re-probe逐claim confirm(6/6, 3/3, C1C2C3C6 confirm+C4C5 unresolved); 4字段(bull-coverage/stability-criteria/funding-oi-timing/public-benchmarks)经DeepSeek+ChatGPT双站LLM交叉核对, 判定均"部分正确", 核心结论全部confirm, 3处表述修正+1处子主张驳回已吸收。

证据：
- loop-artifacts/stages/02.5/r1/web-llm/cross-check-bull-coverage.json
- loop-artifacts/stages/02.5/r1/web-llm/cross-check-stability-criteria.json
- loop-artifacts/stages/02.5/r1/web-llm/cross-check-funding-oi-timing.json
- loop-artifacts/stages/02.5/r1/web-llm/cross-check-public-benchmarks.json
- loop-artifacts/stages/02.5/r1/research/cross-validation-data-history.json
- loop-artifacts/stages/02.5/r1/research/cross-validation-bear-range.json
- loop-artifacts/stages/02.5/r1/research/cross-validation-data-revision.json
