#!/bin/bash
# arxiv_submit.sh — arXiv 提交自动化脚本
# 用法: arxiv_submit.sh <project-dir> <main-paper-name> <pdf-output-dir>
# 例: arxiv_submit.sh papers/2026-GW-BacQFT GW-BacQFT-paper /path/to/supplementary/pdfs
# 产出: tar.gz 提交包 + 完整性校验报告

set -uo pipefail

PROJECT_DIR="${1:?Usage: arxiv_submit.sh <project-dir> <main-paper-name> <pdf-output-dir>}"
MAIN_NAME="${2:?missing main paper name (without .tex)}"
PDF_DIR="${3:?missing pdf output dir}"
MAIN_TEX="${MAIN_NAME}.tex"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
WORKDIR="/tmp/arxiv-submit-$TIMESTAMP"
SUBMIT_DIR="$WORKDIR/source"

echo "=== arXiv Submit Automation ==="
echo "Project: $PROJECT_DIR"
echo "Main paper: $MAIN_TEX"
echo "Supplementary PDF dir: $PDF_DIR"
echo ""

# 1. Setup
mkdir -p "$SUBMIT_DIR/figures" "$SUBMIT_DIR/pdf"

# 2. Copy main .tex
if [ ! -f "$PROJECT_DIR/$MAIN_TEX" ]; then
    echo "  [ERROR] $PROJECT_DIR/$MAIN_TEX not found"
    exit 1
fi
cp "$PROJECT_DIR/$MAIN_TEX" "$SUBMIT_DIR/$MAIN_TEX"
echo "  [OK] Main LaTeX: $MAIN_TEX"

# 3. Copy figures
for fig in "$PROJECT_DIR"/Fig*.png "$PROJECT_DIR"/Fig*.pdf; do
    [ -f "$fig" ] || continue
    FIG_BASE=$(basename "$fig")
    cp "$fig" "$SUBMIT_DIR/figures/$FIG_BASE"
    echo "  [OK] Figure: $FIG_BASE"
done

# 4. Compile main paper
cd "$SUBMIT_DIR"
echo "  [BUILD] Compiling $MAIN_TEX..."
COMPILE_OUTPUT=$(pdflatex -interaction=nonstopmode "$MAIN_TEX" 2>&1; exit 0)
echo "${COMPILE_OUTPUT: -200}"

COMPILE_PDF="${MAIN_NAME}.pdf"
if [ ! -f "$COMPILE_PDF" ]; then
    echo "  [FAIL] Compilation failed"
    exit 1
fi
PDF_SIZE=$(stat -f%z "$COMPILE_PDF" 2>/dev/null || stat -c%s "$COMPILE_PDF" 2>/dev/null)
echo "  [OK] Compiled PDF: $COMPILE_PDF ($PDF_SIZE bytes)"

# 5. Copy supplementary PDFs
for supplementary in "$PDF_DIR"/*.pdf; do
    [ -f "$supplementary" ] || continue
    SUPP_NAME=$(basename "$supplementary")
    cp "$supplementary" "$SUBMIT_DIR/pdf/$SUPP_NAME"
    echo "  [OK] Supplementary: $SUPP_NAME"
done

# 6. Generate manifest
echo "# arXiv Submission Manifest" > "$SUBMIT_DIR/SUBMISSION.manifest.txt"
echo "# Generated: $(date)" >> "$SUBMIT_DIR/SUBMISSION.manifest.txt"
echo "# Main: $MAIN_TEX" >> "$SUBMIT_DIR/SUBMISSION.manifest.txt"
echo "# Files:" >> "$SUBMIT_DIR/SUBMISSION.manifest.txt"
find "$SUBMIT_DIR" -type f | sort | while read -r f; do
    FSIZE=$(stat -f%z "$f" 2>/dev/null || stat -c%s "$f" 2>/dev/null)
    echo "  $(basename "$f") ($FSIZE bytes)" >> "$SUBMIT_DIR/SUBMISSION.manifest.txt"
done

# 7. Create tarball
cd "$WORKDIR"
TARBALL="arxiv-${MAIN_NAME}-${TIMESTAMP}.tar.gz"
tar -czf "$TARBALL" -C "$WORKDIR" source
TOTAL_SIZE=$(stat -f%z "$TARBALL" 2>/dev/null || stat -c%s "$TARBALL" 2>/dev/null)
echo ""
echo "=== Submission Package ==="
echo "Tarball: $TARBALL"
echo "Size: $TOTAL_SIZE bytes"
echo ""
echo "=== Contents ==="
tar -tzf "$TARBALL"
echo ""

# 8. Run checklist
echo "=== Checklist ==="
bash /Users/a1-6/Desktop/workspace/scripts/arxiv_submission_checklist.sh "$SUBMIT_DIR" 2>&1 || true

echo ""
echo "=== NEXT STEP ==="
echo "1. Copy $TARBALL to your machine"
echo "2. Open https://arxiv.org/submission"
echo "3. Upload $TARBALL"
echo "4. Fill metadata: title=$(grep '\\\\title' "$SUBMIT_DIR/$MAIN_TEX" | head -1)"
echo ""
echo "Temporary files: $WORKDIR"
