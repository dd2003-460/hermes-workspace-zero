#!/usr/bin/env bash
# ralph 项目自愈启动器(支持首轮注入任务描述)。
# 用法: ralph-run-task.sh <PROJECT_DIR> "<TASK>"
# 首轮用 `ralph run` 注入任务并启动;崩溃重启时用 `ralph loop` 续跑(不再重置任务)。
set -u
PROJECT="${1:-.}"
TASK="${2:-}"
RALPH=/Users/a1-6/.local/bin/ralph
PY=/Users/a1-6/.local/share/ralph-runtime/venv/bin/python
cd "$PROJECT" || exit 1
while true; do
  stage=$("$RALPH" status . 2>/dev/null | "$PY" -c "import json,sys
try:
 d=json.load(sys.stdin); s=d.get('stage',{}); print(s.get('id',''), s.get('revision',''))
except: print('')")
  has_task=$("$RALPH" status . 2>/dev/null | "$PY" -c "import json,sys
try:
 d=json.load(sys.stdin); print('yes' if d.get('task',{}).get('description') else 'no')
except: print('no')")
  if [ "$has_task" = "no" ] && [ -n "$TASK" ]; then
    echo "[$(date)] 首轮: ralph run (注入任务)"
    RALPH_FIELD_GATE=1 RALPH_PROMPT_TEMPLATE=stage_prompt_fieldcentric.md \
      "$RALPH" run . "$TASK" --mode shadow --dangerously-skip-permissions \
      --auto-compact-window 40000 --auto-compact-percent 80 2>&1 | tee "$PROJECT/ralph.log"
  else
    echo "[$(date)] 续跑: ralph loop"
    RALPH_FIELD_GATE=1 RALPH_PROMPT_TEMPLATE=stage_prompt_fieldcentric.md \
      "$RALPH" loop . --mode shadow --dangerously-skip-permissions \
      --idle-timeout 600 --auto-compact-window 40000 --auto-compact-percent 80 2>&1 | tee -a "$PROJECT/ralph.log"
  fi
  rc=$?
  st=$("$RALPH" status . 2>/dev/null | "$PY" -c "import json,sys
try: print(json.load(sys.stdin).get('status'))
except: print('')")
  echo "[ralph exited rc=$rc status=$st at $(date)]"
  if [ "$st" = "completed" ] || [ "$st" = "stopped" ]; then
    echo "已到终态，停止重启。"; break
  fi
  echo "5 秒后重启 ..."; sleep 5
done
