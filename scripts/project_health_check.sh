#!/bin/bash
# project_health_check.sh — 跨项目状态检查
# 检查所有 D1-* 项目的 arXiv 就绪状态、文件完整性、循环状态

set -uo pipefail

PROJECTS_DIR="/Users/a1-6/Desktop/workspace/projects"
echo "=== Project Health Check ==="
echo "Timestamp: $(date)"
echo ""

for proj_dir in "$PROJECTS_DIR"/D1-*; do
    [ -d "$proj_dir" ] || continue
    PROJ_NAME=$(basename "$proj_dir")
    echo "=== $PROJ_NAME ==="
    echo "  INDEX.md: $([ -f "$proj_dir/INDEX.md" ] && echo OK || echo MISSING)"
    echo "  memory/: $([ -d "$proj_dir/memory" ] && echo "$(ls "$proj_dir/memory" 2>/dev/null | wc -l | xargs) files" || echo MISSING)"
    TASKS_COUNT=$(ls "$proj_dir/tasks/" 2>/dev/null | wc -l | xargs)
    if [ -d "$proj_dir/tasks" ] && [ "$TASKS_COUNT" -gt 0 ]; then
        echo "  tasks/: $TASKS_COUNT files"
    elif [ -d "$proj_dir/tasks" ]; then
        echo "  tasks/: EMPTY"
    else
        echo "  tasks/: NOT FOUND (check path)"
    fi

    # Check for arXiv submission packages
    for tarball in "$proj_dir"/papers/*arxiv*.tar.gz "$proj_dir"/papers/*arxiv-ready*/*.tar.gz; do
        [ -f "$tarball" ] || continue
        TARBALL_SIZE=$(stat -f%z "$tarball" 2>/dev/null || stat -c%s "$tarball" 2>/dev/null)
        TARBALL_NAME=$(basename "$tarball")
        echo "  [arXiv] $TARBALL_NAME ($TARBALL_SIZE bytes)"
    done

    # Check for compiled PDFs
    for pdf in "$proj_dir"/papers/*.pdf "$proj_dir"/papers/*/*.pdf; do
        [ -f "$pdf" ] || continue
        # Skip supplementary PDFs in arxiv-ready/
        echo "$pdf" | grep -q "arxiv-ready" && continue
        PDF_SIZE=$(stat -f%z "$pdf" 2>/dev/null || stat -c%s "$pdf" 2>/dev/null)
        PDF_NAME=$(basename "$pdf")
        echo "  [PDF] $PDF_NAME ($PDF_SIZE bytes)"
    done

    # Check for latex-pandoc-convert
    if [ -d "$proj_dir/papers/latex-pandoc-convert" ]; then
        LATEX_COUNT=$(ls "$proj_dir/papers/latex-pandoc-convert/" 2>/dev/null | wc -l | xargs)
        echo "  [LaTeX] latex-pandoc-convert/ ($LATEX_COUNT files)"
    fi

    echo ""
done

echo "=== Tools ==="
TOOLS_DIR="/Users/a1-6/Desktop/workspace/scripts"
for tool in arxiv_*.sh arxiv_*.py; do
    [ -f "$TOOLS_DIR/$tool" ] || continue
    echo "  [TOOL] $TOOLS_DIR/$tool"
done

echo ""
echo "=== Summary ==="
TOTAL_PROJECTS=$(ls -d "$PROJECTS_DIR"/D1-* 2>/dev/null | wc -l | xargs)
TOTAL_TARBALLS=$(find "$PROJECTS_DIR" -name "*arxiv*.tar.gz" 2>/dev/null | wc -l | xargs)
TOTAL_PDFS=$(find "$PROJECTS_DIR" -name "*.pdf" 2>/dev/null | grep -v "latex-pandoc-convert\|arxiv-ready" | wc -l | xargs)
echo "  Projects: $TOTAL_PROJECTS"
echo "  arXiv tarballs: $TOTAL_TARBALLS"
echo "  Compiled PDFs: $TOTAL_PDFS"
echo ""
echo "Health: $([ "$TOTAL_TARBALLS" -ge 2 ] && echo "GOOD - 2 arXiv submissions ready" || echo "CHECK - fewer submissions than expected")"
