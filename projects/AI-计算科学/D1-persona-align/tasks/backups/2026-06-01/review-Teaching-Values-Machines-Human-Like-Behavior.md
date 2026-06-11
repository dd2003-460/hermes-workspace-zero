# Teaching Values to Machines: Simulating Human-Like Behavior in LLMs

## 基本信息
- **论文**: Teaching Values to Machines: Simulating Human-Like Behavior in LLMs
- **作者**: Asaf Yehudai, Naama Rozen, Ariel Gera
- **来源**: arXiv
- **相关度**: 极高相关

## 核心贡献

探索是否可以通过应用心理学框架使 AI 模型展现"符合人类价值结构的连贯行为"：

1. **心理学框架的模型映射**: 将人类价值心理学的框架 (如 Big Five 人格模型、道德基础理论) 映射到 LLM 的 prompt 系统中
2. **价值观引导的行为一致性**: 证明经过价值观引导的模型可以"紧密模仿人类伦理模式"
3. **价值诱导的深层对齐**: 不是简单的指令跟随，而是内化了一套价值体系

## 与 persona-v3 的关联

### 直接同构: persona-v3 = 心理学框架 → LLM prompt
persona-v3 框架本质上就是在做同样的事：
- persona-v3 的 8 原则 ≈ 心理学框架中的核心价值观
- persona-v3 的 6 维度 ≈ Big Five 人格模型的多维结构
- persona-v3 的 3 行为约束 ≈ 伦理规范

**这篇论文验证了 persona-v3 的方法论**：通过结构化 prompt 内化价值体系，而非简单指令跟随。

### "Behavior that adheres to a coherent, human-like value structure"
这句话完美描述了 persona-v3 的目标 — 让 AI 的行为不是"像人"，而是"符合连贯的人类价值结构"。

### 对齐的"浅层 vs 深层"问题
论文指出"shallow alignment generalizes poorly"，这与 persona-v3 的设计哲学一致：
- Shallow alignment = 指令级跟随 (instruction following)
- Deep alignment = 价值内化 (persona-v3 的 8 原则 + 6 维度)

## 对 persona-v3 的影响

1. **心理学区分**: persona-v3 可以引用道德基础理论 (Moral Foundations Theory) 来区分不同类型的行为约束
2. **价值观评估**: 可以借鉴论文中的"人类伦理模式匹配"指标来评估 persona-v3 的行为约束得分
3. **通用化路径**: 论文证明价值观引导可以跨任务泛化 — 这支持 persona-v3 跨领域应用的可行性

## 评估标准 (ReportBench 视角)

- **引用相关性**: 3/3 — 直接验证 persona-v3 方法论
- **事实可信度**: 4/4 — 心理学框架 + 实验验证
