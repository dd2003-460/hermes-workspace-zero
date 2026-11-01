# F10-R3 调研任务书: 资金动力学与套利空间涌现

# origin: ai (成璐设想 2026-11-01: 气体动理论导致资金跃迁和博弈, 策略更新产生新套利空间)
状态: PENDING — 待 arena agent mode 执行
通道: ego-browser → LMArena agent mode
仓库: dd2003-460/hermes-workspace-zero @ arena/f10-gas-dynamics-research
产出落盘: loop-artifacts/stages/05/r6/research/{A,B,C,D}.md + receipts.json

## 背景 (≤10行)

加密永续市场 F1-F9 已证明: 公开时间序列信号 alpha 系统性衰减 (F9: p95 spread 0.056%→0.01%, 2020-2025)。
F10 R1/R2 预注册回测 FAIL: IV跳升后是动量延续非超调回归, funding极端+OI骤降是趋势加速器非反转源。
结论: 旧套利空间在关闭, 但"预测新空间涌现"本身尚未被正面回答。
成璐设想: 把资金主体当气体分子(异质温度), 套利=压力释放, 聪明钱迁移=碰撞变向,
策略更新产生新的非均衡态。需要文献支撑这个框架是否可行、别人做到哪一步了。

## 子领域拆分 (4个正交子问题, 各1个subagent)

### A. 异质主体市场微观结构模型 (Heterogeneous Agent Models in Market Microstructure)
一句话问题: 学术上用什么模型描述不同类型交易者(HFT/统计套利/趋势/散户/机构)的交互行为? 哪些模型能预测价格偏离的出现位置和持续时间?
要求:
- 列出 ≥5 个代表性模型/论文 (arXiv/qfin 或 SSRN), 每个给: 核心假设/主体分类/可预测什么/局限
- 重点找: evolutionary game theory applied to trading strategies, agent-based models of limit order books, "who eats whom" food-chain models
- 交付: 每篇 ≤8 行摘要 + 一个"对我们最有用的点"

### B. 套利资本流动与均衡收敛速度 (Arbitrage Capital Flows & Equilibrium Convergence)
一句话问题: 已有量化研究测量过套利空间从出现到消失的时间吗? 收敛速度的驱动因子是什么(资本流入率/竞争者数量/交易成本)?
要求:
- 找 ≥3 篇实证论文测量过 "time-to-arbitrage" 或 "convergence speed"
- 关键数据: 不同市场(股票/外汇/期货/加密)的收敛时间量级对比
- 是否有 "capital inflow rate vs profit pool" 的定量关系式?
- 交付: 每篇核心公式/发现 + 能否迁移到加密永续

### C. 策略拥挤与自我瓦解 (Strategy Crowding & Self-Destruction)
一句话问题: 当一个套利策略变得拥挤时, 它的收益如何衰减? 有没有预测 "什么时候会拥挤" 的前置指标?
要求:
- 找 crowding indicators: OI变化/换手率/策略容量上限估算方法
- 重点: "reflexivity" 文献 (Soros 概念的形式化), strategy decay curves
- 加密特有: funding rate 作为拥挤度代理变量是否有效?
- 交付: ≥3 个可操作的拥挤度指标 + 各自的数据可得性

### D. 信息不对称下的被迫流动预测 (Forced Flow Prediction under Information Asymmetry)
一句话问题: 哪些 "被迫交易" (margin calls/ETF rebalancing/options gamma/liquidations) 是可提前预测的? 预测精度到什么程度?
要求:
- 分类: 可日历化预测(期权到期/ETF月度调仓) vs 可实时监测(liquidation cascade/OI spike) vs 不可预测(黑天鹅)
- 每类给: 预测窗口/历史命中率/数据源
- 重点找: liquidation cascade prediction papers (crypto-specific preferred)
- 交付: 一张表(类型/预测窗口/数据源/历史精度/可交易性)

## 交叉验证门禁

每个子领域的结论需要 ≥2 个独立来源支持 (不同论文/不同作者)。
矛盾答案记录矛盾点并标注 confidence。
最终回执: receipts.json 含 {kind: "ralph_web_llm_cross_check", responses[], successful_provider_ids[]≥2, observed_at}

## 回执指纹要求

完成后回执必须含 repo URL (https://github.com/dd2003-460/hermes-workspace-zero) + branch (arena/f10-gas-dynamics-research) + commit_sha。

## 交付格式

每个子领域一个 md 文件 (A.md/B.md/C.md/D.md), 结构:
1. 直接回答一句话问题 (≤3行)
2. 证据列表 (论文/数据, 带URL和日期)
3. 对 F10 模型设计的启示 (≤5行, 具体到"我们应该在模型里加什么")
4. 未解决/矛盾点 (诚实标注)

总长度控制: 每个 ≤80 行。
