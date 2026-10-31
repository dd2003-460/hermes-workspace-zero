# F8 初步结果: DVOL 单因子 — 方向信号 FAIL, 仓位管理信号有效
# origin: ai (2026-11-01)

## 数据
- Deribit BTC DVOL 日线: 1334 行, 2022-04-08 ~ 2025-12-01, 无缺口
- BTCUSDT 日线: Binance vision bulk, 重叠期 1364 天
- 文件: loop-artifacts/stages/05/r4/data/dvol_daily.json

## P1 检验: corr(DVOL_change_1d, next_day_ret)
- 结果: +0.0477 (n=1333), p≈0.22 不显著
- 预测 < -0.05 → **FAIL**（方向反了，弱正相关）

## P2 检验: LOW DVOL z<=-1.5 → 5d forward return
- n=20 panic days, avg 5d = -2.01%, bench = +0.47%, excess = -2.49%
- 预测 > +0.5% → **FAIL**（方向完全反了：低波动后继续跌）

## P3 检验: HIGH DVOL z>=+1.5 SHORT 全 horizon
- 1d/3d/5d/10d t 值全部在 ±0.16 以内, win_rate 46-51%
- |t|>2: **NO** → **FAIL**

## 意外发现: vol-of-vol 效应
- HIGH 组 5d ret std = 6.60% vs LOW 组 4.56%, 比值 1.45x
- DVOL 不是方向信号, 是**仓位管理信号**: 高波动日砍仓到 ~70%
- 这个可以跟 F8 策略层（仓位管理）对接, 但单独不构成 alpha

## 结论
DVOL 单因子作为择时/方向信号在当前数据上**不成立**。
期权维度路线需要换角度: 
1. 用 IV skew (25Δ call-put spread) 而非 DVOL 水平 → 需要历史 skew 数据 (Deribit archive?)
2. 用 DVOL 做 position sizing filter + 另一个方向信号组合
3. 放弃期权维度, 转候选 C (宏观 regime) 或 D (收束报告)

## 下一步决策点
B2 阻塞更新: F8 预注册的 P1/P2/P3 全部 FAIL, 按预注册失败降级条款:
- 选项 A: 找 Deribit 历史 skew 数据 (2019 起 S3 archive), 重跑 skew 信号
- 选项 B: DVOL 降级为 sizing filter, 配合 funding 信号做组合 (但 funding 已闭合负结果)
- 选项 C: 时间戳微观结构路线彻底闭合, 转宏观/跨资产
- 选项 D: 项目收束, 整理 S1/F6/F7/F8 负结果为研究原型报告

## 补充: 10d horizon + sizing 模拟 (2026-11-01)

### HIGH DVOL z>=+1.5 SHORT 10d
- n=104, avg=-0.013%, t=-0.020, win_rate(short)=46.2%
- 完全不显著。高波动后 BTC 没有下跌倾向。

### Sizing 模拟 (z>=1.5 → 0.7x position)
- Sized total: +281.73% vs Buy-hold: +265.27% (overlap period)
- 多赚 ~16pp 是 beta 衰减效应, 不是 alpha, 无统计意义

### 最终判定
**DVOL 单因子 REJECTED。** 方向信号全 horizon 无效, 仓位管理信号无超额。
期权维度路线需要 IV skew (25Δ spread) 而非 DVOL 水平。
Deribit live API 无法获取历史 skew, 需找 S3 archive 或放弃此路线。

## 五分位 + Walk-Forward (2026-11-01)

### DVOL Quintile vs 5d Forward Return (full sample)
| Q | Range | n | avg_fwd5 | t |
|---|-------|---|----------|---|
| Q1 | [0,43.6] | 257 | +0.448% | 1.59 |
| Q2 | (43.6,51.7] | 270 | +0.918% | 2.37 |
| Q3 | (51.7,57.4] | 304 | +0.680% | 2.06 |
| Q4 | (57.4,66.4] | 260 | +0.896% | 2.42 |
| Q5 | (66.4,inf) | 243 | -0.698% | -1.59 |

U-shape: low and high DVOL diverge, middle all positive. Not monotonic.

### Walk-Forward (Q5 = top 20% per period)
| Period | thresh | n | avg_fwd5 | t |
|--------|--------|---|----------|---|
| 2022-2023 | 82.5 | 52 | -0.436% | -0.487 |
| 2023-2024 | 57.9 | 69 | +2.314% | 3.341 |
| 2024-2025 | 59.7 | 128 | +0.885% | 1.689 |

**UNSTABLE**: sign flips in 2022-2023, strength varies 5x across periods.
Fails pre-registered stability criterion (cross-window consistency >= 3/4).

### Final Verdict for DVOL factor
REJECTED as directional signal. REJECTED as stable sizing filter.
The U-shape is likely regime-dependent artifact, not exploitable edge.
