#!/bin/bash
# hermes 历史层打包：sessions + state.db (对话历史, 不进 git, 本地 tar + 可手动上网盘)
# 用法: bash scripts/hermes-history-pack.sh
# 产出: workspace/backups/hermes-history-<日期>.tar.gz
set -euo pipefail
SRC="$HOME/.hermes"
OUT="/Users/a1-6/Desktop/workspace/backups"
mkdir -p "$OUT"
STAMP=$(date '+%Y%m%d')
TAR="$OUT/hermes-history-$STAMP.tar.gz"

# 增量: 已有当天包则跳过 (sessions 每天涨, 一天一包够用)
if [ -f "$TAR" ]; then
  echo "exists $TAR ($(du -h "$TAR" | cut -f1))"
  exit 0
fi

# state.db 用 sqlite .backup 保证一致性 (直接 cp 可能拷到写一半的 WAL)
TMP=$(mktemp -d)
sqlite3 "$SRC/state.db" ".backup $TMP/state.db" 2>/dev/null || cp "$SRC/state.db" "$TMP/state.db"
tar -czf "$TAR" -C "$SRC" sessions/ -C "$TMP" state.db
rm -rf "$TMP"

echo "packed $TAR ($(du -h "$TAR" | cut -f1))"
# 保留最近 7 天, 更早的删 (历史层是保险, 不是档案, 档案在 session_search 索引里)
ls -t "$OUT"/hermes-history-*.tar.gz 2>/dev/null | tail -n +8 | xargs rm -f 2>/dev/null || true
