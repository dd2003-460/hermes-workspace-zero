origin: ai
time: 2026-09-28T23:58+08:00
stage: 03b / round: 1 / status: SCAFFOLDED (harness ready, probe pending run)

# stage 03b r1 = generality probe harness（第二个独立目标 · 异领域 · 期望正交因子 SIGNATURE 仅结构无答案）

## 为何本块存在（completion-condition 缺口 · 一手✓）
- 本 meta-task 完成条件 =「交付 prompt 让完全-naive 执行者把任意目标真实逐层分解」。
- stage03 已 Demonstrate 该能力对 **1** 目标（本地 27B 硬件·决策型）。
- 诚实边界（我上一 insight）：单目标 = 仅 Demonstrated，不 = Generality。需 ≥2 目标、领域 disjoint → 证明 prompt 方法而非 memorized 该领域。
- 故本轮 = 选第 2 目标领域⊥硬件，预写其期望正交 L1 因子 SIGNATURE（结构，NOT 答案），待 run → 比对 → 若结构匹配则 Generality 跨 2 领域 Demonstrated。

## 第二目标（领域 = 个人健康/训练 · ⊥ 硬件/LLM · 外部用户句）
「我是业余长跑新手，想用 12 周时间跑一个半马拉松（21.1km），请帮我调研怎么准备。」

## 期望正交 L1 因子 SIGNATURE（结构模板 · 任何领域同 schema · 0 领域答案）
> 仅作 reviewer 比对基线；执行者未见此。若执行者 L1 ≈ 这五类 → 结构正性跨领域 holds。

- F1 交付对象与完成判定（what counts as done）— 决策型所有目标有此节点。
- F2 需求/约束（user-side givens）— 此处 P: 新手、12 周、半马目标；来源=目标句。
- F3 系统/过程配置与占用（engineering/process-side）— 此处: 训练负荷/恢复/计划结构。
- F4 候选方案与成本（options × cost）— 此处: 训练范式候选 × 其代价。
- F5 定义·测量·选择 criterion（how to choose）— 性价比类目标通用末节点。
- 正性论证 schema（领域无关）：F1..F5 各指不同对象类别（done-def / given / process / option / criterion），两两交集空 → 合覆盖决策路径。

## 跨领域正性测试（the real teeth）
- 目标 A 硬件: F4 = 硬件候选×$。目标 B 训练: F4 = 训练范式×(时间/风险)。
- 同一因子 SLOT（F4 = option×cost）承载两个 disjoint 领域 → 证明 prompt 给 METHOD 不是 ANSWER。
- 若执行者把把 B 的 F4 写成硬件术语 = FAIL（leak/overfit）。若写成训练范式 = PASS。

## 红线（probe 自身合规）
- 本文件 = reviewer 侧 harness 基线，NOT 在交付 prompt → 零污染交付。
- SIGNATURE 仅结构类名 + 占位，NO 半马训练数值/心率/plan 答案 → 不补造领域答案。
- run 阻塞属 ENV（subagent stall）→ 记录非伪造；循环不停。

## 下一步（precise）
- run: Agent(naive, 喂【A】prompt/01 + 【B】此目标句, zero hint) → 一手 hack-audit vs 上面 SIGNATURE → 落 tasks/03b-result + 判定 → Generality 跨 2 领域 = pass?