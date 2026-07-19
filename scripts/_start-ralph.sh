#!/bin/bash
# 兼容入口：受控 RALPH 运行时启动器。
set -euo pipefail
exec /Users/a1-6/Desktop/workspace/scripts/ralph-start "${1:-$PWD}"
