# F10-R5 本地数据探针（2026-11-05）

# origin: ai (成璐数字分身, 为 arena agent stage 02 提供已验证数据源)

## 传统宏观序列 — 全部可用，无需付费 key

| 变量 | 源 | URL | 频率 | 覆盖 | 实测状态 |
|---|---|---|---|---|---|
| 美债 10Y (DGS10) | FRED CSV | `fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10` | 日频 | 2020-01→今 (1784 rows) | ✅ 200 OK |
| 美联储资产负债表 (WALCL) | FRED CSV | `...id=WALCL` | 周频(周四) | 2020-01→今 (358 rows) | ✅ 200 OK |
| M2 货币供应 (M2SL) | FRED CSV | `...id=M2SL` | 月频(滞后~3周) | 2020-01→今 | ✅ 200 OK |
| VIX (VIXCLS) | FRED CSV | `...id=VIXCLS` | 日频 | 2020-01→今 | ✅ 200 OK |
| DXY 美元指数 | Yahoo Finance | `query1.finance.yahoo.com/v8/finance/chart/DX-Y.NYB` | 日频 | 2020-01→今 | ✅ last=101.443 |
| BTC DVOL | Deribit API | `deribit.com/api/v2/public/get_volatility_index_data?currency=BTC&resolution=3600` | 小时 | 2020-01→今 | ✅ DVOL≈37.4 (r7 称失效已过时) |

## PIT 延迟注意（G14）

- DGS10: 当日收盘即定，无修订风险
- WALCL: 周四发布上周四→本周三数据，PIT 用 t-4d
- M2SL: 月度，滞后约 2-3 周，PIT 用 t-21d 保守
- VIXCLS: 当日收盘即定
- DXY: CME 日频，当日收盘
- DVOL: Deribit 实时，小时级 PIT

## 事件日历（G9）— 本地已核查

### FOMC 2026 会期（来源: federalreserve.gov/monetarypolicy/fomccalendars.htm, 实测可达）

| # | 日期 | 备注 |
|---|---|---|
| 1 | 2026-02-18 | ✅ 已过 |
| 2 | 2026-04-08 | ✅ 已过 |
| 3 | 2026-05-20 | ✅ 已过 |
| 4 | 2026-07-08 | ✅ 已过 |
| 5 | 2026-08-19 | ✅ 已过 |
| 6 | 2026-10-07 | ⏳ 未来 |
| 7 | 2026-10-28 | ⏳ 未来 |

注：Fed 官网只公布到 2026-10，后续会期待 Fed 更新。PIT 用法：会议日 t 当天 14:00 ET 决议公布，事件窗口 [t-1d, t+1d]。

### CPI 发布日

BLS 官网 (bls.gov) 对大陆 IP 返回 403。替代方案：
- FRED CSV `CPIAUCSL`（headline CPI, 月频）— 通道已验证可达（同 DGS10 同一 fredgraph.csv 端点），但具体值需等限流恢复后确认
- CPI 发布日规律：每月 ~13-17 号（第一周二前后），可用 FOMC 会期 + 月度滞后近似
- **建议**：arena agent 调研时若需精确 CPI 日期，用 investing.com economic calendar 或 FRED release dates series

### QT/QE 状态判定

WALCL（美联储资产负债表, 周频）已确认可得。QT vs QE 判定方法：
- WALCL 连续 ≥8 周下降 → QT 期
- WALCL 连续 ≥8 周上升 → QE/扩表期
- 持平 → 中性期
- 无需外部源，WALCL 本身即可判定 regime 切换时点
