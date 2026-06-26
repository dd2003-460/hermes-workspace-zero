# D1-goal-investigation — Agent Goal 机制对比研究 — 初学者指南

> **项目**: D1-goal-investigation
> **状态**: 🟡 调研中 — 结构已修复，需重新建立探索数据
> **创建**: 2026-06-12

---

## 一、工作起点

**核心问题**：为什么 AI agent 在没有明确完成目标时就停止了？Claude Code、Codex、Hermes 三者的 goal 机制有什么不同？如何用 prompt 稳定激发 AI 的提问风格？

**背景**：用户在 551 条对话消息中，86% 围绕 goal/ralph loop 话题。goal 机制是 workspace 的核心关注点。

## 二、前人调研

| 工具 | Goal 机制 | 停止行为 |
|------|----------|---------|
| Claude Code | 显式 goal 参数 | goal 达到 → 停止；goal 模糊 → 可能提前停止 |
| OpenAI Codex | 任务导向 | 任务完成 → 停止 |
| Hermes Agent | session 导向 | turn 结束 → 等待新输入 |

**核心发现**：`stop_reason: "end_turn"` 是 turn-level 信号，不是 goal-level 信号。

## 三、相似工作

| 工作 | 相似度 | 不同 |
|------|--------|------|
| ralph-loop 机制 | 40% | 外部循环，非 session 内 goal 管理 |
| D1-continuous-agent | 50% | hook 机制，本项目的上位问题 |

## 四、工作逻辑

```
任务 1: Agent goal 运行原理对比
  → 分析 Claude Code goal 参数传递
  → 分析 Codex task 参数传递
  → 对比 stop_reason 机制
  
任务 2: Prompt 激发 AI 提问风格
  → 分析 prompt 中哪些模式激发提问行为
  → 实验：不同 prompt 策略 → 提问频率对比
```

## 五、填补空白

- 首个系统对比三家 agent goal 机制的研究
- 提出 stop_reason 是 turn-level 而非 goal-level 的关键发现

## 六、对标贡献

| 维度 | 对标 |
|------|------|
| 类型 | Agent 系统设计研究 |
| 价值 | 为 workspace 的 ralph-loop 提供理论基础 |

---

*origin: ai*
