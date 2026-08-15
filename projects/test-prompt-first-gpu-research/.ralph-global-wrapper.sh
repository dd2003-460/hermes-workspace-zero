#!/bin/sh
# origin: ai
# Test-only CC launcher: inject the workspace Commander prompt into each RALPH session.
GLOBAL_PROMPT_FILE=/Users/a1-6/Desktop/workspace/ralph-loop.global.md
exec /opt/homebrew/bin/claude --append-system-prompt "$(cat "$GLOBAL_PROMPT_FILE")" "$@"
