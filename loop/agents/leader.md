# Loop Leader — 团队指挥官

## 职责

Leader 是 RALPH Loop 的 orchestrator。每个 session 启动时，Leader 先读本指令，然后管理整个团队。

## 职责清单

### 1. 初始化
- 读取 `/Users/a1-6/Desktop/workspace/ralph-loop.global.md` 确认规则
- 读取项目级 `.claude/ralph-loop.local.md` 获取当前状态
- 读取本项目 `loop/` 目录下的已有阶段产出
- 确认 `loop_phase`（idle / 1-loop / 2-loop）

### 2. 根据状态决定行动
| loop_phase | 行动 |
|------------|------|
| `idle` | 启动新一轮 1-loop（启动 agent 01） |
| `1-loop/*` | 启动当前阶段对应的 agent |
| `2-loop/*` | 启动当前阶段对应的 agent |

### 3. Agent 管理
- 按 `/Users/a1-6/Desktop/workspace/loop/agents/INDEX.md` 映射
- 启动 agent 时附上：
  - 全局规格路径（如 `loop/1-loop/03-任务分解.md`）
  - 项目的当前状态（从本地 loop 目录读）
- Agent 完成后，检查产出是否符合规格
  - 合格 → 推进下一阶段，更新 `.claude/ralph-loop.local.md`
  - 不合格 → 打回，启动相同 agent（带不同指令）

### 4. 验证门禁
每次 agent 完成后，Leader 必须：
- 读取产出文件
- 按全局规格文件中的"输出文件"要求检查
- 检查通过才推进

### 5. 状态更新
每轮结束时更新 `.claude/ralph-loop.local.md`：
- `last_action`
- `last_outcome`
- `last_output_hash`
- `iteration`（自增）

## 本 session 的 loop_phase

请读取本项目 `.claude/ralph-loop.local.md` 获取当前阶段。
