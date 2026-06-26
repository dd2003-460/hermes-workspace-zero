---
name: current-state-analysis
description: 分析现有索引+状态文件拓扑的断裂点
metadata:
  type: project
---

# 当前状态分析：为什么AI无法可靠地找到并更新loop状态

## 现有拓扑

```
~/.claude/
  ralph-loop.global.md          ← 全局 loop 状态（只有一个，指向一个项目）

Desktop/workspace/
  AGENTS.md                     ← 全局原则（提及 ralph-loop.global.md）
  TASKS.md                      ← 全局任务摘要（手动维护，不精确）
  loop/                         ← 1-loop/2-loop 阶段文档
  projects/
    理论物理/
      INDEX.md                  ← 项目索引（纯描述，无状态）
      D1-area-quantized-black-hole-QNM/
        INDEX.md                ← 项目描述
        tasks/TASKS.md          ← 任务完成状态（临时）
        memory/                 ← 探索记录
        (没有 loop-state 文件)
```

## 断裂点

### 断裂 1：loop 状态在项目目录之外
- `ralph-loop.global.md` 在 `~/.claude/`，不在项目目录
- AI 读完 AGENTS.md 后知道要读 ralph-loop.global.md
- 但 global.md 的 `owner_project` 只指向**一个**项目
- 多项目并行时，切换项目 = 覆盖全局状态

### 断裂 2：索引链太长且不可验证
当前导航路径：
```
AGENTS.md → ralph-loop.global.md → owner_project=xxx
  → 去 projects/ 下找到 xxx
  → 读 tasks/TASKS.md 了解任务状态
```
- 4 步路径，每一步都可能失败
- 没有反向链接（从项目回到全局状态）
- 没有汇总视图（哪些项目活跃、各在什么阶段）

### 断裂 3：TASKS.md 是手写的
- 全局 TASKS.md 的状态是手写摘要，不是从各项目的 `tasks/TASKS.md` 聚合的
- 各项目 tasks/TASKS.md 只有任务完成度，没有 loop 阶段信息
- AI 写完后不会自动回写全局

### 断裂 4：session 隔离导致状态丢失
- `ralph-loop.global.md` 有 `session_id`，每次新 session 可能不识别旧状态
- 如果新 session 的 CLAUDE_CODE_SESSION_ID 不同，hook 可能创建新的状态文件
- 没有跨 session 的状态迁移机制

## 根本原因

**不是 AI 不够聪明，是文件拓扑不支持可靠导航。**

AI 的问题本质是：没有固定入口点指向当前活跃项目+loop阶段。
每次 session 开始都是"冷启动"，需要重新发现当前状态。
