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

## 事件日历（G9）

FOMC 会期/CPI 发布日需单独核查（BLS/Fed 官网），arena agent 负责。
