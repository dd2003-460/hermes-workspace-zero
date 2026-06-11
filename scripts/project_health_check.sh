#!/bin/bash
# project_health_check.sh — 跨项目状态检查
# 检查所有 D1-* 项目的 arXiv 就绪状态、文件完整性、循环状态
# 支持递归搜索嵌套在领域分类下的项目（2026-06-11 重构）

set -uo pipefail

WORKSPACE_DIR="/Users/a1-6/Desktop/workspace"
PROJECTS_DIR="$WORKSPACE_DIR/projects"

echo "=== Project Health Check ==="
echo "Timestamp: $(date)"
echo ""

# 递归查找所有 D1-* 项目（支持嵌套在领域分类下）
PROJECT_LIST=$(find "$PROJECTS_DIR" -maxdepth 3 -name "INDEX.md" -path "*/D1-*" -exec dirname {} \; 2>/dev/null | sort -u)

if [ -z "$PROJECT_LIST" ]; then
    echo "ERROR: No D1-* projects found under $PROJECTS_DIR"
    echo "Expected projects at:"
    echo "  - $PROJECTS_DIR/D1-* (flat, pre-refactor)"
    echo "  - $PROJECTS_DIR/*-*/D1-* (nested, post-refactor)"
    exit 1
fi

TOTAL_PROJECTS=0
TOTAL_TARBALLS=0
TOTAL_PDFS=0

echo "$PROJECT_LIST" | while IFS= read -r proj_dir; do
    [ -d "$proj_dir" ] || continue
    PROJ_NAME=$(basename "$proj_dir")
    TOTAL_PROJECTS=$((TOTAL_PROJECTS + 1))
    
    echo "=== $PROJ_NAME (via $(dirname "$proj_dir" | sed "s|$PROJECTS_DIR/||")) ==="
    
    # 检查 INDEX.md
    echo "  INDEX.md: $([ -f "$proj_dir/INDEX.md" ] && echo OK || echo MISSING)"
    
    # 检查 memory/
    if [ -d "$proj_dir/memory" ]; then
        MEMORY_COUNT=$(ls "$proj_dir/memory" 2>/dev/null | wc -l | xargs)
        echo "  memory/: $MEMORY_COUNT files"
    else
        echo "  memory/: NOT FOUND"
    fi
    
    # 检查 tasks/
    if [ -d "$proj_dir/tasks" ]; then
        TASKS_COUNT=$(ls "$proj_dir/tasks/" 2>/dev/null | wc -l | xargs)
        if [ "$TASKS_COUNT" -gt 0 ]; then
            echo "  tasks/: $TASKS_COUNT files"
        else
            echo "  tasks/: EMPTY"
        fi
    else
        echo "  tasks/: NOT FOUND"
    fi
    
    # 检查 arXiv 提交包
    for tarball in "$proj_dir"/papers/*arxiv*.tar.gz "$proj_dir"/papers/*arxiv-ready*/*.tar.gz; do
        [ -f "$tarball" ] || continue
        TARBALL_SIZE=$(stat -f%z "$tarball" 2>/dev/null || stat -c%s "$tarball" 2>/dev/null)
        TARBALL_NAME=$(basename "$tarball")
        echo "  [arXiv] $TARBALL_NAME ($TARBALL_SIZE bytes)"
        TOTAL_TARBALLS=$((TOTAL_TARBALLS + 1))
    done
    
    # 检查编译后的 PDF
    for pdf in "$proj_dir"/papers/*.pdf "$proj_dir"/papers/*/*.pdf; do
        [ -f "$pdf" ] || continue
        echo "$pdf" | grep -q "arxiv-ready" && continue
        PDF_SIZE=$(stat -f%z "$pdf" 2>/dev/null || stat -c%s "$pdf" 2>/dev/null)
        PDF_NAME=$(basename "$pdf")
        echo "  [PDF] $PDF_NAME ($PDF_SIZE bytes)"
        TOTAL_PDFS=$((TOTAL_PDFS + 1))
    done
    
    # 检查 latex-pandoc-convert
    if [ -d "$proj_dir/papers/latex-pandoc-convert" ]; then
        LATEX_COUNT=$(ls "$proj_dir/papers/latex-pandoc-convert/" 2>/dev/null | wc -l | xargs)
        echo "  [LaTeX] latex-pandoc-convert/ ($LATEX_COUNT files)"
    fi
    
    echo ""
done

echo "=== Summary ==="
# 使用 find 重新统计（subshell 隔离）
TOTAL_PROJECTS=$(find "$PROJECTS_DIR" -maxdepth 3 -name "INDEX.md" -path "*/D1-*" 2>/dev/null | wc -l | xargs)
TOTAL_TARBALLS=$(find "$PROJECTS_DIR" -name "*arxiv*.tar.gz" 2>/dev/null | wc -l | xargs)
TOTAL_PDFS=$(find "$PROJECTS_DIR" -name "*.pdf" 2>/dev/null | grep -v "latex-pandoc-convert\|arxiv-ready" | wc -l | xargs)

echo "  Projects: $TOTAL_PROJECTS"
echo "  arXiv tarballs: $TOTAL_TARBALLS"
echo "  Compiled PDFs: $TOTAL_PDFS"
echo ""

if [ "$TOTAL_TARBALLS" -ge 2 ]; then
    echo "Health: GOOD - $TOTAL_TARBALLS arXiv submissions ready"
elif [ "$TOTAL_TARBALLS" -ge 1 ]; then
    echo "Health: WARNING - Only 1 submission, expected more"
else
    echo "Health: CHECK - No arXiv submissions found"
fi

echo ""
echo "=== Tools ==="
TOOLS_DIR="$WORKSPACE_DIR/scripts"
for tool in arxiv_*.sh arxiv_*.py; do
    [ -f "$TOOLS_DIR/$tool" ] || continue
    echo "  [TOOL] $TOOLS_DIR/$tool"
done
