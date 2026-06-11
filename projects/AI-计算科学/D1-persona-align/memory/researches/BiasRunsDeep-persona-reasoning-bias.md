# Bias Runs Deep: Implicit Reasoning Biases in Persona-Assigned LLMs

**来源**: arXiv 2023-11
**相关度**: 高

## 摘要

浅层人格分配 (浅层 persona assignment) 会产生推理偏差. 证明将 persona 作为角色标签附加到 LLM 上会改变其推理模式, 但这种改变不一定是正确的或期望的.

## 核心发现

1. 浅层 persona 分配 ≠ 深层认知架构
2. 角色标签型 persona 会影响推理, 但这种影响是有偏的
3. persona-v3 的 6 维度设计避免了这个问题 — 6 维度是思维习惯而非角色标签

## 对 persona-v3 的启示

这是 persona-v3 "深层认知架构"设计路线的最重要实证支持:

- **浅层 vs 深层**: 传统 persona 方法 (角色标签) → 有偏推理. persona-v3 (思维习惯 + 自适应维度) → 无偏认知架构.
- **6 维度 = 思维习惯**: 自适应精度、探索、感知、先验、自我、投影 — 这些是认知策略, 不是角色设定.
- **验证**: persona-v3 的 alignment_checker 评估的是认知策略覆盖度, 不是角色一致性.

## 改进建议

- 在 persona-v3-prompt.txt 中明确区分"角色标签"和"认知架构"
- 在评估工具中加入"推理偏差检测" — 检查 persona 是否引入了不期望的推理偏置

## 参考

论文: Bias Runs Deep — 浅层人格分配对推理的影响 (见 iteration-147)
