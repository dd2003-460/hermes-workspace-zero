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
