#!/bin/bash
# stop-ralph-hook.sh — RALPH Loop 优雅停止钩子
# 在会话结束前运行，确保状态同步
# Usage: bash stop-ralph-hook.sh [done|aborted|idle]

set -e

PROJECT_DIR="/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应"
LOCAL_STATE="$PROJECT_DIR/.claude/ralph-loop.local.md"
LOOP_STATE="$PROJECT_DIR/loop-state.json"
SYNC_SCRIPT="$HOME/Desktop/workspace/scripts/ralph-sync.sh"
STOP_FLAG="$PROJECT_DIR/.claude/.ralph-stopped"
EXIT_STATUS="${1:-done}"

echo "[$(date)] Stopping RALPH Loop (exit_status=$EXIT_STATUS)..."

# 1. 写入停止标记
mkdir -p "$PROJECT_DIR/.claude"
echo "stopped_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$STOP_FLAG"
echo "exit_status=$EXIT_STATUS" >> "$STOP_FLAG"

# 2. 更新 loop 状态
if [ -f "$LOCAL_STATE" ]; then
    current_phase=$(grep "^loop_phase:" "$LOCAL_STATE" | head -1 | awk '{$1=""; print}' | xargs)
    current_iter=$(grep "^iteration:" "$LOCAL_STATE" | head -1 | awk '{print $2}')

    # 根据退出状态设置最终 phase
    case "$EXIT_STATUS" in
        done)
            new_phase="idle"  # 正常完成
            ;;
        aborted)
            new_phase="$current_phase"  # 保持当前 phase
            ;;
        idle)
            new_phase="idle"
            ;;
        *)
            new_phase="$current_phase"
            ;;
    esac

    cat > "$LOCAL_STATE" <<EOF
---
active: true
iteration: $current_iter
session_id: $(cat "$PROJECT_DIR/.claude/.ralph-session-id" 2>/dev/null || echo "unknown")
max_iterations: 0
started_at: "$(grep started_at "$LOCAL_STATE" 2>/dev/null | head -1 | awk '{print $2}' | tr -d '"' || echo "unknown")"
loop_phase: $new_phase
last_action: session stop
last_outcome: $EXIT_STATUS
last_insight: ""
last_completed_at: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
---

/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应/CLAUDE.md
EOF

    echo "Updated local state: iteration=$current_iter, phase=$new_phase"
fi

# 3. 更新 loop-state.json
if [ -f "$LOCAL_STATE" ]; then
    iter=$(grep "^iteration:" "$LOCAL_STATE" | head -1 | awk '{print $2}')
    phase=$(grep "^loop_phase:" "$LOCAL_STATE" | head -1 | awk '{$1=""; print}' | xargs)

    jq -n \
        --arg phase "$phase" \
        --argjson iter "${iter:-0}" \
        --arg updated "$(date +%Y-%m-%dT%H:%M:%SZ)" \
        --arg exit_status "$EXIT_STATUS" \
        '{
            project_id: "D1-grav-waves",
            loop_phase: $phase,
            iteration: $iter,
            status: $exit_status,
            last_updated: $updated,
            last_exit: $exit_status
        }' > "$LOOP_STATE"

    echo "Updated loop-state.json: $LOOP_STATE"
fi

# 4. 尝试同步到全局（如果 ralph-sync 存在）
if [ -f "$SYNC_SCRIPT" ]; then
    bash "$SYNC_SCRIPT" 2>/dev/null || true
fi

# 5. 清理临时文件
rm -f /tmp/_ralph-start.sh 2>/dev/null || true

echo "[$(date)] RALPH Loop stopped cleanly."
echo "下次启动: bash /Users/a1-6/Desktop/start-ralph-oneclick.sh"
echo "在 Claude Code 中可直接读取 .claude/ralph-loop.local.md 继续"
