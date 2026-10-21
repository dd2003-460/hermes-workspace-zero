#!/usr/bin/env bash
# run.sh — 项目结构整理入口。用法:
#   bash run.sh --all                 # 扫 projects/ 全部 D1-* + 领域 INDEX
#   bash run.sh <proj> <proj2> ...    # 指定项目（相对 workspace 根）
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

if [ "${1:-}" = "--all" ]; then
  targets=()
  for d in projects/*/; do targets+=("$d"); done
  for d in projects/*/*/; do
    [ -f "$d/loop-state.json" ] && targets+=("$d")
  done
else
  targets=("$@")
fi

[ ${#targets[@]} -eq 0 ] && { echo "无目标"; exit 1; }
bash "$(dirname "$0")/check.sh" "${targets[@]}"
