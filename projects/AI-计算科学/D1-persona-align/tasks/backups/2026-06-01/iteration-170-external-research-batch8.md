---
name: iteration-170-external-research-batch8
description: arXiv 搜集 batch 8 — SimPersona, activation patching, persona evaluation, ToM personalization (learned persona trajectory 路径深入探索)
metadata:
  type: project
  iteration: 170
---

# Iteration 170: 外部研究第八批 — learned persona 路径深入探索

## 方法
arXiv API 搜索 learned persona, discrete persona tokens, latent persona, persona embedding, user modeling LLM inference, behavioral tokens, internal state personalization。共 29 篇原始结果，50 篇独立论文 (batch 8: +8)。

## 新增论文 (43-50)

### 43. SimPersona — 极高相关
- 从原始点击流数据学习离散买家 persona
- K-means 聚类行为轨迹 → persona cluster → 训练专用代理
- persona-v3: prompt 层自适应替代行为聚类 + 训练

### 44. Activation Patching for Persona Reasoning — 极高相关
- persona tokens 在特定层/注意力头激活（社会认知相关）
- **理论支撑**: persona-v3 的 6 维度可能对应不同激活子空间

### 45. Persona Drift in Fine-Tuning — 高相关
- 良性数据微调也会导致 persona drift
- **支持 persona-v3 的 prompt-based 设计选择**

### 46. Eval4Sim: Persona Simulation Evaluation — 极高相关
- consistency vs flexibility 评估框架
- persona-v3 解决此张力的方法

### 47. AdaMem: Adaptive User Memory — 高相关
- 长对话中自适应记忆更新
- 与 persona-v3 的 prompt 内自适应互补

### 48. ScioMind: Multi-Agent Social Simulation — 中相关
- 锚定信念动力学 + 动态 profile
- 与贝叶斯先验正交互补

### 49. Mind Modeling: ToM-Based Personalization — 高相关
- 心智理论 → 心理状态归因 → 个人化
- 与自适应自我共享哲学

### 50. Tutor Steering Vectors — 高相关
- 从对话学习 steering vector 激活 tutor persona
- 与 persona-v3 的 6 维度混合互补

## 关键发现
SimPersona 是最接近"learned persona"路径的论文 — 从行为数据自动学习 persona，无需人工定义。persona-v3 定位: **"唯一不依赖训练的 prompt-based adaptive persona 框架"**。

## 更新
- 总论文: 42 → 50 篇 (+8)
- 高相关: 19 → 23 篇
- 极高相关: 8 → 12 篇
