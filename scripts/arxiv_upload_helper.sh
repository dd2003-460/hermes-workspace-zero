#!/bin/bash
# arXiv upload helper — generate tarball, verify, and prepare upload
#
# Usage:
#   arxiv_upload_helper.sh <paper-directory> [output-tarball]
#
# This is a wrapper around arxiv_tarball.sh that provides a complete
# submission workflow.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PAPER_DIR="${1:?Usage: arxiv_upload_helper.sh <paper-directory> [output-tarball]}"
OUTPUT="${2:-$(basename "$PAPER_DIR" | sed 's/[_.]/-/g').arxiv.tar.gz}"

echo "=========================================="
echo " arXiv Upload Helper"
echo "=========================================="
echo ""

# Step 1: Generate tarball (includes citation verification)
echo "Step 1: Generating arXiv tarball..."
bash "$SCRIPT_DIR/arxiv_tarball.sh" "$PAPER_DIR" "$OUTPUT"
echo ""

# Step 2: Verify tarball contents
echo "Step 2: Verifying tarball contents..."
SIZE=$(du -h "$OUTPUT" | cut -f1)
echo "  Tarball size: $SIZE"

CONTENTS=$(tar tzf "$OUTPUT" | head -20)
FILE_COUNT=$(tar tzf "$OUTPUT" | wc -l | tr -d ' ')
echo "  File count: $FILE_COUNT"

# Check for required .tex file
TEX_FILES=$(tar tzf "$OUTPUT" | grep '\.tex$' | grep -v figures | head -1)
if [ -n "$TEX_FILES" ]; then
    echo "  Source file: $TEX_FILES"
else
    echo "  ERROR: No .tex file found in tarball!"
    exit 1
fi

# Step 3: Print submission instructions
echo ""
echo "=========================================="
echo " Submission Ready"
echo "=========================================="
echo ""
echo "Tarball: $OUTPUT"
echo "Upload: https://arxiv.org/submission"
echo ""
echo "For automated submission with arXiv Python package:"
echo "  pip install arxiv"
echo "  python3 - << 'PYEOF'"
echo "  import arxiv"
echo "  import tarfile"
echo "  import io"
echo ""
echo "  # Read tarball"
echo "  with open('$OUTPUT', 'rb') as f:"
echo "      tar_data = f.read()"
echo ""
echo "  # Create submission"
echo "  paper = arxiv.Paper()"
echo "  # Fill in metadata from the .tex file"
echo "  # Then upload"
echo "  # See: https://arxiv.org/help/batch_ftp"
echo "  PYEOF"
echo ""
echo "Or manually:"
echo "  1. Go to https://arxiv.org/submission"
echo "  2. Select category (gr-qc / cs.AI / ...)"
echo "  3. Upload $OUTPUT"
echo "  4. Fill in metadata"
echo "  5. Submit"
