# ActTraitBench: Persona-Behavior Gap Benchmark

**来源**: arXiv 2025
**相关度**: 极高相关

## 摘要

衡量 persona (知识/能力) 与 behavior (实际决策) 之间的差距, 即 Knowledge-Decision Gap (KDG)。

## 核心发现

1. 模型可以有正确的 persona knowledge 但表现错误的 behavior
2. KDG 是一个核心评估指标 — 知识≠行为
3. 三层评估系统的必要性: 知识层→行为层→一致性

## 对 persona-v3 的启示

- **三层评估**: ActTraitBench 直接支持 persona-v3 的三层评估设计
- **验证模式**: persona-v3 的 "验证模式" 对应 KDG 的检测
- **gap_filler**: gap_filler 可以视为 KDG 的自动修复工具

## 参考

论文: ActTraitBench — 衡量 persona-behavior 差距 (见 iteration-169)
