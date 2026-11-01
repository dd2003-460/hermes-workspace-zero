# F10-R4 预注册: 条件带宽预测 (R4-A)

# origin: ai
日期: 2026-11-01
状态: FROZEN v1 (参数不可改, 回测后只可报告结果)
依据: f10-r4-model-design.md (v0.1) + research/{A,B,C,D}.md (F10-R3 全门禁通过)

## 假设

温度 T(t) 升高 (异质度/波动率 regime shift) 时, 未来 4h |ret| > 2σ 的**条件概率**高于无条件频率;
方向顺前 24h 动量 (冲击动量延续, R1/R2 实测)。
本规则只做分布级预测 (带宽), 不做点位/时长预测 (A.md §3.5)。

## 信号定义 (冻结)

### 状态变量 (每根 1h bar 的决策时刻计算, 全部 PIT — 只用 t 及之前数据)

- **T(t) 温度** = max(T_atr_z, T_fund_z, T_vol_z), 三件套取最大 (design doc 允许"取一"):
  - T_atr_z: ATR(14) 的滚动 30d z-score (窗口 [t-720h, t], 含 t 前一根已收盘 bar)
  - T_fund_z: settled funding rate 序列的滚动 30d z-score (ffill 到小时格; 无数据的 symbol 该项 = NaN → max 忽略 NaN)
  - T_vol_z: 1h 收益 |ret| 的滚动 30d z-score
- **触发**: T(t) ≥ 1.5 (z-score 阈值, 与 R1 DVOL 对齐便于对比)
- **c_套利 / carrying capacity 条件**: design doc 要求 "c_套利 < carrying capacity (倒U左支)"。
  代理可得性核查 (诚实约束): c_s 需要策略篮构造 + ΔOI×杠杆协方差, aggTrades 历史未拉取 (见 model-design 数据缺口)。
  **本轮降级声明**: c_套利 条件无法以预注册方式实现 → 本轮 R4-A 在**不含 c_套利 条件**下运行,
  记为 R4-A-degraded; 完整版本标记 research_required (需 aggTrades + 策略篮)。
  该降级是执行期数据约束, 不是参数改动 — 触发阈值/输出/方向/持有均不变。

### 输出与方向 (冻结)

- **事件定义**: E_t = {max(|ret_{t+1}|, ..., |ret_{t+4}|) > 2·σ_base}, σ_base = 1h 收益滚动 30d std (PIT, 截至 t)
- **条件概率估计 p̂_t**: walk-forward logistic 回归, 特征 = [T_atr_z, T_fund_z, T_vol_z, mom24, |funding| z]
  (特征集冻结, 不迭代); 训练窗 6m / 验证窗 3m 滚动, 与 R1/R2 一致
- **基准对照**: 无条件频率 p_uncond = P(E_t) over all bars (同一 30d 滚动口径), Brier 对比对象
- **方向**: sign(mom24), mom24 = close[t]/close[t-24] - 1; |mom24| < 0.1% → 不交易 (方向不明)
- **入场**: 触发且 |mom24|≥0.1% → 当根 1h bar open 入场 (决策用截至上一根收盘的信息, 无前视)

## 策略规则 (冻结)

1. 持有: 固定 4h (与 R1 对齐便于对比)
2. **止损 √Q 律** (替换 ATR 固定倍数, A.md §3.3):
   stop_dist = Y · σ_base · √(Q/V)
   - σ_base: 同上 (1h 收益滚动 30d std)
   - Q/V: 冲击量比, 代理 = 当根 1h quote volume / 滚动 30d 中位 1h quote volume (PIT)
   - **Y = 1.0** (冻结常数, 首次标定; A.md 只给形状不给系数, 取 1 使 stop ≈ 常态波动幅度的 √(Q/V) 倍)
   - **执行层下限 (冻结)**: stop_dist ≥ 2×往返成本 (0.28%) — 止损距离小于成本 2 倍时止损出场必亏成本、
     信号无意义; 这是可行性约束不是参数拟合 (常态 q/v≈1 时 stop≈σ_base≈3-4×成本, 下限不触发;
     仅在 σ_base 极低的死水时段生效)。回测若显示下限触发占比 >5%, 需在报告中单列其贡献。
   - 盘中 (i+1..i+4) 触及则提前出场
3. 仓位: 等权, 同一 symbol 同时最多 1 仓 (重叠触发跳过); 不同 symbol 并行
4. 拥挤度调节 (C.md §3.1): **本轮不启用** — C.md 结论是 ΔOI 作拥挤度代理被双重否定,
   可用代理不足 → 记录为局限性, 不虚构参数

## 验收标准 (冻结, 来自 model-design 验收节)

- **主判据 (校准)**: OOS Brier(p̂_t, E_t) < Brier(p_uncond, E_t) — 条件概率校准优于无条件基准
- **次判据 (方向)**: 方向正确率 (gross ret 符号 = 预测方向占比) > 55%, exact binomial two-sided p < 0.05 (n ≥ 30 才检验)
- PASS = 主判据 AND 次判据 (若 n < 30, 次判据记 insufficient, PASS 需主判据 + Commander 裁定)
- Walk-forward: 训练 6m / 测试 3m 滚动 (2022-01 → 2025-12 数据窗内)

## 成本假设 (冻结)

同 R1/R2: 单边 0.07%, 往返 0.14%

## 数据边界 (预先声明)

- Klines 1h: Binance vision um monthly zip (本地 cache 已有 2022-01→2025-12, BTC/ETH/SOL 各 48 月)
- Funding: Binance vision monthly (BTC extracted 已有; ETH/SOL 从 r2/funding zip 解压, 复用 run_f10_backtest.load_funding)
- σ_base/ATR/z-score 全部滚动 PIT, 无未来信息; 入场价 = 决策 bar 自身 open, 特征只用此前数据
- 已知局限: ① c_套利 缺失 (degraded); ② 拥挤度调节缺失; ③ Y=1.0 未标定 (敏感性分析留 post-hoc, 不进判据)

## 与 R1/R2 的关系

R1 = IV regime shift (DVOL) 单信号; R2 = funding+OI 结构信号 (均值回归方向, 失败);
R4-A = 多源温度 max 聚合 + 分布级输出 (带宽而非点位) + 顺动量方向 + √Q 止损。
机制链: T 高 → 流动性薄/异质度高 → 短窗大偏离概率升 (A.md A1/A7), 方向由冲击动量决定 (R1 实测)。