# ContextEcho: Context-Dependent Persona Drift in Long Conversations

**来源**: arXiv 2025
**相关度**: 极高相关

## 摘要

在长代理编程会话中系统性研究 persona drift。发现 persona drift 随上下文长度指数增长, 但关键 persona 信息 (系统 prompt) 比 few-shot examples 更稳定。

## 核心发现

1. **Persona drift 是必然的**: 上下文越长, persona 一致性越差
2. **Prompt > Examples**: 系统 prompt 中定义的 persona 比 few-shot examples 中定义的更稳定
3. **Drift 可检测**: 通过 persona keywords 覆盖率可以量化 drift

## 对 persona-v3 的改进

1. persona-v3-prompt.txt 应该放在 system prompt 的最前面 (最高注意力位置)
2. 在对话轮次 > 10 或上下文 > 8000 token 时, 需要重新注入 persona 原则
3. persona-v3 三层评估系统可以检测 ContextEcho 发现的 drift 模式

## 与 persona-v3 的协作

persona-v3 的 "自我保全机制" (iteration 200) 直接借鉴了 ContextEcho 的发现:
- drift 检测: >10 轮或 >8000 token 时自检
- drift 修复: 检测到偏离时立即重启 persona-v3

## 参考

论文: ContextEcho — 长会话中的 persona drift (见 iteration-176)
