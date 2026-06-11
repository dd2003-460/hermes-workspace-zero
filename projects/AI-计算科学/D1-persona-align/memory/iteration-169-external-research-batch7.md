---
name: iteration-169-external-research-batch7
description: arXiv 搜集 batch 7 — UniSteer, Teaching Values, ActTraitBench, 自适应访谈等 (learned persona + activation-based steering + value alignment)
metadata:
  type: project
  iteration: 169
---

# Iteration 169: 外部研究第七批 — activation-based persona steering + value alignment + test-time adaptation

## 方法
arXiv API 搜索多个关键词组合: dynamic prompt, persona LLM, self-model, cognitive architecture, test-time adaptation, discrete tokens persona, meta-prompt, identity preservation。共 35 篇原始结果，42 篇独立论文 (batch 7: +9)。

## 新增论文 (33-42)

### 33. UniSteer — 极高相关
- 激活空间中的 persona/风格控制
- 文本引导的流匹配生成 steering directions
- 支持多维度、组合式 persona 控制
- 与 persona-v3 正交互补: activation 层 (UniSteer) vs prompt 层 (persona-v3)

### 34. Teaching Values to Machines — 极高相关
- 心理学价值理论诱导人类价值到 LLM
- 500 万题大规模验证
- persona-v3 提供"机制"，心理学提供"内容"

### 35. ActTraitBench — 极高相关
- 衡量 persona-behavior 差距 (Knowledge-Decision Gap)
- 直接支持"为什么需要三层评估"

### 36. 自适应访谈框架 — 高相关
- 批评静态 persona 描述，提出三阶段动态对话
- 与 persona-v3 共享"persona 是动态过程"哲学

### 37. Co-Ontogeny / Humorphic Partnership — 中相关
- 共享自我模型概念
- 与"自适应自我"维度正交互补

### 38. PAVE — 中相关
- 认知架构用于"合法违规"决策
- 与 persona-v3 目标不同但正交互补

### 39. SkillTTA — 高相关
- 推理时技能合成
- 与 persona-v3 共享"推理时自适应"哲学

### 40. OMEGA — 中相关
- meta-prompt 驱动 AI 研究
- persona-v3 可视为 specialized meta-prompt

### 41. Governed Collaborative Memory — 中相关
- 持久记忆作为人工选择
- 与"贝叶斯先验"正交互补

## 更新
- arxiv-persona-research-2026-q2.md: 33 → 43 篇 (+9)
- 总高相关: 15 → 19 篇
- 总极高相关: 4 → 8 篇
