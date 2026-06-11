# RGoT: RL-Driven Adaptive Prompt Generation

**来源**: arXiv 2025
**相关度**: 高

## 摘要

通过强化学习驱动自适应 prompt 生成. 证明静态 prompt 结构不足以应对所有任务场景, 需要动态生成.

## 核心方法

1. 使用 RL 训练 prompt 生成器
2. 根据任务上下文动态调整 prompt 结构
3. 证明自适应 prompt 优于固定 prompt

## 对 persona-v3 的启示

- **自适应 vs 静态**: RGoT 证明静态 prompt 结构不足, 需要自适应. persona-v3 在 prompt 层实现自适应替代 RL 训练.
- **维度级控制**: persona-v3 的 6 维度是"低分辨率"自适应 — 通过 prompt 选择, 而不是通过 RL 生成.
- **成本效益**: RL 训练 adaptive prompt 成本高, persona-v3 的 prompt 层自适应零训练成本.

## 改进建议

- 研究 persona-v3 维度权重与 RGoT 自适应策略的映射关系
- 考虑引入"prompt 结构自适应" — 不仅仅是内容自适应

## 参考

论文: RGoT — RL 驱动的自适应 prompt 生成 (见 iteration-166)
