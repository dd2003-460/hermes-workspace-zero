# F10-R3 / A — 异质主体市场微观结构模型

# origin: ai (成璐 F10-R3 调研任务书 2026-11-01) | 执行: arena agent mode | 观测日: 2026-11-01
# 子问题: 学术上用什么模型描述不同类型交易者(HFT/统计套利/趋势/散户/机构)的交互? 哪些能预测偏离的出现位置和持续时间?
# 交叉验证: 每结论 ≥2 独立团队, 明细见同目录 receipts.json

## 1. 直接回答 (≤3 行)

模型谱系成熟(生态选择 / 自适应信念 / 订单簿 ABM / 动理学 四支), 但**没有一支能预测"偏离出现在哪个价位、持续多久"**。
它们能预测的是**条件与形状**: 利润-资本倒 U(carrying capacity)、冲击的 √Q 律、以及"谁吃谁"随财富状态变化的捕食矩阵。
把 A 类模型直接当点位/时长预测器用 = 重走 F10-R1/R2 的失败路径。

## 2. 证据列表 (7 个代表性模型)

### A1 · Farmer (2002) Market Force, Ecology and Evolution — Industrial and Corporate Change 11(5):895-953
- 假设/分类: 线性市场冲击; 策略资本 c_i 按利润复利; 非对称增益矩阵 G_ij(能"预判"他人者赚, 与他人同质者亏)。**按策略分而非按机构分**(value / trend(lag θ) / noise)。
- 可预测: 利润对资本呈**倒 U**, 顶点 = carrying capacity; 单主体利润最大化只把既有 pattern **削掉约一半**; "走向有效的时间尺度是年—十年"。([1])
- 局限 / 对我们最有用: 无订单簿/无 queue; G 不可从公开数据识别。"套利空间"当**资源**、"资金"当**种群**; "新空间涌现" = 入侵(invasion)条件(新策略在小资本下能否正利润), 而不是偏离回归。

### A2 · Brock & Hommes (1998) Heterogeneous beliefs and routes to chaos — JEDC 22(8-9):1235-1274
- 假设/分类: 基本面派 vs 图表派两类以上信念, 按过去 fitness 用 logit 切换, 切换强度 = 选择强度 β。
- 可预测: β 增大 → 分叉 → 混沌; 即"稳定 ↔ 暴涨暴跌"的**相变点**, 是少数有解析边界的结论。([2])
- 局限 / 对我们最有用: 价格由超额需求映射直接给定, 无订单簿; β 不可直接观测。成璐的"温度"不需要新概念 — **β 就是温度**(异质度/切换强度), 可用策略收益离散度或资金费离散度代理。

### A3 · Scholl, Calinescu & Farmer (2021) How market ecology explains market malfunction — PNAS 118(26):e2015574118
- 假设/分类: value / trend / noise 三类; 收益对**整个财富向量**密度依赖; 用生态学 community matrix + 食物网营养级刻画"谁吃谁"。
- 可预测: 捕食关系**随财富分布变化** — 效率均衡处三者互惠(mutualistic), 偏离处出现捕食甚至同类相食; 系统长期停留在非有效状态。([3])
- 局限 / 对我们最有用: 玩具模型(1 股 1 债), 未校准真实市场; 作者含 Farmer, 与 A1 同源。"谁吃谁"不是固定食物链而是**状态依赖矩阵**; F10 应输出 M(状态) 而不是"聪明钱 vs 散户"的静态标签。

### A4 · Sueshige, Kanazawa, Takayasu & Takayasu (2018) Ecology of trading strategies in a forex market — PLOS ONE 13(12):e0208332
- 假设/分类: 实证派 — EBS USD/JPY 一周个体交易者数据, 按"对历史价格的响应模式"聚类 limit / market 策略, 做成 4×5 生态矩阵。
- 可预测: 流动性消费者的 Sharpe 与"流动性消费概率" Spearman **0.54**; HFT 与 LFT 都赚钱但机制不同(降风险 vs 承担风险)。([4])
- 局限 / 对我们最有用: 一周、一个货币对、无时间序列预测能力。**taker/maker 角色可从成交数据直接分类**(Binance aggTrades 有 `is_buyer_maker` 字段) → 加密永续的捕食矩阵是"今天就能实现"的截面特征, 不需要 ORATS 级数据。

### A5 · Cordier, Pareschi & Toscani (2005) On a kinetic model for a simple market economy — J. Stat. Phys. 120:253-277 (+ Pareschi & Toscani 2014, arXiv:1401.4550)
- 假设/分类: 二体碰撞式交易(储蓄倾向 + 随机风险), Fokker-Planck 极限给出 Pareto 尾稳态; 2014 版加入"知识/信息异质性"作为温度参数。([5][6])
- 可预测: 稳态**分布形状**(尾部指数), 不是路径; 知识异质性增大 → 富人阶层出现、不平等上升。
- 局限 / 对我们最有用: 无价格、无 alpha、无套利; 只描述财富分布的均衡态。成璐的"气体动理论"在文献里**已有严格形式**, 但全部止步于财富分布, **没人把碰撞接到"价格偏离的产生"上** — 这是 F10 的真空, 也是最大的可识别性风险。

### A6 · ABM-LOB 现代版: arXiv:2607.04280 (2026-07) + arXiv:2510.27334 (2025-10-31)
- 假设/分类: 四类主体(机构 metaorder / HFT 做市 / 散户 / 流动性), 最小 LOB 反事实消融; 另一篇用 RL 做市商 vs 中频 metaorder 复现逆向选择。([7][8])
- 可预测: 冲击律**形状** — 模型 ⟨δ⟩=0.539 vs 东交所实测 0.489(√Q 律), 以及"撤单/补单到底是谁在推动"的因果归因。
- 局限: 校准到 stylized facts, 参数不可从公开数据反推; 无跨资产。
- 对我们最有用: √Q 律是把"资金压力"折算成"价格位移"的唯一现成公式 — 这是 F10 的"压强 → 体积"换算层。

### A7 · Tóth, Lempérière, Deremble, de Lataillade, Kockelkoren & Bouchaud (2011) Anomalous price impact and the critical nature of liquidity — Phys. Rev. X 1:021006 (arXiv v1 2009-01, v3 2011-11) · 团队 Bouchaud/CFM, 与 Farmer/Hommes/Takayasu/Pareschi-Toscani/Jafree-Firoozye 无共同作者 ([9])
- 假设/分类: **不按主体类型分类**, 而按"潜在流动性(latent order book)"分类 — 平均供给/需求剖面呈 V 形且在现价处**趋于消失**; 分类维度是"距现价的流动性密度", 不是"谁在交易"。
- 可预测(只给形状): 局部流动性趋零 ⇒ 线性响应失效 ⇒ 必然 **√Q 冲击律**(Δp ∝ σ√(Q/V)); 大 metaorder 必须切片 ⇒ 订单流符号**长记忆**; 二者用最小 order-flow 模型数值复现。无任何单事件位移/持续时间的点预测主张。
- 局限 / 对我们最有用: 无"谁吃谁"矩阵、冲击律只是平均曲线, 潜在密度不可从公开逐笔数据反演; 但它是 A6 所引 √Q 的**原始出处+解析推导**, 且"局部流动性趋零"直接判定**任何按 ATR 线性缩放的止损宽度在结构上就是错的**(R2 止损 80-84% 被扫的数学原因), 提供仅需 σ 与 Q/V 的"压强→位移"换算层。
- 候选替换: 任务卡列 "Challet & Bouchaud (trader ecology)" **未检索到联合署名文献**(Challet 的订单簿 ABM 合作者是 Stinchcombe), 故改用可双路核验(arXiv 摘要页 + PRX DOI)的 CFM/Bouchaud 组论文, 未虚构出处。

## 3. 对 F10 模型设计的启示 (≤5 行)

1. **加状态变量 c_s(策略资本) + 倒 U 关系**: "套利空间"的量纲是资源量不是价格量; 代理用 名义敞口(ΔOI×杠杆) 与 策略篮收益协方差。
2. **温度 = β**: 用策略收益离散度 / 资金费离散度 / ATR 三件套, 不另造新参数(可直接接 F10-R1 的 DVOL 触发口径)。
3. **压强 → 位移用 √Q 律**: Δp = Y·σ·√(Q/V), 替换现在 ATR 标定的止损宽度(这正是 R2 止损 80-84% 被扫的病根)。
4. **捕食矩阵 M(t)**: aggTrades 的 taker/maker 分类 + 策略篮收益滚动协方差估 M; 看 M 的谱半径与特征向量 = "谁在吃谁"的扩张方向。
5. **放弃点位/时长预测**, 改为预测条件带宽 — F10-R1 已实测 60% 触发后 4h 内 |ret|>2σ, 这个"可预测性"是分布级的, 不是路径级的。

## 4. 未解决 / 矛盾点 (诚实标注)

- **矛盾①(conf 0.45)**: A1 说单主体最优化只削掉一半 pattern(偏离**长期存在**), A3 说系统趋近有效但**很慢**, 而实证 McLean-Pontiff 显示发表后几年内就衰减 58%。三者"收敛速度"差 1-2 个数量级, 无法统一。
- **矛盾②(conf 0.50)**: A2 认为异质度↑ → 不稳定(混沌); 生态文献(A1/A3)认为多样性 → 市场更有效/更稳。β 高到底是"过热"还是"稳定", 两种叙事不能同时成立, 我们暂取"β 高 = 过热"(与 F10-R1 实测一致)。
- **矛盾③(conf 0.55)**: A4 的"流动性消费者跑赢提供者"(Spearman 0.54) 与 A1/A3 的"套利资本积累终将抹平收益"方向相反 — 前者是截面快照, 后者是动态; 我判为时间尺度不同而非真矛盾, 但未验证。
- **空白(conf 0.30)**: 无任何模型给出 out-of-sample 的"偏离位置/持续时间"点预测; A3 是玩具模型, A4 只有一周一个货币对。
- **可识别性(conf 0.30)**: c_s 不可从公开数据观测 → 倒 U 能标定**形状**不能标定**位置**; 这是 F10 框架最大风险。
- **矛盾④(conf 0.40, 新增)**: A7 表明"只用潜在流动性密度 + 订单流"、**完全不区分主体类型**就能推出 √Q 律与长记忆; 而 A1/A3 主张必须用"策略资本/捕食矩阵"才能解释 malfanction。二者不必然冲突(一个解释冲击形状, 一个解释长期有效性), 但 A7 确实压缩了"必须建主体异质性"的必要性认定空间 → F10 的 M(t)/c_s 若无法给出 A7 之外的增量预测力, 应降级为可选层。
- **独立性说明**: A1 与 A3 同为 Farmer 团队, 只算一条独立证据线; A2(Brock/Hommes) / A4(Takayasu) / A6(Jafree-Firoozye) / **A7(Tóth-Bouchaud, 2011-11 发表)** 为四条独立线 → A 子领域"生态/动力学框架可行但不可作点位/时长预测器"这一结论有 **5 条**独立来源支持。计数口径: 仅计"结论直接支撑 A-C1 且至少一个可核验来源(DOI 或机构页)"的团队; A5(Pareschi/Toscani) 只支撑财富分布形状、不支撑 A-C1, **仍不计入**线数(保守口径, 不虚增)。

---
URLs (观测 2026-11-01):
[1] https://oms-inet.files.svdcdn.com/production/files/marketforce.pdf · https://ora.ox.ac.uk/objects/uuid:98f268e7-cfd3-4597-a39c-c38963f06503
[2] https://doi.org/10.1016/S0165-1889(98)00011-6 · https://ideas.repec.org/p/ams/ndfwpp/01-05.html
[3] https://pmc.ncbi.nlm.nih.gov/articles/PMC8256038/
[4] https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0208332
[5] https://www.researchgate.net/publication/5085126_On_a_Kinetic_Model_for_a_Simple_Market_Economy (JSP 120:253-277)
[6] https://arxiv.org/abs/1401.4550
[7] https://arxiv.org/html/2607.04280
[8] https://arxiv.org/abs/2510.27334
[9] https://arxiv.org/abs/1105.1694 · https://doi.org/10.1103/PhysRevX.1.021006 (Tóth et al. 2011, PRX 1:021006; 摘要页核验 2026-11-01)
