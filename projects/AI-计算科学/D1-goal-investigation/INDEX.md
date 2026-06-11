# D1 Goal Investigation — INDEX

## 项目目标

调查 Claude Code 的 goal 机制，理解其与 Ralph Loop 的区别、交互和整合方式。

## 背景

用户在551条对话消息中，86%围绕goal/ralph loop。goal机制是项目的核心关注点。

## 结构

| 目录 | 内容 |
|------|------|
| researches/ | 调研文档 |
| memory/ | 探索记录 |
| tasks/ | 任务板 |
| raw/ | 原始资料 |

## 任务

1. **goal机制技术调查** — /goal命令的工作原理、持久化、执行
2. **Ralph Loop vs /goal 对比** — 两者区别、互补、冲突
3. **提取对话记录中的用户消息** — 从JSONL日志中提取551条用户消息
4. **goal架构设计** — 设计一个更robust的goal管理系统
