# F7 多信号组合回测报告 — funding + 现货-期货基差 (05 r3)
# origin: ai

- 阶段: loop-artifacts/stages/05/r3
- 执行: 2026-11-01 · seed=20261031 · B=2000 permutation · N_TRIALS=60 · 本地数据，无 live API
- 预注册: `f7-preregistration.md`（2026-10-31 冻结, human+ai）
- 配套产物: `f7_results.json`（全量）/ `f7_trades_{BTC,ETH,SOL}USDT.parquet` / `scripts/run_f7.py`（幂等复跑 ~90s）

## 1. 降级记录（D1-D3，如实标注）

**D1**: Binance vision bulk 现货 klines 已下线（2024-01 起 404）+ fapi live API IP-banned → 现货改用 **OKX 日线 API**（免费无 key），cache/okx_spot/*.csv，BTC/ETH 2019-12→2026-10（2496 行）、SOL 2020-09→2026-10（2223 行）。
**D2**: 永续 klines + funding 沿用 F6 r2 本地 cache（官方 CHECKSUM 136+136 全过）。
**D3**: BTC 永续/funding 取自 04/r1 S1 cache（consolidated CSV/parquet，源自官方 vision zips）。

**信号与协议（冻结）**：
- basis_t = (spot_close − perp_close)/spot_close；PIT 用 t−1 日值（双腿均为 t 日 00:00 UTC 已知）
- funding: T1 sign / T2 short-crowding(≤−1e-4)；basis: B05 ±0.05% / B10 ±0.10%
- 组合规则: 同向 1x / 单信号 0.5x / 无或反向空仓（反向天数已审计入 meta）
- 矩阵: 3 regime × 2 funding-th × 2 basis-th × 5 window = **60 tests/市场**；BH-FDR/DSR 按 N=60
- 成本: taker 0.05% + 滑点 0.01% base（stress 0.02% 单独报告不 gate）

## 2. 结果（主变体 T1×B05，per-market gates）

| Gate | BTC | ETH | SOL |
|------|-----|-----|-----|
| F1 t≥2 | ❌ | ❌ | ❌ |
| F2 ≥30 trades | ❌ | ❌ | ✅ |
| F3 net excess > 0 | ❌ | ❌ | ❌ |
| F4 跨窗方向一致 | ❌ | ✅ | ✅ |
| F5 perm p<0.001 | ❌ | ❌ | ❌ |
| F6 PSR>0.95 | ❌ | ❌ | ✅ |
| F7 BH-FDR@60 | ✅ | ❌ | ✅ |
| F8 DSR>0 | ✅ | ✅ | ✅ |
| **overall** | **FAIL** | **FAIL** | **FAIL** |

**最强单格**（tested cells, |t| top）：
- BTC bear×T1×B05×2022: t=−3.53, p=0.0015, trades=189, net=−0.95（负超额显著——熊市组合继续亏）
- SOL bull×T1×B10×2021: t=3.27, p=0.0025, trades=117, net=+3.63
- SOL bull×T1×B05×2021: t=3.22, p=0.0025, trades=146, net=+4.09
- ETH bear×T1×B10×2022: t=−2.46, p=0.0165, trades=151, net=−0.83

**主变体 T1×B05 全样本**：BTC net=−0.15 / ETH net=+1.03 / SOL net=+5.07（base 成本）；stress 成本下几乎不变。反向信号天数: BTC 399 / ETH 382 / SOL 360（占活跃日 ~40%，组合规则大量空仓）。

## 3. P1/P2 预言对账（pre-registration §可验证预言）

| 市场 | ρ(funding,basis) | 分支 | combo best t | single best t（正 t 口径） | Δt | 预言成立? |
|------|------------------|------|--------------|---------------|-----|-----------|
| BTC | −0.352 | P2 (\|ρ\|≥0.3) | 1.723 (T1×B10×2023) | 1.199 (T1×2023) | +0.525 | ❌ |
| ETH | −0.392 | P2 | 1.114 (T1×B05×2021) | 1.115 (T1×2021) | −0.001 | ✅ |
| SOL | −0.305 | P2 | 3.268 (T1×B10×2021) | 3.222 (T1×2021) | +0.046 | ✅ |

**解读**：三市场 |ρ| 全部 ≥0.3（funding 与 basis 信息高度重叠，非正交）→ 走 P2 分支"无增量"预期。ETH/SOL 成立（Δt≈0，组合相对单信号零增量）。BTC "失败"需拆开看：combo best 是 range×2023 的 t=1.72，而 funding 单信号在 2023 只有 t=1.20——但 **basis 单信号从未被单独回测**（预注册矩阵只含组合格），无法归因该 +0.52 来自基差还是组合交互；且 BTC 主变体全样本 net=−0.15（负），不构成可交易增量。**实质结论不变：|ρ|≥0.3 → 组合无统计意义上的增量信息**（P2 2/3 市场直接成立，第 3 个市场证据不足而非反证）。

## 4. 结论

1. **F7 FAIL（3/3 市场，P3 判据：任一 gate 不过 = 负结果）**：funding+basis 组合在 60 格检验中无一通过全部 8 gate。与 F6（单信号三市场 FAIL）方向一致：**两个公开时间戳信号的线性组合仍无 point-in-time 可验证的稳定超额收益**。
2. **机制**：funding 与 basis 相关系数 −0.30~−0.39（空头拥挤时 funding 为正、basis 为负，经济上同源——多头付费维持仓位压低永续价格），信息冗余度高，组合无法提供正交增量。
3. **亮点（不升级）**：SOL bull×T1×B10×2021（t=3.27, p=0.0025, trades=117, net=+3.63）——比 F6 单信号同格（trades=17）交易数达标且 net 更高，但 p 未达 0.001 硬线 + 单格不构成跨窗口一致性 → 仍为 post-hoc 观察。若下轮要追，需新预注册 + 新数据，禁止 in-sample 调参。
4. **多重检验诚实性**：本轮 N=60/市场；全局 trial count 累计 S1(45)+F6(90)+F7(180)=315，若按全局重算 DSR/BH-FDR 门槛更高，结论只会更 FAIL 不翻转。
5. **下一步（对齐 TASKS）**：F7 判定落定 → 候选路径 (a) 链上指标/期权 skew 等真正正交信号源 (b) 非线性组合（交互项/门控）(c) 接受负结果收束项目。F8 策略层维持阻塞（依赖显著信号）。

## 锚点

- 复跑: `cd stages/05/r3 && /opt/homebrew/bin/python3 scripts/run_f7.py`（~90s 幂等）
- checksum: r2 cache 136 ok / funding 136 ok（meta.checksums）
- 数据范围: merged BTC/ETH 2192 天、SOL 1913 天（2020-01→2025-12）；funding rows 7395/6576/5881
- 时间: 2026-11-01 ~02:07 +0800
