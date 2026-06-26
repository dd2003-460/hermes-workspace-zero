---
name: implementation-plan
description: 具体实现步骤——创建loop-state.json模板、聚合脚本、更新索引
metadata:
  type: project
---

# 实现计划

## Step 0：为当前活跃项目创建 loop-state.json

为 `D1-area-quantized-black-hole-QNM` 创建初始 loop-state.json：

```json
{
  "project_id": "D1-area-quantized-black-hole-QNM",
  "loop_phase": "1-loop/decision",
  "iteration": 13,
  "status": "active",
  "current_task": "Teukolsky+AIM 实现路线",
  "last_action": "E_lm high-order coefficient analysis",
  "last_outcome": "Teukolsky+AIM confirmed as only path",
  "last_updated": "2026-06-22",
  "blocker": null
}
```

## Step 1：更新 projects/INDEX.md

在理论物理 INDEX.md 顶部增加 ACTIVE 区：

```markdown
## 当前焦点

- D1-area-quantized-black-hole-QNM (iteration 13, phase: 1-loop/decision)
```

## Step 2：创建聚合脚本

```bash
#!/bin/bash
# scripts/aggregate-active.sh
# 从所有 loop-state.json 聚合，生成 ACTIVE 表

find projects/ -name "loop-state.json" -exec jq -r '[.project_id,.loop_phase,.iteration,.status] | @tsv' {} \;
```

## Step 3：修改 AGENTS.md 入口链

在 AGENTS.md 的"会话最小阅读链路"部分添加 projects/INDEX.md。

## Step 4：定义 loop 迭代的双写规范

在每个 2-loop 迭代的 verify 阶段，增加一步：
- 写 `loop-state.json`（当前迭代结果）
- 跑 `aggregate-active.sh`（更新全局索引）

## 给 RALPH hook 的改造建议

在 stop-hook.sh 迭代更新后，加一个 sync 步骤：
```bash
# After updating iteration in global state, also write to project
if [ -n "$OWNER_PROJECT" ]; then
    OWNER_DIR=$(echo "$OWNER_PROJECT" | sed 's/D1-//')
    # Find the project directory
    PROJECT_PATH=$(find "$WORKSPACE" -name "$OWNER_PROJECT" -type d 2>/dev/null | head -1)
    if [ -n "$PROJECT_PATH" ]; then
        # Extract relevant fields and write loop-state.json
        jq -n \
          --arg pid "$OWNER_PROJECT" \
          --arg phase "$LOOP_PHASE" \
          --argjson iter "$ITERATION" \
          --arg action "$LAST_ACTION" \
          --arg outcome "$LAST_OUTCOME" \
          --arg updated "$(date +%Y-%m-%d)" \
          '{
            project_id: $pid,
            loop_phase: $phase,
            iteration: $iter,
            last_action: $action,
            last_outcome: $outcome,
            last_updated: $updated,
            status: "active"
          }' > "$PROJECT_PATH/loop-state.json"
    fi
fi
```

这样 hook 自动维护项目状态，AI 不需要手动双写。
