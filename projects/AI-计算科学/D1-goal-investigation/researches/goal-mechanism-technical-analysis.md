# Goal 机制技术调查

**生成时间**: 2026-06-10 (Iteration 26)
**项目**: D1-goal-investigation
**目的**: 调查 Claude Code 的 goal 机制，理解与 Ralph Loop 的区别

---

## 核心发现

### Claude Code 没有内置的 /goal 命令

经过调查确认：**Claude Code 没有原生的 /goal 命令**。用户在对话中多次提及 "/goal"，但实际存在的是：

1. **Ralph Loop 插件** (`/ralph-loop`, `/cancel-ralph`) — 用 stop hook 实现无限循环
2. **Ralph Loop 全局状态** (`~/.claude/ralph-loop.global.md`) — 跨会话状态持久化
3. **Claude Code 的技能/命令系统** — 但没有 goal 相关的内置命令

用户所指的 "goal" 实际上是 Ralph Loop 的全局状态文件 (`ralph-loop.global.md`) 中的隐含目标声明。

---

## Ralph Loop 机制架构

### 组件

| 组件 | 路径 | 作用 |
|------|------|------|
| 状态文件 (session) | `.claude/ralph-loop.local.md` | 当前会话的迭代状态 |
| 状态文件 (global) | `~/.claude/ralph-loop.global.md` | 跨会话的全局状态 |
| Stop Hook | `hooks/stop-hook.sh` | 阻止退出，注入相同prompt |
| Setup Script | `scripts/setup-ralph-loop.sh` | 创建状态文件 |

### 执行流程

```
用户启动 /ralph-loop "prompt"
       ↓
setup-ralph-loop.sh 创建 .claude/ralph-loop.local.md
       ↓
Claude 执行任务
       ↓
Claude 尝试 exit
       ↓
stop-hook.sh 拦截
       ↓
检查状态文件 → 检查 session_id → 提取 prompt
       ↓
输出 JSON: {"decision": "block", "reason": prompt, "systemMessage": msg}
       ↓
Claude 收到相同 prompt，看到之前的输出，继续
       ↓
直到 completion-promise 或 max-iterations
```

### 关键机制

1. **Stop Hook 拦截**: 当 Claude 尝试退出时，stop hook 返回 JSON 阻止退出
2. **Prompt 注入**: Hook 读取状态文件中的 prompt 文本，通过 `reason` 字段注入
3. **自引用**: Claude 在下次迭代中"看到"自己之前的工作（通过文件内容），而非通过 prompt 传递
4. **Session 隔离**: hook 检查 `session_id` 匹配，防止跨会话干扰
5. **Completion Promise**: 检测 `<promise>TEXT</promise>` 标签来决定何时退出

### 局限性

1. **Single-session**: local.md 只在当前会话有效，新会话需重新启动
2. **Prompt 固定**: 每次迭代注入相同的 prompt，无法动态调整
3. **无优先级**: 只有一个 prompt，无法多任务并行
4. **No goal hierarchy**: 没有目标树/子目标机制
5. **Single task per session**: 一个 loop 只处理一个任务
6. **Manual state management**: 需要手动创建/删除状态文件

---

## 用户的全局 Goal 机制

### `~/.claude/ralph-loop.global.md`

这是用户的**自定义 goal 持久化机制**，不是 Claude Code 内置功能。

```yaml
active: true
iteration: 25
session_id: goal-autonomous-execution
max_iterations: 100000
loop_phase: 1-loop/09 (iteration 25 — S17-1 empirical verification complete)
started_at: "2026-06-02"
last_action: "..."
last_outcome: "..."
last_insight: "..."
last_output_hash: CHANGING_EVERY_ITERATION
```

**设计**: 将 loop 状态持久化到全局文件，实现跨会话的 goal 继承。

**限制**:
- 需要 Agent 在每次会话开始时手动读取并恢复状态
- 没有自动的 session 隔离（任何新会话都会"继承"goal）
- 没有自动的 goal 优先级管理

---

## /goal vs Ralph Loop 对比

| 特性 | Ralph Loop (/ralph-loop) | 用户的全局 Goal 机制 | 理想 Goal 系统 |
|------|-------------------------|---------------------|---------------|
| 持久化 | .claude/ (session-local) | ~/.claude/global.md (global) | 服务端/分布式 |
| 跨会话 | No | Yes (手动恢复) | Yes (自动) |
| 任务优先级 | No (single prompt) | No (single prompt) | Yes (task queue) |
| 子目标 | No | No | Yes |
| 并行执行 | No | No | Yes |
| 自动恢复 | Yes (stop hook) | No (需手动启动) | Yes |
| 状态可见性 | Local only | Global readable | Web dashboard |
| 验证机制 | Promise-based | 无 | 可验证输出 |
| 阻塞管理 | Max iterations | 跳过用户阻塞 | 自动优先级调整 |

---

## 建议: 理想 Goal 系统

### 核心原则

1. **Goal 声明独立于执行**: Goal 是声明式的，执行是命令式的
2. **Goal 可分解**: 大目标自动分解为子目标
3. **Goal 有优先级**: 高优先级 goal 优先执行
4. **Goal 可追踪**: 每个 goal 有状态 (pending → running → completed → blocked)
5. **Goal 可取消**: 随时可以取消或修改 goal

### 设计方向

1. **Goal 任务板**: 类似 TASKS.md 的可视化目标管理系统
2. **Goal 状态机**: Pending → Planning → Running → Verification → Completed
3. **Goal 优先级**: P0 (critical), P1 (important), P2 (nice-to-have)
4. **Goal 依赖**: 子目标不能阻塞父目标，但父子目标之间有依赖链
5. **Goal 进度追踪**: 每个 goal 有完成度百分比

### 与 Ralph Loop 的整合

当前 Ralph Loop 是**执行层**机制。理想的 Goal 系统应该是**规划层**机制。

整合方案:
```
Goal System (规划层)
  ├── 目标: "完成 Chimera 论文并提交 arXiv"
  │     ├── 子目标: "绘制 Fig4" (P0)
  │     ├── 子目标: "补充引用到35篇" (P1)
  │     └── 子目标: "添加作者信息" (P2)
  │
  └── Task Queue (任务队列)
        ├── A1: D-persona-align 外部研究 [P0, 置信度0.9]
        ├── A2: D-academic-AI 多chimera共存实验 [P0, 置信度0.95]
        └── ...

Ralph Loop (执行层)
  └── 每次执行一个任务，通过 stop hook 循环直到完成
```

---

## 数据来源

- 对话日志: `/Users/a1-6/.claude/projects/-Users-a1-6/16e2bd51-0bed-4528-a207-45bc976e29ee.jsonl` (33,945行)
- 用户消息: 551条 (86% 关于 goal/ralph loop)
- Ralph Loop 插件: `~/.claude/plugins/marketplaces/claude-plugins-official/plugins/ralph-loop/`
