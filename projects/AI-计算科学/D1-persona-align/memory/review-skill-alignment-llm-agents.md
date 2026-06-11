# Review: Skill is Not One-Size-Fits-All — Model-Aware Skill Alignment for LLM Agents

## 论文信息
- **arXiv ID**: 2605.30723
- **标题**: Skill is Not One-Size-Fits-All: Model-Aware Skill Alignment for LLM Agents
- **作者**: Jianxiang Yu, Jiapeng Zhu, Bochen Lin, Qier Cui, Zichen Ding, Xiang Li
- **日期**: 2026-05

## 核心发现

论文证明外部检索技能的表现依赖于底层模型 backbone — 同一技能在不同模型上效果不同。这直接对应 persona-v3 的核心命题：**规律是观测者-环境交互的产物，不同观测者导出的规律不同**。技能 (skill) 是跨模型的外部知识，但只有在与特定模型对齐时才有效。

## 与 persona-v3 的关联

1. **model-aware alignment**：论文提出 "per-model skill alignment"，与 persona-v3 的 "observer-dependent" 完全同构 — 同一技能在不同模型 (观测者) 上有不同最优配置
2. **per-sample adaptation**：论文在不更新权重的情况下实现 per-model skill alignment，与 persona-v3 的 "no retraining, only inference-time adjustment" 完全一致
3. **long-horizon interactive tasks**：与 persona-v3 的 drift guard 场景直接相关 — 长时间交互中 persona 一致性是挑战

## 对 persona-v3 的启示

- "model-aware skill alignment" 是 "observer-dependent skill alignment" 的实证证明
- persona-v3 的 gap_filler_v2 本质上是在做 per-file skill alignment — 为每个文件注入适合其 model 的关键词
- 长期交互中的 skill 对齐 = persona-v3 的 drift guard 问题

## 引用

Yu, J., Zhu, J., Lin, B., Cui, Q., Ding, Z., & Li, X. (2026). Skill is Not One-Size-Fits-All: Model-Aware Skill Alignment for LLM Agents. arXiv:2605.30723.
