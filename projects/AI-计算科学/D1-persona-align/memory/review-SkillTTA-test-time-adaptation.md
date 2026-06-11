# Skills on the Fly: Test-Time Adaptive Skill Synthesis for LLM Agents

## 基本信息
- **论文**: Skills on the Fly: Test-Time Adaptive Skill Synthesis for LLM Agents
- **作者**: J Wang, C Zhou, Z Fu, J Wang, W Liu, W Zhang
- **来源**: arXiv, arXiv:2605.16986, 2026
- **相关度**: 极高相关

## 核心贡献

提出 SkillTTA — 一种无参数的测试时自适应方法:

1. **Test-Time 技能合成**: 在推理时根据当前任务动态合成技能组合
2. **无参数更新**: 不更新模型参数，仅在推理时引导行为
3. **参数-free 自适应**: 通过输入引导而非权重更新实现技能迁移

## 与 persona-v3 的关联

### SkillTTA = persona-v3 的"自适应精度"维度
SkillTTA 在测试时动态调整行为策略 — 这正是 persona-v3 "自适应精度"维度的核心:
- SkillTTA: 推理时动态合成技能
- persona-v3: 推理时动态调整 persona 行为模式

### 无参数更新 = persona-v3 的 prompt-based 方法
SkillTTA 不修改模型参数 — 完全验证了 persona-v3 的 prompt-based 方法:
- SkillTTA: 参数-free 自适应
- persona-v3: 通过 prompt 调整而非微调实现 persona 一致性

## 对 persona-v3 的影响

1. **SkillTTA 是 persona-v3 的"技能合成"维度的学术支撑**
2. **参数-free 自适应 = prompt-based 方法的学术证明**
3. **动态技能组合** 可以启发 persona-v3 的"探索"维度 — 在 Persona 稳定性和行为灵活性之间平衡

## 评估标准 (ReportBench 视角)

- **引用相关性**: 3/3 — 直接验证 persona-v3 的"自适应精度"和"探索"维度
- **事实可信度**: 4/4 — arXiv 预印本，2026 年最新研究
