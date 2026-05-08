#!/bin/bash
# Reusable LaTeX paper compilation helper
# Usage: compile_paper.sh <path/to/paper.tex> [pdflatex|xelatex]

set -e

# Source shell config for PATH (TinyTeX, etc.)
for rc in "$HOME/.zshrc" "$HOME/.bashrc"; do
    [ -f "$rc" ] && source "$rc" 2>/dev/null || true
done

PAPER="${1:?Usage: compile_paper.sh <paper.tex> [pdflatex|xelatex]}"
ENGINE="${2:-pdflatex}"
DIR="$(cd "$(dirname "$PAPER")" && pwd)"
BASENAME="$(basename "$PAPER" .tex)"

cd "$DIR"

# Check engine availability
if ! command -v "$ENGINE" &> /dev/null; then
    echo "ERROR: $ENGINE not found. Install TinyTeX: curl -L https://yihui.name/tinytex/install-unx.sh | sh"
    exit 1
fi

echo "=== Compiling $BASENAME with $ENGINE ==="
echo "Working directory: $DIR"

# Clean previous output files (but keep .tex)
for ext in aux bbl blg lof log lot toc out dvi ps idx ind ilg gfg brf run.pdf ps1 pdf fig1 vrb snb fdb_latexmk fls mlg mlf nav soc synctex.gz doi bbl-cache xml; do
    rm -f "${BASENAME}.${ext}" "${BASENAME%.*}.${ext}" 2>/dev/null || true
done

# Compile twice (first pass generates refs, second pass resolves them)
$ENGINE -interaction=nonstopmode "$PAPER" 2>&1 | tail -20
$ENGINE -interaction=nonstopmode "$PAPER" 2>&1 | grep -E 'Output written|Error|Fatal' | tail -5

# Check output
if [ -f "${BASENAME}.pdf" ]; then
    SIZE=$(ls -lh "${BASENAME}.pdf" | awk '{print $5}')
    if command -v pdfinfo &> /dev/null; then
        PAGES=$(pdfinfo "${BASENAME}.pdf" 2>/dev/null | grep "Pages:" | awk '{print $2}')
        echo "=== SUCCESS: ${BASENAME}.pdf (${PAGES} pages, ${SIZE}) ==="
    else
        echo "=== SUCCESS: ${BASENAME}.pdf (${SIZE}) [pdfinfo not installed] ==="
    fi
else
    echo "=== FAILED: No PDF generated ==="
    exit 1
fi
