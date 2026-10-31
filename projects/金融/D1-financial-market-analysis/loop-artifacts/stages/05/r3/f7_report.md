# origin: ai
# F7 多信号组合报告 — funding + 现货-期货基差 (05 r3)

- 阶段: projects/金融/D1-financial-market-analysis/ loop-artifacts/stages/05/r3
- 执行: 2026-10-31 · seed=20261031 · B=2000 permutation · N_TRIALS=60 · 本地 cache，无 live API（现货拉取除外）
- 配套产物: `f7_results.json`（全量）/ `f7_trades_{BTC,ETH,SOL}USDT.parquet` / `scripts/run_f7.py`（可重跑，幂等，~5s）/ `scripts/build_f7_data.py` + `cache/okx_spot/`
- 预注册: `stages/05/r3/f7-preregistration.md`（2026-10-31 冻结，run 前）

## 1. 降级与偏差记录（如实标注，均在预注册 §失败降级 授权范围内）

**D1 现货数据源**：Binance vision bulk spot klines 已下线（2024-01 起 404，2020-2023 段亦无法补齐），fapi live API 被 IP ban。按预注册失败降级条款改用 **OKX 现货日线 API**（免费无 key，`bar=1Dutc` 保证 UTC 日界与 Binance 对齐；after-pagination 翻全历史）。残余风险：OKX 为 live API，历史日 K 可能含修订；对 ±0.05%/±0.10% 阈值下方向性结论的影响有限但非零，记入局限性。
**D2 永续/funding**：ETH/SOL 沿用 F6 r2 本地 cache（官方 CHECKSUM 逐文件复验 ok=272/bad=0/missing=0）。
**D3 BTC 路径**：BTC 永续 klines 与 funding 在 04/r1 S1 cache（consolidated CSV/parquet，源自官方 vision zips）；r2 cache 只含 ETH/SOL。
**D4 矩阵口径**：预注册写 "2 threshold(funding)" 未点名，取 T1(sign)/T2(short-crowding)，与 F6 主阈值一致；T3 不在 F7 范围。每市场实检格 = 3 regime × 2 fth × 2 bth，仅匹配 regime 年实检（20 格），regime-mismatch 格平仓计数保持 60 诚实。
**D5 反向冲突分支**：冻结文本只定义同向/单信号/无信号三分支，两信号反向触发实现为 **0 仓位**（无共同方向），审计计数：BTC 421 天 / ETH 418 天 / SOL 389 天（≈18-20% 交易日）。
**PIT 口径**：t 日 00:00 UTC 决策，funding 用 ts_norm ≤ t−1d 最新 settled 值（与 F6 完全同构），basis 用 t−1 日收盘价差，当日 open taker 成交。成本 taker 0.05% + slippage 0.01% base per side（stress 0.02% 单独报告不 gate）。

## 2. 数据范围

| 市场 | perp K线 | OKX 现货 | funding 行数 | merged 天数 |
|---|---|---|---|---|
| BTCUSDT | 2020-01-01 → 2025-12-31 | 2020-01-01 → 2026-10-31 | 7395 | 2192 |
| ETHUSDT | 2020-01-01 → 2025-12-31 | 2020-01-01 → 2026-10-31 | 6576 | 2192 |
| SOLUSDT | 2020-09-14 → 2025-12-31 | 2020-10-01 → 2026-10-31 | 5881 | 1913 |

OOS 窗口 2021-2025 全覆盖。SOL 上市 2020-09-14（币安），OKX 最早 2020-10-01，2020-09 缺失不影响 OOS 窗口。

## 3. 结果总览

**final_verdict = FAIL（三市场全灭；P3 成立：部分通过 = 负结果）**

| 市场 | F1 t≥2 | F2 ≥30笔 | F3 net>0 | F4 方向一致 | F5 p<0.001 | F6 PSR>0.95 | F7 BH-FDR | F8 DSR>0 | overall |
|---|---|---|---|---|---|---|---|---|---|
| BTCUSDT | ❌(20格) | ❌(4格) | ❌(9格) | ❌(T2xB10 2/4) | ❌(0) | ❌(0.5592) | ❌(0 reject) | ✅(0.0215) | **FAIL** |
| ETHUSDT | ❌(20格) | ❌(3格) | ❌(9格) | ✅ | ❌(0) | ❌(0.8249) | ❌(0 reject) | ✅(0.1077) | **FAIL** |
| SOLUSDT | ❌(17格) | ✅ | ❌(5格) | ✅ | ❌(0) | ✅(0.9967) | ✅(2 reject) | ✅(0.7063) | **FAIL** |

主变体 T1×B05 全样本：BTC net_base=+0.1479（stress +0.1017，858 trades）；ETH net_base=+1.2467（stress +1.1983，898 trades）；SOL net_base=+4.7053（stress +4.6538，913 trades）。

## 4. P1/P2 预言对账（核心科学问题）

| 市场 | ρ(funding, basis) 日频 | 分支 | 单信号最优正变体 | 组合最优格 | Δt | 预言成立? |
|---|---|---|---|---|---|---|
| BTCUSDT | **−0.3519** | P2 (冗余) | T1×2024, t=1.105 | bull×T1×B10×2024, t=1.480 | +0.376 | ❌ 提升 34% ≥ 10% |
| ETHUSDT | **−0.3923** | P2 (冗余) | T1×2021, t=1.296 | range×T1×B10×2023, t=1.346 | +0.049 | ✅ 增量 <10% |
| SOLUSDT | **−0.3053** | P2 (冗余) | T1×2021, t=3.285 | bull×T1×B10×2021, t=3.346 | +0.062 | ✅ 增量 <10% |

判定口径说明：单信号基线取**正向 t 的最优变体**（负 t 变体是失败模式，不是"最优"，拿它当分母会制造伪 Δt——初版脚本犯过此错，已修并在 reconciliation 中保留原始数值供审计）。

**结论：三市场 |ρ| 全部 ≥ 0.3 → P2 分支（冗余）。** 基差与 funding 是同一持仓拥挤度的两种定价（贴水加深 ↔ funding 转负），不构成正交信息源。

- ETH、SOL：P2 预言字面成立——组合相对单信号最优变体几乎零增量（Δt ≈ 0.05-0.06）。
- BTC：P2 预言字面不成立（Δt=+0.376 > 10%），但拆解后是**跨窗择优假象**：单信号最优在 2024（t=1.105），组合最优恰在同窗 2024（t=1.480，p=0.139）；该格远未过任何 gate，且组合在单信号其他窗口并无系统性优势。**按预注册口径记 P2 不成立，实质解读仍为冗余。**

## 5. post-hoc 观察（不升级，仅记录）

- **SOL bull×T1×B10×2021: t=3.3464, p=0.001999, 115 trades, net=+3.6846** —— 全场最强正向格，BH-FDR@60 下被 reject（统计上勉强存活）。但与 F6 已记录的 SOL bull×T1×2021 单信号（t=3.165/p=0.0015）几乎同源：同一牛市窗口、同一 funding 腿，基差腿只是加了暴露。**判为同一现象的重复计数，不升级为结论。**
- 2022 bear 三市场一致大幅负超额：组合规则在熊市系统性反向（funding 转负→T1 空仓、基差贴水→B1 做多，opposite 冲突日被迫空仓或半仓接刀）。若未来要利用该效应，须作为**新的预注册假设**（bear regime 反向规则）重新设计，不得事后捞。
- opposite_days 占比 18-20%（389-421/2192）：两信号方向冲突频繁，佐证 ρ 偏高的判断。

## 6. 局限

1. OKX 现货为 live API 数据，存在历史修订风险（D1 降级代价）；±0.05%/±0.10% 阈值下的方向性结论对小幅修订稳健，但需下一轮双源交叉验证才能闭合。
2. 单一交易所对（Binance perp × OKX spot）：跨所基差本身含所间价差成分，非纯资金成本信号。
3. 判定器初版对 negative single-best 的处理缺陷已修复（§4 口径说明），f7_results.json reconciliation 保留原始数值供审计。
4. 成本模型 0.05% taker + 0.01%/0.02% slippage per side，未建模 funding 收付的税务/保证金占用。

## 7. 结论与下一步

**F7 闭合：funding + 基差组合信号在预注册的 8-gate 标准下三市场全部 FAIL，且 |ρ(funding,basis)| ≥ 0.3 三市场一致（−0.31 ~ −0.39）→ 基差不提供独立信息增量（P2 精神成立，P1 前提不成立；BTC 表面反例为跨窗择优假象）。** 时间戳类微观结构信号（funding/basis 同源）路线至此两条腿都走不通。

按预注册失败降级条款，候选后续（待 Commander 决策，均需新预注册）：
- A. 链上数据（交易所净流入/大户仓位；Bybit/Binance 免费 OI 短窗口此前已否决，需找新源）
- B. 期权隐含波动率/偏斜（Deribit 免费 API，2019 起历史）
- C. 宏观/跨资产时间戳（美债收益率、美元流动性）作为 regime 增强而非入场信号
- D. 项目收束：把 S1/F6/F7 负结果整理成完整研究原型报告（point-in-time 方法论 + 负结果本身是贡献）