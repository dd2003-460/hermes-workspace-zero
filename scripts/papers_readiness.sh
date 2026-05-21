#!/bin/bash
# papers_readiness.sh — 综合论文就绪度检查
# 检查所有 D1 项目的 arXiv 就绪状态

PROJECTS_DIR="/Users/a1-6/Desktop/workspace/projects"

echo "====================================="
echo "  论文就绪度综合检查"
echo "  $(date)"
echo "====================================="
echo ""

PASS=0
FAIL=0
WARN=0

for proj_dir in "$PROJECTS_DIR"/D1-grav-waves "$PROJECTS_DIR"/D1-academic-AI; do
    [ -d "$proj_dir" ] || continue
    PROJ_NAME=$(basename "$proj_dir")

    echo "=== $PROJ_NAME ==="

    # Find all tarballs
    TARBALLS=$(find "$proj_dir" -name "*arxiv*.tar.gz" -o -name "*submission*.tar.gz" 2>/dev/null | grep -v latex-pandoc)
    if [ -z "$TARBALLS" ]; then
        echo "  [WARN] No submission tarballs found"
        WARN=$((WARN + 1))
    else
        for tb in $TARBALLS; do
            TARBALL_SIZE=$(stat -f%z "$tb" 2>/dev/null || stat -c%s "$tb" 2>/dev/null)
            echo "  [PASS] Tarball: $(basename "$tb") ($TARBALL_SIZE bytes)"
            PASS=$((PASS + 1))
        done
    fi

    # Find compiled PDFs
    PDFS=$(find "$proj_dir" -name "*.pdf" -not -name "*.pdfa" 2>/dev/null | grep -v latex-pandoc | grep -v arxiv-ready)
    for pdf in $PDFS; do
        PDF_SIZE=$(stat -f%z "$pdf" 2>/dev/null || stat -c%s "$pdf" 2>/dev/null)
        echo "  [PASS] PDF: $(basename "$pdf") ($PDF_SIZE bytes)"
        PASS=$((PASS + 1))
    done

    # Check for non-ASCII in .tex files
    TEX_FILES=$(find "$proj_dir" -name "*.tex" 2>/dev/null | grep -v latex-pandoc | grep -v "arxiv-ready")
    for tex in $TEX_FILES; do
        NON_ASCII=$(grep -Pc '[^\x00-\x7F]' "$tex" 2>/dev/null || true)
        if [ "$NON_ASCII" -gt 0 ] 2>/dev/null; then
            echo "  [WARN] Non-ASCII in $(basename "$tex") ($NON_ASCII lines)"
            WARN=$((WARN + 1))
        fi
    done

    echo ""
done

# Tools check
echo "=== 工具链 ==="
TOOLS="/Users/a1-6/Desktop/workspace/scripts"
for tool in arxiv_submit.sh arxiv_submission_checklist.sh arxiv_cat.py arxiv_prepare.py project_health_check.sh; do
    if [ -f "$TOOLS/$tool" ]; then
        echo "  [PASS] $tool"
        PASS=$((PASS + 1))
    else
        echo "  [FAIL] $tool"
        FAIL=$((FAIL + 1))
    fi
done

echo ""
echo "====================================="
echo "  总计: PASS=$PASS FAIL=$FAIL WARN=$WARN"
echo "====================================="

if [ "$FAIL" -gt 0 ]; then
    echo "状态: 有阻塞项"
elif [ "$WARN" -gt 3 ]; then
    echo "状态: 有警告，建议审查"
else
    echo "状态: 论文就绪，等待作者确认"
fi
