#!/usr/bin/env bash
# 稳定观测运行中的 ralph 会话（不依赖 tmux 回显，直接读 ralph 持久化状态）。
# 用法：ralph-watch.sh <项目目录>   （缺省当前目录）
set -u
PROJECT="${1:-.}"
RALPH=/Users/a1-6/.local/bin/ralph
PY=/Users/a1-6/.local/share/ralph-runtime/venv/bin/python
cd "$PROJECT" || exit 1

while true; do
  clear
  echo "===== $(date '+%Y-%m-%d %H:%M:%S') | $(basename "$PWD") ====="
  RALPH_FIELD_GATE=1 "$RALPH" status . 2>/dev/null | \
    "$PY" -c "import json,sys;d=json.load(sys.stdin);s=d.get('stage',{});print('阶段:',s.get('id'),s.get('revision'),'| 状态:',d.get('status'),'| 阶段文件:',d.get('current_artifact'))"
  echo
  echo "----- 当前字段快照 (ralph render) -----"
  RALPH_FIELD_GATE=1 "$RALPH" render . 2>/dev/null | head -40
  echo
  echo "----- 最近事件 (ralph events --tail 6) -----"
  RALPH_FIELD_GATE=1 "$RALPH" events . --tail 6 2>/dev/null | \
    "$PY" -c "import json,sys;d=json.load(sys.stdin);[print(' -',e['type'],'|',(e.get('observation') or {}).get('tool_name') or (e.get('observation') or {}).get('role'),'@',e['timestamp'][11:19]) for e in d.get('events',[])[-6:]]"
  sleep 5
done
