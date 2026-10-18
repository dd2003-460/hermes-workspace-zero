# 数据修订与迟报机制

**disposition**: confirmed（核心加密端修订机制已被一手官方来源证实；Coinglass 修订行为与财报重述 URL 未核验，留待 03 阶段补证）
**观察时间**: 2026-10-17 00:23–01:20 CST（子代理调研；web_search 不可用，全程 ego-browser 直读官方一手文档 + 1 次 web_fetch）

## 工具可用性（如实记录，失败≠证据）

- `web_search` 不可用：报错 `DeepSeek search has no API key for DEEPSEEK_API_KEY`。全程未依赖搜索引擎，改为直接抓取官方一手文档/仓库（更权威）。
- `web_fetch` 可用：4 次配额中用 1 次（`data.binance.vision` → HTTP 200，"Binance Data Collection" Market Data 落地页，列表截断）。其余抓取用 ego-browser（浏览器导航，非 web_fetch 工具）。
- DuckDuckGo html：bot CAPTCHA（"select all squares containing a duck"），未解决（浏览器持有提示，按 skill 不硬解）。
- Bing（本 zh locale）：结果多为泛化/无关（"data" 词典释义、交易所首页），技术查询效果差 → 弃用，改直读官方来源。
- Brave：可加载，本次未依赖。
- `fapi.binance.com` 公开 API 在本沙箱网络不可达（connection reset，疑似沙箱网络策略/地域限制）→ 无法对线上 API 实测"末根 K 线未定版"的实时行为，仅能从官方文档推断。

## 关键主张与来源

### 加密（S1 主场景）— 免费源 data.binance.vision

**1. data.binance.vision 归档文件会被历史修订（mutable archive，非严格 point-in-time）** ⚠️ 核心主张
- 来源标题: Binance 公开数据仓库 README（CHECKSUM 章节）
- URL: https://github.com/binance/binance-public-data/
- 发布/更新时间: "Updates" 修订清单最后一条为 2022-08-08；页面实际观察 2026-10-17
- 实际观察: 原文 "Archived files may be updated at a later date as a result of recently discovered issues. Below is an exhaustive list of updates performed to the archive, containing the file path for reference, and CHECKSUMs of the replaced file and the replacement file:"。列出 2 个已执行修订实例：
  - `2022-08-08 updates/2022-08-08_kline_updates.zip` — "Fixed inconsistent data"
  - `2022-04-21 updates/2022-04-21_aggregate_trade_updates.zip` — "Align to the Spot aggregate trade data change"
- 具体观察: 官方明确承认归档文件"日后可能被更新"，并提供"被替换文件 vs 替换文件"的 CHECKSUM 对照清单。→ **当前下载到的文件 ≠ 当时点看到的文件**（若修订发生在下载时点之前）。
- 不确定性: 修订清单只显式列出 2 例（均 2022 年）；"exhaustive list" 表述暗示有维护，但**未确认 2022-08 之后是否还有修订**，也未确认修订是否覆盖 futures（fundingRate/OI）文件还是仅 spot。

**2.（独立印证主张1，同一事件的另一角度）** 2022-04 Spot 聚合成交数据审计
- 来源标题: Binance Spot API 文档 CHANGELOG（2022-04-12 条目）
- URL: https://github.com/binance/binance-spot-api-docs/blob/master/CHANGELOG.md
- 发布/更新时间: 条目日期 2022-04-12；页面实际观察 2026-10-17
- 实际观察: 原文 "During a market data audit, we detected some issues with the Spot aggregate trade data. Missing aggregate trades were recovered. Duplicated records were marked invalid with the following values: p='0' // price, q='0' // qty, f=-1 // first_trade_id, l=-1 // last_trade_id"
- 独立性说明: 此为 **API 变更日志仓库**（与主张1 的"数据归档仓库"不同仓库/不同文档），从 API 侧记录同一 2022-04 事件；主张1 的 `2022-04-21_aggregate_trade_updates.zip` 文件名 "Align to the Spot aggregate trade data change" 与此审计直接对应。两来源独立但相互印证。
- 不确定性: CHANGELOG 只记录审计动作，未逐文件说明归档是否被同步替换（由主张1 的 zip 名称补全该链条）。

**3. 迟报 / T+1：日线文件次日发布，月线文件当月第一个周一发布**
- 来源标题: Binance 公开数据仓库 README
- URL: https://github.com/binance/binance-public-data/
- 发布/更新时间: 页面实际观察 2026-10-17
- 实际观察: 原文 "new `daily` data becoming available the next day and new `monthly` data at the first monday of the month"
- 具体观察: 第 X 天的日线文件在第 X+1 天才能下载 → 回测中"当日信号不可用当日日线文件，最早 X+1 日"；这是迟报（late reporting），需按 T+1 对齐时间戳。
- 不确定性: "the next day" 的具体时刻（UTC 几点）未明确 → 影响"当日能否用当日日线"的边界判断；futures 文件是否同样 T+1 未单独确认。

**4. 实时 K 线未定版（PIT 隐患，从 API 拉取时）**
- 来源标题: Binance Spot REST API 文档（Kline/Candlestick data）
- URL: https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md
- 发布/更新时间: master 分支，页面实际观察 2026-10-17
- 实际观察: "Klines are uniquely identified by their open time." + "If `startTime` and `endTime` are not sent, the most recent klines are returned."（Data Source: Database）。另有 `uiKlines` = "modified kline data, optimized for presentation of candlestick charts"（与原始 klines 不同，展示用）。
- 具体观察: 不传时间边界时返回"最近 klines" → 最后一根是**进行中（未定版）K 线**，其 OHLCV 会随交易推进而变化，收盘后才冻结。回测若误用未定版末根 = 引入当时未知的最终值（前视）。
- 不确定性: 此版本文档无显式"last kline not finalized"措辞，结论由"返回最近 klines + open-time 唯一标识"推出；`fapi.binance.com` 沙箱不可达，未能线上实测末根 K 线实时变化。

**5. 永续 funding/OI 端点语义（直接对应 S1 信号）**
- 来源标题: Binance USDⓈ-M Futures API 文档（Market Data REST）
- URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Open-Interest
- 发布/更新时间: 在线文档，页面实际观察 2026-10-17
- 实际观察（逐端点）:
  - `GET /fapi/v1/fundingRate`（Get Funding Rate History）: params symbol/startTime/endTime/limit(max 1000, default 100)；"If startTime and endTime are not sent, the most recent 200 records are returned"（升序）；响应含 fundingRate / fundingTime / markPrice。
  - `GET /fapi/v1/openInterest`（Get present open interest）: **仅当前 OI**（openInterest/symbol/time）。
  - `GET /futures/data/openInterestHist`（Open Interest Statistics）: period 枚举 5m/15m/30m/1h/2h/4h/6h/12h，limit max 500，startTime/endTime → 历史 OI。
  - `GET /futures/data/basis`: "**Only the data of the latest 30 days is available.**"
- 具体观察: funding/OI 历史可经 API 回看（PIT 可取），但"当前值"类端点（openInterest）本质是时点值；basis 仅近 30 天。
- 不确定性: 这些端点返回的历史数据是否被修订，API 文档未说明（需看 data.binance.vision 归档的 updates 清单是否覆盖 futures）；免费批量文件的起点见同目录 `data-history-depth.md`（主代理已实测免费批量窗口 = 2020-01 起）。

**6. Coinglass（独立第三方聚合商）**
- 来源标题: Coinglass API v4 文档 + Change Log
- URL: https://docs.coinglass.com/ ；https://docs.coinglass.com/reference/change-log
- 发布/更新时间: Change Log 最新条目 2026-04-13；页面实际观察 2026-10-17
- 实际观察:
  - API v4 提供丰富 OI/funding 历史端点：Open Interest History (OHLC)、Aggregated History (OHLC)、Aggregated Stablecoin/Coin Margin History、Funding Rate History (OHLC)、OI Weight History、Vol Weight History、Delisted Pairs、Long-Short Ratio、Liquidation History 等。
  - API 需 Authentication + Pricing（登录/付费）→ **非免费 API 访问**（图表页面可免费看，但结构化 API 需 key/计划）。
  - Change Log **只记录 "New endpoints"**（2025-12 ~ 2026-04 的条目），无任何数据修订/修正（revision/correction/backfill/reconcile）条目。
- 具体观察: Coinglass 作为跨所聚合商是可行的免费（图表）/付费（API）OI/funding 历史源；但其**历史数据是否被回溯修订，公开来源无记录**。
- 不确定性 / 未解决: Coinglass 历史 OI/funding 的修订行为**未解决**——公开文档不披露；其跨所聚合口径/延迟变更也无公开说明。作为免费约束下的数据源，API 档需付费，仅图表档免费但无程序化 PIT 取数。

## 横向对照（A股/美股）— 同类的未来信息泄露机制

**7. A股 指数成分调整（PIT 隐患）**
- 来源标题: 中证指数有限公司 — 沪深300指数（000300）
- URL: https://www.csindex.com.cn/#/indices/family/detail?indexCode=000300
- 发布/更新时间: 页面成分/权重"更新日期: 2026-10-16"；页面实际观察 2026-10-17
- 实际观察: 沪深300（000300），发布 2005-04-08，基日 2004-12-31；页面含 **"拟生效样本"**（生效前发布、尚未生效的拟调整成分）→ **用"当前成分"回看历史 = 幸存者/前视偏差**，必须用"生效日当时"的成分清单（PIT）。
- 独立性说明: 此为主张唯一已核验来源（1 个）。原因：A股指数调整规则以中证指数官网为权威一手来源，且本项属"横向对照"（非本项目核心加密主张）；半年度定期调整规则未在本次抓到具体规则页 URL。
- 未核验领域知识（待补URL）: 沪深300 半年度定期调整（惯例每年 6 月、12 月第二个周五的次日生效，含拟生效样本公示期）。
- 不确定性: 具体调整时点/规则未从本次抓取页面直接确认。

**8. 美股 指数成分调整 + 供应商提供回溯历史（PIT 友好对照）**
- 来源标题: S&P Dow Jones Indices — S&P 500®
- URL: https://www.spglobal.com/spdji/en/indices/equity/sp-500/
- 发布/更新时间: 页面 "As of Oct 15, 2026"；页面实际观察 2026-10-17
- 实际观察: S&P 500（500 家，覆盖 ~80% US 大盘）；原文 "The index Launch Date is Mar 04, 1957. All information for an index prior to its Launch Date is hypothetical back-tested, not actual performance, based on the index methodology in effect on the Launch Date." → 供应商**提供"按当时生效方法学"的回溯历史**（PIT 友好，是加密端缺失能力的对照样本）。
- 独立性说明: 唯一已核验来源（1 个）；对照项。
- 未核验领域知识（待补URL）: S&P 500 季度复核（惯例 Feb/May/Aug/Nov），成分变更提前公告 + 固定生效日。
- 不确定性: 页面以性能/事实表为主，季度调整的具体规则未在本次抓取中直接确认。

**9. 财报重述 + 数据供应商回溯修正（两市场共有机制，核心对照逻辑）**
- 标记: **未核验领域知识（待补URL）** —— 本次工具/预算内未抓到具体权威 URL，不编造。
- 具体机制（领域知识，逻辑清晰但需补一手来源）:
  - 财务重述（美股 restatement / A股 会计差错更正·追溯重述）+ 数据供应商回溯修正（如 CRSP/Compustat 对已发布财务数据的修订）→ 回测若用"重述后/回溯修正后"的财务数据 = **前视偏差**（用了当时尚未公开的信息）。
  - 幸存者偏差：回测样本只含当前仍上市/未退市标的 → 系统性高估收益（与加密端"仅当前在市交易对"同构）。
  - 这正是与加密端"归档文件被修订（主张1）"同类的**未来信息泄露**：都是"回测样本混入了事后才知道的值"。
- 不确定性: 缺一手权威 URL；机制描述为领域通识，置信度中等。

## 对阶段03的建议输入

**暂定结论 — 加密端（data.binance.vision 免费逐日文件）修订风险等级：中（MEDIUM）**
- 依据：官方一手来源（binance-public-data README "CHECKSUM" 章节）**明确承认**归档文件"日后可能被更新"，且已记录 2 例历史修订（2022-04-21 aggTrades、2022-08-08 klines）。故"严格 point-in-time 快照（当时看到的原始文件）"**不可从 data.binance.vision 免费直接获得**——下载到的是"截至下载时点"的文件。
- 但风险被**部分缓释**：(a) 修订是**罕见、离散、且有 CHECKSUM 清单可审计**的事件（非连续漂移），已记录的修订集中在 2022 年、且主要针对 spot aggTrades/klines；(b) 本项目 S1 信号是 funding rate/OI（futures），现有公开修订清单**未显式覆盖 futures 文件**（待补证）；(c) 若回测时间窗从 2020-01 起（见 data-history-depth.md 实测），则 2022 年的 spot 修订对 **futures funding/OI 样本的影响大概率可忽略**，但**未 100% 排除**。
- 关键待验证（决定风险是否可从"中"降到"低"）：futures（fundingRate/OI）归档文件是否在 2022-08 之后或针对 futures 发生过修订 —— 需抓 data.binance.vision 的完整 updates 清单或对照 CHECKSUM。

**仍未解决的空缺（03 阶段需补证）**
1. futures（fundingRate/OI）归档文件是否被修订 —— data.binance.vision updates 清单是否覆盖 futures（核心，直接决定 S1 样本纯度）。
2. 修订/迟报的"具体时刻（UTC）"与"下载时点 vs 文件内时间戳"的对齐规则（T+1 的确切边界）。
3. Coinglass 历史 OI/funding 的修订行为（公开无记录 → 未解决；且 API 档付费，免费约束下是否可用待定）。
4. 实时未定版末根 K 线的线上实测（`fapi.binance.com` 本沙箱不可达，仅文档推断）。
5. A股/美股 财报重述 + 供应商回溯修正的一手权威 URL（当前为未核验领域知识）。
6. A股半年度调整、美股季度复核的具体规则页 URL（当前为未核验领域知识）。

**（不写最终推荐 —— 数据源选型与 PIT 处理方案属 03/04 阶段决策）**
