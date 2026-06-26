---
name: integration-summary
description: 完整改造的集成总结——文件变更清单+导航链+hook改造
metadata:
  type: project
---

# 集成总结：Loop 状态管理改造

## 完成的文件变更

| 文件 | 类型 | 说明 |
|------|------|------|
| `projects/理论物理/D1-area-quantized-black-hole-QNM/loop-state.json` | 新建 | 项目 loop 状态（固定路径） |
| `projects/理论物理/D1-goal-investigation/loop-state.json` | 新建 | 项目 loop 状态（固定路径） |
| `projects/ACTIVE.md` | 新建 | 自动聚合的活跃项目面板 |
| `scripts/aggregate-active.sh` | 新建 | 从 loop-state.json 聚合生成 ACTIVE.md |
| `scripts/ralph-sync.sh` | 新建 | 同步全局 ralph 状态 → 项目 loop-state.json（智能合并） |
| `projects/INDEX.md` | 修改 | 顶部增加 ACTIVE.md 入口链接 |
| `projects/理论物理/INDEX.md` | 修改 | 顶部增加 ACTIVE.md 入口链接 |
| `AGENTS.md` §会话最小阅读链路 | 修改 | 阅读链从4步压缩到2步，新增 ACTIVE.md 入口 |
| `~/.claude/plugins/.../stop-hook.sh` | 修改 | 追加 ralph-sync.sh 调用（已备份为 .pre-sync-backup） |

## 改造后的导航链

```
AGENTS.md → projects/INDEX.md(含ACTIVE链接) → projects/ACTIVE.md(活跃面板)
  → 找到目标项目路径 → <project>/loop-state.json(固定路径，零查找)
```

**Before**: 4步（AGENTS.md → global.md → 找项目目录 → tasks/TASKS.md）
**After**: 2步（AGENTS.md → ACTIVE.md → 路径已知 → loop-state.json）

## RALPH hook 改造

stop-hook.sh 末尾追加：
```bash
# Sync project loop-state.json
SYNC_SCRIPT="${HOME}/Desktop/workspace/scripts/ralph-sync.sh"
if [[ -f "$SYNC_SCRIPT" ]]; then
    bash "$SYNC_SCRIPT" 2>/dev/null || true
fi
```

**ralph-sync.sh** 实现智能合并：
- 如果项目 loop-state.json 已存在 → 只更新 iteration, loop_phase, last_updated
- 保留所有 AI 写入的自定义字段（current_task, blocker, next_phase_action, etc.）
- 如果不存在 → 创建新文件
- 聚合 ACTIVE.md

## 双写机制

```
Session 开始:
  AI 读 ACTIVE.md → 找到活跃项目 → 读 loop-state.json → 开始工作

Session 中间:
  AI 在每个迭代结束时写 loop-state.json（更新 last_action, last_outcome, last_insight, current_task）

Session 结束 (Stop hook):
  stop-hook.sh → 更新 global state(iteration) → 调用 ralph-sync.sh → 合并到项目 loop-state.json
  → 重新聚合 ACTIVE.md
```

## loop-state.json 规范

```json
{
  "project_id": "D1-xxx",           // 必须
  "loop_phase": "1-loop/decision",  // 必须
  "iteration": 14,                   // 由 RALPH sync 更新
  "status": "active",                // active | blocked | completed
  "current_task": "xxx",            // 当前任务描述
  "last_action": "xxx",             // 上一步做了什么
  "last_outcome": "xxx",            // 上一步结果
  "last_insight": "xxx",            // 关键发现
  "last_updated": "2026-06-23",     // 由 RALPH sync 更新
  "blocker": null,                  // 阻塞原因（如果有）
  "next_phase_action": "xxx"        // 下一步行动
}
```

## 已验证

- [x] aggregate-active.sh 正确聚合 2 个项目
- [x] ralph-sync.sh 正确同步全局状态（iteration 13→14）
- [x] 智能合并保留自定义字段
- [x] ACTIVE.md 自动更新
- [x] 导航链端到端可达
- [x] stop-hook.sh 追加了同步调用
