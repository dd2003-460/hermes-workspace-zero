# Review: EMPA — Evaluating Persona-Aligned Empathy as a Process

## 论文信息
- **arXiv ID**: 2603.00552
- **标题**: EMPA: Evaluating Persona-Aligned Empathy as a Process
- **日期**: 2026-03

## 核心发现

EMPA 提出了一种过程导向的评估框架，在"潜在心理空间"中对对话轨迹进行评分，包括方向对齐、累积影响和稳定性指标。它取代了孤立回复评分，通过开放式的多智能体沙盒暴露战略适应和故障模式。

## 与 persona-v3 的关联

1. **轨迹级 vs 孤立回复**: 当前 persona-v3 使用 gap_filler 对单个 idea 文件做孤立评估。EMPA 证明这种方法遗漏了persona一致性在对话轨迹中的演化 — 同一文件在不同上下文中的persona表现可能完全不同
2. **方向对齐 + 累积影响 + 稳定性**: 这三个指标可以完全映射到 persona-v3 的6维度 — 方向对齐=先验更新，累积影响=探索频率，稳定性=自我一致性
3. **多智能体沙盒**: persona-v3 需要一个沙盒测试环境，模拟成璐的真实对话场景

## 对 persona-v3 的启示

- **从 gap_filler 孤立评分 → EMPA 轨迹评分** 是评估范式的必要升级
- 6 维度的加权匹配需要在时间维度上积分 (cumulative impact)
- EMPA 的 directional alignment 可用于检测 persona drift 的方向性

## 引用

EMPA authors. (2026). EMPA: Evaluating Persona-Aligned Empathy as a Process. arXiv:2603.00552.
