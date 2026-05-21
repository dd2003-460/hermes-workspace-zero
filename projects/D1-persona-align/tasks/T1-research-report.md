# T1: 开源人格对齐项目搜索结果

> **完成时间**: 2026-05-19 (Iteration 20)
> **执行者**: Ralph Loop

## 搜索概述

搜索关键词: "LLM persona alignment", "character AI open source", "system prompt preservation"
搜索范围: GitHub 活跃项目 + 学术论文

---

## 直接相关项目 (Persona Alignment)

### 1. Persona-Evolve (HATS-ICT)
- **URL**: https://github.com/HATS-ICT/PersonaEvolve
- **Stars**: 9
- **论文**: "Implicit Behavioral Alignment of Language Agents in High-Stakes Crowd Simulations"
- **重点**: 通过隐含行为对齐实现 LLM 代理在模拟场景中的行为匹配
- **相关度**: ⭐⭐⭐⭐ 与 T3/T4 (prompt injection vs fine-tuning) 直接相关
- **关键发现**: 隐含行为对齐 > 显式 prompt 对齐的稳定性

### 2. Persona_Alignment (priyadip)
- **URL**: https://github.com/priyadip/Persona_Alignment
- **Stars**: 1
- **重点**: 高效微调技术实现模型人格特质一致性
- **相关度**: ⭐⭐⭐⭐ 与 T6 (实现方案) 直接相关
- **关键发现**: LoRA/QLoRA 微调比全参数微调更适合 persona 保持

### 3. Personality-Illusion (psychology-of-AI)
- **URL**: https://github.com/psychology-of-AI/Personality-Illusion
- **Stars**: 67
- **重点**: 模型自我描述与实际行为之间的脱节
- **相关度**: ⭐⭐⭐ 与 T5 (最小样本量验证) 相关
- **关键发现**: 模型声称的 persona 与实际行为存在系统性偏差

---

## 间接相关项目 (Character/Persona 平台)

### 4. OpenPerso (Daewooki)
- **URL**: https://github.com/Daewooki/OpenPerso
- **Stars**: 2
- **重点**: 自托管 Web 应用，设计/对话/分发 AI 人格
- **相关度**: ⭐⭐⭐ 架构参考
- **技术栈**: 基于 ChatGPT API 的 Web 界面

### 5. amica (semperai)
- **URL**: https://github.com/semperai/amica
- **Stars**: 1,500
- **重点**: 3D 数字虚拟角色实时语音对话
- **相关度**: ⭐⭐ 架构启发 (人格 + 视觉)
- **技术栈**: PyTorch, speech recognition, 3D rendering

### 6. shard (matjsz)
- **URL**: https://github.com/matjsz/shard
- **Stars**: 2
- **重点**: 将开源 LLM 适配为特定虚拟角色的 Python 工具包
- **相关度**: ⭐⭐⭐⭐ 实现方案参考
- **技术栈**: 微调框架，LoRA

---

## 学术论文 (预印本)

### 7. LLM Alignment with Persona Dynamics (AIKU)
- **URL**: https://github.com/AIKU-Official/aiku-24-1-llm_alignment_with_persona_dynamics
- **会议**: AKU 2024
- **重点**: LLM 人格动力学的对齐方法
- **相关度**: ⭐⭐⭐⭐ 理论基础

### 8. Medical Personas as Behavioral Priors (rsinghlab)
- **URL**: https://github.com/rsinghlab/Persona_Paradox
- **重点**: 使用临床角色作为医疗 LLM 的行为先验
- **相关度**: ⭐⭐ 方法论启发

---

## 安全相关 (Prompt Injection)

### 9. Persona_Anchor_Exploit
- **URL**: https://github.com/HFgh1276/LLM-Persona-Anchor-Exploit
- **Stars**: 1
- **重点**: 通过多轮上下文锚定绕过安全对齐
- **相关度**: ⭐⭐⭐ 与 T3 (prompt injection 方案) 安全考量相关

---

## T1 结论与 T2-T6 建议

### 技术路线评估

| 方法 | 稳定性 | 数据需求 | 可实现性 | 推荐度 |
|------|--------|----------|----------|--------|
| Prompt-based (ephemeral system prompt) | ⭐⭐ | 极低 | 最高 | ⭐⭐⭐ |
| Fine-tuning (LoRA/QLoRA) | ⭐⭐⭐⭐ | 中等 | 中等 | ⭐⭐⭐⭐ |
| RAG-based memory | ⭐⭐⭐ | 低 | 高 | ⭐⭐⭐ |

### T2 建议: 语言风格分析
- 现有 raw.md 和历史对话数据足以开始
- 需要提取的维度: 词汇频率、句法结构、修辞手法、语气模式

### T3 建议: Prompt Injection 方案
- 参考 Persona-Evolve 的 "implicit behavioral alignment"
- 关键设计: 系统 prompt 应描述行为模式而非直接规定输出
- 安全考虑: 参考 Persona_Anchor_Exploit 的脱靶案例

### T6 建议: Hermes Personality Entry
- shard 项目提供了实际实现参考
- LoRA 微调是最可行的方案 (QLoRA 可在消费级硬件运行)

---

*此报告由 RALPH Loop iteration 20 自动完成*
