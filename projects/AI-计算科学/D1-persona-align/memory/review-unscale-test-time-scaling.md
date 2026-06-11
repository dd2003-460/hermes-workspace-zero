# Review: UniScale — Adaptive Unified Inference Scaling via Online Joint Optimization

## 论文信息
- **arXiv ID**: 2605.30898
- **标题**: UniScale: Adaptive Unified Inference Scaling via Online Joint Optimization of Model Routing and Test-Time Scaling
- **作者**: Kaiyu Huang, Xingyu Wang, Mingze Kong, Zhubo Shi, Yuqian Hou, Hong Xu, Zhongxiang Dai, Minchen Yu, Qingjiang Shi
- **日期**: 2026-05

## 核心发现

UniScale 提出了一种 adaptive unified inference scaling 方法，通过 contextual multi-armed bandit 动态平衡推理质量和计算成本。这与 persona-v3 的**自适应感知**和**自适应探索**维度高度相关 — 我们在 idea 文件中讨论的 t_p (感知时间) 就是 test-time compute 的一种形式。

## 与 persona-v3 的关联

1. **t_p 的实证验证**：UniScale 证明 test-time compute 确实可以改善特定任务的性能。这验证了 persona-v3 中感知时间 t_p 的设计 — 对高信息密度内容投入更多分析时间是正确的
2. **信息密度 × 计算预算**：UniScale 的 "adaptive inference scaling" 本质上是在不同任务间分配计算预算。persona-v3 的信息密度自适应正是同一原则在 persona 层面的应用
3. **contextual bandit**：persona-v3 的自适应维度选择可以看作一个 contextual bandit 问题 — 根据上下文 (问题类型) 选择最优的维度激活模式

## 关键方法对比

| 维度 | persona-v3 | UniScale |
|------|------------|----------|
| 优化目标 | 6 维度 alignment | 推理质量 × 计算成本 |
| 方法 | 关键词加权匹配 | Contextual bandit |
| 自适应维度 | 感知/探索/精度 | 模型路由 × test-time scaling |
| 理论基础 | empirical weighted matching | PAC-Bayes + bandit regret bound |

## 对 persona-v3 的启示

- UniScale 的 **contextual bandit** 可作为 persona-v3 维度选择的优化方法
- **test-time compute** 的可量化改善支持 persona-v3 的 t_p 理论
- **adaptive inference scaling** 与 persona-v3 的自适应精度高度同构

## 引用

Huang, K., Wang, X., Kong, M., Shi, Z., Hou, Y., Xu, H., Dai, Z., Yu, M., & Shi, Q. (2026). UniScale: Adaptive Unified Inference Scaling via Online Joint Optimization of Model Routing and Test-Time Scaling. arXiv:2605.30898.
