#!/bin/bash

PAPER_DIR="$(cd "$(dirname "$0")" && pwd)"
PLATEX="$HOME/Library/TinyTeX/bin/universal-darwin/platex"
DVI2PDF="$HOME/Library/TinyTeX/bin/universal-darwin/dvipdfmx"

success=0
fail=0
skip=0

for d in "$PAPER_DIR"/D*-*; do
    [ -d "$d" ] || continue
    base=$(basename "$d")
    pdf="$d/$base.pdf"
    tex="$d/$base.tex"
    log="$d/$base.log"
    dvi="$d/$base.dvi"

    # Skip if PDF already exists
    if [ -f "$pdf" ]; then
        skip=$((skip + 1))
        continue
    fi

    # Skip if no tex file
    if [ ! -f "$tex" ]; then
        skip=$((skip + 1))
        continue
    fi

    echo "=== COMPILING: $base ==="

    # Clean old files
    rm -f "$d"/*.aux "$d"/*.dvi "$d"/*.toc "$d"/*.out "$d"/*.log "$d"/*.blg "$d"/*.bbl 2>/dev/null || true

    # Run platex
    $PLATEX "$tex" 2>&1 | tail -3

    # Check .log file for "Output written"
    if [ -f "$log" ] && grep -q "Output written" "$log"; then
        pages=$(grep "Output written" "$log" | grep -o "[0-9]* page" || echo "unknown")
        echo "  OK platex succeeded: $pages"

        # Now run dvipdfmx
        $DVI2PDF "$dvi" > "$d/dvipdfmx.log" 2>&1 || true

        if [ -f "$pdf" ]; then
            size=$(stat -f%z "$pdf" 2>/dev/null || echo 0)
            echo "  OK PDF generated: $size bytes"
            success=$((success + 1))
        else
            echo "  FAIL dvipdfmx failed to produce PDF"
            fail=$((fail + 1))
        fi
    else
        echo "  FAIL platex failed or log not found"
        fail=$((fail + 1))
    fi
done

echo ""
echo "=== SUMMARY ==="
echo "Success: $success"
echo "Failed:  $fail"
echo "Skipped (PDF exists): $skip"
