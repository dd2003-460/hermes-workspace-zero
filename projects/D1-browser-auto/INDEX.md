# D1-browser-auto — 浏览器自动化大模型对话

**领域**：AI Agent / 浏览器自动化
**状态**：📋 待启动
**创建时间**：2026-07-10

## 目标

用本地 AI 驱动 Playwright 操控浏览器，稳定地与网页大模型（ChatGPT、Claude、Kimi 等）对话。

**核心挑战**：持久化登录状态 + 反自动化检测 + 多轮对话稳定性

## 项目结构

```
D1-browser-auto/
├── INDEX.md
├── raw/                          # 原始材料、方案文档
├── memory/                       # 探索记录
└── tasks/                        # 任务计划
```

## 关键概念

- **launchPersistentContext**：Playwright 持久化浏览器上下文，最稳定的登录状态保存方式
- **storageState**：轻量级状态保存/注入方式
- **反自动化检测**：网站检测 WebDriver 特征的对抗策略
- **人类行为模拟**：随机化操作节奏，避免机械模式
