# 资金费率/OI 发布时点与更新频率

<!-- # origin: ai -->
<!-- 调研时间: 2026-10-16 16:06–17:10 UTC（实际观察时间均在此窗口内） -->
<!-- 调研环境: DSH 沙箱（web_search 不可用；交易所 API 直连全部被网络阻断；官方文档经 bybit-exchange.github.io / docs.coinglass.com / PyPI 官方 SDK 获取） -->

## 0. 工具与来源可用性记录（失败如实记录）

| 渠道 | 结果 | 说明 |
|---|---|---|
| web_search | **不可用** | 报错 `DeepSeek search has no API key for "DEEPSEEK_API_KEY"`，无法执行任何搜索 |
| web_fetch ×4（预算已用尽） | 全部失败 | developers.binance.com ×2 → `URL hostname "developers.binance.com" resolves to a non-public IP address`（本环境不可达）；bybit-exchange.github.io/docs/v5/market/funding → HTTP 404（slug 错误，正确为 history-fund-rate / open-interest）；docs.cooldata.io → DNS ENOTFOUND（域名错误，实为 docs.coinglass.com） |
| 交易所 API 直连（bash curl） | **全部不可达** | fapi.binance.com（DNS 正常但 TCP 连接超时，IP 66.220.147.11）、api.binance.com、api.bybit.com、www.okx.com 均 000/超时 → **无法实证抓取响应体验证时间戳字段**，只能依赖官方文档与官方 SDK |
| archive.org（Wayback） | 不可达 | 000，无法回捞旧版 Binance 文档 |
| binance-docs.github.io/apidocs/futures/en/ | 入口已失效 | 页面 200 但 meta-refresh 跳转 developers.binance.com（不可达）→ 旧版 Binance 期货文档已下架 |
| OKX 官方文档站 www.okx.com/docs-v5 | 不可达 | → OKX 相关主张仅有官方 SDK 一个来源（见 §3 说明） |
| Bybit 文档站 sitemap | 404 | /sitemap.xml 与 /sitemap-0.xml 均 404；正确页面 slug 经 pybit SDK docstring 中的官方文档链接定位后抓取成功 |
| Coinglass 定价页 www.coinglass.com/pricing | 200 但**JS 渲染（Next.js）** | 静态 HTML 无价格数字 → API 付费档位**未解决** |

**替代证据链（可用）**: pypi.org（官方 SDK wheel + 上传时间）、github.com（官方仓库）、bybit-exchange.github.io（官方文档，实时抓取）、docs.coinglass.com（官方文档，实时抓取，任意页面 URL 加 `.md` 可得 markdown 版，含 `updatedAt` front-matter）。

---

## 1. 资金费率：结算周期与 t 时刻可用性

### 主张 1.1 标准结算周期 8 小时（00:00/08:00/16:00 UTC），按交易对可不同（存在 4h/1h 调整）

- **来源 A**: Bybit V5 官方文档「Query historical funding rate」, https://bybit-exchange.github.io/docs/v5/market/history-fund-rate
  - 发布/更新时间: 页面未标注（GitHub Pages，随官方仓库更新）；实际观察时间 2026-10-16 16:51 UTC
  - 具体观察（原文）: "Each symbol has a different funding interval. For example, if the interval is 8 hours and the current time is UTC 12, then it returns the last funding rate, which settled at UTC 8. To query the funding rate interval, please refer to the instruments-info endpoint." → 官方明示：周期按 symbol 不同、以 instruments-info 为准；示例给出 8h 周期下"当前 UTC 12 → 最新已结算的是 UTC 8 的那笔"
- **来源 B**: Binance 官方 Python SDK `binance-futures-connector` 4.2.0（PyPI 上传 2026-04-30T06:14:08，https://pypi.org/project/binance-futures-connector/4.2.0/ ；仓库 https://github.com/binance/binance-futures-connector-python ），`binance/um_futures/market.py` 中 `GET /fapi/v1/fundingInfo` 的 docstring
  - 发布/更新时间: 2026-04-30（wheel）；实际观察时间 2026-10-16 16:12 UTC（本地解包 /tmp/sdk/）
  - 具体观察（原文）: "queries funding rate info for symbols whose FundingRateCap/FundingRateFloor/fundingIntervalHours have been adjusted" → 官方确认**存在** fundingIntervalHours 被调整过的交易对（即 8h 不是全局唯一周期）
- **具体观察（周期=8h 的默认值）**: Binance 00/08/16 UTC 三档为 8h 周期的直接推论 + 高置信领域知识（Bybit 文档示例落在 08:00 UTC 边界，与之互洽）；**4h/1h 具体交易对清单 = 未核验领域知识（待补URL）**（Binance 官方文档 developers.binance.com 本环境不可达）
- **不确定性**: 两家文档互证了"周期按 symbol 可变 + 8h 示例"，但"默认即 8h、多数主流合约 00/08/16 UTC"这一默认值只有 Bybit 单侧示例支撑，Binance 侧文档不可达 → 标**部分未核验**

### 主张 1.2 t 时刻决策可用的是"最近一笔**已结算**费率"，历史 API 不返回未结算值

- **来源 A**: Bybit 官方文档（同 1.1-A，https://bybit-exchange.github.io/docs/v5/market/history-fund-rate ，观察 2026-10-16 16:51 UTC）
  - 具体观察（原文）: "if the interval is 8 hours and the current time is UTC 12, then it returns the last funding rate, which settled at UTC 8" → **t 时刻（如 12:00 UTC）能取到的最新记录是 t−4h 结算的那笔**；12:00–16:00 这期的费率在 16:00 结算前不可用。这是 point-in-time 语义的官方书面确认，无 look-ahead。
  - 分页规则（原文）: "Passing only startTime returns an error. Passing only endTime returns 200 records up till endTime. Passing neither returns 200 records up till the current time." + limit [1,200] 默认 200 → 可用 startTime/endTime 窗口向前翻页，理论可回溯至 symbol 上线（**回溯深度未在页面明示，未解决**）
- **来源 B**: Bybit 官方 SDK `pybit` 5.17.0（PyPI 上传 2026-07-14T02:31:42，https://pypi.org/project/pybit/5.17.0/ ），`pybit/_v5_market.py` `get_funding_rate_history` docstring
  - 具体观察: 与文档页**逐字一致**的 8h/UTC 12→settled at UTC 8 示例（独立分发渠道，同一发布方）
- **来源 C（Binance 侧）**: SDK 4.2.0 `GET /fapi/v1/fundingRate` docstring: "Funding Rate History", limit 默认 500 最大 1000, startTime/endTime, 升序；`GET /fapi/v1/premiumIndex` "Mark Price and Funding Rate"。docstring 中引用的官方文档 URL 为 https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History 与 .../Mark-Price （**本环境不可达，未能直接核验**）
  - Binance 历史接口是否同样"只返回已结算"、响应字段（fundingTime 等）语义 = **未核验领域知识（待补URL）**，但"只返回已结算历史"为三所通用惯例，置信度高
- **look-ahead 检查结论**: t 时刻用 `fundingRateTimestamp ≤ t` 的已结算记录 = 安全；t 时刻"当期预测费率"（由当前 mark price 实时推算，Binance premiumIndex/markPrice 流提供）不是未来信息（t 时刻可算出），但**最终结算值在边界时刻才确定**，信号须区分 settled vs predicted（字段区分语义 = 未核验领域知识（待补URL））
- **不确定性**: Bybit 侧有官方原文双渠道互证（文档+SDK）；Binance/OKX 侧只有 SDK docstring（单一来源，见 §3）

### 主张 1.3 历史费率记录的 timestamp 语义 = **结算时刻**（非观测时刻）

- **来源 A**: Bybit 官方文档（同 1.1-A）响应示例行: `fundingRate: "0.0001", fundingRateTimestamp: "1672041600000"`
  - 具体观察: 1672041600000 ms = **2022-12-26T08:00:00Z**，精确落在 08:00 UTC 结算边界 → 该字段记录的是结算时间。故 PIT 规则: `fundingRateTimestamp ≤ t` 的记录在 t 时刻可用
- **来源 B**: 同 1.1-B pybit SDK（示例文本一致）
- **不确定性**: 仅 Bybit 有实证样本；Binance/OKX 的对应字段名与语义 = 未核验领域知识（待补URL）

---

## 2. OI（持仓量）：更新频率与时间戳语义

### 主张 2.1 OI 为交易所实时汇总值；快照接口给"当前值"，历史接口给 bar（最小粒度普遍 5min）

- **来源 A（快照）**:
  - Binance SDK 4.2.0 `GET /fapi/v1/openInterest`: "Get present open interest of a specific symbol"（实时快照）
  - OKX 官方 SDK `python-okx` 0.4.4（PyPI 上传 2026-09-07T04:16:33，https://pypi.org/project/python-okx/0.4.4/ ），`okx/consts.py`: `/api/v5/public/open-interest`（实时快照，instType/instId 参数）
- **来源 B（历史 bar，粒度）**:
  - Binance SDK 4.2.0 `GET /futures/data/openInterestHist`: period ∈ {5m,15m,30m,1h,2h,4h,6h,12h,1d}，**最小 5min**；limit 默认 30 最大 500
  - Bybit 官方文档「Open Interest History」, https://bybit-exchange.github.io/docs/v5/market/open-interest （观察 2026-10-16 16:51 UTC）: intervalTime ∈ {5min,15min,30min,1h,4h,1d}，**最小 5min**；startTime/endTime（ms）；limit [1,200] 默认 50；cursor 翻页；响应每 bar 字段: `openInterest`（双边合计）、`singleOpenInterest`（单边）、`timestamp`（ms）
  - OKX SDK `python-okx` `TradingData.get_open_interest_history` → `/api/v5/rubik/stat/contracts/open-interest-history`: period "Bar size, the default is 5m, e.g. [5m/15m/30m/1H/2H/4H]"（**最小 5min**）；begin/end（ms 时间戳翻页，begin=较新方向、end=较旧方向）；limit 最大 100 默认 100；速率限制 "10 requests per 2 seconds"（IP+Instrument ID）
- **具体观察（更新频率）**: 快照级为实时（交易所内部计算频率未公开；秒级更新 = 未核验领域知识（待补URL））；历史 bar 最小粒度三家一致为 **5min** → 5min 是免费 OI 历史的最小可用分辨率
- **不确定性**: 三家均为官方 SDK/官方文档（Binance+OKX 仅 SDK 单源，Bybit 有文档站直接抓取）；"交易所内部 OI 更新频率"无任何官方公开 → 未解决

### 主张 2.2 Binance 免费 OI 历史**只有 30 天回看窗口**（5 年回测不可行）；Bybit 可回溯至 symbol 上线

- **来源 A**: Binance SDK 4.2.0 `GET /futures/data/openInterestHist` docstring Notes 原文: **"Only the data of the latest 30 days is available."**
  - 发布/更新时间: wheel 2026-04-30；观察 2026-10-16 16:12 UTC
  - 具体观察: 免费 REST 的 OI 历史上限 = **最近 30 天**。→ 对本项目"≥5年含牛熊"的硬约束，Binance OI 历史**直接出局**（除非自本项目起向前滚动积累，或改走付费/第三方）
  - 来源独立性说明: 该主张仅有 1 个直接来源（官方 SDK docstring，官方文档页不可达）；**为什么可接受**: SDK 为 Binance 官方发布方、docstring 逐字镜像官方文档 Notes，且与 30 天窗口这一限制性条款的低修改概率一致；仍标**单源**
- **来源 B**: Bybit 官方文档（同 2.1-B）原文: **"The upper limit time you can query is the launch time of the symbol."**
  - 具体观察: OI 历史可回溯至**交易对上线日**（BTCUSDT 永续 2019-09 上线 → 可覆盖 5 年以上）→ Bybit 是唯一经文档书面确认的免费 5 年 OI 来源
  - **官方 PIT 警示（原文）**: "During periods of extreme market volatility, this interface may experience increased latency or temporary delays in data delivery." → 官方承认极端行情下数据投递可能延迟 → timestamp 是 bar 时间，**不保证该时刻即时可用**，回测须留延迟缓冲
- **来源 C（对照）**: Coinglass 官方文档（见 §4）: OI/Funding 历史单次请求窗口 **≤90 天**（可分页拼接），且为**付费 plan 门控**
- **不确定性**: Bybit 回测深度到上线日有官方原文；Binance 30 天为单源 SDK；"BTCUSDT 2019-09 上线"为领域知识（未核验，待补URL）

### 主张 2.3 bar 时间戳语义 = bar **开始**时间；PIT 规则: t 时刻最新可用 bar 满足 bar_start + bar_duration(+发布延迟) ≤ t

- **来源 A**: Bybit 官方文档（同 2.1-B）响应字段 `timestamp`（ms）逐 bar 返回（无 "close time" 字段）
- **来源 B**: OHLC/bar 惯例（timestamp=bar 起点，bar 在其 duration 结束后才定型）= **未核验领域知识（待补URL）**——三家文档均未明文写"timestamp 是 bar 开始时间"
- **具体观察（推导）**: 5min bar 的数值在 bar 结束时刻才完整 → 保守 PIT 规则: t 时刻只允许使用 `bar_start + 5min ≤ t` 的 bar（若按 Bybit 延迟警示再加缓冲，可用"上一根 bar"策略）。**直接消费"最新快照 OI"等于消费了 t−(秒级~分钟级) 的近似值，回测须显式建模取数时刻**
- **不确定性**: bar 起点语义与发布延迟量级（秒~分钟）均无官方数字 → 标未解决，建议阶段03用可运行环境实测响应头/响应时间

---

## 3. 主要数据源时间戳语义对照（Binance / Bybit / OKX / Coinglass）

| 源 | 接口（本调研确认存在） | 时间戳字段/单位 | 语义 | 最小粒度 | 历史深度 | 免费性 | 本环境来源 |
|---|---|---|---|---|---|---|---|
| Binance | `GET /fapi/v1/fundingRate` | fundingTime（字段名未核验）/ms | 已结算（惯例，未直接核验） | 事件序列 | 深度未核验（limit≤1000/次，startTime 翻页） | 免费 | 官方 SDK docstring（单源） |
| Binance | `GET /futures/data/openInterestHist` | timestamp /ms | bar 开始（惯例，未直接核验） | 5m | **仅最近 30 天**（SDK 原文） | 免费 | 官方 SDK docstring（单源） |
| Binance | `GET /fapi/v1/openInterest` | —（请求时快照） | 当前值 | 快照 | 无历史 | 免费 | 官方 SDK docstring |
| Bybit | `GET /v5/market/funding/history` | fundingRateTimestamp /ms | **结算时刻**（官方示例 08:00:00Z 实证） | 事件序列 | 分页至更深（深度未明示） | 免费 | 官方文档站+SDK（双渠道） |
| Bybit | `GET /v5/market/openInterest/history` | timestamp /ms | bar 开始（惯例） | 5min | **至 symbol 上线日**（官方原文） | 免费 | 官方文档站+SDK |
| OKX | `GET /api/v5/public/funding-rate-history` | 字段未核验 /ms | 已结算（惯例） | 事件序列 | 深度未核验（after/before 翻页） | 免费 | 官方 SDK（单源，文档站不可达） |
| OKX | `GET /api/v5/rubik/stat/contracts/open-interest-history` | ts /ms | bar 开始（惯例） | 5m | **深度未核验**（文档站不可达） | 免费 | 官方 SDK（单源） |
| Coinglass | `GET /open/v1/funding_rate`（V3） | timestamp /s（startTs/endTs 为秒） | OHLC bar（结算事件计数在 volume） | 未标注（无 period 参数）= 未解决 | **单请求 ≤90 天**，可分页 | **付费 plan 门控**（定价未解决） | 官方文档站（.md 直抓） |
| Coinglass | `GET /open/v1/open_interest`（V3） | timestamp /s | OHLC bar | 未标注 = 未解决 | 单请求 ≤90 天 | 付费 plan 门控 | 官方文档站 |
| Coinglass | `GET /open/v1/exchange/open_interest_history`（V3） | timestamp /s | 逐交易所 OI 点值 [timestamp,price,volume,oi,oiUsdt] | 未标注 = 未解决 | 单请求 ≤90 天 | 付费 plan 门控 | 官方文档站 |

**单位陷阱**: Binance/Bybit/OKX 用**毫秒**，Coinglass 用**秒**——归一到 UTC 毫秒是阶段03 数据管道的必做项。
**OKX 单源说明**: OKX 文档站（www.okx.com/docs-v5）本环境 TCP 不可达，OKX 全部主张来自官方 SDK（python-okx 0.4.4，2026-09-07 上传）docstring 与端点常量——SDK 为官方发布物，置信度中高，但按"关键主张≥2 独立来源"标准，OKX 各条均**仅 1 源**，已在表中如实标注。

**Coinglass 补充观察**（docs.coinglass.com，观察 2026-10-16 17:05 UTC；页面 front-matter updatedAt: oi-ohlc-histroy=2025-12-31、fr-ohlc-histroy=2026-09-28、exchange-open-interest-history=2025-04-21、getting-started=2026-03-30 → 均**超过 7 天**，接口可用性类事实按规则标"未解决/待复核"）:
- 每页均有 "This endpoint is available on the following API plans: [pricing 链接]" → OI/Funding 历史接口**不是全免费**；www.coinglass.com/pricing 为 JS 渲染，档位与价格**未解决**
- getting-started 页（updatedAt 2026-03-30）: "Some endpoints will require an API Key"; V4 base = https://open-api-v4.coinglass.com（本次核验的 OI/Funding 端点属 V3 `open-api-v3.coinglass.com/open/v1`）
- 对本项目"免费数据"硬约束: Coinglass API **大概率不可用**（付费门控已确认，具体档位未核验）→ 降级为备选，不作为 S1 默认数据源

---

## 4. Look-ahead bias 检查汇总（t 时刻信号可用性判定）

1. **已结算资金费率（fundingRateTimestamp ≤ t）: 可用，无泄露**（Bybit 官方原文确认语义，双渠道）。
2. **当期未结算费率的"实时预测值": t 时刻可算出（基于当前 mark price），不算泄露，但必须与已结算值区分字段**；其最终结算值在 8h 边界才确定（settled vs predicted 字段语义 = 未核验领域知识（待补URL））。
3. **OI bar: t 时刻可用集 = {bar : bar_start + bar_duration ≤ t}**，且按 Bybit 官方延迟警示，极端行情下应再加保守缓冲（如只用到上一根已确认 bar）。bar 起点时间戳语义 = 领域知识（待补URL）。
4. **OI 快照: 是"请求时刻"的近似值**，回测中消费快照 = 隐含秒级~分钟级数据时滞，须显式建模。
5. **Binance OI 历史 30 天窗口 = 结构性约束**（非时滞问题，是深度问题）：5 年 OI 回测免费可行源仅 **Bybit**（至上线日，官方原文）；OKX 深度未核验；Coinglass 付费。
6. **所有交易所官方均未按"发布时刻"承诺 SLA**：Bybit 有明确的极端行情延迟警示原文；Binance/OKX 未见类似条款（文档不可达，无法确认有无）→ PIT 假设"timestamp = 可用时刻"是**近似**，回测框架应内置"可用时刻 = 标称时间 + 延迟缓冲"参数化设计。

---

## 5. 未解决空缺（unresolved）

1. **Binance 官方文档全环境不可达**（developers.binance.com 解析到非公网 IP；旧 binance-docs.github.io 已重定向）→ `/fapi/v1/fundingRate`、`/fapi/v1/premiumIndex` 响应字段语义（fundingTime / lastFundingRate / nextFundingTime）、funding 历史深度、OI bar timestamp 语义，均为单源 SDK docstring 或领域知识。
2. **OKX OI 历史（rubik 接口）历史深度**未核验（文档站不可达）。
3. **Coinglass**: OI/Funding OHLC bar 粒度未标注；API 定价档位未提取（pricing 页 JS 渲染）；各 endpoint 对应哪个 plan 未确认。
4. **4h/1h fundingInterval 的具体交易对清单**未核验（仅确认"存在调整"这一事实）。
5. **所有交易所 API 在本沙箱被网络阻断** → 无一次真实 API 响应实证（无响应体字段、无响应头时间戳）；本文件全部"实证"级别证据 = 官方文档原文 + 官方 SDK 原文。
6. **web_search 不可用**（缺 DEEPSEEK_API_KEY）→ 无法做搜索式交叉验证，交叉验证仅能靠"文档 vs 官方 SDK"双渠道。
7. **Bybit funding 历史可回溯深度**（是否真到 symbol 上线）文档未明示，仅从分页规则推断可行。

---

## 对阶段03的建议输入

**暂定结论：S1 默认场景下 t 时刻可用信号集合（point-in-time 合规）**

| 信号 | t 时刻可用形式 | 免费源 | 历史深度 | 备注 |
|---|---|---|---|---|
| 资金费率 | 最近一笔已结算费率（fundingRateTimestamp ≤ t） | Bybit（语义文档最完整）；Binance/OKX 接口存在、字段语义待补核验 | 未明示（分页推断可深） | 8h 结算周期按 symbol 可变，须逐 symbol 从 instruments-info / exchangeInfo 取 interval |
| 资金费率（实时预测） | 当期 predicted 值（基于 mark price） | 同上各所快照接口 | — | 必须与 settled 值分字段，不可混用 |
| OI（5min bar） | bar_start+5min ≤ t 的 bar（建议加延迟缓冲） | **Bybit（唯一免费+深度确认）** | 至 symbol 上线日（官方原文） | Binance 仅 30 天；OKX 深度未核验 |
| OI（快照） | 请求时刻近似值 | 三家均可 | 无 | 回测须显式建模取数时滞 |

**仍未解决的空缺（阶段03 需在可联网/可直连 API 的环境补做）**:
1. Binance 文档直连核验（fundingRate/premiumIndex 响应字段、funding 历史深度、OI bar timestamp 语义）；
2. OKX rubik OI 历史深度核验（docs-v5 可达环境）；
3. 三家 API 实测：抓真实响应体确认字段名/单位 + 观测"标称时间戳 vs 实际可得时间"的延迟分布（支撑回测延迟缓冲参数）；
4. Coinglass 定价/plan 门控核验（浏览器渲染 pricing 页）——决定是否作为付费备选；
5. 4h/1h funding interval 交易对清单（各所 instruments 接口实测）。

**数据管道硬性要求（从本调研直接导出）**: 时间戳统一归一为 UTC 毫秒（Coinglass 为秒）；funding 与 OI 的"可用时刻"参数化（标称时间 + 延迟缓冲）；funding 按 symbol 读取 interval，不得假设全局 8h。

（本节为暂定输入，非最终推荐。）
