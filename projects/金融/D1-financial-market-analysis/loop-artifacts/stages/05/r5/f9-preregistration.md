# F9 预注册: 跨所资金费率套利 (game-theoretic angle)
# origin: human (成璐 2026-11-01: "博弈模型预测套利空间") + ai
日期: 2026-11-01 | 状态: PRE-REGISTERED

## 核心问题
F6/F7/F8 闭合：单交易所公开时间序列无方向性 alpha。
换维度：不做方向预测，做**相对定价**——同一资产在不同交易所的永续合约资金费率（funding rate）存在差异，
当差异超过交易成本时出现无风险套利窗口。这是博弈论角度：每个做市商/套利者在"抢窗口"，
窗口大小和持续时间由参与者数量决定（Nash equilibrium of speed competition）。

## 为什么这条线可能通（vs F6-F8）
1. **不是预测未来价格**，是检测当前价差——信息优势来自数据聚合速度，不是预测力
2. **套利空间是结构性的**：只要多交易所共存 + 资金费率机制不同步，价差必然周期性出现
3. **可验证性强**：历史数据里能精确算出"如果当时执行了能赚多少"，不需要假设市场无效
4. **博弈维度**：可以建模"如果 N 个套利者同时看到信号，每人分到多少"——这决定了策略是否可持续

## 可验证预言（跑前冻结）
- P1: Binance vs OKX BTCUSDT 永续 funding rate 日频差值 |Δf| > 0.02% 的天数占比 > 5%（即套利窗口频繁出现）
- P2: 在 |Δf| > 0.05% 的日子执行（做多低费率所、做空高费率所），扣除双边 taker 费 0.1% 后，
  单笔平均净收益 > 0（即存在正期望套利）
- P3: 套利窗口持续时间中位数 < 4h（即窗口短，需要自动化执行；手动不可行）
- P4: 博弈均衡检验：若假设 3 个独立套利者同时入场，人均收益仍 > 0（策略容量未耗尽）

## 数据源
- Binance 永续 funding: 已有 cache (stages/04/r1/funding/um/extracted/)
- OKX 永续 funding: 需拉取 (OKX API 免费, 历史数据到 2020)
  - endpoint: https://www.okx.com/api/v5/public/funding-rate-history?instId=BTC-USDT-SWAP
- Bybit 永续 funding: 备选第三所 (https://api.bybit.com/v5/market/funding/history?symbol=BTCUSDT)
- 对齐: 按 UTC 8h 结算周期对齐 (Binance/OKX/Bybit 都是 8h)

## 回测协议
- PIT: 用 t 时刻已公布的 funding rate 决策，t+8h 结算时收/付
- 成本: 开仓 taker 0.05% x2 (两所) + 平仓 taker 0.05% x2 = 0.2% roundtrip; slippage 忽略 (大所流动性好)
- 矩阵: 3 交易所对 (B-O, B-BY, O-BY) x 2 阈值 (0.02%, 0.05%) x 3 持有期 (8h, 24h, 48h) = 18 tests
- Gate: t>=2, >=30 trades, net excess>0, perm p<0.001 B=2000, PSR>0.95, BH-FDR@18, DSR>0
- 基准: 无（纯套利，不跟大盘比）

## 博弈模型（P4 实现）
- 简化为 symmetric game: N 个套利者同时看到信号，总套利利润 Π 均分
- Π = |Δf| * notional - costs
- 人均 = Π/N, N in {1, 2, 3, 5}
- 判定: N=3 时人均仍 > 0 → 策略有容量; N=5 时人均 ≈ 0 → 容量上限约 3-5 个参与者
- 进一步: 用历史窗口持续时间估计"实际竞争者数量"（窗口越短 → 越快被吃完 → 有效 N 越大）

## 失败降级
- OKX/Bybit 历史 funding 数据不可得 → 仅用 Binance 内部不同币种对的 funding spread（BTC vs ETH 基差代理）
- 18 tests 全 FAIL → 跨所 funding arb 在日线级别已被完全套利，需转 tick 级数据（超出本项目范围）或收束

## 执行清单
1. 拉取 OKX + Bybit BTC/ETH/SOL 永续 funding history (2020-2025)
2. 与 Binance funding 对齐 (UTC 8h grid)
3. 计算 pairwise Δf 分布, 检验 P1
4. 模拟执行, 检验 P2/P3
5. 博弈容量分析, 检验 P4
6. 输出 f9_results.json + f9_report.md
