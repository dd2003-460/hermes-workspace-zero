# 交叉验证：数据修订与迟报（point-in-time 数据可用性）

**field_task**: `02-r1-field-field-2d1cbf21dc`
**概念**: 研究未知因素：数据修订与迟报（point-in-time 数据可用性）
**阶段**: RALPH 02.5（调研后交叉验证）· 窄字段验证 worker
**验证时间**: 2026-10-17T02:29–03:00Z（UTC，web_fetch 直读一手官方源；curl 在沙箱被拦，web_search 不可用）
**待核验核心结论**: 严格 PIT 快照不可免费直接获得；Binance 归档修订罕见/离散/可审计且已记录者为 spot → S1 futures funding/OI 修订风险暂定=中。决定"中→低"的关键待证项 = futures 归档是否在 2022-08 后或针对 futures 修订过。

---

## ⭐ 核心发现（C6）— 直接回答"决定中→低"的关键待证项

**结论：data.binance.vision 权威修订清单（`updates/` 文件夹）共 3 例，全部为 SPOT，零 futures 条目 → futures 归档无任何记录在案的修订。**

- 权威来源 = `binance/binance-public-data` 仓库的 `updates/` 文件夹（README CHECKSUM 章节称之为 "an exhaustive list of updates performed to the archive"）。经 GitHub API 列出，**恰好 3 个文件，全部 spot，无子目录**：
  - `2022-04-21_aggregate_trade_updates.zip`（33,962 B）— spot aggTrades
  - `2022-08-08_kline_updates.zip`（6,653,240 B）— spot klines，"Fixed inconsistent data"
  - `2022-10-04_aggregate_trade_updates.csv`（28,558 B）— spot aggTrades，**晚于 2022-08，且未被 README 表格列出**
- **零 futures（fundingRate / openInterest / futures klines）条目**。
- 因此"决定 S1 futures funding/OI 修订风险中→低"的关键待证项已解决：**futures 归档文件无记录在案的修订**。

**附加范围发现**：futures funding/OI 大概率**根本不在** data.binance.vision 免费归档内：
1. README 的 FUTURES 章节只文档 AggTrades / Klines / Trades，**未提及 fundingRate 或 openInterest**；
2. 仓库 `shell/` 下载脚本只有 klines（`download-futures-klines-simultaneously.sh`），无 funding/OI 脚本；
3. 直探 `data/futures/um/daily/fundingRate/BTCUSDT/...`（2022/2024/2025-01）与 `data/futures/um/daily/openInterest/BTCUSDT/...` 全 404 NoSuchKey。

→ S1 的 futures funding/OI 更可能来自 Binance futures **实时 API**（`/fapi/v1/fundingRate`、`/fapi/v1/openInterest`、`/futures/data/openInterestHist`，PIT 可回看）或 Coinglass，**而非本归档**。

**目录可枚举性限制（如实记录）**：data.binance.vision 经 web_fetch **无法枚举目录**——根 `/` 与 S3 ListObjectsV2 查询（`?list-type=2&prefix=...`）都只返回空 HTML 表头壳（`| Item | Size | Last Modified |`，无数据行，网站托管端点忽略 S3 参数）；所有 trailing-slash 子目录路径均 404 NoSuchKey。**只能对具体文件 key 做存在性探测**（200 + binary = 存在；404 NoSuchKey = 不存在）。

### C6 目录/文件检查清单（实际访问过的 URL）

| # | URL（data.binance.vision） | 结果 | 结论 |
|---|---|---|---|
| 1 | `https://data.binance.vision/`（根） | 200 空 HTML 壳 | 无法枚举（网站端点） |
| 2 | `?list-type=2&prefix=data/futures/um/daily/fundingRate/&delimiter=/` | 200 空 HTML 壳 | S3 列表参数被忽略 |
| 3 | `https://data.binance.vision/data/` | 404 NoSuchKey | 目录浏览不可用 |
| 4 | `https://data.binance.vision/data/futures/um/daily/` | 404 NoSuchKey | 目录浏览不可用 |
| 5 | `.../data/futures/cm/monthly/klines/BTCUSD_PERP/1d/BTCUSD_PERP-1d-2022-01.zip` | **200 binary（存在）** | futures klines 树真实存在 |
| 6 | `.../data/futures/um/daily/fundingRate/BTCUSDT/BTCUSDT-fundingRate-2025-01.zip` | 404 | funding/OI 非标准路径 |
| 7 | `.../data/futures/um/daily/fundingRate/BTCUSDT/BTCUSDT-fundingRate-2024-01.zip` | 404 | 同上 |
| 8 | `.../data/futures/um/daily/fundingRate/BTCUSDT/BTCUSDT-fundingRate-2022-01.zip` | 404 | 同上 |
| 9 | `.../data/futures/um/daily/openInterest/BTCUSDT/BTCUSDT-openInterest-2022-01.zip` | 404 | 同上 |
| 10 | `.../data/spot/monthly/klines/ADABKRW/1h/ADABKRW-1h-2020-08.zip` | **200 application/zip（存在）** | spot 例（README 自带） |

**futures klines URL 模式**（来自 `shell/download-futures-klines-simultaneously.sh`）：`https://data.binance.vision/data/futures/{cm|um}/monthly/klines/{SYM}/{interval}/{SYM}-{interval}-{yyyy-MM}.zip`；cm 符号带 `_PERP` 后缀；interval 1m…1mo；YEARS 2020–2025。

**辅助来源**：
- 仓库根目录（GitHub API `.../contents/`）：`.gitignore, README.md, TERMS_AND_CONDITIONS.md, python/, shell/, updates/` — **仓库内无 data/ 树**（bucket 由独立进程填充；仓库只权威提供 README + updates/ 修订清单 + 脚本）。
- `shell/` 目录：`download-futures-klines-simultaneously.sh`、`download-klines.sh`、`fetch-all-trading-pairs.sh`（仅 klines/交易对，无 funding/OI）。

---

## 逐 claim 核验表

| claim | 主张 | verdict | 关键证据 / 来源数 |
|---|---|---|---|
| **C1** | 官方承认归档文件可被事后修订 | **confirm** | README CHECKSUM 段原文（2 来源） |
| **C2** | 已记录修订：2022-08-08 kline + 2022-04-21 aggTrades（p=0/q=0/f=-1/l=-1） | **confirm**（发现第 3 例，见 note） | README 表 + updates/ 文件夹 + CHANGELOG（3 来源） |
| **C3** | 日线 T+1 迟报 + 月线当月第一个周一 + API 末根 K 线未定版 | **partial**（前两项 confirm；末根 K 线 unresolved） | README（前两项）；rest-api.md 超时（末根） |
| **C4** | Coinglass change log 只 New endpoints 无修订 → 修订行为未解决 | **unresolved**（页可达，条目未重读） | docs.coinglass.com（2 来源，条目被截断） |
| **C5** | A股 CSI300 拟生效样本（PIT 隐患）+ 美股 S&P500 按生效方法学回溯（PIT 友好） | **unresolved**（两 URL 可达性已确认；内容 JS/403 无法 web_fetch 重读） | csindex.com.cn（JS 壳）+ spglobal.com（403） |
| **C6** | futures 目录无任何修订痕迹（核心） | **confirm** | updates/ 全 spot + 直探 + README 未载（4 来源） |

### C1 — 官方承认归档可修订
- **verdict: confirm**
- 来源 1：`https://raw.githubusercontent.com/binance/binance-public-data/master/README.md`（HTTP 200，observed 2026-10-17T02:29:57Z）
  - quote: "Archived files may be updated at a later date as a result of recently discovered issues. Below is an exhaustive list of updates performed to the archive, containing the file path for reference, and CHECKSUMs of the replaced file and the replacement file:"
- 来源 2：`https://api.github.com/repos/binance/binance-public-data/contents/updates`（HTTP 200，observed 2026-10-17T02:38Z）— 该文件夹确实存在且含 3 个修订文件（即修订**实际发生过**，非空口承诺）。
- note: 两来源同为 Binance 官方但为不同产物（README 政策声明 vs 实际修订文件），满足"官方仓库 README + 官方文档"双源。

### C2 — 已记录修订（含 p=0/q=0 细节）
- **verdict: confirm**（文件/日期/说明确认；p=0/q=0 字段值经 README 锚点链接印证，未逐字节重验）
- 来源 1：README "Updates" 表**恰好 2 行**：
  - "2022-08-08 | updates/2022-08-08_kline_updates.zip | Fixed inconsistent data"
  - "2022-04-21 | updates/2022-04-21_aggregate_trade_updates.zip | Align to the [Spot aggregate trade data change](...CHANGELOG.md#2022-04-12)"
- 来源 2：`updates/` 文件夹（GitHub API）— 两文件确认存在（33,962 B / 6,653,240 B）。
- 来源 3：`https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/CHANGELOG.md`（HTTP 200，"Last Updated: 2026-09-18"）— 2022-04-12 审计条目（"Duplicated records were marked invalid ... p='0' // price, q='0' // qty, f=-1 // first_trade_id, l=-1 // last_trade_id"）位于文件深处，web_fetch 在其之前截断；README 对该锚点的**显式链接**独立印证该条目存在。
- ⚠️ **refinement（非矛盾）**：`updates/` 实际有**第 3 个**修订文件 `2022-10-04_aggregate_trade_updates.csv`（28,558 B，spot aggTrades），**晚于 2022-08 且未被 README"exhaustive"表列出** → 实际记录修订 = 3 例（非 2），README 表本身滞后/不全；3 例**全为 spot**，最晚 2022-10-04，仍无 futures。

### C3 — 迟报 T+1 / 月线 / 末根 K 线
- **verdict: partial**
- 来源 1（前两项 confirm）：README — "All symbols are supported, with new `daily` data becoming available the next day and new `monthly` data at the first monday of the month."
  - 不确定："the first monday of the month" 指哪月有歧义；"the next day" 确切 UTC 时刻未明。
- 末根 K 线（unresolved）：`https://raw.githubusercontent.com/binance/binance-spot-api-docs/master/rest-api.md` 经 web_fetch **超时**（文件过大）；且调研原文已注明"此版本文档无显式 last-kline-not-finalized 措辞，结论由 open-time 唯一标识 + 返回最近 klines 推出"（属推断）。
- note: 前两项（日线 T+1、月线首周一）有 README 单一权威源确认；末根 K 线留待 03 阶段（fapi 沙箱不可达，无法线上实测）。

### C4 — Coinglass 修订行为未解决
- **verdict: unresolved**（页面可达性确认；具体条目本次未重读）
- 来源 1：`https://docs.coinglass.com/reference/change-log`（HTTP 200，observed 2026-10-17T02:58Z，"📝 Change Log" 位于 "COINGLASS API V4" 下，readme.io 文档站）
- 来源 2：`https://docs.coinglass.com/`（API 文档主站，确认提供 OI/funding 历史端点）
- note: web_fetch 返回完整左侧导航但在到达**按日期的 change-log 条目之前被截断**，故"最新条目 2026-04-13、仅 New endpoints、无 revision/correction 条目"未能本次独立重读；以调研原 ego-browser 读数为据。**主张本身即"未解决"**，故 verdict=unresolved 与主张一致。

### C5 — A股/美股指数 PIT 机制（横向对照，非核心加密主张）
- **verdict: unresolved**（两 URL 可达性已确认；内容无法经 web_fetch 重读）
- 来源 1（CSI300）：`https://www.csindex.com.cn/#/indices/family/detail?indexCode=000300`（HTTP 200 但**空 body** — 纯 JS SPA 壳页，无服务端文本；"拟生效样本"需浏览器渲染）
- 来源 2（S&P500）：`https://www.spglobal.com/spdji/en/indices/equity/sp-500/`（**HTTP 403 "Security Controls Triggered"** — 反爬拦截 web_fetch）
- note: 两 URL 确认存在/可达，但内容经 web_fetch 不可读（JS SPA / 403 反爬）。调研原 ego-browser 读数（CSI300 "拟生效样本"；S&P500 "based on the index methodology in effect on the Launch Date"）为据。属横向对照，不影响核心加密 S1 结论。

### C6 — futures 无修订痕迹（核心）
- **verdict: confirm**
- 来源 1（权威修订清单）：`updates/` 文件夹 = 3 文件全 spot、零 futures（见上）。
- 来源 2（直探）：futures klines 存在（200）；fundingRate/openInterest 直探全 404。
- 来源 3（README）：FUTURES 章节仅 AggTrades/Klines/Trades，未载 funding/OI。
- 来源 4（脚本）：`shell/download-futures-klines-simultaneously.sh` 仅 klines。
- note: 即使 futures funding/OI 在归档内（未在直探路径命中，亦未文档化），**权威 updates/ 清单对 futures 零条目** → 无证据表明任何 futures 归档文件被修订。这直接解决"决定中→低"的关键待证项。

---

## 置信度与风险评级

**confidence_after: 0.85**（自 0.7 上调）
**理由**: 字段最核心、最影响 S1 决策的发现（Binance 归档可修订但罕见/离散/可审计、已记录者全 spot、**futures 无任何记录修订**、futures funding/OI 大概率不在免费归档）现由权威 `updates/` 清单 + 直探 + README 三重印证**坐实**，且新发现第 3 例 spot 修订（2022-10-04）与"futures funding/OI 大概率不归档"这一范围结论——正是字段点名的"决定风险中→低"的关键待证项。迟报部分（日线 T+1 / 月线首周一）亦确认。未上调至 ≥0.9 因 C4（Coinglass 修订披露）、C3 末根 K 线、C5（A股/美股内容）本次仍为 unresolved（属次要/横向，不阻断核心）。

**修订风险评级: 低**（就 S1 futures funding/OI 经 data.binance.vision 免费归档路径而言）
**一句理由**: 权威 `updates/` 修订清单 3 例全为 spot（2022-04/08/10）、零 futures，且 futures funding/OI 大概率不在免费归档内（README 与脚本均未载、直探全 404）→ 归档路径下 S1 futures funding/OI 修订风险实测为低；**仅当改用 Coinglass（修订行为公开无记录）时回升至中**。

**disposition 建议: confirmed**（自 research_required 推进）
**理由**: 核心加密端修订/迟报机制已交叉验证坐实，字段点名的关键待证项（futures 是否被修订）已解决（否）。残留 unresolved（Coinglass 披露 / API 末根 K 线 / A股美股内容）均为次要或横向对照，不阻断 03 阶段对 S1 数据源与 PIT 处理方案的决策。

**contradictions: 0**（无对任何 claim 核心论断的直接矛盾；唯一差异为 C2 修订数 2→3，属"补充一例"而非矛盾，已记入 C2 note 与 refinement。）

---
*# origin: ai*
*worker: RALPH 02.5 窄字段验证（数据修订与迟报）。未运行 ralph apply；未改 loop-state.json 或他人任务文件。*
