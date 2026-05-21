#!/bin/bash
# Generate a comprehensive author review package for arXiv submission
#
# Usage:
#   arxiv_author_review.sh <paper-directory> [output-tarball]
#
# Produces a tarball with:
#   - source/ (arXiv submission package)
#   - compiled/ (compiled PDF)
#   - verification/ (all verification reports and logs)
#   - SUBMISSION_READY.md (comprehensive review checklist)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PAPER_DIR="$1"
OUTPUT="$(cd "$(pwd)" && pwd)/${2:-$(basename "$PAPER_DIR" | sed 's/[_.]/-/g').submission-review.tar.gz}"

if [ ! -d "$PAPER_DIR" ]; then
    echo "ERROR: $PAPER_DIR is not a directory"
    exit 1
fi

echo "========================================"
echo "  arXiv Submission Readiness Review"
echo "========================================"
echo ""

# Find .tex file
TEX_FILE=$(find "$PAPER_DIR" -maxdepth 1 -name '*.tex' -not -name '*.tex.*' | head -1)
if [ -z "$TEX_FILE" ]; then
    echo "ERROR: No .tex file found in $PAPER_DIR"
    exit 1
fi

TEX_NAME=$(basename "$TEX_FILE" .tex)
echo "Paper: $TEX_NAME"

# Step 1: Compile PDF
cd "$PAPER_DIR"
echo ""
echo "[1/4] Compiling PDF..."
COMPILE_LOG="compile-verification.log"
COMPILE_OK=0
pdflatex -interaction=nonstopmode "$TEX_NAME.tex" > "$COMPILE_LOG" 2>&1 || true
if grep -q "Output written" "$COMPILE_LOG"; then
    COMPILE_OK=1
    PAGES=$(grep "Output written" "$COMPILE_LOG" | grep -o '[0-9]* page' | head -1 | cut -d' ' -f1)
    PDF_SIZE=$(du -h "$TEX_NAME.pdf" | cut -f1)
    echo "  OK: $PAGES pages, $PDF_SIZE"
else
    # Try xelatex fallback
    xelatex -interaction=nonstopmode "$TEX_NAME.tex" >> "$COMPILE_LOG" 2>&1 || true
    if grep -q "Output written" "$COMPILE_LOG"; then
        COMPILE_OK=1
        PAGES=$(grep "Output written" "$COMPILE_LOG" | grep -o '[0-9]* page' | head -1 | cut -d' ' -f1)
        PDF_SIZE=$(du -h "$TEX_NAME.pdf" | cut -f1)
        echo "  OK (xelatex): $PAGES pages, $PDF_SIZE"
    else
        echo "  WARNING: Compilation may have issues, check log"
        PAGES="unknown"
        PDF_SIZE="unknown"
    fi
fi

# Step 2: Citation verification
echo ""
echo "[2/4] Verifying citations..."
CITE_RESULT=$(python3 "$SCRIPT_DIR/verify_citations.py" "$TEX_FILE" 2>&1 || true)
echo "$CITE_RESULT" > citation-verification.log
echo "  $CITE_RESULT" | tail -1

# Step 3: Title extraction
echo ""
echo "[3/4] Extracting title for arXiv..."
TITLE=$(python3 "$SCRIPT_DIR/_extract_title.py" "$TEX_FILE" 2>/dev/null || echo "UNKNOWN")
echo "  Title: $TITLE"

# Step 4: Generate review report
echo ""
echo "[4/4] Generating submission review report..."
SUBMISSION_METADATA=$(find "$PAPER_DIR" -name "arxiv-submission-metadata.md" -o -name "arxiv-submission-*.md" | head -1)
REVIEW_REPORT=$(find "$PAPER_DIR" -name "*review-report*.md" -o -name "*review*.md" | head -1)
ORIG_VERIFICATION=$(find "$PAPER_DIR" -name "02-originality*.md" | head -1)

# Create staging directory
STAGING=$(mktemp -d)
mkdir -p "$STAGING/source" "$STAGING/compiled" "$STAGING/verification"

# Source package
cd "$PAPER_DIR"
bash "$SCRIPT_DIR/arxiv_tarball.sh" "$PAPER_DIR" "/dev/stdout" 2>/dev/null | tar xzf - -C "$STAGING/source" 2>/dev/null || {
    cp "$TEX_NAME.tex" "$STAGING/source/"
    for fig in *.png *.jpg *.eps; do
        [ -f "$fig" ] && (mkdir -p "$STAGING/source/figures/" && cp "$fig" "$STAGING/source/figures/") 2>/dev/null || true
    done
}

# Compiled PDF
if [ -f "$TEX_NAME.pdf" ]; then
    cp "$TEX_NAME.pdf" "$STAGING/compiled/"
fi

# Verification materials
cp citation-verification.log "$STAGING/verification/" 2>/dev/null || true
cp compile-verification.log "$STAGING/verification/" 2>/dev/null || true
[ -f "$SUBMISSION_METADATA" ] && cp "$SUBMISSION_METADATA" "$STAGING/verification/" 2>/dev/null || true
[ -f "$REVIEW_REPORT" ] && cp "$REVIEW_REPORT" "$STAGING/verification/" 2>/dev/null || true
[ -f "$ORIG_VERIFICATION" ] && cp "$ORIG_VERIFICATION" "$STAGING/verification/" 2>/dev/null || true

# Generate SUBMISSION_READY.md
cat > "$STAGING/verification/SUBMISSION_READY.md" << REVIEW_EOF
# arXiv Submission Readiness Report
# Generated: $(date '+%Y-%m-%d %H:%M:%S')
# Paper: $TEX_NAME

## Author Review Checklist
- [ ] **PDF Review**: Check compiled PDF in \`compiled/\` for formatting, figures, and content
- [ ] **Citation Check**: Review citation verification in \`verification/citation-verification.log\`
- [ ] **Compile Log**: Review compilation log in \`verification/compile-verification.log\`
- [ ] **Metadata**: Confirm arXiv metadata in \`verification/arxiv-submission-metadata.md\`
- [ ] **Originality**: Review originality verification in \`verification/02-originality*.md\`

## Compilation Status
- **Method**: $([ -f "$TEX_NAME.pdf" ] && echo "pdflatex" || (cd "$PAPER_DIR" && xelatex -interaction=nonstopmode "$TEX_NAME.tex" 2>&1 > /dev/null && echo "xelatex" || echo "unknown"))
- **Pages**: $PAGES
- **PDF Size**: $PDF_SIZE

## Citation Status
$(cat citation-verification.log 2>/dev/null || echo "Not available")

## arXiv Metadata
- **Title**: $TITLE
- **Classification**: See \`verification/arxiv-submission-metadata.md\` for details

## Submission Instructions
1. Review all files above
2. Go to https://arxiv.org/submission
3. Upload \`source/\` directory contents (repack as tar.gz)
4. Fill in metadata from \`verification/arxiv-submission-metadata.md\`
5. Submit

## Toolchain
- \`arxiv_tarball.sh\` — Source tarball creation
- \`verify_citations.py\` — Citation verification
- \`_extract_title.py\` — Title extraction
- \`arxiv_submission_checklist.sh\` — Checklist validation
- \`arxiv_review_tarball.sh\` — Review tarball (source + compiled)
- \`arxiv_author_review.sh\` — This comprehensive review generator
REVIEW_EOF

# Create final tarball
cd "$STAGING"
tar czf "$OUTPUT" source/ compiled/ verification/
cd -

rm -rf "$STAGING"

# Clean up compile artifacts
rm -f "$COMPILE_LOG" citation-verification.log 2>/dev/null || true

echo ""
echo "========================================"
echo "  Review package: $OUTPUT"
echo "========================================"
echo "Contents:"
tar tzf "$OUTPUT" | head -30
echo ""
echo "Please review SUBMISSION_READY.md and all compiled PDF before submission."
