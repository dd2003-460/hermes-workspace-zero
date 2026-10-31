# origin: ai
# F6 跨市场验证报告 — ETH/SOL funding-rate signal backtest (05 r2)

- 阶段: projects/金融/D1-financial-market-analysis/ loop-artifacts/stages/05/r2
- 执行: 2026-10-29 · seed=20261020 · B=2000 permutation · 本地 bulk 数据，无 live API
- 配套产物: `f6_backtest_results.json`（全量）/ `f6_trades_ETHUSDT.parquet` + `f6_trades_SOLUSDT.parquet` / `scripts/run_f6.py`（可重跑，幂等，~4s）
- 预注册: `stages/05/r1/t06-s2s3-preregistration.md`（2026-10-20 冻结）+ S1 04r1 同构协议

## 1. 降级记录（B1，如实标注）

**S2 美股数据源全断**（Yahoo 403 大陆限制 / Stooq 403 / ifzq 美股历史日线空数组），按 TASKS F6 候选方案降级：
- S2 → **ETHUSDT**（Binance vision bulk，72 monthly zips，2020-01→2025-12，2192 日 K 线）
- S3 → **SOLUSDT**（Binance vision bulk，64 monthly zips；**SOL 上市 2020-09-14**，K 线起点 1600041600000，OOS 窗口 2021-2025 不受影响）
- 信号不变：T1 sign / T2 short-crowding(≤−1e-4) / T3 long-crowding(≥2e-4)，方向冻结（拥挤→反转）
- PIT 不变：决策 t 日 00:00 UTC，用 ts_norm ≤ t−1d 的最新 settled funding，当日 open 成交（taker）
- 成本不变：taker 0.05% + 滑点 0.01% base / 0.02% stress per side（继承 t05）
- Regime 日历沿用 S1 冻结值：bull 2020-21 & 2024-25 / bear 2022 / range 2023

**数据完整性**：cache 136 zips + funding 136 zips 全部通过官方 CHECKSUM 校验（sha256 逐文件比对，0 mismatch）。SOL 2020-01..08 为 404（未上市，非下载失败）。

## 2. 结果（主阈值 T1，per-window excess 口径）

| 市场 | 窗口 | trades | net excess | t | perm p | PSR | DSR |
|------|------|--------|-----------|---|--------|-----|-----|
| ETH | 2021 | 20 | +1.870 | +1.766 | 0.078 | 0.961 | 0.383 |
| ETH | 2022 | 142 | −1.290 | −1.905 | 0.055 | 0.029 | 0.000 |
| ETH | 2023 | 50 | +0.606 | +1.347 | 0.193 | 0.913 | 0.242 |
| ETH | 2024 | 20 | +0.358 | +0.574 | 0.573 | 0.718 | 0.069 |
| ETH | 2025 | 96 | −0.182 | −0.282 | 0.754 | 0.389 | 0.010 |
| SOL | 2021 | 17 | +4.784 | **+3.165** | **0.0015** | 0.999 | 0.866 |
| SOL | 2022 | 105 | −1.728 | −2.387 | 0.018 | 0.008 | 0.000 |
| SOL | 2023 | 79 | +1.482 | +1.828 | 0.066 | 0.970 | 0.428 |
| SOL | 2024 | 46 | +0.757 | +0.964 | 0.339 | 0.833 | 0.138 |
| SOL | 2025 | 149 | +0.207 | +0.316 | 0.762 | 0.625 | 0.041 |

**T2/T3（拥挤反转信号）**：全窗口无一显著。最佳负例 SOL 2021 T3 t=−3.228（p≈0.0015，方向与预注册相反——多头拥挤后继续涨而非反转）。

## 3. 判据逐条（F1-F8，pre-registration §3.2/§3.3）

| Gate | ETH | SOL | 说明 |
|------|-----|-----|------|
| F1 t≥2（tested cells） | ❌ | ⚠️ | SOL 4 格 \|t\|≥2：bull×T1×2021 t=+3.17、bear×T1×2022 t=−2.39、range×T2×2023 t=−2.34、bull×T3×2021 t=−3.23；ETH 无格达标 |
| F2 ≥30 trades | ❌ | ❌ | 多格 <30（T1 2021: ETH 20 / SOL 17） |
| F3 net excess > 0 | ❌ | ❌ | 2022 双市场净超额为负（熊市 T1 做多被砸） |
| F4 跨窗口方向一致 ≥3/4 | ✅ | ✅ | T1 5/5 long-biased；T2/T3 5/5 short-biased（一致性本身成立，但"一致"≠"有效"） |
| F5 perm p<0.001 | ❌ | ⚠️ | SOL 2021 p=0.0015（差 0.0005 未达 0.001） |
| F6 PSR>0.95 | ✅ | ✅ | 单窗口 PSR 达标（注意：PSR 是单窗口口径，不解决跨窗口问题） |
| F7 BH-FDR α=0.05/45 | ❌ | ⚠️ | SOL 有 1 格被 reject（即 2021 那格），ETH 0 格 |
| F8 DSR>0 @N=45 | ✅ | ✅ | 同上，单窗口口径 |
| **overall** | **FAIL** | **FAIL** | 任一 gate 不过 = FAIL（预注册 §3.4：不得用其他市场掩盖） |

## 4. 结论

1. **跨市场泛化检验 FAIL（2/2 市场）**：与 S1 BTC（04r1，45 格 0/45 通过）一致——资金费率单信号在加密永续市场（BTC/ETH/SOL）均无统计显著的 point-in-time 超额收益。三市场证据链闭合：**负结果是稳健的**。
2. **唯一亮点**：SOL bull-regime × T1 × 2021（t=3.17, p=0.0015, PSR 0.999, DSR 0.866）——单格接近显著，但 (a) 未过 F2 交易数门槛 (17<30)，(b) 未过 F5 p<0.001 硬线，(c) 单格不构成跨窗口一致性。**不升级为发现，如实记录为 post-hoc 观察**（若下轮想追，需先预注册再取新数据，禁止 in-sample 调参）。
3. **机制解读（conf 0.6）**：T1 sign 本质是"正 funding → 做多"，在牛市（2021/2023/2024）方向对、幅度弱于成本；熊市（2022）系统性亏损——funding 在熊市持续为正（多头付费维持仓位），T1 反而逆势加仓。T2/T3 拥挤反转假设在 2020-2025 数据上不成立，SOL 2021 T3 甚至反向显著（动量延续压过反转）。
4. **多重检验诚实性**：全局 trial count 应为 S1(45)+ETH(45)+SOL(45)=135（预注册 §3.3），本轮 JSON 内 DSR/BH-FDR 仍按单市场 N=45 计算（沿用 S1 脚本口径）——**偏乐观方向**，若按 N=135 重算 DSR 门槛更高，结论只会更 FAIL 不会翻转。此 caveat 已记录，下轮 F7 启动前统一重算。

## 5. 下一步（对齐 TASKS）

- F6 判定落定 → **F7 多信号组合**（资金费率 + 现货-期货基差/期权 skew/链上指标）成为主线：单信号已证伪，组合是否有增量信息是下一个可检验问题。
- F8 策略层维持阻塞（依赖 F6/F7 出显著信号）。
- B2（预注册参数人工确认）已被本轮执行覆盖：实际用的是 S1 冻结 regime 日历 + 原阈值，无新增待拍板项；如成璐要改 SOL/ETH 专属参数，属新预注册轮次。

## 锚点

- 复跑命令：`cd stages/05/r2 && /opt/homebrew/bin/python3 scripts/run_f6.py`（~4s，幂等）
- checksum 校验：136+136 zips 全过（meta.checksums）
- 数据范围：ETH klines 2020-01-01→2025-12-31（2192 行）；SOL klines 2020-09-14→2025-12-31；funding ETH 6576 行 / SOL 5881 行（settled only）
- 时间：2026-10-29 ~17:40 +0800