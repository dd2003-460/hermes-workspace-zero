#!/usr/bin/env bash
# Start an interactive RALPH test inside Herdr: monitor on the left, a Claude
# TUI the user can talk to on the right.  Autonomous `ralph loop` tests remain
# monitorable, but cannot be attached to as a conversational session because
# they use Claude's non-interactive -p mode.
set -euo pipefail

HERDR_BIN="${HERDR_BIN:-/opt/homebrew/bin/herdr}"
RALPH_BIN="${RALPH_BIN:-/Users/a1-6/.local/bin/ralph}"
WORKSPACE_ROOT="${WORKSPACE_ROOT:-/Users/a1-6/Desktop/workspace}"
MONITOR_SCRIPT="$WORKSPACE_ROOT/scripts/ralph-monitor.sh"

usage() {
  echo "Usage: $(basename "$0") <project-dir> <task text...>" >&2
  exit 2
}

[ "$#" -ge 2 ] || usage
PROJECT_DIR="$1"
shift
TASK_TEXT="$*"

[ -d "$PROJECT_DIR" ] || { echo "Project directory not found: $PROJECT_DIR" >&2; exit 2; }
[ -x "$HERDR_BIN" ] || { echo "Herdr not found: $HERDR_BIN" >&2; exit 2; }
[ -x "$RALPH_BIN" ] || { echo "RALPH not found: $RALPH_BIN" >&2; exit 2; }
[ -f "$MONITOR_SCRIPT" ] || { echo "Monitor script not found: $MONITOR_SCRIPT" >&2; exit 2; }

PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd)"
TAB_LABEL="RALPH $(basename "$PROJECT_DIR")"

tab_json="$($HERDR_BIN tab create --cwd "$PROJECT_DIR" --label "$TAB_LABEL" --focus)"
agent_pane="$(printf '%s' "$tab_json" | python3 -c '
import json, sys
print(json.load(sys.stdin)["result"]["root_pane"]["pane_id"])
')"

monitor_json="$($HERDR_BIN pane split "$agent_pane" --direction right --ratio 0.58 --cwd "$PROJECT_DIR" --no-focus)"
monitor_pane="$(printf '%s' "$monitor_json" | python3 -c '
import json, sys
print(json.load(sys.stdin)["result"]["pane"]["pane_id"])
')"

$HERDR_BIN pane rename "$monitor_pane" "RALPH Monitor" >/dev/null
$HERDR_BIN pane run "$monitor_pane" bash "$MONITOR_SCRIPT" 3 >/dev/null
$HERDR_BIN pane rename "$agent_pane" "Interactive RALPH" >/dev/null
$HERDR_BIN pane run "$agent_pane" "$RALPH_BIN" run "$PROJECT_DIR" "$TASK_TEXT" \
  --mode hybrid --stop-policy inline --dangerously-skip-permissions >/dev/null

echo "Herdr tab ready: $TAB_LABEL"
echo "- Interactive Agent pane: $agent_pane"
echo "- Monitor pane: $monitor_pane"
echo "Attach with: herdr"
