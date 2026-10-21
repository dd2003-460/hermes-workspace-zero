#!/usr/bin/env bash
# check.sh <dir>... — 结构体检。领域目录(projects/<域>/)只查 INDEX + 子项目可达；
# 项目目录(含 loop-state.json 或 D1-*)查完整标准结构。只报告 + 删 .DS_Store/空目录。
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
: > /tmp/tidy-report.$$.md
report(){ echo -e "$@" >> /tmp/tidy-report.$$.md; }

report "# 项目结构整理报告 $(date '+%Y-%m-%d %H:%M')"
report

for p in "$@"; do
  p="$ROOT/$p"
  [ -d "$p" ] && [ -n "$(ls -A "$p" 2>/dev/null)" ] || continue
  rel="${p#$ROOT/}"
  report "## $rel"
  report

  is_project=0
  [ -f "$p/loop-state.json" ] && is_project=1
  [[ "$p" == */D1-* ]] && is_project=1
  [ -d "$p/memory" ] && [ -d "$p/tasks" ] && is_project=1

  # 杂物（通用）
  ds=$(find "$p" -name .DS_Store -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | wc -l | tr -d ' ')
  [ "$ds" -gt 0 ] && report "- [AUTO-FIX] 删除 $ds 个 .DS_Store" && find "$p" -name .DS_Store -not -path "*/node_modules/*" -not -path "*/.git/*" -delete 2>/dev/null
  empty=$(find "$p" -type d -empty -not -path "*/.git/*" -not -path "*/node_modules/*" -not -path "*/.ttsenv/*" 2>/dev/null)
  [ -n "$empty" ] && report "- [AUTO-FIX] 删除空目录: $(echo "$empty" | tr '\n' ' ' | sed "s|$ROOT/||g")" && find "$p" -type d -empty -not -path "*/.git/*" -not -path "*/node_modules/*" -not -path "*/.ttsenv/*" -exec rmdir {} + 2>/dev/null

  if [ "$is_project" -eq 1 ]; then
    # 1. INDEX 完整性
    [ -f "$p/INDEX.md" ] && report "- [OK] INDEX.md" || report "- [MISSING] INDEX.md"
    # 2. 标准结构
    for d in memory tasks; do
      [ -d "$p/$d" ] && report "- [OK] $d/" || report "- [MISSING] $d/（红线0 标准结构）"
    done
    [ -f "$p/loop-state.json" ] && report "- [OK] loop-state.json" || report "- [MISSING] loop-state.json"
    [ -f "$p/memory/INDEX.md" ] && report "- [OK] memory/INDEX.md" || report "- [WARN] memory/INDEX.md（建议补，探索记录多时必需）"
    # 3. 顶层散文件
    topfiles=$(ls "$p" 2>/dev/null | wc -l | tr -d ' ')
    [ "$topfiles" -gt 15 ] && report "- [WARN] 项目根 $topfiles 个条目（>15，建议归类进 memory/ 或子目录）"
    # 4-5. gitignore + git 状态
    if git -C "$p" rev-parse --git-dir >/dev/null 2>&1; then
      gi=$(git -C "$p" ls-files --others --exclude-standard | wc -l | tr -d ' ')
      big=$(du -sm "$p" 2>/dev/null | awk '{print $1}')
      report "- [INFO] git 未跟踪 $gi 个；总大小 ${big}MB"
      for cand in node_modules .ttsenv; do
        [ -d "$p/$cand" ] && ! grep -qE "^/?${cand}" "$p/.gitignore" 2>/dev/null && \
          report "- [WARN] $cand/ 存在但 .gitignore 未覆盖（中间产物请补规则）"
      done
      n=$(git -C "$p" status --short | wc -l | tr -d ' ')
      unpushed=$(git -C "$p" log --oneline @{u}..HEAD 2>/dev/null | wc -l | tr -d ' ')
      report "- [INFO] 工作区变更 $n 项；未 push ${unpushed:-?} 个提交"
    fi
    # 6. 层级扇出
    subdirs=$(find "$p" -mindepth 1 -maxdepth 1 -type d -not -name .git -not -name node_modules -not -name .ttsenv 2>/dev/null | wc -l | tr -d ' ')
    [ "$subdirs" -gt 7 ] && report "- [INFO] 直接子目录 $subdirs 个（>7：迭代编号方案豁免，否则考虑拆层）"
  else
    # 领域目录：只查 INDEX + 子项目可达性
    [ -f "$p/INDEX.md" ] && report "- [OK] 领域 INDEX.md" || report "- [MISSING] 领域 INDEX.md（红线0：每层 INDEX 只描述下一层）"
    subp=$(find "$p" -mindepth 1 -maxdepth 1 -type d -name "D1-*" | wc -l | tr -d ' ')
    report "- [INFO] 子项目 $subp 个（目标 3-7；>7 考虑拆子域，迭代编号豁免）"
  fi
  report
done

cat /tmp/tidy-report.$$.md
rm -f /tmp/tidy-report.$$.md
