# SPASM: Stable Persona-driven Agent Simulation for Multi-turn Dialogue Generation

## 基本信息
- **论文**: SPASM: Stable Persona-driven Agent Simulation for Multi-turn Dialogue Generation
- **作者**: Han Luo, Guy Laban
- **来源**: arXiv
- **相关度**: 高相关

## 核心贡献

解决 LLM-LLM 多轮对话中积累的身份相关失败 (identity-related failures):

1. **Schema Sampling**: 在对话开始前采样 agent 的 schema (结构化 persona 定义)
2. **Egocentric Context Projection (ECP)**: 将对话历史存储为 perspective-agnostic 格式，然后投影到每个 agent 的视角
3. **多模型后端验证**: 在多个模型上验证 persona drift 减少效果

## 与 persona-v3 的关联

### SPASM = persona-v3 的"对抗性"验证
persona-v3 通过 prompt 激发 persona，SPASM 通过架构约束防止 persona drift。两者从不同方向解决同一问题：
- persona-v3: "如何让 persona 在输出中体现"
- SPASM: "如何让 persona 在多轮对话中保持稳定"

### ECP 与 persona-v3 的"自适应自我"维度
SPASM 的"Egocentric Context Projection"与 persona-v3 的"自适应自我"维度同构：
- ECP: 从 perspective-agnostic 历史投影到第一人称视角
- 自适应自我: 从不同观测者视角理解系统行为
- 两者都强调：观点不是固定的，而是需要主动转换

### persona drift 是 persona-v3 的核心挑战
这篇论文直接证明了 persona drift 是 LLM 对话中的**系统性问题**，而非偶发现象。这为 persona-v3 提供了外部验证：通过结构化 prompt 内化 persona 是必要的（而非可选）。

## 可迁移的技术

1. **Schema Sampling**: 可以为 persona-v3 添加 schema 级别的 persona 定义
2. **ECP**: 可以为 persona-v3 添加对话历史的人称投影转换
3. **多模型验证**: 可以为 persona-v3 添加跨模型的通用性测试

## 评估标准 (ReportBench 视角)

- **引用相关性**: 3/3 — 直接支持 persona-v3 核心假设
- **事实可信度**: 4/4 — 实证论文，多模型验证
