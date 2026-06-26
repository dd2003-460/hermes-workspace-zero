#!/bin/bash
# aggregate-active.sh — 从所有 loop-state.json 聚合生成 projects/INDEX.md 的 ACTIVE 表
# 用法: bash scripts/aggregate-active.sh [projects_root]
# 默认 projects_root = 脚本所在目录的 projects/

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECTS_DIR="${1:-$SCRIPT_DIR/projects}"
OUTPUT_FILE="$PROJECTS_DIR/ACTIVE.md"

if [ ! -d "$PROJECTS_DIR" ]; then
    echo "ERROR: projects directory not found: $PROJECTS_DIR"
    exit 1
fi

# Collect all loop-state.json files
STATE_FILES=$(find "$PROJECTS_DIR" -name "loop-state.json" 2>/dev/null)

if [ -z "$STATE_FILES" ]; then
    echo "No loop-state.json found under $PROJECTS_DIR"
    exit 0
fi

# Generate ACTIVE table
{
    echo "# ACTIVE — 活跃项目面板"
    echo ""
    echo "**自动生成**: $(date +%Y-%m-%d\ %H:%M) — 由 scripts/aggregate-active.sh 聚合"
    echo ""
    echo "## 焦点项目"
    echo ""
    echo "| 项目 | 相对路径 | 阶段 | 迭代 | 状态 | 当前任务 |"
    echo "|------|----------|------|------|------|----------|"

    # Sort by iteration descending (most active first)
    echo "$STATE_FILES" | while read -r state_file; do
        project_id=$(jq -r '.project_id // empty' "$state_file" 2>/dev/null)
        [ -z "$project_id" ] && continue

        phase=$(jq -r '.loop_phase // "unknown"' "$state_file" 2>/dev/null)
        iter=$(jq -r '.iteration // 0' "$state_file" 2>/dev/null)
        status=$(jq -r '.status // "unknown"' "$state_file" 2>/dev/null)
        task=$(jq -r '.current_task // "—" | if . == "null" then "—" else . end' "$state_file" 2>/dev/null)
        blocker=$(jq -r '.blocker // "null"' "$state_file" 2>/dev/null)

        # Relative path from projects/
        rel_path=$(dirname "$state_file" | sed "s|$PROJECTS_DIR/||")

        blocker_str=""
        if [ "$blocker" != "null" ] && [ -n "$blocker" ]; then
            blocker_str=" ⚠️ $blocker"
        fi

        echo "| $project_id | \`$rel_path/\` | $phase | $iter | $status | $task$blocker_str |"
    done | sort -t'|' -k4 -rn

    echo ""
    echo "---"
    echo ""
    echo "*此文件由脚本自动生成，不要手动编辑。修改请通过各项目 loop-state.json。*"
} > "$OUTPUT_FILE"

echo "Generated $OUTPUT_FILE with $(echo "$STATE_FILES" | wc -l | tr -d ' ') projects"
