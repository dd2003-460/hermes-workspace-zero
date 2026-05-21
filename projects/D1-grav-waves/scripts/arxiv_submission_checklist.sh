#!/bin/bash
# arXiv submission checklist - validate paper before submission
# Usage: arxiv_submission_checklist.sh <paper-directory>

PAPER_DIR="${1:?Usage: arxiv_submission_checklist.sh <paper-directory>}"
cd "$PAPER_DIR"

echo "=== arXiv Submission Checklist ==="
echo "Directory: $PAPER_DIR"
echo ""

PASS=0
FAIL=0
WARN=0

check() {
    local result="$1"
    local msg="$2"
    if [ "$result" = "pass" ]; then
        echo "  [PASS] $msg"
        PASS=$((PASS + 1))
    elif [ "$result" = "fail" ]; then
        echo "  [FAIL] $msg"
        FAIL=$((FAIL + 1))
    else
        echo "  [WARN] $msg"
        WARN=$((WARN + 1))
    fi
}

# 1. Paper file exists
TEX_FILES=$(find . -name "*.tex" -not -name "*.log" 2>/dev/null | wc -l | tr -d ' ')
[ "$TEX_FILES" -ge 1 ] && check "pass" "LaTeX source file found (${TEX_FILES} files)" || check "fail" "No .tex file found"

# 2. PDF generated
PDFS=$(find . -name "*.pdf" -not -name "*.pdfa" 2>/dev/null | grep -vc "arxiv" || echo "0")
[ "$PDFS" -ge 1 ] && check "pass" "PDF file found" || check "warn" "No PDF generated yet (run pdflatex/xelatex first)"

# 3. References/bibliography
REF_COUNT=$(grep -rh '\\bibitem' *.tex 2>/dev/null | wc -l | tr -d ' ')
[ "$REF_COUNT" -ge 1 ] && check "pass" "Bibliography entries found (${REF_COUNT})" || check "warn" "No \\bibitem (may use other bibliography style)"

# 4. Math expressions
MATH_COUNT=$(grep -c '\\(\|\$\|\\[\|\\\]' *.tex 2>/dev/null || echo "0")
[ "$MATH_COUNT" -ge 1 ] && check "pass" "Math expressions found (${MATH_COUNT})" || check "warn" "No math expressions"

# 5. Keywords
grep -qi "keyword\|关键词" *.tex 2>/dev/null && check "pass" "Keywords section found" || check "warn" "No keywords found"

# 6. Author information
grep -qi "author\|作者" *.tex 2>/dev/null && check "pass" "Author information found" || check "warn" "No author information found"

# 7. Abstract
grep -qi "abstract\|摘要" *.tex 2>/dev/null && check "pass" "Abstract section found" || check "warn" "No abstract found"

# 8. Image files
IMG_COUNT=$(find . \( -name "*.png" -o -name "*.pdf" -o -name "*.jpg" -o -name "*.eps" \) 2>/dev/null | wc -l | tr -d ' ')
[ "$IMG_COUNT" -ge 1 ] && check "pass" "Image files found (${IMG_COUNT})" || check "warn" "No image files found"

# 9. Figures in LaTeX
grep -q "includegraphics" *.tex 2>/dev/null && check "pass" "Figures included in LaTeX" || check "warn" "No includegraphics in LaTeX"

# 10. Citations in text
CIT_COUNT=$(grep -rh '\\cite' *.tex 2>/dev/null | wc -l | tr -d ' ')
[ "$CIT_COUNT" -ge 1 ] && check "pass" "Citations referenced (${CIT_COUNT} occurrences)" || check "warn" "No citations in text"

# 11. Section structure
SECTIONS=$(grep -rh '\\section\|\\subsection\|\\subsubsection' *.tex 2>/dev/null | wc -l | tr -d ' ')
[ "$SECTIONS" -ge 3 ] && check "pass" "Section structure found (${SECTIONS} sections/subsections)" || check "warn" "Minimal section structure"

echo ""
echo "=== Summary ==="
echo "  Pass: $PASS"
echo "  Fail: $FAIL"
echo "  Warn: $WARN"
echo ""

if [ "$FAIL" -gt 0 ]; then
    echo "STATUS: BLOCKED - $FAIL item(s) need attention before submission"
elif [ "$WARN" -gt 2 ]; then
    echo "STATUS: WARNING - $WARN item(s) may need review"
else
    echo "STATUS: READY for arXiv submission"
fi
