#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL_ROOT="${RALPH_RUNTIME_HOME:-$HOME/.local/share/ralph-runtime}"
VENV="$INSTALL_ROOT/venv"

mkdir -p "$INSTALL_ROOT" "$HOME/.local/bin"
python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install -e "$ROOT/loop/ralph_runtime"

cat >&2 <<EOF
RALPH runtime installed.
Binary: $VENV/bin/ralph
Convenience launcher: $HOME/.local/bin/ralph
EOF
