# F8 最终报告: DVOL 单因子 REJECTED
# origin: ai (2026-11-01)
日期: 2026-11-01 | 状态: CLOSED (negative result)

## 一句话结论
Deribit BTC DVOL（波动率指数）作为方向性择时信号或稳定仓位管理信号，在 2022-2025 数据上**不成立**。

## 检验汇总
| 检验 | 预测 | 实际 | 判定 |
|------|------|------|------|
| P1: corr(DVOL_chg, next_ret) < -0.05 | 负相关 | +0.048 (p=0.22) | FAIL |
| P2: LOW z<=-1.5 → 5d excess > +0.5% | 正超额 | -2.49% (n=20) | FAIL |
| P3: HIGH z>=+1.5 SHORT 过 8 gate | t>=2 | t=-0.02~0.16 | FAIL |
| Walk-forward Q5 stability | 跨期一致 | 符号翻转+强度5x差异 | FAIL |

## 人话解释
DVOL 是 Deribit 算的"BTC 恐惧指数"——期权市场里大家愿意花多少钱买保险。直觉上恐慌时应该抄底（反弹），但数据说：恐慌后 BTC 该跌还跌，该涨还涨，DVOL 水平跟未来 5 天涨跌基本没关系。
唯一有点用的地方：高 DVOL 日子的后续波动确实更大（1.45x），但这只是"该少拿点仓"的风险管理提示，不是赚钱信号。而且这个效应跨期不稳定，2022 年反号了。

## 为什么失败（我的判断）
1. **信息已被定价**：DVOL 是公开数据，所有做市商和量化基金都在看，任何可交易的 edge 早被套利掉了。
2. **加密市场效率高于预期**：BTC 日线级别的价格发现比 A 股快得多，慢变量（波动率水平）没有预测力。
3. **样本窗口偏短**：3.7 年只覆盖了一个完整牛熊周期，regime 切换时信号方向会翻转。

## 对项目的意义
时间戳微观结构路线（funding rate → basis → IV level）三条腿全部走不通：
- F6: funding 单信号 3 市场 0/135 通过
- F7: funding+基差同源无增量, 3 市场全 FAIL
- F8: DVOL 方向信号全 horizon 无效, walk-forward 不稳定

下一步只能换维度：
- 候选 C: 宏观/跨资产（美债收益率、美元流动性）作为 regime 增强
- 候选 D: 项目收束，把 S1/F6/F7/F8 负结果整理成研究原型报告

## 文件索引
- 预注册: loop-artifacts/stages/05/r4/f8-preregistration.md
- 初步结果: loop-artifacts/stages/05/r4/f8_preliminary_results.md
- DVOL 数据: loop-artifacts/stages/05/r4/data/dvol_daily.json (1334 rows)
