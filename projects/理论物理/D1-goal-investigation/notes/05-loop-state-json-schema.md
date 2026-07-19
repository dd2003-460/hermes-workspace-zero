# loop-state.json Schema

> 定义 loop-state.json 的结构规范，确保脚本（aggregate-active.sh, ralph-sync.sh）的正确互操作性。

## 1. 规范版本

| 字段 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `project_id` | string | 是 | — | 项目标识符，格式 `D1-<name>` |
| `loop_phase` | string | 是 | — | 当前循环阶段，格式 `<loop>/<phase>` |
| `iteration` | integer | 是 | 0 | 循环迭代次数 |
| `status` | string | 是 | `"active"` | 项目状态：`active` / `paused` / `completed` / `blocked` |
| `current_task` | string | 是 | — | 当前任务摘要（≤80字） |
| `last_action` | string | 是 | — | 上一次动作描述 |
| `last_outcome` | string | 否 | `null` | 上一次动作的结果 |
| `last_insight` | string | 否 | `null` | 本轮迭代的核心洞察 |
| `last_updated` | string | 是 | — | ISO 8601 日期 (YYYY-MM-DD) |
| `session_id` | string | 否 | `null` | 当前会话标识 |
| `blocker` | string | 否 | `null` | 阻塞描述（如有） |
| `next_phase_action` | string | 否 | `null` | 下一阶段行动计划 |

## 2. 枚举值约束

### loop_phase 合法值

| 值 | 含义 | 子阶段 |
|---|------|--------|
| `1-loop/information` | 1-loop: 信息搜集 | — |
| `1-loop/clarification` | 1-loop: 目标澄清（等待人类确认） | — |
| `1-loop/decomposition` | 1-loop: 任务分解 | — |
| `1-loop/decision` | 1-loop: 决策 | — |
| `1-loop/execution` | 1-loop: 执行 | — |
| `1-loop/verification` | 1-loop: 验证 | — |
| `2-loop/backup` | 2-loop: 备份 | — |
| `2-loop/execution` | 2-loop: 执行 | — |
| `2-loop/verification` | 2-loop: 验证 | — |
| `2-loop/decision` | 2-loop: 决策 | — |
| `idle` | 空闲 | — |
| `idle(<reason>)` | 空闲，带原因 | 如 `idle(waiting_for_author)` |

### status 合法值

| 值 | 含义 |
|---|------|
| `active` | 进行中 |
| `paused` | 暂停（可随时恢复） |
| `completed` | 已完成 |
| `blocked` | 阻塞（需人类介入） |

## 3. 脚本契约

### aggregate-active.sh
- **读**: `project_id`, `loop_phase`, `iteration`, `status`, `current_task`, `blocker`
- **输出**: projects/ACTIVE.md（按 iteration 降序排列）
- **触发**: 每次 ralph-sync 后自动执行

### ralph-sync.sh
- **写**: `iteration`, `loop_phase`, `last_updated`, `status`
- **保留**: `current_task`, `last_action`, `last_outcome`, `last_insight`, `next_phase_action`
- **行为**: 从 ralph-loop.global.md 解析全局状态，合并到项目 loop-state.json

## 4. 示例

```json
{
  "project_id": "D1-example",
  "loop_phase": "1-loop/execution",
  "iteration": 5,
  "status": "active",
  "current_task": "示例任务描述",
  "last_action": "上一次执行的行动",
  "last_outcome": "行动结果",
  "last_insight": "本轮核心洞察",
  "last_updated": "2026-07-14",
  "session_id": null,
  "blocker": null,
  "next_phase_action": "下一步行动计划"
}
```

## 5. 迁移指南

### 旧格式 (.claude/ralph-loop.local.md)

旧格式是纯文本 key-value 对，与新格式不完全兼容。迁移步骤：

1. 解析 `.claude/ralph-loop.local.md` 的 key-value 对
2. 映射到 loop-state.json 字段
3. 添加缺失字段（`project_id`, `blocker`, `next_phase_action`）
4. 删除 `.claude/ralph-loop.local.md`
5. 在 ACTIVE.md 中可见

**注意**: `ralph-sync.sh` 已支持自动迁移，对新格式项目执行 smart merge。
