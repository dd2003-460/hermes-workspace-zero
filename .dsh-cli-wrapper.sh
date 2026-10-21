#!/bin/bash
# Wrapper: run the dsh CLI (embedded in DSH Desktop app.asar) as node via the Electron helper.
export ELECTRON_RUN_AS_NODE=1
HELPER="/Applications/DSH Desktop.app/Contents/Frameworks/DSH Desktop Helper.app/Contents/MacOS/DSH Desktop Helper"
BIN="/Applications/DSH Desktop.app/Contents/Resources/app.asar/node_modules/@deepseek-ai/dsh/lib/bin.js"
exec "$HELPER" "$BIN" "$@"
