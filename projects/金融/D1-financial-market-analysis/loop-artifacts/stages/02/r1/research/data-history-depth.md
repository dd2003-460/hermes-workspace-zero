# 数据历史深度与退市标的覆盖（幸存者偏差规避）

**disposition**: research_required（confidence 0.55）
**观察时间**: 2026-10-17（子代理 a829e197 调研；其沙箱 web_search 不可用，全程 web_fetch 直取官方文档）

## 关键主张与来源

### 加密永续（S1 主场景）— 免费源可支撑 5 年 OOS 且可规避幸存者偏差（首选）

1. **Coinglass API v4 提供 Funding Rate / Price / OI 历史及显式 Delisted Pairs 接口**
   - 来源: Coinglass API 文档（getting started / endpoints）
   - URL: https://docs.coinglass.com/reference/getting-started-with-your-api
   - 观察: 确认存在 Funding Rate History (OHLC)、Price History (OHLC)、Open Interest History (OHLC)、Delisted Pairs、Long-Short Ratio、Liquidation History 端点
   - 不确定性: 文档未明确可回看年限；**2026-10-17 主代理补充: Coinglass API 无免费档（HOBBYIST $29/mo 起，定价页实证）→ 免费场景下可回看年限不适用**
2. **Binance 官方免费公共数据门户存在**
   - 来源: data.binance.vision（交易所官方，免费）
   - URL: https://data.binance.vision/
   - 观察: 页面确认可访问；交易所原始逐日文件天然含历史上市/退市对
   - 不确定性: ~~目录结构/起始日期未抓到~~ **已实证（2026-10-17 主代理 HTTP 直探，见下方复核节）: 免费批量文件（逐日K线+monthly fundingRate）最早 2020-01**
3. **Binance 官方 GitHub 公开数据仓库存在**
   - 来源: github.com/binance/binance-public-data
   - URL: https://github.com/binance/binance-public-data
   - 观察: 仓库可访问；README 正文被截断未抓
   - 不确定性: 内容深度未验证
4. **幸存者偏差判断**: 交易所原始逐日文件（Binance public data）天然含历史在上市/退市对；聚合商仅返回当前上市列表的接口有幸存者偏差，Coinglass 以 Delisted Pairs 接口缓解。

### 美股（S2）— 免费档日线不足

5. **Alpha Vantage 日线覆盖 25+ 年（自 2000-01），但免费档仅最近 100 根**
   - 来源: Alpha Vantage 官方文档
   - URL: https://www.alphavantage.co/documentation/
   - 观察: TIME_SERIES_DAILY 免费档仅 outputsize=compact（最近100根）；outputsize=full 需 premium → 5 年日线（约1260根）免费档不可行
   - 不确定性: Listing/Delisting Status 工具接口存在（TOC 确认），免费档可用性未验证
6. **Stooq 待验证**: https://stooq.com/db/ 本次访问 HTTP 403，历史深度与退市覆盖未验证（未解决）。
7. **Yahoo Finance**: 本次未验证（先验含部分已退市代码历史，需实测，不作为证据）。

### A股（S3）— 免费退市覆盖未证实

8. **Baostock 官网为 JS 壳页**: www.baostock.com 可访问（HTTP 200）但无有效文本；历史起点（先验1990）与退市股覆盖未获证据（未解决）。
9. **AkShare/Tushare**: 未验证（未解决）。备选：CSMAR/Wind（付费）或交易所原始逐日文件。

## 2026-10-17 主代理一手复核（HTTP 状态码直探 data.binance.vision）

- 探测方法: `curl -r 0-0` 取 HTTP 状态（206=文件存在，404=不存在），对照已知有效 spot 文件（BTCUSDT-1h-2017-08.zip → 206）验证方法有效。
- **futures/um/daily/klines/BTCUSDT/1h**: 2019-09/10/11/12 全部 404；**2020-01-01 → 206**。官方免费逐日 K 线最早 = 2020-01-01。
- **futures/um/monthly/fundingRate/BTCUSDT**: 2019-08~2019-12 全部 404；**2020-01 → 206**。funding rate 免费批量文件最早 = 2020-01（funding rate 文件仅 monthly 粒度，无 daily）。
- Binance 公开 API（fapi.binance.com/fapi/v1/fundingRate）在本环境不可达（connection reset，疑似沙箱网络策略/地域限制）→ 2019 数据只能经 API 获取，批量免费不可行。
- **修正结论**: 免费批量数据窗口 = **2020-01 起**（非先前假设的 2019-09）。2019-09~12 段（含 2019-11 局部顶）不可免费批量获取。
- 不确定性: 未穷举其他路径命名（如 2019 数据以 archive 形式存放的可能性低但未 100% 排除）。

## 5年窗口影响（暂定）

| 资产类别 | 5年OOS可行性 |
|---|---|
| 加密 | 免费源直接支撑，可规避幸存者偏差（首选） |
| 美股 | AV 免费档不足（仅100根），需 Stooq 等免费全历史源验证 |
| A股 | 免费退市覆盖未证实，需补证据或改交易所原始文件/付费源 |

## 待补证据清单

- ~~Binance 永续/funding 确切起始日期~~ **已实证: 免费批量文件 2020-01 起（2026-10-17 主代理 HTTP 直探；API 在本环境不可达）**
- Binance openInterestHist 保留期（API 本环境不可达，未能一手验证；先验仅近期）
- Bybit/OKX 数据起点
- Stooq 历史深度与退市覆盖（本次 403）
- Baostock/AkShare 历史起点与退市股覆盖
- Alpha Vantage Listing/Delisting 接口免费档可用性

## 对阶段03的建议输入

- 主数据源定为 **Binance 官方逐日文件（data.binance.vision）+ Coinglass**（免费、含退市对、point-in-time 友好）。
- 美股/A股分支（S2/S3）在免费退市覆盖落实前保持 S1 单场景推进。
- 不写最终推荐（属 03/04 阶段）。
