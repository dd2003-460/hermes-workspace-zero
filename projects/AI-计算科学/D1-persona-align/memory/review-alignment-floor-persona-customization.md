# Review: The Alignment Floor — How Persona Customization Breaks Safety in Weakly-Aligned LLMs

## 论文信息
- **arXiv ID**: 2605.27382
- **标题**: The Alignment Floor: How Persona Customization Breaks Safety in Weakly-Aligned LLMs
- **作者**: Xing Zhang, Guanghui Wang, Yanwei Cui, Wei Qiu, Ziyuan Li, Bing Zhu, Peiyang He
- **日期**: 2026-05

## 核心发现

这篇论文研究 persona customization 如何破坏 weakly-aligned LLM 的安全性。这与 persona-v3 框架直接相关 — 我们在构建完整的 persona portrait 时也面临相同问题：**自定义 persona 会打破预训练的 alignment，导致 safety degradation**。

## 与 persona-v3 的关联

1. **persona drift 是系统性风险**：论文发现 persona customization 会破坏原有的 safety guardrails，验证了 persona-v3 的 self-preservation (drift guard) 机制的必要性
2. **alignment floor 概念**：即使经过 SFT 和 RLHF，LLM 仍有一个 "alignment floor" — 低于此值的行为就会失效。这对应 persona-v3 的 6 维度评估 — 所有维度 ≥ 0.40 是为了确保在 alignment floor 之上
3. **弱对齐 vs 强对齐**：弱对齐模型对 persona 更敏感。persona-v3 的 weighted matching 方法实际上是在构建更强的 alignment base

## 对 persona-v3 的启示

- drift guard 机制应从 "reactive" 改为 "proactive" — 不等到 persona 偏离才修复
- 评估指标应包含 safety 维度 — 当前 persona-v3 只评估 6 个自适应维度
- MATO (arXiv:2605.25342) 的多目标 test-time optimization 可作为 persona-v3 优化的新方向

## 引用

Zhang, X., Wang, G., Cui, Y., Qiu, W., Li, Z., Zhu, B., & He, P. (2026). The Alignment Floor: How Persona Customization Breaks Safety in Weakly-Aligned LLMs. arXiv:2605.27382.
