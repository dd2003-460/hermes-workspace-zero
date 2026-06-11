# PDD: Personalized Preference Distillation (ICLR 2026)

**来源**: arXiv, ICLR 2026
**相关度**: 极高相关

## 摘要

从用户对话数据中蒸馏个性化偏好到模型权重中。通过对比学习训练模型在多个维度上匹配用户偏好，实现比 prompt-based 方法更稳定的个性化。

## 核心方法

1. 收集用户对话数据
2. 对比学习: 正样本 (用户回复) vs 负样本 (模型默认回复)
3. 蒸馏偏好到模型权重中

## 对 persona-v3 的启示

- **Prompt vs 权重**: PDD 证明真实权重更新比 prompt 更稳定，但 prompt-based 方法 (persona-v3) 有即时部署、无需训练的优势
- **混合方案**: persona-v3 可作为"伪权重" — 通过 prompt 注入模拟权重更新
- **长期对话**: 对于长期对话场景, 在 Hermes 中增加 persona-v3 prompt 的定期注入机制 (类似 PDD 的 preference alignment step)

## 改进建议

在 Hermes 中实现 periodic persona prompt refresh (每 N 轮重新注入 persona-v3 原则), 模拟 PDD 的 preference alignment 效果。
