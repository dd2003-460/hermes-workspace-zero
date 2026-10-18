# 交叉验证: 候选资产类别的公开行情数据历史深度与退市标的覆盖

# origin: ai

**field_task**: 02-r1-field-field-bf9c402578
**验证时间**: 2026-10-17 (UTC)
**验证方法**: web_fetch 直接访问官方页面/数据源，逐 claim 找 ≥2 独立来源

---

## C1: Binance 免费批量文件最早批次 = 2020-01（daily klines + monthly fundingRate 均自 2020-01 起）

| 来源 | URL | 关键摘录 | observed_at |
|------|-----|---------|-------------|
| data.binance.vision 直接探测 | https://data.binance.vision/data/futures/um/daily/klines/BTCUSDT/1h/ | BTCUSDT-1h-2020-01-01.zip → 206 (application/zip); BTCUSDT-1h-2019-12-31.zip → 206 (存在, 异常); 2019-09-01/12-01/12-15/12-30 → 404 NoSuchKey; 2018-01-01 → 404 | 2026-10-17T04:00:00Z |
| data.binance.vision fundingRate | https://data.binance.vision/data/futures/um/monthly/fundingRate/BTCUSDT/ | BTCUSDT-fundingRate-2020-01.zip → 206; BTCUSDT-fundingRate-2019-12.zip → 404 NoSuchKey | 2026-10-17T04:00:00Z |
| GitHub 官方仓库 README | https://raw.githubusercontent.com/binance/binance-public-data/master/README.md | Futures (UM) 数据类别: aggTrades, klines, trades。示例 URL: data/futures/um/monthly/klines/ADABKRW/1h/ADABKRW-1h-2020-08.zip。未显式声明最早日期。 | 2026-10-17T04:00:00Z |

**verdict: confirm**

**异常记录**: 2019-12-31 的 daily kline 文件存在（BTCUSDT-1h-2019-12-31.zip → 206），但 2019 年其他日期（09-01, 12-01, 12-15, 12-30）均为 404。研究文件中"2019-09/10/11/12 全部 404"的描述不完全准确（12-31 存在），但实际结论（连续数据自 2020-01 起）不受影响。可能原因：2019-12-31 是 Binance 启动 USDT 本位合约的最后一天（合约 2019-09 上线，但批量文件从 2020-01 才开始规范发布）。

---

## C2: Binance 免费批量文件无 OI（open interest）文件

| 来源 | URL | 关键摘录 | observed_at |
|------|-----|---------|-------------|
| data.binance.vision 直接探测 | https://data.binance.vision/data/futures/um/monthly/openInterestHist/BTCUSDT/ | 404 (路径不存在) | 2026-10-17T04:00:00Z |
| GitHub 官方仓库 README | https://raw.githubusercontent.com/binance/binance-public-data/master/README.md | UM Futures 数据类别仅列出: aggTrades, klines, trades。无任何 openInterest 类别。 | 2026-10-17T04:00:00Z |

**verdict: confirm**

两个来源一致：免费批量下载不含 OI 数据。OI 数据需通过 Binance API 实时获取或付费数据源。

---

## C3: Coinglass API 无免费档（HOBBYIST $29/month 起），且存在 Delisted Pairs 端点

| 来源 | URL | 关键摘录 | observed_at |
|------|-----|---------|-------------|
| Coinglass 官方 API 文档 | https://docs.coinglass.com/reference/getting-started-with-your-api | 端点列表包含: "Delisted Pairs" (GET /reference/delisted-exchange-and-pair); "Open Interest History"; "Funding Rate History"; "Price History (OHLC)" | 2026-10-17T04:00:00Z |
| Coinglass 官方定价页 | https://www.coinglass.com/pricing | 套餐: HOBBYIST $29/month, STARTUP $79/month, STANDARD $299/month, PROFESSIONAL $699/month。无免费档。 | 2026-10-17T04:00:00Z |

**verdict: confirm**

无免费档，最低 HOBBYIST $29/month。Delisted Pairs 端点存在，可用于获取已退市交易对列表以规避幸存者偏差。

---

## C4: Alpha Vantage 免费档 TIME_SERIES_DAILY 只返回最近 100 根（compact），5 年日线(~1260根)免费档不可行

| 来源 | URL | 关键摘录 | observed_at |
|------|-----|---------|-------------|
| Alpha Vantage 官方 API 文档 | https://www.alphavantage.co/documentation/ | "By default, outputsize=compact. compact returns only the latest 100 data points; full returns the full-length time series of 25+ years of historical data. The 'compact' outputsize is available to both free and premium API keys. The 'full' outputsize is available to premium keys. Please subscribe to any premium membership plan to unlock the outputsize=full capability." | 2026-10-17T04:00:00Z |
| Alpha Vantage Premium 页 | https://www.alphavantage.co/premium/ | "For use cases that exceed our standard API usage limit (25 API requests per day) or require certain premium API functions, we offer a premium plan to scale your use cases." | 2026-10-17T04:00:00Z |

**verdict: confirm**

官方文档明确：免费档仅 compact（100 bars），full 需 premium。5 年日线 ~1260 根，免费档不可行。

---

## C5: A股端 Baostock 起点(先验1990)与退市覆盖未证实；CSMAR/Wind 为付费 → A股端(S3)数据缺口

| 来源 | URL | 关键摘录 | observed_at |
|------|-----|---------|-------------|
| Baostock 官网 | https://www.baostock.com | 页面仅返回 "www.baostock.com ×"（JavaScript 渲染壳页面），无服务端内容可供验证数据起点或退市覆盖声明 | 2026-10-17T04:00:00Z |
| CSMAR 官网 | https://www.csmar.com | 深圳希施玛数据科技有限公司。产品: CSMAR中国经济金融研究数据库、CSMAR数据超市 (data.csmar.com)。客户: 1500+ 国内外高校及研究机构, 500+ 国内外金融机构。商业模式为 B2B 付费数据服务 | 2026-10-17T04:00:00Z |
| Wind 官网 | https://www.wind.com.cn | "Wind Financial Data, Terminal & Data Service Platform"。产品: WFT (Wind Financial Terminal), AMS, EDB, WDS — 均为付费专业数据服务 | 2026-10-17T04:00:00Z |

**verdict: confirm**

三部分均得到支持：
1. Baostock 数据起点与退市覆盖**未证实** — 官网为 JS 壳页面，无法通过 web_fetch 验证
2. CSMAR 为付费 — 商业数据公司，B2B 销售模式，数据超市
3. Wind 为付费 — 专业金融终端，明确为付费数据服务平台

→ A股端(S3)免费数据缺口成立。

---

## C6: 加密端可支撑 5 年 OOS（2020-01 起）且可规避幸存者偏差（依赖 Delisted Pairs 端点）

| 来源 | URL | 关键摘录 | observed_at |
|------|-----|---------|-------------|
| data.binance.vision (5年OOS支撑) | https://data.binance.vision/data/futures/um/daily/klines/BTCUSDT/1h/ + /monthly/fundingRate/BTCUSDT/ | daily klines + monthly fundingRate 均自 2020-01 起可用 → 2020-01 至 2025-01 共 5 年 OOS 窗口可行 | 2026-10-17T04:00:00Z |
| Coinglass API 文档 (幸存者偏差规避) | https://docs.coinglass.com/reference/getting-started-with-your-api | "Delisted Pairs" 端点存在 (GET /reference/delisted-exchange-and-pair) → 可获取已退市交易对列表，将退市标的纳入回测宇宙 | 2026-10-17T04:00:00Z |
| Coinglass 定价页 (付费依赖) | https://www.coinglass.com/pricing | Delisted Pairs 端点需 Coinglass API 访问权限，最低 HOBBYIST $29/month（无免费档） | 2026-10-17T04:00:00Z |

**verdict: confirm**（附条件）

- 5 年 OOS: 免费 Binance 数据（2020-01 起）支撑 ✓
- 幸存者偏差规避: Delisted Pairs 端点存在，能力上可行 ✓
- **条件**: 幸存者偏差规避依赖 Coinglass API（付费 $29/mo 起）。若项目严格限制免费数据，则幸存者偏差规避不可行，只能基于现存交易对回测（有幸存者偏差）

---

## 总结

| Claim | Verdict | 备注 |
|-------|---------|------|
| C1 | confirm | 异常: 2019-12-31 daily kline 存在，但连续数据自 2020-01 起 |
| C2 | confirm | 无 OI 文件 |
| C3 | confirm | 无免费档，Delisted Pairs 端点存在 |
| C4 | confirm | 免费档仅 100 bars，5 年日线不可行 |
| C5 | confirm | Baostock 不可验证，CSMAR/Wind 付费，A股缺口成立 |
| C6 | confirm | 5 年 OOS 免费可行；幸存者偏差规避需付费 Coinglass |

**contradictions: 0**
**confidence_after: 0.82**
