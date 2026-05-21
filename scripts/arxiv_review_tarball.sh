#!/bin/bash
# Create a review tarball with both source AND compiled PDF for author review
#
# Usage:
#   arxiv_review_tarball.sh <paper-directory> [output-tarball]
#
# Creates a review package containing:
#   - source/ (arXiv submission package)
#   - compiled/ (PDF for review)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PAPER_DIR="$1"
OUTPUT="${2:-$(basename "$PAPER_DIR" | sed 's/[_.]/-/g').review.tar.gz}"

if [ ! -d "$PAPER_DIR" ]; then
    echo "ERROR: $PAPER_DIR is not a directory"
    exit 1
fi

echo "Creating review tarball: $OUTPUT"
echo ""

# Find .tex file
TEX_FILE=$(find "$PAPER_DIR" -maxdepth 1 -name '*.tex' -not -name '*.tex.*' | head -1)
if [ -z "$TEX_FILE" ]; then
    echo "ERROR: No .tex file found"
    exit 1
fi

TEX_NAME=$(basename "$TEX_FILE" .tex)
echo "Paper: $TEX_NAME"

# Compile PDF
cd "$PAPER_DIR"
echo "Compiling PDF..."
if xelatex -interaction=nonstopmode "$TEX_NAME.tex" 2>&1 | tail -3 | grep -q "Output written"; then
    echo "  PDF compiled successfully"
elif pdflatex -interaction=nonstopmode "$TEX_NAME.tex" 2>&1 | tail -3 | grep -q "Output written"; then
    echo "  PDF compiled successfully (pdflatex)"
else
    echo "  WARNING: Compilation failed, no PDF included in review"
fi

# Create staging directory
STAGING=$(mktemp -d)
mkdir -p "$STAGING/source" "$STAGING/compiled"

# Source package (no PDF)
cd "$PAPER_DIR"
bash "$SCRIPT_DIR/arxiv_tarball.sh" "$PAPER_DIR" "/dev/stdout" 2>/dev/null | tar xzf - -C "$STAGING/source" 2>/dev/null || {
    # Fallback: manual source copy
    cp "$TEX_NAME.tex" "$STAGING/source/"
    for fig in *.png *.jpg *.eps; do
        [ -f "$fig" ] && cp "$fig" "$STAGING/source/figures/" 2>/dev/null || true
    done
    for bib in *.bib; do
        [ -f "$bib" ] && cp "$bib" "$STAGING/source/" 2>/dev/null || true
    done
}

# Compiled PDF
if [ -f "${TEX_NAME}.pdf" ]; then
    cp "${TEX_NAME}.pdf" "$STAGING/compiled/"
    SIZE=$(du -h "$STAGING/compiled/${TEX_NAME}.pdf" | cut -f1)
    echo "  PDF: ${SIZE}"
else
    echo "  WARNING: No PDF available for review"
fi

# Create review tarball
cd "$STAGING"
tar czf "$OUTPUT" source/ compiled/
cd -

rm -rf "$STAGING"

echo ""
echo "Review tarball: $OUTPUT"
echo "Contents:"
tar tzf "$OUTPUT" | head -20
echo ""
echo "This package includes both source (for arXiv) and compiled PDF (for review)."
