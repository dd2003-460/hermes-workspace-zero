---
name: design-solution
description: 可靠loop状态管理的设计方案——固定入口+双写机制
metadata:
  type: project
---

# 设计方案：让AI可靠地找到→更新→返回 loop 状态

## 核心思路：固定入口点 + 双写机制

**问题本质**：AI 每次 session 冷启动，需要重发现当前状态。
**解法**：在 session 起点放一个固定入口文件，项目内放 loop 状态。两者自动同步。

## 设计

### 1. 项目内 loop 状态（项目内唯一真相）

每个项目新增 `loop-state.json`（固定路径）：

```json
{
  "project_id": "D1-area-quantized-black-hole-QNM",
  "loop_phase": "1-loop/decision",
  "phase_step": 3,
  "iteration": 13,
  "status": "active",
  "current_task": "Teukolsky+AIM 实现路线",
  "last_action": "E_lm high-order coefficient analysis",
  "last_outcome": "Teukolsky+AIM confirmed as only path",
  "last_updated": "2026-06-22T10:30:00",
  "session_id": "ada2e24c-13b0-4896-88ff-ba033e18f049",
  "blocker": null,
  "next_phase_action": "进入 2-loop: 实现 Teukolsky 方程的 AIMS 离散化"
}
```

**路径规范**：`projects/<domain>/<project-id>/loop-state.json`

### 2. 全局活跃面板（AI的session入口）

在 `workspace/projects/ACTIVE.md`（或者 `workspace/projects/INDEX.md` 顶部加 active 区）：

```markdown
# ACTIVE — 当前活跃项目

## 焦点项目（一个session只聚焦一个）

| 项目 | 路径 | 阶段 | 迭代 | 状态 | 阻塞 |
|------|------|------|------|------|------|
| D1-area-quantized-black-hole-QNM | `理论物理/D1-area-quantized-black-hole-QNM/` | 1-loop/decision | 13 | active | — |

## 其他活跃项目

| 项目 | 路径 | 阶段 | 迭代 | 状态 |
|------|------|------|------|------|
| D1-goal-investigation | `理论物理/D1-goal-investigation/` | 1-loop/info | 1 | active |
```

**生成方式**：由聚合脚本从各项目 `loop-state.json` 生成，不是手写。

### 3. 双写机制

每个 loop 迭代结束时执行：

```
项目 loop-state.json → 更新
projects/INDEX.md → 运行聚合脚本 → 更新 ACTIVE 表
~/.claude/ralph-loop.global.md → 同步（RALPH hook 仍读这个，兼容现有 hook）
```

或者反过来（session 开始时）：

```
~/.claude/ralph-loop.global.md → 读
projects/INDEX.md → 读 active 表
projects/<path>/loop-state.json → 读详细状态
```

**简化方案**：不维护 3 个文件的同步，只维护 2 个。
- `loop-state.json` 是项目内真相（每次迭代更新）
- `projects/INDEX.md` 的 active 表由脚本生成（不手动编辑）
- `~/.claude/ralph-loop.global.md` 仅作为 RALPH hook 兼容层，由 hook 写、不要求 AI 读

### 4. 聚合脚本

```bash
# scripts/aggregate-active.sh
# 遍历所有 loop-state.json，生成 projects/ACTIVE.md
for state in $(find projects/ -name "loop-state.json"); do
    project=$(jq -r '.project_id' $state)
    phase=$(jq -r '.loop_phase' $state)
    iteration=$(jq -r '.iteration' $state)
    status=$(jq -r '.status' $state)
    # ... append to table
done
```

在每个 loop 迭代结束时或 session 开始时调用一次。

### 5. AI 的 Session 入口流程（4步 → 3步 → 2步）

**Before（4步）**：
```
AGENTS.md → ralph-loop.global.md → 找项目目录 → tasks/TASKS.md
```

**After（2步）**：
```
AGENTS.md → projects/INDEX.md(包含active表) → 路径已知 → loop-state.json
```

如果极致简化，甚至 AGENTS.md 里加一行：
```
当前入口: projects/INDEX.md（含活跃项目表和 loop-state.json 路径）
```
这样 AI 读完 AGENTS.md 就直接知道去哪里读状态。

## 文件变更清单

| 文件 | 变更 | 说明 |
|------|------|------|
| `projects/<id>/loop-state.json` | **新建** | 每个项目的 loop 状态（固定路径） |
| `projects/INDEX.md` | 修改 | 顶部加 ACTIVE 表格 |
| `scripts/aggregate-active.sh` | **新建** | 从 loop-state.json 聚合生成 ACTIVE 表 |
| `AGENTS.md` | 修改 | 添加入口点指向 projects/INDEX.md |
| `~/.claude/ralph-loop.global.md` | 不修改 | 兼容 RALPH hook，由 hook 自动写 |

## RALPH hook 兼容性

现有 stop-hook.sh 读写 `~/.claude/ralph-loop.global.md`。
方案：**hook 保持不变**，但增加一个后处理 hook 同步全局状态到项目状态。

具体做法：在 stop-hook.sh 的最后（迭代更新完成后）加一行：
```bash
# Sync to project state
cp "$RALPH_LOOP_FILE" "$WORKSPACE_DIR/projects/$OWNER_DIR/loop-state.json"
```

或者更简洁地：让 AI 在每次迭代结束时自己写 `loop-state.json`。
RALPH hook 只管迭代计数和阻止停止，不负责状态内容。
