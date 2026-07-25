#!/usr/bin/env bash
# ralph loop 的健壮启动器：ralph 退出后自动重启（到终态 completed/stopped 才停），
# 避免一次崩溃就让 tmux 会话/服务整个退出。
set -u
PROJECT="${1:-.}"
RALPH=/Users/a1-6/.local/bin/ralph
PY=/Users/a1-6/.local/share/ralph-runtime/venv/bin/python
cd "$PROJECT" || exit 1
while true; do
  RALPH_FIELD_GATE=1 RALPH_PROMPT_TEMPLATE=stage_prompt_fieldcentric.md \
    "$RALPH" loop . --mode hybrid --dangerously-skip-permissions \
    --idle-timeout 600 --auto-compact-window 40000 --auto-compact-percent 80 \
    2>&1 | tee "$PROJECT/ralph.log"
  rc=$?
  st=$("$RALPH" status . 2>/dev/null | "$PY" -c "import json,sys
try: print(json.load(sys.stdin).get('status')) 
except Exception: print('')" 2>/dev/null)
  echo "[ralph exited rc=$rc status=$st at $(date)]"
  if [ "$st" = "completed" ] || [ "$st" = "stopped" ]; then
    echo "已到终态，停止重启。"; break
  fi
  echo "5 秒后重启 ralph loop ..."; sleep 5
done
