# F10-R5-H1 预注册: funding 极值 × 当日方向分组 (条件套利容量复现)

# origin: ai
日期: 2026-11-05
状态: DRAFT v1 (待成璐确认后冻结; 参数不可改, 回测后只可报告结果)
依据: f10-r5-macro-survey.md §3 H1 (S5 Shek 2026 SSRN 7520320) + f10-r2-preregistration.md (事件定义复用)

## 假设

当 BTC/ETH/SOL 当日收益 > 0 时，"负 funding 极值"信号的 24h 反转幅度**大于**当日收益 < 0 时的同一信号（差距 > 0），且仅在上涨日子样本上可通过 8 gate。

机制 = limits-to-arbitrage 下的条件套利容量：上涨日套利资本充足 → 负 funding 被快速修正（反转）；下跌日资本撤离 → 拥挤继续（延续）。

**关键限定**：本假设的条件变量是**当日价格方向**（快变量），不是宏观变量。若 H1 成立而 H2/H3 全 FAIL，结论 = "条件有效性存在但非宏观驱动"——这本身就是对 H_macro 的否定性回答。

## 信号定义 (冻结)

### 事件定义 (复用 R2, 不改口径)

- **funding 极端**: settled funding rate f[t] 满足 |f| ≥ 该 symbol 滚动 90 天 p95
- **本轮只用负侧**: f ≤ -p95 (空头拥挤 → 预期多头被迫平 → 做多)。S5 的核心发现是**负 funding 极值**的方向分组效应，正侧作为稳健性检查但不作主判据。
- **OI 条件**: 与 R2 一致 (Bybit OI 3d 降幅 ≤ -5%)。若 OI 数据不可得 → 退化为 "funding 极端 alone" 组 (与 R2 降级路径一致)。

### 新增: 当日方向分组 (H1 核心, 冻结)

- **方向定义**: dir[t] = sign(close[t-1] / close[t-2] - 1)
  - 即**入场前一日**的日收益符号 (PIT: 决策时刻 t 日 08:00 UTC 之后, close[t-1] 已确定)
  - dir[t] = +1: 上涨日 (前一日收涨)
  - dir[t] = -1: 下跌日 (前一日收跌)
  - dir[t] = 0: 前一日收益 |ret| < 0.1% → **排除** (方向不明, 不纳入任何组)
- **分组**: 所有 funding 极值事件按 dir[t] 分为两组:
  - G_up: dir[t] = +1 的事件
  - G_down: dir[t] = -1 的事件
- **主对比**: mean_ret(G_up) vs mean_ret(G_down), 其中 ret = 24h 持有期净收益 (扣成本)

### PIT 规则 (与 R2 一致)

- 决策时刻 = 当日 08:00 UTC 之后 (funding 已结算, 前一日收盘已确定)
- 入场价 = 当日 09:00 UTC 那根 1h kline open
- 收益计算: ret = close[t_entry+24h] / open[t_entry] - 1

## 策略规则 (冻结)

1. 触发即入场, 持有固定 24h (主判据), 8h 版本作为稳健性检查
2. 止损: 2×ATR (14 期 1h, 截至入场前一根) — 与 R2 一致
3. 同一 symbol 重叠触发跳过; 不同 symbol 可并行
4. 无 OI 数据的时段 → 退化为 "funding 极端 alone" 对照组 (只统计不交易)

## 判定阈值 (冻结, 双条件)

### 条件 ①: 分组差显著性

- Δgap = mean_net_ret(G_up) - mean_net_ret(G_down)
- **block bootstrap 95% CI 不含 0**, 且方向为 G_up > G_down
- block size = 5 天 (消除日内自相关)
- B = 2000 次重采样

### 条件 ②: 上涨日子样本通过 8 gate

G_up 子样本独立过 8 gate (与 F6/F7 协议一致):
1. t ≥ 2.0
2. n ≥ 30 trades
3. net > 0 (扣成本后净收益为正)
4. 跨窗 ≥ 3/4 (至少 3 个 walk-forward 窗口为正)
5. permutation p < 0.001 (B = 2000)
6. PSR > 0.95 (Probabilistic Sharpe Ratio)
7. BH-FDR @ family size = 60 (3 symbols × 20 windows)
8. DSR > 0 (Deflated Sharpe Ratio)

**下跌日子样本是否盈利不作为要求** (S5 已示其为负, 我们只验证"差距存在")。

## OOS 设计 (冻结, 防样本重叠)

S5 样本 2021-2026 与我们的 2020-2025 高度重叠 → 不是独立验证。

- **OOS 段**: 2020-01→2020-12 + 2025-01→2025-12 (S5 未重点覆盖的两端)
- **IS 段**: 2021-01→2024-12 (与 S5 重叠, 仅作复现参考)
- **主判据用 OOS 段**; IS 段结果单列, 标注"非独立验证"
- 若 OOS 段符号翻转 → 判 FAIL, 理由"样本重叠导致的伪 OOS"

## Walk-forward (与 R1/R2 一致)

- 训练 6m / 测试 3m 滚动
- 在 OOS 可用窗口内执行
- 跨窗一致性: ≥ 3/4 窗口方向一致

## 成本假设 (冻结, 与 R1/R2 一致)

- 单边 0.07%, 往返 0.14%
- slippage: 0.01% (BTC) / 0.02% (ETH/SOL)

## 数据需求

| 数据 | 源 | 状态 |
|---|---|---|
| Binance perp funding (8h→日聚合) | 本地已有 2020-01→2026-09 | ✅ |
| BTC/ETH/SOL 日线 OHLC | Binance API (大陆可达, U3 已补测) | ✅ |
| Bybit 1d OI | 本地已有 (R2 已拉取) | ✅ |
| 1h kline (入场价) | Binance API | ✅ |

## 验收标准 (冻结)

- **PASS**: 条件 ① AND 条件 ② 同时满足 (OOS 段)
- **FAIL**: 任一条件不满足
- **边缘**: 条件 ① 满足但 ② 不满足 → 记为 "gap 存在但策略层不通过", 单独分析原因

## 与 R2 的关系

R2 = funding 极值 + OI 骤降 → 反向弹射 (无条件, 全 FAIL)
H1 = 同一事件集 + **当日方向分组** → 检验条件有效性

H1 不改变 R2 的事件定义和策略规则, 只加一个分组维度。若 H1 PASS 而 R2 FAIL, 结论 = "R2 的失败可能是漏了方向分组"。

## 全部 FAIL 的收束判据 (与 survey §3.4 一致)

- H1 FAIL → 检查 H2/H3 (若尚未跑)
- H1-H3 全 FAIL → H_macro 未获支持, 宏观维度关闭, TASKS.md 候选 C 记负结果
- 收束后不得开第 4 个假设; 任何新假设须走新的 R 轮派发