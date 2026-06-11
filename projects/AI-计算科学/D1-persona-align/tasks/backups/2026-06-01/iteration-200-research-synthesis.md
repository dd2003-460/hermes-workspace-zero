---
name: iteration-200-research-synthesis
description: 外部研究综述 + persona-v3 prompt self-preservation (inspired by SPASM/ContextEcho)
metadata:
  type: project
  iteration: 200
---

# Iteration 200: Research synthesis + self-preservation mechanism

## 操作

1. 将 54 篇外部研究论文信息整合为综述文档 `researches/persona-research-synthesis.md`
2. 将 SPASM/ContextEcho 的 self-preservation 机制加入 persona-v3-prompt.txt
3. 补全缺失的 iteration logs (191, 192, 193, 195)

## 关键研究洞察

### SPASM: Self-Preservation of AI Personas via Active Steering
- persona drift 是长期交互的必然现象
- AI 需要主动检测并自我修正 persona drift
- 实现: 定期检查 persona 一致性 + 自动重启

### ContextEcho: Context-Dependent Persona Drift
- persona drift 随上下文长度指数增长
- 系统 prompt 比 few-shot examples 更稳定
- persona-v3 原则应放在 system prompt 最高注意力位置

### SimPersona: Activation Patching for Persona Drift
- persona 是一个可观测的 activation subspace
- 长期对话中 persona drift 可被检测和修复
- 对 persona-v3 的启示: 6 维度可能对应 6 个 steering vector

## persona-v3-prompt.txt 变更

新增 "自我保全机制" 章节:
- drift 检测: >10 轮或 >8000 token 时自检
- drift 修复: 检测到偏离时立即重启 persona-v3
- 锚定: persona-v3 原则作为每次回应的第一思考层
- 记忆传递: 重要决策应被记录并传递

## 补全的迭代日志

- iteration-191: dashboard v1 (零 fork, 关键词匹配)
- iteration-192: drift detection --baseline
- iteration-193: dashboard v3 baseline 全量扫描
- iteration-195: behavioral negative word fix

## 教训

外部研究的价值不在于引用, 而在于具体的技术改进。SPASM 的 self-preservation 是最直接可实现的改进。
