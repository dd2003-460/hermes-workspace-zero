---
name: iteration-155-external-research-batch4
description: arXiv 搜集 batch 4 — PDD/ICLR 2026, P-GenRM, PICCO, AI-GENRM, SimPersona, Prober.ai
metadata:
  type: project
  iteration: 155
---

# Iteration 155: 外部研究第四批 — adaptive persona + prompt engineering

## 方法
arXiv API (HTTPS) 搜索 "adaptive persona" 和 "prompt engineering AND persona"。

## 新增论文 (17-22)

### 17. PDD (2603.01438, ICLR 2026) — 极高相关
- CAPS 理论驱动的动态 persona 重要性估计
- 核心论点：人格影响随场景变化
- 支持 persona-v3 核心理念：persona = 方法论动态应用 ≠ 身份标签

### 18. P-GenRM (2602.12116, ICLR 2026 Oral) — 高相关
- 测试时用户缩放提升 3%
- dual-granularity scaling (个体 + 原型)
- 支持 persona-v3 的 prompt-based 而非 fine-tuning 策略

### 19. PICCO Framework — 中相关
- prompt 五要素架构: Persona, Instructions, Context, Constraints, Output
- 支持 persona-v3 将 persona 定义为方法论而非身份标签

### 20. AI-GENRM (generative psychometrics) — 高相关
- adaptive prompting > non-adaptive prompting 实验验证
- 直接验证 persona-v3 的 6 维度自适应设计哲学

### 21. SimPersona — 中相关
- VQ-VAE 学习离散 persona tokens，在 837 万买家上验证
- learned persona > hand-crafted persona，提供未来路径

### 22. Prober.ai — 中相关
- persona-specific prompts 约束 LLM 输出格式
- "推进而非停滞"行为约束的正面实例

## 关键发现
- 2026 ICLR 2 篇直接相关 (PDD, P-GenRM Oral)
- adaptive persona 是活跃研究领域，但无人涉及认知维度（均为应用层面）
- persona-v3 的独特定位：通用认知人格框架 + 测试时自适应 + 方法论层面

## 更新
- arxiv-persona-research-2026-q2.md: 22 → 36 篇 (+14)
- 高相关: 5 → 9 篇
- 极高相关: 1 → 2 篇
