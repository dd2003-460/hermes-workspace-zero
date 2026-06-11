# CoPrompter: User-Centric Evaluation of LLM Instruction Alignment

**来源**: arXiv 2024-11
**相关度**: 中

## 摘要

从用户视角评估 LLM 的指令对齐能力. 提出用户中心的评价框架, 而非仅依赖自动化测试.

## 核心方法

1. 用户中心评估框架
2. 多层指令对齐检测
3. 自动化 + 人工评估混合

## 对 persona-v3 的启示

- 三层评估体系是自动化对齐评估的体现
- persona-v3 alignment_checker 可以视为 CoPrompter 框架的自动化实现
- 用户中心视角是 persona-v3 评估工具的补充 — 自动化评估 + 用户反馈

## 改进建议

- 考虑在 persona-v3 评估中加入用户反馈循环
- 将 CoPrompter 的"多层指令对齐"概念映射到 persona-v3 的三层评估

## 参考

论文: CoPrompter — 用户中心 LLM 指令对齐评估 (见 iteration-147)
