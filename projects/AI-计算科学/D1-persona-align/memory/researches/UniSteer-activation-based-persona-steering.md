# UniSteer: Universal Steering Vector for Persona/Style Control

**来源**: arXiv 2025
**相关度**: 极高相关

## 摘要

在激活空间中通过文本引导学习 steering directions, 实现多维度、组合式的 persona/风格控制。

## 核心方法

1. 在激活空间中查找 persona/风格的 steering vector
2. 文本引导: 用自然语言描述目标风格, 生成对应的 steering vector
3. 组合式控制: 多个 steering vector 可以组合使用

## 对 persona-v3 的启示

- **正交互补**: activation 层 (UniSteer) vs prompt 层 (persona-v3)
- **维度映射**: persona-v3 的 6 维度可能对应 UniSteer 的 6 个 steering vector
- **混合控制**: prompt + steering 的混合控制可能比单一方法更稳定

## 改进建议

研究 steering vector 与 persona-v3 维度的映射关系, 可能实现更精确的维度级控制。

## 参考

论文: UniSteer — 激活空间中的 persona 控制 (见 iteration-169)
