# F7 多信号组合预注册 — funding + 现货-期货基差
# origin: human (成璐 2026-10-31) + ai
日期: 2026-10-31 | 状态: PRE-REGISTERED

## 核心问题
F6 闭合：funding 单信号三市场无显著超额收益。F7：加基差信号能否产生增量？

## 可验证预言
- P1: |ρ(funding,basis)| < 0.3 → 组合 t 值应高于单信号最优 ≥20%
- P2: |ρ| ≥ 0.3 → 组合 t 提升 <10%，判"无增量"
- P3: 必须过全部 8 gate 才算成功，部分通过 = 负结果

## 数据源
- 基差: basis_t = (spot_close - perp_close)/spot_close × 100%
- Binance vision 需确认现货/永续；若只有永续改用 OKX 现货 API

## 信号逻辑（冻结）
- B1: basis ≤ -0.05% → 做多; B2: basis ≥ +0.05% → 做空
- 组合: 同向→1x, 单信号→0.5x, 无→空仓

## 回测协议（同 F6）
- PIT: 00:00 UTC 决策, ts≤t−1d, 开盘 taker
- 矩阵: 3 regime × 2 thr(funding) × 2 thr(basis) × 5 window = 60 tests/市场
- Gate F1-F8: t≥2, ≥30 trades, net>0, 跨窗≥3/4, perm p<0.001 B=2000, PSR>0.95, BH-FDR@60, DSR>0
- 成本: 0.05% taker + 0.01%/0.02% slippage
- 市场: BTC/ETH/SOL USDT

## 失败降级
- 数据不可得 → OKX 现货或 funding 双阈值组合
- 全 FAIL → 负结果记录，转链上/期权

## 执行清单
1. 确认数据源 2. 拉现货 3. 写 run_f7.py 4. 跑回测 5. 对账 P1-P3
