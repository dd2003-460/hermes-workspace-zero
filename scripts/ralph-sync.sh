#!/bin/bash
# ralph-sync.sh — 从项目 loop-state.json 生成兼容的 ACTIVE 面板。
# 运行时状态的唯一来源是项目根目录的 loop-state.json；旧版
# ~/.claude/ralph-loop.global.md 不再覆盖项目状态。

set -euo pipefail

WORKSPACE="/Users/a1-6/Desktop/workspace"
PROJECTS_ROOT="$WORKSPACE/projects"

if [[ ! -d "$PROJECTS_ROOT" ]]; then
    exit 0
fi

if [[ -f "$WORKSPACE/scripts/aggregate-active.sh" ]]; then
    bash "$WORKSPACE/scripts/aggregate-active.sh" "$PROJECTS_ROOT" 2>/dev/null || true
fi

echo "RALPH state projection refreshed from project loop-state.json files" >&2
