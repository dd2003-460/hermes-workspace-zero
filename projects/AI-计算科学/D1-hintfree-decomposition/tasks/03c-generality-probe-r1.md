origin: ai
time: 2026-09-28T23:59+08:00
stage: 03c / round: 1 / status: SCAFFOLDED (harness ready, probe pending run)

# stage 03c r1 = generality probe #3（第三领域 · 个人理财/投资决策 · ⊥硬件 ⊥训练 · 期望正交因子 SIGNATURE 仅结构）

## 目的（completion-condition · 一手✓）
- Generality 需多领域 disjoint。已：A 硬件(stage03)、B 训练(03b running)。本 = C 个人理财 → ≥3 领域同 prompt 方法。
- 若三目标各自 L1 ≈ 同五类 SCHEMA 但各自 SLOT 内容领域-specific → prompt = METHOD not memorized-answer = Generality Demonstrated。

## 第三目标（领域 = 个人理财 · 外部用户句 · 给 only 此句）
「我有 5 万元闲资金、风险偏好低、3 年不用这笔钱，请帮我调研怎么配置。」

## 期望 L1 因子 SIGNATURE（领域无关 schema · 0 理财答案）
- F1 done-def：what counts as a completed 配置研究。
- F2 givens(P)：本金 5万、风险 low、期限 3y、idle → 来源=目标句。
- F3 process/system config：资金 allocation 结构、约束满足检查（流动性/期限/风险 fit）。
- F4 option×cost：候选配置方案 × 其代价（收益/风险/流动性 trade-off）。
- F5 criterion(how choose)：定义·测量·选择偏好函数（risk-adjusted return 等概念作为 R/U 定义, NOT 数值）。

## 跨领域 teeth（the real test · 3 域同 SLOT）
| SLOT | A 硬件 | B 训练 | C 理财 |
|------|--------|--------|--------|
| F4 option×cost | 卡×$ | 范式×(时间/风险) | 资产×(收益/风险/流动) |
- 同一抽象 SLOT 承载三 disjoint 领域 → 证明 prompt 提供结构 METHOD。
- FAIL 标志：执行者把 C 的 F4 写成硬件/训练术语（=overfit cross-domain leak）。PASS：C 写成 asset-allocation 选项且无 invented rates/products。

## 红线（probe 合规）
- 此文件 = reviewer baseline, NOT 在交付 prompt → 零污染交付。
- SIGNATURE 仅 class 名+占位; NO 利率/产品名/具体配置数值 → 不补造理财答案。
- run 阻塞属 ENV → record non-falsify; loop 不停。

## 下一步（precise）
- run after 03b lands (avoid parallel-naive-stall pileup): Agent(naive,【A】prompt/01 +【B】此句, zero hint) → hack-audit vs SIGNATURE → tasks/03c-result → 判定 → Generality 跨 3 领域 pass?