# 市场状态覆盖（牛/熊/震荡）交叉验证 — 02.5 阶段工件

- **字段任务**: `02-r1-field-field-e1e76b2921`
- **字段概念**: 研究未知因素：牛市、熊市与震荡市状态（市场状态覆盖）
- **核验时间**: 2026-10-17T03:45Z（本 worker 会话；跨会话重探时间精确到分钟，本会话前已压缩的观测时间标注"重建估计 ±5min"）
- **核验者**: RALPH 02.5 窄字段验证 worker（仅本字段）
- **前序工件**: `loop-artifacts/stages/02/r1/research/bear-range-coverage.md`（主代理一手实证记录）

## 结论摘要

| Claim | 场景 | verdict | 来源数 | 关键证据 |
|-------|------|---------|--------|----------|
| C1 | S1 加密 (Binance USDT-M) | **confirm** | 2（数据直探 + 官方文档库） | 起点实为 2019-12-31（206）；2020-01→2025-01 五节点全 206，含 2020-21牛+2022熊+2023震荡 |
| C2 | S2 美股 (Yahoo / Stooq) | **confirm** | 2（Yahoo 主代理一手 + 新浪 .INX 本 worker 一手） | Yahoo 覆盖 2000-02/2008/2022 三熊底；新浪 .INX 起点 2004-01-02，2008-03-10 两源吻合 (1273.37≈1273.4) |
| C3 | S3 A股 (免费日线源) | **confirm** | 2（腾讯 ifzq 实际取数 + AKShare 文档） | 6 节点全过：2015-06-12 h=5178.19 / 2018-10-19 l=2449.20 / 2022-04-27 l=2863.65 / 2008-10-28 l=1664.93 / 2016-01-27 l=2638.30 / 2017-12-29 h=3308.22 |

**confidence_after = 0.85**（原 0.7）。disposition 建议：`verified`（见文末；本 worker 不执行 field-apply）。

## C1 — S1 加密：Binance USDT-M 免费日线覆盖

**主张**: Binance USDT-M 免费数据（2020-01 起）完整覆盖 2022 熊 + 2019/2023 震荡，2018 熊仅尾部 → "≥5年含牛熊震荡"窗口 (2020-01→2025-01) 在加密端成立。

### 来源 1：data.binance.vision 数据直探（一手，本 worker 2026-10-17T03:44Z 重探 + 主代理前序直探）

URL 模式：`https://data.binance.vision/data/futures/um/daily/klines/BTCUSDT/1h/BTCUSDT-1h-YYYY-MM-DD.zip`（curl Range 0-0 请求）

| 文件 | HTTP | 含义 |
|------|------|------|
| BTCUSDT-1h-2019-12-31.zip | **206** | **实际数据起点**（完整单日，1387 bytes，前序已核验非残片） |
| BTCUSDT-1h-2018-12-31.zip | 404 | 早于起点（另有 2019-12-30 及此前 11 个日期均 404） |
| BTCUSDT-1h-2020-03-12.zip | 206 | 2020 崩盘底 |
| BTCUSDT-1h-2022-11-21.zip | 206 | 2022 熊底 |
| BTCUSDT-1h-2023-10-01.zip | 206 | 2023 震荡 |
| BTCUSDT-1h-2025-01-02.zip | 206 | 窗口末端（前序另核验 2020-01-01/2023-01-02/2023-07-03/2024-06-03 均 206） |

### 来源 2：Binance 官方 GitHub 文档库 README（binance/binance-public-data）

- URL: https://raw.githubusercontent.com/binance/binance-public-data/master/README.md
- 发布方: Binance 官方（GitHub），HTTP 200（curl，5282 bytes）
- 观察时间: 2026-10-17T03:44Z
- 引用: *"The website Binance Data Collection (https://data.binance.vision/) offers easy access for anyone to download Binance's public market data, which is aggregated into `daily` or `monthly` files. All symbols are supported, with new `daily` data becoming available the next day…"*；FUTURES 节明确 *"USD-M Futures / COIN-M Futures"*，Klines *"from /fapi/v1/klines API endpoint"*。
- 旁证: https://data.binance.vision/ 门户首页 HTTP 200（页面标题 "Binance Data Collection — Market Data"，观察 2026-10-17T03:43Z）。

### 判定: confirm（附修正）

- **修正 1**: 主张称"2020-01 起"，实际起点 = **2019-12-31**（更优，非劣化）。
- **修正 2**: "2019 震荡"实际仅覆盖 2019-12-31 单日；2020 年及以后才完整。2023 震荡完整覆盖（2023-01-02/07-03/10-01 均 206）。
- 窗口 2020-01→2025-01（5 年）含 2020-21 牛 + 2022 熊 + 2023 震荡 → **A4 判据在加密端成立**。
- **局限性（如实记录）**: 两个来源均为 Binance 发布方（数据文件 + 官方文档仓库），未找到独立第三方文档（www.binance.com 本沙箱 DNS 不可达；AKShare 加密货币页无 Binance 历史日线接口；binance-spot-api-docs README 无 data.binance.vision 引用）。数据本身为一手直探（206/404 状态码 + 字节数），证据强度不受 publisher 重复影响。

## C2 — S2 美股：免费日线源覆盖三大熊市

**主张**: 免费日线源（Yahoo Finance chart API 或 Stooq）覆盖 2000-02/2008/2022 三大熊市；需确认 Yahoo 日线历史精确起点（先验: 1993 或更早）。

### 来源 1：Yahoo Finance chart API（主代理一手，本沙箱不可复探）

- URL: `https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?interval=1d`
- 发布方: Yahoo Finance。观察时间: 主代理一手（时间戳未记录，见 `loop-artifacts/stages/02/r1/research/bear-range-coverage.md`）；本沙箱访问该域返回 403（大陆屏蔽页），无法独立复探。
- 引用（主代理记录）: 三个熊底节点全部 HTTP 200 — 2002-10-09 close 776.8 / 2008-03-10 close 1273.4 / 2022-10-13 close 3577.0；历史起点不晚于 2002-10。
- 备注: 2000-01-03 窗口探测返回 HTTP 400（更可能是查询格式错误而非 no-data），**Yahoo 精确起点未验证**。

### 来源 2：新浪财经美股日线 API（本 worker 一手直探）

- URL: `https://stock.finance.sina.com.cn/usstock/api/json_v2.php/US_MinKService.getDailyK?symbol=.INX`
- 发布方: 新浪财经（.INX = S&P 500 指数）。HTTP 200，观察时间: 2026-10-17T02:50Z（重建估计 ±5min）。
- 引用: 全量 5737 bars。首 bar 2004-01-02 o=1111.92 h=1118.85 l=1105.08 c=1108.48；**2008-03-10: o=1293.16 h=1295.01 l=1272.66 c=1273.37**（与 Yahoo 1273.4 吻合）；2009-03-09: l=672.88 c=676.53（2008 熊市底）；2022-10-13: o=3520.37 h=3685.41 l=3491.58 **c=3669.91**；末 bar 2026-10-16 c=7659.44。
- 含义: 新浪 .INX 起点 **2004-01-02** → 覆盖 2008/2022 熊市，**不覆盖** 2000-02 熊底（2002-10 早于起点）。

### 来源 3（死路记录，非支持来源）：FRED SP500

- URL: https://fred.stlouisfed.org/series/SP500（HTTP 200，观察 ≈2026-10-17T02:40Z 重建估计）
- 引用: *"FRED and its associated services will include 10 years of daily history for Standard & Poors and Dow Jones Averages series"*；Frequency: Daily, Close；Source: S&P Dow Jones Indices LLC。
- 含义: FRED 日线**官方仅保留 10 年**（CSV 直探实测 2016-10-17 起，cosd/coed 参数被忽略）→ 不能覆盖 2000/2008 熊市，对 C2 为死路；仅证明"免费官方 S&P 日线源存在"的弱旁证。

### 判定: confirm（附 2 项保留 + 1 项矛盾记录）

- 两个**独立**免费日线源确认: Yahoo（主代理一手，覆盖 2000-02/2008/2022）+ 新浪 .INX（本 worker 一手，覆盖 2008/2022；2008-03-10 两源值吻合）。Stooq 本沙箱不可达（JS challenge/403），未纳入。
- **保留 1**: 2000-02 熊底为单源（仅 Yahoo）。
- **保留 2**: Yahoo 精确日线起点（先验 1993 或更早）未验证。非阻塞：A4 在 2000-02 起点或 2004-01 起点下均成立（2004+ 窗口仍含 2008 熊+2020 崩+2022 熊+牛/震荡）。
- **矛盾记录（非阻塞）**: 2022-10-13 收盘价两源差 2.6%（Yahoo 记录 3577.0 vs 新浪 3669.91，超 ±2% 容忍）。新浪 bar 为真实 2022-10-13 交易日（当日为 +3.5% 反弹日，3669.91 与公开 S&P 收盘一致）；主代理 Yahoo 值疑为窗口首 bar 日期偏移。**后续若用该节点做节点校验，应以 3669.91 为准。**

## C3 — S3 A股：免费日线源 + 关键节点可取数

**主张**: 找一个免费 A股日线源，验证 2015-06 顶 / 2018-10 底 / 2022-04 底节点可取数，从而覆盖 2008/2015/2018/2022 熊 + 2016-17 震荡。

### 来源 1：腾讯 ifzq K 线 API 实际取数（本 worker 一手）

- URL: `https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=sh000001,day,START,END,640,qfq`（上证指数 sh000001，日 K）
- 发布方: 腾讯财经。HTTP 200，观察时间: 2026-10-17T02:46Z（重建估计 ±5min）。
- 节点值（JSON `data.sh000001.day`，±2% 容忍）:

| 日期 | open | close | high | low | 预期 | 判定 |
|------|------|-------|------|-----|------|------|
| 2015-06-12 | 5143.34 | 5166.35 | **5178.19** | 5103.40 | ~5178 顶 | ✓ 精确 |
| 2018-10-19 | — | 2550.47 | — | **2449.20** | ~2449 底 | ✓ 精确 |
| 2022-04-27 | — | 2958.28 | — | **2863.65** | ~2863 底 | ✓ 精确 |
| 2008-10-28 | — | — | — | **1664.93** | 2008 熊底 | ✓ |
| 2016-01-27 | — | — | — | **2638.30** | 2016-01-28 ~2638（差 1 天） | ✓ |
| 2017-12-29 | — | 3307.17 | **3308.22** | — | ~3300 | ✓ |

### 来源 2：AKShare 官方文档（指数数据页）

- URL: https://akshare.akfamily.xyz/data/index/index.html
- 发布方: AKShare 1.19.1 文档。HTTP 200（web_fetch），观察时间: 2026-10-17T02:45Z（重建估计 ±5min）。
- 引用: 确认免费 A股指数日线接口 — `stock_zh_index_daily`（新浪，"单次返回指定 symbol 的所有历史行情数据"，示例数据自 2005-01-04 起）、`stock_zh_index_daily_tx`（腾讯，"支持自定义时间范围"，底层即来源 1 的 web.ifzq.gtimg.cn 端点）、`stock_zh_index_daily_em`（东财）。

### 判定: confirm

- 2 来源达成（实际取数 + 文档，任务允许口径）。腾讯源 6 节点全部在容忍内，其中 3 节点与预期值精确吻合 → **2008/2015/2018/2022 熊 + 2016-17 震荡覆盖成立**。
- 已排除候选（如实记录）: 网易 163 K 线 API 死（HTTP 000/空响应）；新浪 CN `datalen` 上限 1023（最旧 bar 2022-07-26，深度不够）；Yahoo 000300.SS 返回 400（不支持）。

## 环境可达性地图（本 worker 沙箱，2026-10-17T02:34Z 起）

| 主机/端点 | 状态 |
|-----------|------|
| data.binance.vision | ✅（curl Range 探测） |
| stock.finance.sina.com.cn（美股 .INX） | ✅ |
| web.ifzq.gtimg.cn（腾讯 A股 K 线） | ✅ |
| akshare.akfamily.xyz | ✅（web_fetch） |
| fred.stlouisfed.org | ✅（系列页 200；CSV 参数被忽略） |
| raw.githubusercontent.com | ✅ 不稳（偶超时） |
| query1/query2.finance.yahoo.com | ❌ 403（大陆屏蔽） |
| stooq.com | ❌（JS challenge / 403） |
| www.binance.com | ❌（DNS 解析非公网 IP） |
| img1/2.money.126.net（网易） | ❌（服务已停） |
| en.wikipedia.org / api.nasdaq.com / ranaroussi.github.io/yfinance | ❌（DNS / 400 / 404） |

## 矛盾与差异记录

1. **C2 交叉源值差异（非阻塞）**: 2022-10-13 S&P 500 收盘 Yahoo 记录 3577.0 vs 新浪 .INX 3669.91（差 2.6%，超 ±2% 容忍）。判断：新浪值正确（真实 2022-10-13 为 +3.5% 反弹日）；主代理 Yahoo 记录疑为窗口首 bar 偏移。不影响 C2 覆盖性结论；后续节点校验以 3669.91 为准。
2. **C1 主张措辞修正（非矛盾，事实更优）**: "2020-01 起" → 实际起点 2019-12-31；"2019 震荡"实际仅单日。

## confidence_after 与理由

**0.85**（原 0.7，↑0.15）。

理由:
- 三条 claim 全部 confirm，且各满足 ≥2 来源口径（C3 = 实际取数+文档；C2 = 两个独立发布方一手数据；C1 = 数据一手直探+官方文档库）。
- 关键节点值全部实测落地（C3 六节点、C2 两源交叉、C1 状态码+字节数）。
- 未给 ≥0.9 的残留不确定性: ① Yahoo 精确日线起点年份未验证（先验 1993 或更早，400 疑格式错误但本沙箱不可复测）；② 2000-02 美股熊底单源（仅 Yahoo）；③ C1 两来源同发布方（Binance），无独立第三方文档佐证起点；④ C2 存在一处 2.6% 跨源值差异（非阻塞但需后续节点校验时注意）。

## disposition 建议

建议父代理将本字段处置为 **verified / research_complete**（三 claim 均 confirm，A4"≥5年含牛熊震荡"在 S1/S2/S3 三端均可由免费数据源支撑：S1 = 2020-01→2025-01 Binance USDT-M；S2 = 2000-02(或 2004-01)→2025 Yahoo+.INX；S3 = 2008→2025 腾讯 ifzq）。本 worker 依禁令不执行 ralph field-apply/apply，不改 loop-state.json，由父代理落盘。
