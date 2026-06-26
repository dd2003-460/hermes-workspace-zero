# D1-continuous-agent — Agent 持续循环机制 — 初学者指南

> **项目**: D1-continuous-agent
> **状态**: 🟡 研究阶段 — Hermes Gateway Hook 机制已验证
> **创建**: 2026-05-13, **最后更新**: 2026-05-25 (iteration 95)

---

## 一、工作起点

**核心问题**：如何让 AI agent 在完全停止后自动恢复工作？当 agent 没有工具在跑、没有子 agent、没有命令执行时，如何注入新 prompt 让它继续工作而不中断？

**动机**：在 ralph-loop 工作流中，agent 完成任务后经常"停住"等待用户输入。理想情况下，agent 应该能自主继续探索新方向。

## 二、前人调研

| 工具 | stop hook 能力 | 说明 |
|------|---------------|------|
| Claude Code | ✅ stop hook (sh/bash) | 可以在 agent 结束时触发脚本 |
| OpenAI Codex | ❌ 无公开 hook 机制 | — |
| Hermes Agent | ✅ Gateway hooks (agent:end) | 观察者型事件，但**不能注入 prompt** |

## 三、相似工作

| 工作 | 相似度 | 不同 |
|------|--------|------|
| Claude Code stop-hook.sh | 70% | 我们深入分析了 stop hook 的注入限制 |
| ralph-loop 方案 | 50% | 通过 global.md + cron 触发，非 session 内注入 |

## 四、工作逻辑

```
Step 1: 分析 Claude Code stop hook 机制
  → 发现 stop hook 可以执行外部脚本
  → 但无法注入 prompt 到当前 session
  
Step 2: 分析 Hermes Gateway Hooks
  → 发现 agent:end 是观察者型事件（broadcast）
  → 源码验证：是单向广播，不能注入 prompt
  
Step 3: 结论 — 真正的"session 内注入"在所有平台都不可行
  → 替代方案：ralph-loop + cron + global.md（当前工作区使用）
```

## 五、填补空白

- 首次系统对比 Claude Code / Codex / Hermes 三种 agent 的 hook 机制
- 明确"stop hook 不能注入 prompt"的技术限制
- 提出替代方案：通过外部文件（global.md）+ cron 触发实现等效效果

## 六、对标贡献

| 维度 | 对标 |
|------|------|
| 类型 | Agent 系统分析 / 基础设施 |
| 价值 | 为 workspace 的持续循环机制提供技术基础 |

---

*origin: ai*
