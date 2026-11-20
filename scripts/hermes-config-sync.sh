#!/bin/bash
# hermes-config 同步脚本：把 ~/.hermes 关键资产快照到私有 git 仓库
# 用法: bash scripts/hermes-config-sync.sh   (cron 每小时跑一次)
# 保护对象: rules/ agent-hooks/ config.yaml .stage-gate/ (迁移 harness 不丢)
set -euo pipefail
REPO="$HOME/.hermes/.hermes-config-repo"
SRC="$HOME/.hermes"

# 排除大文件/缓存/备份噪声
EXCLUDES=(
  --exclude='__pycache__'
  --exclude='*.pyc'
  --exclude='*.bak-*'
  --exclude='.chat-counter-*'
  --exclude='*.jsonl'
  --exclude='state/'
)

if [ ! -d "$REPO/.git" ]; then
  git clone --quiet https://github.com/dd2003-460/hermes-config.git "$REPO" 2>/dev/null || {
    mkdir -p "$REPO"
    git -C "$REPO" init --quiet
    git -C "$REPO" remote add origin https://github.com/dd2003-460/hermes-config.git
  }
fi

# rsync 快照 (不删远端仓库已有文件, 只增量同步)
for asset in rules agent-hooks .stage-gate; do
  rsync -a --delete "${EXCLUDES[@]}" "$SRC/$asset/" "$REPO/$asset/" 2>/dev/null || \
  rsync -a "${EXCLUDES[@]}" "$SRC/$asset/" "$REPO/$asset/"
done
cp "$SRC/config.yaml" "$REPO/config.yaml"

# 生成资产清单 (人可读的迁移说明)
{
  echo "# hermes-config 资产清单 (自动生成 $(date '+%F %T'))"
  echo
  echo "## 迁移恢复步骤"
  echo '1. 把本仓库各目录 rsync 回 ~/.hermes/ 对应位置'
  echo '2. config.yaml 的 hooks 段指向 ~/.hermes/agent-hooks/ 和 workspace/.hooks/, 路径不变则直接生效'
  echo '3. 验证: hermes 起一轮, 看规则注入是否出现'
  echo
  echo "## 当前资产"
  ls "$REPO"
} > "$REPO/MANIFEST.md"

cd "$REPO"
git add -A
if git diff --cached --quiet; then
  echo "no-change $(date '+%F %T')"
else
  git commit --quiet -m "snapshot $(date '+%F %T %z')"
  git push --quiet origin HEAD
  echo "pushed $(git rev-parse --short HEAD) $(date '+%F %T')"
fi
