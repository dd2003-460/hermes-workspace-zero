# F10-R3 / B — 套利资本流动与均衡收敛速度

# origin: ai (成璐 F10-R3 调研任务书 2026-11-01) | 执行: arena agent mode | 观测日: 2026-11-01
# 子问题: 有人测量过套利空间从出现到消失的时间吗? 收敛速度由什么驱动(资本流入率/竞争者数量/交易成本)? 有无 capital inflow vs profit pool 的定量式?
# 交叉验证: 每结论 ≥2 独立团队, 明细见 receipts.json

## 1. 直接回答 (≤3 行)

有, 但测的是"价差回到阈值内的中位时间", 不是"空间全生命周期"; 量级从毫秒到年跨度 **~10 个数量级**(相邻市场间 3-5 个):
股票同标的跨场所 毫秒-秒 → 加密 CEX 跨所 分钟-小时(无管制)/天-周(有管制) → 可转债等场外 月-年 → 学术异象 年。
驱动排序: **资本到位延迟(融资/托管/合规) > 竞争资本量 > 交易成本**; "capital inflow vs profit pool" 在理论上是负反馈稳态(有闭式), **没有跨市场可校准的经验公式**。

## 2. 证据列表 (7 篇实证/理论, 带跨市场量级对比)

### B1 · Duffie (2010) Asset Price Dynamics with Slow-Moving Capital — J. Finance 65(4):1237-1267
- 核心: 资本到位延迟从"电子订单簿的零点几秒"到"巨灾保险的几个月"; 冲击后价格 = 尖峰 + **更长**的回复, 回复形态可反推资本不流动性。
- 可迁移: 永续的"资本"= 保证金 + 对冲现货; 到位延迟 = 跨所划转(分钟)到链上确认(小时)。([1])
- 迁移判定: ✅ 直接适用, 且给了"用回复形态反推资本延迟"的方法 — 我们可用 basis 回复曲线估。

### B2 · Gromb & Vayanos (2010, ARFE 2:251-275; 2018, J. Finance "The Dynamics of Financially Constrained Arbitrage")
- 核心公式(定性): spread 对套利资本 W **单调递减**; dW/dt 由利润 Π(W) 减消费率 β 决定, 收敛到稳态 W*; **"time to convergence" u_n 是内生变量** — 基本面波动大或 u_n 长的机会, spread 更大、套利者减仓更多。这就是任务书问的 "capital inflow vs profit pool" 关系, 但它是**负反馈稳态**不是线性公式。([2][3])
- 迁移判定: ⚠️ 部分 — 结构可借(u_n 做状态变量), 但 u_n 不可从公开数据识别。

### B3 · Mitchell & Pulvino (2012) Arbitrage Crashes and the Speed of Capital — JFE 104(3):469-490
- 核心: 2008 可转债, **即时变现成本 >10%**(极端 >13%); 资本到位以"月"计, 套利者从流动性提供者变成需求者, 市场错价持续数月。([4])
- 迁移判定: ❌ 不适用 — 我们的腿(永续)是流动的; 但它给出收敛上界由**最不流动的那条腿**决定这条原则。

### B4 · Makarov & Schoar (2020) Trading and Arbitrage in Cryptocurrency Markets — JFE 135(2):293-319
- 核心: 34 所 19 国 tick 数据; 跨所偏离持续**数小时到数天/数周**; 跨国 > 同国(韩溢价均值 <15%, 峰值 40%); 共同成分子解释 5min/hour 收益 ~50%、日 ~85%; 买 1 万 BTC 使 5min 收益 +4%、hourly +6%。([5])
- 迁移判定: ✅ 我们的基线 — 加密的收敛尺度本身就是"小时-周", 与股票差 3-4 个数量级。

### B5 · 稳定币与跨境整合 (2025, Economics Letters 类): 泡菜溢价 VECM
- 核心: BTC 与 USDT 溢价偏离的半衰期 ≈ **24 分钟**(每 interval 调整 12.61% / 12.83%), 共整系数 [1, −0.992]。([6])
- 意义: 稳定币通道把"周级"收敛压到"分钟级" — **收敛速度本身在结构性地变快**, 这是 F9 "旧空间在关闭"的机制解释。
- 迁移判定: ✅ 直接可测 — 我们可对 spot/perp 溢价做同样 VECM 估半衰期。

### B6 · McLean & Pontiff (2016) Does Academic Research Destroy Stock Return Predictability? — J. Finance 71(1):5-32
- 核心: 97 个横截面预测因子, 样本外 **-26%**, 发表后 **-58%**(差 32% 归因于发表后资本涌入); 低流动性/高特质风险组合衰减更大。([7])
- 迁移判定: ⚠️ 时间尺度是**年**, 与 B4/B5 差 5 个数量级 — 因为一个是"信息扩散+资本重配", 一个是"同资产跨场所搬运"。

### B7 · (补充) Falck, Rej & Thesmar (2022) When do systematic strategies decay? — Quant. Finance 22(11):1955-1969
- 核心: 发表异象在样本外平均只保留 **约 50%** 样本内表现 → 与 B6 的 -58% 互相印证(不同作者/样本)。([8])

### 跨市场收敛时间量级表

| 市场 / 空间类型 | 收敛时间 | 来源 |
|---|---|---|
| 股票同标的跨场所 | 毫秒-秒 | B1(制度描述) |
| 加密 CEX 跨所(无资本管制) | 分钟-小时 | B4 |
| 加密 稳定币通道跨境 | 中位 **24 分钟**半衰期 | B5 |
| 加密 CEX 跨所(有资本管制) | 天-周 | B4 |
| 可转债/场外错价 | 月-年 | B3 |
| 学术异象(横截面因子) | 年(发表后 -58%) | B6 / B7 |

## 3. 对 F10 模型设计的启示 (≤5 行)

1. **收敛速度写成状态依赖**: k(s) = 1/资本到位延迟; 用 basis/溢价 VECM 半衰期**实时估计**(8h funding 结算天然给离散观测点)。
2. **H2 需要可测的"资本流入"代理**: 用 名义敞口增量(ΔOI×杠杆) 而非资金流 — 交易所净流入只有部分可得且 PIT 差。
3. **选对空间类型**: 只有"同资产跨场所/跨期限"(分钟-小时级)落在可交易窗口内; 跨资产的"新逻辑"是年级, 不可交易。
4. **用衰减曲线做空间寿命先验**: B6/B7 的"样本外保留 ~50%、发表后 -58%"与 F9 的 p95 spread 0.056%→0.01%(5 年 ~5.6x)量级一致, 可作 F10 的先验。
5. **负反馈稳态 ⇒ 观测即衰减**: 一旦某空间收益被观测到, 它已在衰减 — "已实现收益"应直接进拥挤项, 不应再当 alpha。

## 4. 未解决 / 矛盾点 (诚实标注)

- **矛盾① 冲击后方向(conf 0.40)**: B1 说尖峰后**部分回复**; B4 说升值时跨所偏离**同向扩大**(co-move and open up); F10-R1/R2 实测是**动量延续**。"回归"只在资本可无摩擦搬运的场所成立, 而保证金/强平机制把永续变成了反方向放大器。
- **矛盾② 收敛速度的时代差异(conf 0.60, 判为时变而非矛盾)**: B4(2017-2019)的"数天-数周" vs B5(2025)的"24 分钟"。稳定币通道+做市商专业化把收敛压缩了 2-3 个数量级 → 收敛速度在**变快**, 意味着任何"空间时长"先验都会过期, 必须滚动重估。
- **空白(conf 0.30)**: 无任何论文测量过 **永续-永续跨所**套利时长(现有只测 spot 跨所); 无跨市场可校准的 k(capital inflow) 闭式; B2 的 u_n 不可从公开数据识别。
- **方法学风险(conf 0.50)**: B5 与 B7 的关键数字来自摘要/二手转述, 未直核原文表格; B3 的 16.8% 类数字(见 D)同此。
- **结论**: "收敛速度可测量、且由资本到位延迟主导"有 **B1+B2(理论) + B3+B4+B5(实证)** ≥2 独立来源支持, conf 0.75; "存在可用公式"则**不支持**, conf 0.2。

---
URLs (观测 2026-11-01):
[1] https://www.darrellduffie.com/uploads/1/4/8/0/148007615/duffieafapresidentialaddress2010.pdf
[2] https://www.fmg.ac.uk/publications/discussion-papers/limits-arbitrage-state-theory
[3] https://personal.lse.ac.uk/vayanos/Papers/DFCA_JF18.pdf
[4] https://www.cambridge.org/core/services/aop-cambridge-core/content/view/F6DE9274FD97DE3DB142D9B5327BB353/S0022109023000583a.pdf/convertible-debt-arbitrage-crashes-revisited.pdf
[5] http://eprints.lse.ac.uk/100409/
[6] https://www.sciencedirect.com/science/article/abs/pii/S0165176525005415
[7] https://onlinelibrary.wiley.com/doi/abs/10.1111/jofi.12365
[8] https://dspace.mit.edu/entities/publication/e48d406c-5c40-4607-9924-72484366411b
