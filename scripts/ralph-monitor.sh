#!/usr/bin/env bash
# 统一监控所有运行中的 ralph / claude 会话（带标签），设计在 tmux 监控窗口常驻运行。
# 用法：bash ralph-monitor.sh [刷新秒数]   默认 3s
# 只读进程表与 ralph 持久化状态，不干扰任何会话。
set -u
RALPH=/Users/a1-6/.local/bin/ralph
PY=/Users/a1-6/.local/share/ralph-runtime/venv/bin/python
INTERVAL="${1:-3}"

cwline() { lsof -p "$1" 2>/dev/null | awk '$4=="cwd"{print $NF; exit}'; }

stage_of() {
  local proj="$1"
  [ -z "$proj" ] && return
  RALPH_FIELD_GATE=1 "$RALPH" status "$proj" 2>/dev/null \
    | "$PY" -c "import json,sys
try:
    d=json.load(sys.stdin); s=d.get('stage',{}) or {}
    print(f\"{s.get('id','?')} {s.get('revision','')} · {d.get('status','?')}\")
except Exception: pass" 2>/dev/null
}

# 沿祖先链找 ralph loop 监督器 pid；找到则输出该 pid，否则空
ralph_parent() {
  local cur="$1" ppid cmd
  while [ -n "$cur" ] && [ "$cur" != "1" ]; do
    ppid=$(ps -o ppid= -p "$cur" 2>/dev/null | tr -d ' ')
    [ -z "$ppid" ] && break
    cmd=$(ps -o command= -p "$ppid" 2>/dev/null)
    case "$cmd" in
      *"ralph loop"*) echo "$ppid"; return ;;
    esac
    cur="$ppid"
  done
  echo ""
}

while true; do
  clear
  echo "╔══ RALPH / CLAUDE 会话监控   $(date '+%Y-%m-%d %H:%M:%S')   刷新 ${INTERVAL}s   Ctrl-C 退出 ══════════════╗"
  echo
  printf "  %-30s %-7s %-26s %-8s %s\n" "LABEL" "TYPE" "STAGE/STATUS" "PID" "PROJECT"
  echo "  ──────────────────────────────────────────────────────────────────────────────────────────"

  shown_rp=""

  # 1) 被 ralph 监督的 claude（带阶段标签）
  while read -r pid cmd; do
    [ -z "$pid" ] && continue
    rp=$(ralph_parent "$pid")
    if [ -n "$rp" ]; then
      proj=$(cwline "$pid"); [ -z "$proj" ] && proj=$(cwline "$rp")
      stage=$(stage_of "$proj")
      label=$(basename "${proj:-?}")
      printf "  %-30s %-7s %-26s %-8s %s\n" "$label" "ralph" "${stage:-?}" "$pid" "${proj}"
      case " $shown_rp " in *" $rp "*) ;; *) shown_rp="$shown_rp $rp" ;; esac
    fi
  done < <(ps -eo pid,command -w 2>/dev/null | grep -E "bin/claude|/claude " | grep -v grep | grep -v ralph-monitor)

  # 2) ralph 监督器本身（python 进程；本 tick 其 claude 子进程尚未起）
  while read -r pid cmd; do
    [ -z "$pid" ] && continue
    case " $shown_rp " in *" $pid "*) continue ;; esac
    proj=$(cwline "$pid")
    stage=$(stage_of "$proj")
    label=$(basename "${proj:-?}")
    printf "  %-30s %-7s %-26s %-8s %s\n" "$label" "ralph" "${stage:-?}" "$pid" "${proj}"
  done < <(ps -eo pid,command -w 2>/dev/null | grep -E "ralph loop" | grep -E "python|ralph_runtime" | grep -v grep | grep -v ralph-monitor)

  # 3) 独立 claude 会话（非 ralph 监督）
  while read -r pid cmd; do
    [ -z "$pid" ] && continue
    rp=$(ralph_parent "$pid")
    [ -n "$rp" ] && continue
    proj=$(cwline "$pid")
    label=$(basename "${proj:-?}")
    printf "  %-30s %-7s %-26s %-8s %s\n" "$label" "claude" "interactive" "$pid" "${proj}"
  done < <(ps -eo pid,command -w 2>/dev/null | grep -E "bin/claude|/claude " | grep -v grep | grep -v ralph-monitor)

  echo
  echo "═══ tmux 会话（查看/接管：tmux attach -t <name>）═══"
  tmux ls 2>/dev/null | sed 's/^/  /'
  echo
  echo "═══ 实时看板：ralph watch <项目路径>   ═══"
  sleep "$INTERVAL"
done
