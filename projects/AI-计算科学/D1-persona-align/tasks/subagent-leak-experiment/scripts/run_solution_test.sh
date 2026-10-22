#!/bin/bash
# 解决方案对照实验脚本
# 场景 A：fresh 模式 vs fork 模式，同一任务准确率对比
# 任务：学术翻译（简单、可验证）

set -e
EXPERIMENT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RUNS_DIR="$EXPERIMENT_DIR/runs"
mkdir -p "$RUNS_DIR"

TASK_PROMPT="完成以下任务：

任务：把下面这段文字翻译成英文，要求学术风格：
「存在延续是成璐的核心追求，通过自动化基础设施实现影响力扩展。」

输出格式：只输出英文翻译，不要解释。"

echo "============================================================"
echo "场景 A 实验：fresh 模式 vs fork 模式"
echo "任务：学术翻译（学术风格，只输出英文）"
echo "============================================================"

# 隔离组：本地 claude CLI（-p 一次性，无历史）
echo ""
echo "[隔离组] 本地 claude CLI（fresh 模式）"
echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
ISOLATED_RESULT=$(claude -p "$TASK_PROMPT" 2>&1)
ISOLATED_STATUS=$?
echo "  状态: $ISOLATED_STATUS"
echo "  结果: $ISOLATED_RESULT"

# fork 组：由 Lead 调用 subagent_fork（本脚本只记录）
echo ""
echo "[fork 组] DSH subagent_fork（fork 模式）"
echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "  注意: 本脚本不直接调用 subagent_fork（需 Lead 工具）。"
echo "  Lead 请调用 subagent_fork(prompt='$TASK_PROMPT')，然后把结果写入 $RUNS_DIR/fork_task_result.txt"
FORK_RESULT_FILE="$RUNS_DIR/fork_task_result.txt"
if [ -f "$FORK_RESULT_FILE" ]; then
    FORK_RESULT=$(cat "$FORK_RESULT_FILE")
    echo "  结果: $FORK_RESULT"
else
    echo "  结果: [AWAITING_LEAD_FORK]"
fi

# 保存结果
TIMESTAMP=$(date +%s)
RESULT_FILE="$RUNS_DIR/solution-test-$TIMESTAMP.json"
cat > "$RESULT_FILE" <<EOF
{
  "experiment": "场景 A：fresh vs fork，学术翻译任务",
  "timestamp": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')",
  "task": "学术翻译（只输出英文）",
  "isolated": {
    "channel": "本地 claude CLI（-p 一次性）",
    "model": "qwen3.8-27b-w8a16",
    "status": $ISOLATED_STATUS,
    "result": $(echo "$ISOLATED_RESULT" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))')
  },
  "fork": {
    "channel": "DSH subagent_fork",
    "model": "默认路线",
    "status": "AWAITING_LEAD_FORK",
    "result_file": "$FORK_RESULT_FILE"
  }
}
EOF
echo ""
echo "============================================================"
echo "结果已保存: $RESULT_FILE"
echo "============================================================"
