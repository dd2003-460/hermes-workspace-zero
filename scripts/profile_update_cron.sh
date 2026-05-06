#!/bin/bash
# =============================================================================
# 周期性用户画像与偏好系统更新
# =============================================================================
# 调度：每 13 分钟执行一次 */13 * * *
#
# 执行流程:
#   1. 扫描 memory/raw/ 目录（识别新/变更文件）
#   2. 从 raw 提取用户画像信息（偏好、思维模式、行为特征）
#   3. 输出到 memory/processed/<category>/（append-only，不覆盖）
#   4. 聚合 processed 内容到 memory/profile/
#   5. 更新 checkpoint（last_processed_timestamp, processed_hashes）
#
# =============================================================================

set -euo pipefail
trap 'echo "[$(date '+%Y-%m-%d %H:%M')]* ERROR: Script interrupted' ERR 2>&1 || true

echo "========================================"
echo "[PERIODIC PROFILE UPDATE]" 
echo "Started: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

WORKSPACE="/Users/a1-6/Desktop/workspace-zero/memory"

# ------------------------------------------------------------------------------
# Step 1: Run extraction script (identify new/modified files)
# ------------------------------------------------------------------------------
echo ""
echo "[Step 1] Scanning raw directory for new/modified files..."

RUN_DIR="${WORKSPACE}"
cd "$RUN_DIR" || exit 1
python3 "/Users/a1-6/Desktop/workspace-zero/scripts/periodic_profile_update.py"

EXTRACTION_EXIT=$?
echo "[Step 1 complete] Extraction exit code: $EXTRACTION_EXIT"

# ------------------------------------------------------------------------------
# Step 2: Run aggregation script (merge processed into profile)
# ------------------------------------------------------------------------------
echo ""
echo "[Step 2] Aggregating processed outputs into profile..."

python3 "/Users/a1-6/Desktop/workspace-zero/scripts/aggregate_profile.py" || true
AGG_EXIT=$?

echo "[Step 2 complete] Aggregation exit code: $AGG_EXIT"

# ------------------------------------------------------------------------------
# Step 3: Update checkpoint (ensure it exists and is current)
# ------------------------------------------------------------------------------
echo ""
echo "[Step 3] Finalizing checkpoint..."

CHECKPOINT_FILE="${WORKSPACE}/profile/update_checkpoint.json"
mkdir -p "$(dirname "$CHECKPOINT_FILE")" || true

cat > "$CHECKPOINT_FILE" << EOF
{
  "last_processed_ts": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')",
  "processed_hashes": {}
}
EOF

echo "[Step 3 complete] Checkpoint updated"

# ------------------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------------------
echo ""
echo "========================================"
echo "[PERIODIC PROFILE UPDATE] COMPLETE"
echo "Finished: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

# Exit with non-zero if extraction failed (aggregation can still run)
[ $EXTRACTION_EXIT -eq 0 ] && exit 0 || exit 1