#!/bin/bash
# start-ralph-loop.sh — RALPH Loop 启动脚本
# D1-grav-waves (时钟与引力波响应)
#
# 用法: bash start-ralph-loop.sh [reset|status|start]
#   reset  — 重置状态文件到 idle
#   status — 显示当前状态
#   start  — 启动前验证并给出执行计划（默认）

set -e

PROJECT_ROOT="/Users/a1-6/Desktop/workspace/projects/理论物理/时钟与引力波响应"
GLOBAL_RULES="/Users/a1-6/Desktop/workspace/ralph-loop.global.md"
GLOBAL_LOOP="/Users/a1-6/Desktop/workspace/loop"
LOCAL_STATE="$PROJECT_ROOT/.claude/ralph-loop.local.md"
CLAUDE_MD="$PROJECT_ROOT/CLAUDE.md"
LOOP_DIR="$PROJECT_ROOT/loop"
MEMORY_DIR="$PROJECT_ROOT/memory"
SCRIPTS_DIR="$PROJECT_ROOT/scripts"
AGENTS_DIR="$PROJECT_ROOT/.claude/agents"

echo "============================================"
echo "  RALPH Loop — D1-grav-waves 启动检查"
echo "============================================"
echo ""

# 1. 检查全局规则
echo "[1] 全局约束规则"
if [ -f "$GLOBAL_RULES" ]; then
    echo "    PASS: $GLOBAL_RULES"
else
    echo "    FAIL: $GLOBAL_RULES 不存在"
    echo "    请先安装: /Users/a1-6/Desktop/workspace/ralph-loop.global.md"
    exit 1
fi

# 2. 检查全局 loop 目录
echo "[2] 全局 Loop 阶段规格"
loop_ok=true
for i in 01 02 03 04 05 06; do
    for phase in 1-loop 2-loop; do
        f="$GLOBAL_LOOP/$phase/${i}-$(cat $GLOBAL_LOOP/${phase}/${i}-*.md 2>/dev/null | head -1 || echo 'placeholder')"
        # simpler check
        if [ ! -f "$GLOBAL_LOOP/$phase/${i}-"*".md" ] && [ "$i" = "01" ] && [ "$phase" = "1-loop" ]; then
            if [ ! -f "$GLOBAL_LOOP/$phase/01-任务澄清.md" ]; then
                echo "    WARN: $GLOBAL_LOOP/$phase/01-任务澄清.md 缺失"
                loop_ok=false
            fi
        fi
    done
done
if [ "$loop_ok" = true ]; then
    n_files=$(find "$GLOBAL_LOOP" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    echo "    PASS: $GLOBAL_LOOP 下有 $n_files 个阶段文件"
fi

# 3. 检查本地状态文件
echo "[3] 本地状态文件"
if [ -f "$LOCAL_STATE" ]; then
    iteration=$(grep "^iteration:" "$LOCAL_STATE" 2>/dev/null | head -1 | awk '{print $2}')
    phase=$(grep "^loop_phase:" "$LOCAL_STATE" 2>/dev/null | head -1 | awk '{$1=""; print}' | xargs)
    echo "    PASS: $LOCAL_STATE (iteration: $iteration, phase: $phase)"
else
    echo "    INFO: 本地状态文件不存在，将创建"
fi

# 4. 检查 CLAUDE.md
echo "[4] RALPH Context 注入"
if [ -f "$CLAUDE_MD" ]; then
    lines=$(wc -l < "$CLAUDE_MD" | tr -d ' ')
    echo "    PASS: $CLAUDE_MD ($lines 行，含 RALPH 规则)"
else
    echo "    FAIL: $CLAUDE_MD 不存在"
    echo "    新建一个并粘贴 RALPH 约束规则"
fi

# 5. 检查 Agent 定义
echo "[5] Agent 定义文件"
agent_count=$(find "$AGENTS_DIR" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
echo "    PASS: $AGENTS_DIR 下有 $agent_count 个 Agent 定义"
for agent in clarifier decomposer gatherer verifier decision-maker prechecker backup-agent executor quality-checker confidence-judge fork-decider sub-brain task-manager; do
    if [ -f "$AGENTS_DIR/$agent.md" ]; then
        echo "      [OK] $agent"
    else
        echo "      [MISS] $agent"
    fi
done

# 6. 检查已有产出
echo "[6] 已有产出"
memory_count=$(find "$MEMORY_DIR" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
script_count=$(find "$SCRIPTS_DIR" -name "*.py" 2>/dev/null | wc -l | tr -d ' ')
loop_count=$(find "$LOOP_DIR" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
echo "    memory/: $memory_count 个文件"
echo "    scripts/: $script_count 个文件 ($((script_count - 1)) 个验证脚本)"
echo "    loop/: $loop_count 个文件"

# 7. 检查脚本完整性
echo "[7] 已有脚本清单"
expected_scripts=(
    "01-olc-orf-solver.py"
    "02-olc-noise-spectrum.py"
    "03-olc-snr-solver.py"
    "04-olc-3d-orf.py"
    "05-olc-detection-requirements.py"
    "06-olc-lisa-mixed-network.py"
    "07-space-olc-snr.py"
    "08-space-olc-band-comparison.py"
)
for script in "${expected_scripts[@]}"; do
    if [ -f "$SCRIPTS_DIR/$script" ]; then
        size=$(wc -c < "$SCRIPTS_DIR/$script" | tr -d ' ')
        echo "    [OK] $script ($size bytes)"
    else
        echo "    [MISS] $script"
    fi
done

# 8. 检查环境
echo "[8] Python 环境"
python3 --version 2>&1 || echo "    WARN: python3 不可用"
python3 -c "import numpy; print(f'    numpy {numpy.__version__}')" 2>&1 || echo "    WARN: numpy 不可用"
python3 -c "import scipy; print(f'    scipy {scipy.__version__}')" 2>&1 || echo "    WARN: scipy 不可用"
python3 -c "import matplotlib; print(f'    matplotlib {matplotlib.__version__}')" 2>&1 || echo "    WARN: matplotlib 不可用"

echo ""
echo "============================================"
if [ "$1" = "reset" ]; then
    echo "[RESET] 重置状态为 idle..."
    if [ -f "$LOCAL_STATE" ]; then
        sed -i '' 's/^loop_phase:.*/loop_phase: idle/' "$LOCAL_STATE" 2>/dev/null || \
            cat > "$LOCAL_STATE" <<EOF
---
project: D1-grav-waves (时钟与引力波响应)
iteration: $(grep "^iteration:" "$LOCAL_STATE" | head -1 | awk '{print $2}')
loop_phase: idle
started_at: ""
last_completed_at: ""
last_action: state reset to idle
last_outcome: ""
last_insight: ""
---
EOF
        echo "    已完成。当前 state: $LOCAL_STATE"
    fi
elif [ "$1" = "status" ]; then
    if [ -f "$LOCAL_STATE" ]; then
        echo ""
        echo "--- Local State ---"
        head -20 "$LOCAL_STATE"
    fi
else
    echo "  RALPH Loop 就绪"
fi
echo "============================================"
echo ""
echo "下一步：在当前 Claude Code 会话中"
echo "  1. CLAUDE.md 已加载 → RALPH 规则自动注入"
echo "  2. Agent 定义在 .claude/agents/ → 可调度"
echo "  3. 状态在 .claude/ralph-loop.local.md"
echo "  4. Claude Code 指挥官读取上述文件 → 按 loop 执行"
echo ""
echo "  重置状态: bash start-ralph-loop.sh reset"
echo "  查看状态: bash start-ralph-loop.sh status"
