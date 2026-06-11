---
name: iteration-166-external-research-batch6
description: arXiv 搜集 batch 6 — LATTE, RGoT, PPAI, TAME, HydraPrompt (learned persona + RL adaptive prompting)
metadata:
  type: project
  iteration: 166
---

# Iteration 166: 外部研究第六批 — learned persona trajectory + RL adaptive prompting

## 方法
arXiv API (HTTPS) 搜索 "adaptive prompt OR dynamic persona OR personalized LLM"。

## 新增论文 (28-32)

### 28. LATTE — 极高相关
- learned persona trajectory 预测
- 证明 learned persona (静态 profile) < learned persona trajectory (动态预测)
- 支持 persona-v3: prompt 层动态适应替代序列预测器

### 29. RGoT — 高相关
- RL 驱动的自适应 prompt 生成
- 证明静态 prompt 结构不足，需要自适应
- 支持 persona-v3: prompt 层自适应替代 RL 训练

### 30. PPAI — 中相关
- 个性化 LLM 代理互操作性
- persona-v3 6 维度 = 代理专业化定义

### 31. HydraPrompt — 低相关
- 视觉模型自适应 prompt

### 32. TAME — 中相关
- MoE prompt tuning
- 6 维度 = 可学习 expert 的 prompt 替代

## 更新
- arxiv-persona-research-2026-q2.md: 50 → 60 篇 (+10)
- 总高相关: 13 → 15 篇
- 总极高相关: 3 → 4 篇
