# 金融 D1 综合收口报告：Crypto 日频信号探索（F 系列全量）

> origin: ai · 2026-11-02 · 汇总 F1-F10 + 数据源调研全部结果
> 状态：CLOSED — 所有预注册实验完成，无剩余可执行方向（免费数据约束下）

## 一句话总结

**在免费公开数据约束下，crypto 市场不存在可交易的日频统计套利/择时信号。** 8 个独立假设全部 FAIL 或条件性弱正，且失败模式高度一致：信号要么冗余（同一因子的不同表达），要么方向反了（动量延续而非超调回归），要么幅度不够覆盖交易成本。

## 全量结果表

| 编号 | 假设/信号 | 数据 | 判定 | 核心发现 |
|------|-----------|------|------|----------|
| S1/F1-F8 | Funding rate 方向性择时（8 判据） | Binance Vision 2020-2026, BTC/ETH/SOL | **FAIL** (8/8) | DSR deflated Sharpe = -4.87, p=5.5e-07。资金费率不携带可交易的方向信息 |
| F7 | 现货-期货基差方向信号 | OKX 现货 + Binance 期货 | **FAIL** (三市场全灭) | P3 成立：部分通过 = 负结果。基差与 funding rate 信息冗余 (ρ=-0.30~-0.39) |
| F8 (r4) | Deribit DVOL 波动率择时 | Deribit API 2022-2025 | **FAIL** (CLOSED negative) | DVOL 作为方向/仓位管理信号不成立 |
| F9 | 跨所/跨币 funding arb | Binance vs OKX, BTC vs ETH | **FAIL** (CLOSED conditional) | 跨所价差 <0.01% 噪声级；同所跨币 2020-21 有信号但 2022 后收敛到不可交易 |
| F10 (r6) | 新套利空间预测规则 (R1/R2) | Binance+Bybit 2022-2025 | **FAIL** (negative + mechanism) | R1 DVOL 流动性真空 / R2 funding+OI 级联 全部 FAIL。方向翻转后胜率 70-87% → 市场是动量延续不是超调回归 |
| F10-R4 (r7) | 条件带宽预测 (logistic) | r6 cache, walk-forward | **FAIL** (主 PASS 次 FAIL) | 校准微增 (Brier Δ0.002-0.011) 但方向正确率 13-15%（远低于 50%）。触发命中率仅比基线高 15pp |
| F8-survey | 正交信号源可得性 | 7 个数据源实测 | **负面结论** | 免费+PIT+2020-2026 约束下无正交日频信号。TVL ρ=0.43 冗余；IV/OI/链上流/稳定币均无免费历史 |

## 关键机制发现（负结果中的正产出）

### 1. 动量延续 > 超调回归（F10-R6）

我们假设"结构冲击后价格会超调然后回归"，实测恰恰相反：冲击后 4h-24h 窗口内价格**继续朝冲击方向走**。方向翻转后三币种 × 两规则胜率 70-87%，跨年度稳定。

**含义**：如果要做 crypto 日内策略，应该做动量跟随而不是均值回归。但这超出了本项目"统计套利"的框架，属于趋势跟踪范畴。

### 2. 免费信息高度同源（F7 + F8-survey）

Funding rate、基差、TVL、OI 变化——这些看起来不同的指标，本质上是同一个"市场杠杆拥挤度"因子的不同投影。它们之间的相关系数 0.3-0.5，偏相关（控制价格后）降到 0.2 以下但方差解释力也几乎为零（R²<0.01），意味着它们共享的是极慢的结构性周期，不是日频可交易信息。

**含义**：要找到真正正交的信号，需要（a）付费链上数据（Glassnode/CryptoQuant 的 exchange netflow、active addresses），或（b）期权隐含波动率（forward-looking，与 backward-looking 的 funding 理论上正交），或（c）微观结构数据（order book imbalance、trade flow toxicity）——后两者需要 Level 2 数据订阅。

### 3. 信号衰减的时间尺度（F9）

BTC vs ETH funding spread 在 2020-2021（牛市、高波动、低效率）有可交易信号，2022 后（熊市→复苏、做市商进场、效率提升）收敛到 <0.01%。

**含义**：crypto 市场的定价效率在快速提升。即使曾经有效的信号也在以年为单位衰减。这跟传统金融的"alpha decay"一致，只是速度快了一个数量级。

## 项目状态判定

### 已完成
- ✅ 数据基础设施（Binance Vision ingest, PIT 自检 8/8 PASS）
- ✅ 8 个独立假设的预注册 + 回测 + 报告
- ✅ 数据源穷尽调研（7 个方向）
- ✅ 机制发现（动量延续、信息同源、信号衰减）

### 不再继续（理由）
- ❌ 更多免费数据组合 → F8-survey 已证明无正交信号
- ❌ 更复杂的 ML 模型 → 信号本身不存在，模型复杂度不能创造信息
- ❌ 更高频（分钟级）→ 需要 Level 2 数据 + 低延迟基础设施，超出当前资源

### 如果要继续（需要新资源）
1. **Deribit IV 采集器**（零成本，时间成本）：从今天开始每天拉一次 option book，3 个月后有 90 天 IV 数据可做初步验证。这是唯一确认理论上正交的信号。
2. **Glassnode free tier**（5 分钟注册）：exchange_netflow 等链上指标，但只有 90 天历史，不够回测，只能做实时监控。
3. **转向动量策略**（框架变更）：F10 的机制发现暗示动量跟随可能有效，但这需要重新立项（不再是"统计套利"而是"趋势跟踪"），且需要处理过拟合风险（我们是在看到负结果后才想到翻转方向的）。

## 文件索引

| 文件 | 内容 |
|------|------|
| `loop-artifacts/stages/04/r1/t06-signal-backtest-report.md` | S1 funding rate 8 判据回测 |
| `loop-artifacts/stages/05/r3/f7_report.md` | F7 基差方向信号 |
| `loop-artifacts/stages/05/r4/f8_report.md` | F8 DVOL 择时 |
| `loop-artifacts/stages/05/r5/f9_report.md` | F9 funding arb |
| `loop-artifacts/stages/05/r6/f10_report.md` | F10 新套利规则 |
| `loop-artifacts/stages/05/r7/f10-r4-report.md` | F10-R4 条件带宽 |
| `loop-artifacts/stages/exploration/r7-f8-data-survey/research-results.md` | 数据源穷尽调研 + TVL 正交性检验 |

## 置信度

- "免费数据下无正交日频信号"：**conf 0.85**（7 个方向穷尽，但可能有我没想到的数据源）
- "动量延续 > 超调回归"：**conf 0.70**（样本内方向翻转验证，但未做独立的 OOS 预注册确认）
- "信号以年为单位衰减"：**conf 0.60**（只有 F9 一个数据点支持，n=1）