# ID-RAG: Identity Retrieval-Augmented Generation for Long-Horizon Persona Coherence

## 来源
Platnick, Bengueddache, Alirezaie, Newman, Pentland, Rahnama

## 核心问题
Long-horizon generative agents 中 identity drift（身份漂移）导致 coherence breakdown：
- 身份漂移：Agent 随对话轮数增加逐渐偏离初始设定
- 忽视已建立信念：忽略之前表达过的核心观点
- 幻觉传播：虚假信息在长对话中累积

## 方案
ID-RAG = Identity RAG，查询结构化知识图谱中的核心特质来 grounding 决策。

## 与 persona-v3 的关联

### 相同发现
1. **drift 是时间尺度问题** — 不是 prompt 质量问题，而是长窗口中注意力衰减
2. **结构化知识图谱 grounding** — 与 persona-v3 的 self-preservation 锚定机制完全一致
3. **定期 re-grounding** — 在关键决策点重新查询身份属性

### 对 persona-v3 的改进建议
1. **显式身份图谱** — persona-v3-prompt.txt 目前是扁平文本，可考虑增加结构化 identity section
2. **对话阶段 re-grounding** — 在每 10-15 轮对话后自动 re-anchor（比 SPASM 的 >10 轮更主动）
3. **信念一致性检查** — 输出前检查是否与之前表达的信念冲突

### 关键引用
> "identity drift, ignoring established beliefs, and the propagation of hallucinations"

## 评分影响
- 当前 persona-v3 的 self-preservation 已有 drift detection，ID-RAG 验证了这个方向的必要性
- 可以增加 **identity grounding** 作为 self-preservation 的第三条机制（检测 → 修复 → 锚定 → 身份图谱）
