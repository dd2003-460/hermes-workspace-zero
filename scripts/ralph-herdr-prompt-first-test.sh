#!/usr/bin/env bash
# Launch a real interactive prompt-first Commander from a Herdr pane.
# Herdr's pane runner may split task text into argv entries; joining "$@"
# here preserves the task as one positional argument for ralph.
set -euo pipefail

RALPH_BIN="${RALPH_BIN:-/Users/a1-6/.local/bin/ralph}"

if [ "$#" -lt 2 ]; then
  echo "Usage: $(basename "$0") <project-dir> <task text...>" >&2
  exit 2
fi

PROJECT_DIR="$1"
shift
TASK_TEXT="$*"

RALPH_ARGS=(
  prompt-first loop "$PROJECT_DIR" "$TASK_TEXT"
  --max-cycles 1
  --idle-timeout 0
  --retry-delay 0
  --dangerously-skip-permissions
)
if [ -n "${RALPH_PROMPT_FIRST_EFFORT:-medium}" ]; then
  RALPH_ARGS+=(--effort "${RALPH_PROMPT_FIRST_EFFORT:-medium}")
fi
# Same default model weights; lower effort only keeps the local Reviewer from
# monopolizing the shared model while the Commander remains visible in Herdr.
export RALPH_PROMPT_FIRST_REVIEW_EFFORT="${RALPH_PROMPT_FIRST_REVIEW_EFFORT:-low}"
# When oMLX is available, the Reviewer calls the same default weights through
# its local OpenAI-compatible endpoint with thinking disabled and a short cap.
# It remains serial with the Commander; the runtime falls back to claude -p if
# the endpoint is unavailable.
export RALPH_PROMPT_FIRST_REVIEW_TRANSPORT="${RALPH_PROMPT_FIRST_REVIEW_TRANSPORT:-auto}"
exec "$RALPH_BIN" "${RALPH_ARGS[@]}"
