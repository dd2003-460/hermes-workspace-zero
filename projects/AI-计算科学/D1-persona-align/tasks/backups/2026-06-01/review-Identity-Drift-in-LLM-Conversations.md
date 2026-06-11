# Examining Identity Drift in Conversations of LLM Agents

## 基本信息
- **论文**: Examining Identity Drift in Conversations of LLM Agents
- **作者**: Junhyuk Choi, Yeseon Hong, Minju Kim, Bugeun Kim
- **来源**: arXiv
- **相关度**: 极高相关

## 核心贡献

研究 LLM 在多轮对话中如何演化自己的交互风格和身份:

1. **身份漂移 (Identity Drift)**: 长时间对话中，LLM 的交互模式或风格会逐渐变化
2. **参数规模效应**: 更大规模的模型反而表现出**更多的**身份漂移
3. **九种模型对比**: 分析了不同架构和规模模型的漂移行为

## 与 persona-v3 的关联

### 身份漂移 = persona-v3 需要解决的问题
这篇论文直接验证了 persona-v3 的设计假设：如果没有外部约束（如结构化 prompt），LLM 会在多轮对话中**逐渐失去 persona 一致性**。

### 参数规模与漂移的关系
更大的模型更容易漂移 — 这与直觉相反（通常认为更大的模型应该更有"记忆"）。可能的解释：
- 更大的模型有更多"灵活"的表示空间
- 更大的模型更善于"顺应"当前上下文，而非坚持固定 persona
- 这对 persona-v3 意味着：**persona 稳定性不依赖模型规模，而依赖 prompt 结构**

### 对 persona-v3 的影响
1. **persona-v3 的 3 行为约束 (简洁直接, 不解释, 推进而非停滞) 可以视为身份漂移的对抗机制**
2. **结构化 prompt 比模型规模更重要** — 这验证了 persona-v3 的 prompt-based 方法
3. **多轮验证** — persona-v3 可以在长对话中持续验证身份稳定性

## 评估标准 (ReportBench 视角)

- **引用相关性**: 3/3 — 直接支持 persona-v3 核心假设
- **事实可信度**: 4/4 — 实证论文，九种模型对比
