# TASKS — D1-financial-market-analysis

> origin: ai
> 更新时间: 2026-10-20（arena 审计 P0 修复后重写）
> 规则：只接取未完成、无人工阻塞、依赖已完成的任务；候选任务必须显式标记 candidate。

## 已完成（负结果也是交付物）

| ID | 任务 | 状态 | 产物 | 结论 |
|---|---|---|---|---|
| F1 | 明确资产类别、数据频率、持有期、数据源、评价指标 | ✅ 完成 | `loop-artifacts/stages/02/r1/` | BTCUSDT 1d, 资金费率, 2020-2026, PIT B6 8/8 PASS |
| F2 | 带时间戳的数据模式 + 信息泄露检查 | ✅ 完成 | `loop-artifacts/stages/03/r1/` | 无幸存者偏差, funding rate 发布时间对齐 |
| F3 | 滚动样本外回测 + 基准 + 交易成本 | ✅ 完成 | `loop-artifacts/stages/04/r1/backtest_results.json` | 45 格检验矩阵, BH-FDR 0/45 通过 |
| F4 | 资金费率信号研究 (T1 sign/T2 空头拥挤/T3 多头拥挤) | ✅ 完成 | `loop-artifacts/stages/04/r1/backtest_trades.parquet` (6576 行) | **S1 FAIL 8/8**: 3 信号 × 3 regime × 5 window 全部不显著 |
| F5 | 综合验证 + 研究报告 | ✅ 完成 | `loop-artifacts/stages/04/r1/t06-signal-backtest-report.md` | **负结果**: 资金费率单信号在 BTC 市场无统计显著超额收益 (DSR z=-4.87, pooled Sharpe T1=-1.031) |

## 待办

| ID | 任务 | 状态 | 优先级 | 依赖 | 说明 |
|---|---|---|---|---|---|
| F6 | 05 跨市场验证 (ETH/SOL) | ✅ 完成 (负结果) | P1 | F5 | `stages/05/r2/f6-crossmarket-report.md`: ETH FAIL / SOL FAIL, 单信号三市场闭合; SOL bull×T1×2021 t=3.17 post-hoc 观察不升级 |
| F7 | 多信号组合 (资金费率 + 基差) | ✅ 完成 (负结果) | P2 | F6 | `stages/05/r3/f7-report.md`: BTC/ETH/SOL 全 FAIL (P3), ρ(funding,basis)=−0.30~−0.39 信息冗余 → P2 "无增量" 分支; SOL bull×T1×B10×2021 t=3.27 post-hoc 不升级 |
| F8 | 策略层 (仓位管理 + 执行) | ⏳ 待办 | P2 | F6,F7 | 仅在 F6/F7 有显著信号后启动 |
| F9 | 跨所/跨币资金费率套利 | ✅ 完成 (条件性正) | P1 | F7 | `stages/05/r5/f9_report.md`: 跨所 FAIL; 同所跨币 2020-21 有效但 2022 后 p95 收敛到 <maker 成本 — "正在关闭的窗口" |
| F10 | 主体博弈模型: 预测新兴套利空间 (R1 DVOL 真空 / R2 funding+OI 级联) | ✅ 完成 (负结果+机制发现) | P1 | F9 | `stages/05/r6/f10_report.md`: R1/R2 预注册回测全 FAIL; 机制修正: 结构冲击后是**动量延续**非超调回归 (翻转方向胜率 70-87%, post-hoc 不升级); H3 半成立 (事件时点可预测, 方向判断错) |

## 阻塞

| ID | 阻塞项 | 类型 | 说明 |
|---|---|---|---|
| B1 | 05 S2 美股数据源全断（已在 F6 r2 按候选①降级为 ETH/SOL，本阻塞对 F6 关闭） | 技术 | Yahoo 403(大陆限制) / Stooq 403 / ifzq 美股历史日线空数组(仅实时报价). 候选: ①S2 换 Crypto (ETH/SOL, Binance API 已验证) ②等网络环境变化 ③换付费源 |
| B2 | 05 预注册需人工确认参数 | 人依赖 | 跨市场参数 (ETH/SOL 的 threshold/window) 需成璐拍板 |
