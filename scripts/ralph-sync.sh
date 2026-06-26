#!/bin/bash
# ralph-sync.sh — Sync ralph-loop.global.md state to project loop-state.json
# Called by the Stop hook after ralph-loop updates iteration
# Usage: bash ralph-sync.sh

set -euo pipefail

RALPH_STATE_FILE="${HOME}/.claude/ralph-loop.global.md"
WORKSPACE="/Users/a1-6/Desktop/workspace"

if [[ ! -f "$RALPH_STATE_FILE" ]]; then
    exit 0
fi

# Parse frontmatter
FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$RALPH_STATE_FILE")
get_meta() {
    echo "$FRONTMATTER" | grep "^${1}:" | head -1 | sed "s/^${1}: *//" | sed 's/^"\(.*\)"$/\1/' || true
}

OWNER_PROJECT=$(get_meta "owner_project")
LOOP_PHASE=$(get_meta "loop_phase")
ITERATION=$(get_meta "iteration")
LAST_ACTION=$(get_meta "last_action")
LAST_OUTCOME=$(get_meta "last_outcome")
LAST_INSIGHT=$(get_meta "last_insight")

if [[ -z "$OWNER_PROJECT" ]] || [[ "$OWNER_PROJECT" == "null" ]]; then
    exit 0
fi

# Find project directory
PROJECT_PATH=$(find "$WORKSPACE/projects" -name "$OWNER_PROJECT" -type d 2>/dev/null | head -1)

if [[ -z "$PROJECT_PATH" ]]; then
    echo "WARN: project directory not found for $OWNER_PROJECT" >&2
    exit 0
fi

# Smart merge: update fields from global state, preserve AI-written fields
if [[ -f "$PROJECT_PATH/loop-state.json" ]]; then
    # Merge: update iteration, loop_phase, last_updated from global
    jq \
        --arg phase "$LOOP_PHASE" \
        --argjson iter "${ITERATION:-0}" \
        --arg updated "$(date +%Y-%m-%d)" \
        '.loop_phase = $phase | .iteration = $iter | .last_updated = $updated | .status = "active"' \
        "$PROJECT_PATH/loop-state.json" > "$PROJECT_PATH/loop-state.json.tmp"
    mv "$PROJECT_PATH/loop-state.json.tmp" "$PROJECT_PATH/loop-state.json"
else
    # Create new
    jq -n \
        --arg pid "$OWNER_PROJECT" \
        --arg phase "$LOOP_PHASE" \
        --argjson iter "${ITERATION:-0}" \
        --arg updated "$(date +%Y-%m-%d)" \
        '{
            project_id: $pid,
            loop_phase: $phase,
            iteration: $iter,
            status: "active",
            last_updated: $updated
        }' > "$PROJECT_PATH/loop-state.json"
fi

# Aggregate ACTIVE.md
if [[ -x "$WORKSPACE/scripts/aggregate-active.sh" ]]; then
    bash "$WORKSPACE/scripts/aggregate-active.sh" "$WORKSPACE/projects" 2>/dev/null || true
fi

echo "Synced $OWNER_PROJECT (iter $ITERATION, phase $LOOP_PHASE) → $PROJECT_PATH/loop-state.json" >&2
