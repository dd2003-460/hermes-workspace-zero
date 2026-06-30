#!/usr/bin/env bash
# tmux-monitor.sh — RALPH Loop 团队监控面板
# 用法: bash tmux-monitor.sh <project-dir>
# 创建 4 个 pane:
#   Pane 1 (top):    全局状态 + 迭代历史
#   Pane 2 (left):   当前 1-loop/2-loop 阶段文件
#   Pane 3 (right):  memory/ 最新修改
#   Pane 4 (bottom): 实时日志/agent 输出

set -e
PROJECT_DIR="${1:-.}"

# 创建 tmux 会话
SESSION="ralph-loop"
tmux kill-session -t "$SESSION" 2>/dev/null || true
tmux new-session -d -s "$SESSION" -n "monitor" -c "$PROJECT_DIR"

# 分割窗口
# 上半部分 (Pane 0): 全局状态
tmux split-window -v -t "$SESSION:monitor" -c "$PROJECT_DIR"
# 左下 (Pane 1): 1-loop 阶段文件
tmux split-window -h -t "$SESSION:monitor" -c "$PROJECT_DIR"
# 右下分割为两格
tmux split-window -v -t "$SESSION:monitor.2" -c "$PROJECT_DIR"
tmux split-window -v -t "$SESSION:monitor.3" -c "$PROJECT_DIR"

# ===== Pane 0: 全局状态 =====
tmux send-keys -t "$SESSION:monitor.0" "watch -n 5 'cat ~/.claude/ralph-loop.global.md'" Enter

# ===== Pane 1: 当前循环阶段文件 =====
LOOP_DIR="$PROJECT_DIR/loop"
if [ -d "$LOOP_DIR" ]; then
    tmux send-keys -t "$SESSION:monitor.1" "tail -f loop-state.json | jq ." Enter
else
    tmux send-keys -t "$SESSION:monitor.1" "echo 'No loop/ directory found'" Enter
fi

# ===== Pane 2: memory/ 最近修改 =====
tmux send-keys -t "$SESSION:monitor.2" "find notes/ memory/ -name '*.md' -type f 2>/dev/null | xargs ls -lt 2>/dev/null | head -20" Enter

# ===== Pane 3: 文件变更实时监听 =====
tmux send-keys -t "$SESSION:monitor.3" "inotifywait -m -r -e modify,create,delete notes/ memory/ tasks/ loop/ 2>/dev/null | head -50" Enter 2>/dev/null || \
tmux send-keys -t "$SESSION:monitor.3" "ls -lR notes/ memory/ | head -40" Enter

# 连接
tmux select-pane -t "$SESSION:monitor.0"
tmux attach-session -t "$SESSION"
