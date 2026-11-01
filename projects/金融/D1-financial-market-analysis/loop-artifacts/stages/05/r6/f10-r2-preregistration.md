# F10-R2 预注册: 被迫平仓级联 (funding 极端 + OI 骤降 → 反向弹射)

# origin: ai
日期: 2026-11-01
状态: FROZEN v1 (参数不可改, 回测后只可报告结果)

## 假设 H3 子项

保证金追缴 → 强制平仓 → 超调 → 均值回归。
可观测代理: funding rate 连续 N 期极端(单侧拥挤) + OI 骤降(仓位被砍) → 未来 8-24h 反向弹射。

## 信号定义 (冻结)

- **funding 极端**: settled funding rate f[t] 满足 |f| ≥ 该 symbol 滚动 90 天 p95 (单侧判定: f≥+p95 = 多头拥挤; f≤-p95 = 空头拥挤)
- **OI 骤降**: Bybit 1d OI[t] / OI[t-3] - 1 ≤ -5% (3 日窗口)
- **触发**: 两条件同日满足 (funding 结算时刻 08:00 UTC 用 t 日值; OI 用 Bybit 当日快照)
- **PIT 规则**: 决策时刻 = 当日 08:00 UTC 之后 (funding 已结算); 入场价 = 当日 09:00 UTC 那根 1h kline open
- **方向**: 多头拥挤(f≥+p95)+OI 降 → 做空 (预期多头被迫平); 空头拥挤(f≤-p95)+OI 降 → 做多
- **收益计算**: ret = close[t_entry+H] / open[t_entry] - 1, H = 24h (主) / 8h (次)

## 策略规则 (冻结)

1. 触发即入场, 持有固定 24h (主判据), 8h 版本作为稳健性检查
2. 止损: 2*ATR (14 期 1h, 截至入场前一根)
3. 同一 symbol 重叠触发跳过; 不同 symbol 可并行
4. 无 OI 数据的时段 (Bybit 深度不足) → 退化为 "funding 极端 alone" 对照组 (只统计不交易, 用于检验 OI 条件的增量)

## 数据边界 (预先声明, 诚实约束)

- Bybit 1d OI 历史深度实测: 请求 2022-01 返回 2022-01 数据 (31 行/月), 但每页上限 ~31 行且近期请求回最近 31 天;
  实际可用窗口以拉取脚本落盘为准 (预计 2021 底/2022 起, BTC/ETH/SOL)
- Binance funding: 本地已有 2020-01→2026-09 (vision monthly) — 注意 R2 的 funding 用 Binance, OI 用 Bybit,
  跨所组合的 PIT 风险: Bybit OI 快照时刻与 Binance funding 结算时刻不完全同步 → 记录为局限性
- 若 Bybit OI 深度 < 1 年 → R2 降级为 "funding 极端 alone" 研究 (OI 条件标记 research_required, 与 T02 决策一致)

## 验收标准 (冻结)

- Walk-forward: 训练 6m / 测试 3m 滚动 (在 OI 可用窗口内)
- PASS 条件: 样本外 Sharpe > 1.0 AND t-stat > 2.0 AND win_rate > 52%
- 方向正确率 binomial test p < 0.05 (n ≥ 30 才检验)
- 对照: funding-alone 组 vs funding+OI 组的分离度 (检验 OI 条件是否真有增量)

## 成本假设 (冻结)

- 同 R1: 单边 0.07%, 往返 0.14%

## 与 R1 的关系

R1 = 波动率结构信号 (DVOL, 期权市场信息); R2 = 仓位结构信号 (funding+OI, 现货-永续套利者行为)。
两者机制独立 (做市商撤单 vs 杠杆客爆仓), 若各自通过则构成 H1 "结构变化+反应延迟" 的两个证据分支。