#!/bin/bash
# Create a clean arXiv tar.gz submission package.
#
# Usage:
#   arxiv_tarball.sh <paper-directory> [output-tarball]
#
# Examples:
#   arxiv_tarball.sh /path/to/paper /tmp/submission.tar.gz
#
# Requirements:
#   - .tex file must exist in the paper directory
#   - Figures (.png, .jpg, .pdf, .eps) should be in the directory
#   - .bib files are optional
#
# Creates:
#   - tar.gz archive following arXiv's format:
#     - Source directory contains: .tex, figures, .bib
#     - NO auxiliary files (.aux, .log, .out, .toc, etc)
#     - NO PDFs (arXiv compiles from .tex)
#     - Figures organized in figures/ subdirectory
#

set -euo pipefail
shopt -s nullglob

PAPER_DIR="$1"
OUTPUT="${2:-$(basename "$PAPER_DIR" | sed 's/[_.]/-/g').arxiv.tar.gz}"

if [ ! -d "$PAPER_DIR" ]; then
    echo "ERROR: $PAPER_DIR is not a directory"
    exit 1
fi

cd "$PAPER_DIR"

# Find .tex file (exclude auxiliary .log, .aux etc, but allow -converted.pdf names)
TEX_FILES=$(find . -maxdepth 1 -name '*.tex' 2>/dev/null)
if [ -z "$TEX_FILES" ]; then
    echo "ERROR: No .tex file found in $PAPER_DIR"
    exit 1
fi

# If multiple .tex files, skip auxiliary/compiled ones (those with two dots)
TEXT_ONLY=""
while IFS= read -r f; do
    [ -z "$f" ] && continue
    basename_f=$(basename "$f")
    # Skip files like foo.tex.bak or foo.tex.old
    if [[ "$basename_f" == *.tex.* ]]; then
        continue
    fi
    TEXT_ONLY="$f"
    break
done <<< "$TEX_FILES"

TEX_FILE=$(echo "$TEXT_ONLY" | cut -d/ -f2)
echo "Paper: $TEX_FILE"

# Get title from .tex file
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TITLE=$(python3 "$SCRIPT_DIR/_extract_title.py" "$TEX_FILE" 2>/dev/null || echo 'UNKNOWN')
echo "Title: $TITLE"

# Create staging directory
STAGING=$(mktemp -d)
SRC_DIR="$STAGING/source"
mkdir -p "$SRC_DIR/figures"

# Copy .tex file
cp "$TEX_FILE" "$SRC_DIR/"

# Copy figures (exclude compiled paper PDFs like <texname>.pdf)
TEX_BASE="${TEX_FILE%.tex}"
for fig in *.png *.jpg *.jpeg *.pdf *.eps; do
    [ -f "$fig" ] || continue
    # Skip compiled output PDF
    [ "$fig" = "$TEX_BASE.pdf" ] && continue
    # Skip other PDFs that look like compiled output
    [[ "$fig" == *.pdf ]] && continue
    echo "  Copy figure: $fig"
    cp "$fig" "$SRC_DIR/figures/"
done

# Copy .bib files
for bib in *.bib; do
    [ -f "$bib" ] || continue
    cp "$bib" "$SRC_DIR/"
    echo "  Copy bibliography: $bib"
done

# Create tar.gz
cd "$STAGING"
tar czf "$OUTPUT" source/
cd -

# Cleanup
rm -rf "$STAGING"

# Report
SIZE=$(du -h "$OUTPUT" | cut -f1)
echo ""
echo "Created: $OUTPUT ($SIZE)"
echo "Contents:"
tar tzf "$OUTPUT" | head -20
echo ""
echo "Next step: Upload $OUTPUT to https://arxiv.org/submission"
