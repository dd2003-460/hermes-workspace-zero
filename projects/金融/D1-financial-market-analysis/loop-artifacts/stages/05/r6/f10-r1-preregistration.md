# F10-R1 预注册: 流动性真空预测 (DVOL regime shift → 短窗价格偏离)

# origin: ai
日期: 2026-11-01
状态: FROZEN v2 (参数不可改, 回测后只可报告结果; v2 修正数据路径 + 明确 PIT 规则)

## 假设 H1/H3 子项

DVOL 日度跳升(IV regime shift)次日, BTC 永续出现异常价格偏离(|ret|>2σ),
做市商撤单保护(adverse selection)导致深度变薄, 小资金推动大价差 → 超调后可反向交易。

## 信号定义 (冻结)

- **触发**: DVOL[t] - mean(DVOL[t-20:t]) > 1.5 * std(DVOL[t-20:t])
  (t = 该日 00:00 UTC; DVOL 为 Deribit 日度值)
- **PIT 规则**: 决策时刻 = t+1d 00:00 UTC (DVOL[t] 在 t 日收盘后才可得, 最早决策点是 t+1d 开盘);
  入场价 = t+1d 00:00 UTC 那根 1h kline 的 open (无前视)
- **观察窗口**: 入场后 1-4h
- **收益计算**: ret = close[t_entry+4h] / open[t_entry] - 1 (方向性, 含成本前)
- **方向**: 与触发前 24h 动量同向 = "超调"(做空/做多反打); 反向 = "确认"(不交易, 记录为对照)

## 策略规则 (冻结)

1. 仅对"超调"类型触发入场 (前 24h 涨且 DVOL 跳升 → 做空; 前 24h 跌且跳升 → 做多)
2. 持有: 固定 4h (t_entry → t_entry+4h 收盘价出场)
3. 止损: 2*ATR (ATR = 14 期 1h high-low 均值, 截至 t_entry 前一根; 盘中触发则提前出场)
4. 仓位: 等权, 同一时刻最多 1 仓 (重叠触发跳过)
5. 不做"确认"类型 (对照组只统计不交易)

## 验收标准 (冻结)

- Walk-forward: 训练 6m / 测试 3m, 滚动 (在 DVOL 可用窗口 2022-04 → 2025-12 内)
- PASS 条件: 样本外 Sharpe > 1.0 AND t-stat > 2.0 AND win_rate > 52%
- 方向正确率 binomial test p < 0.05 (n ≥ 30 才检验)
- 附加: 报告 |ret|>2σ 事件占比 (验证"偏离出现"本身, 独立于方向)

## 数据 (实际路径, v2 修正)

- DVOL: `loop-artifacts/stages/05/r4/data/dvol_daily.json` (Deribit daily, 2022-04-08 → 2025-12-01, 1334 点; API 现已返回空, 此缓存为最后可用)
- Klines 1h: Binance data.binance.vision futures um monthly `BTCUSDT-1h-YYYY-MM.zip` (2020-01 起全量可得, 本次拉 2022-04 → 2025-12)
- 本地 python: `/opt/homebrew/bin/python3` (pandas 3.0.3)

## 成本假设 (冻结)

- Taker fee: 0.05% (Binance VIP0)
- Slippage: 0.02%
- 总单边成本: 0.07%, 往返 0.14% (从毛收益中扣除)

## 局限性 (预先声明)

- DVOL 窗口仅 2022-04→2025-12 (~3.7 年), 不含 2020-21 牛市; 结论不外推到无 DVOL 时期
- 单 venue (Binance 永续) + 单标的 (BTC) 先行; ETH/SOL 扩展若通过再报告
- Deribit DVOL 是期权 IV 代理, 与现货订单簿深度非直接测量 → 机制解释保留 uncertainty