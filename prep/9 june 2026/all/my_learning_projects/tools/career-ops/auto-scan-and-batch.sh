#!/usr/bin/env bash
# auto-scan-and-batch.sh
# Scheduled agent: scan portals → score new roles → draft tailored CVs
# Run via cron or manually. Logs to batch/logs/auto-run-{date}.log
# Usage: ./auto-scan-and-batch.sh [--dry-run] [--parallel N] [--min-score N]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/batch/logs"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H%M)
LOG_FILE="$LOG_DIR/auto-run-${DATE}-${TIME}.log"
PIPELINE_FILE="$SCRIPT_DIR/data/pipeline.md"
BATCH_INPUT="$SCRIPT_DIR/batch/batch-input.tsv"

mkdir -p "$LOG_DIR"

# Forward any extra args to batch-runner
EXTRA_ARGS=("$@")

echo "========================================" | tee -a "$LOG_FILE"
echo " career-ops auto-scan-and-batch" | tee -a "$LOG_FILE"
echo " Started: $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# Step 1: Scan portals for new roles
echo "" | tee -a "$LOG_FILE"
echo "[1/4] Scanning portals..." | tee -a "$LOG_FILE"
claude -p "Run /career-ops scan and output the list of new URLs found in data/pipeline.md. Do nothing else." \
  --dangerously-skip-permissions 2>&1 | tee -a "$LOG_FILE" || {
  echo "WARN: scan step had non-zero exit — continuing with existing pipeline.md" | tee -a "$LOG_FILE"
}

# Step 2: Extract new URLs from pipeline.md and add to batch-input.tsv
echo "" | tee -a "$LOG_FILE"
echo "[2/4] Extracting new URLs from pipeline.md..." | tee -a "$LOG_FILE"

# Init batch-input.tsv if missing
if [[ ! -f "$BATCH_INPUT" ]]; then
  printf 'id\turl\tsource\tnotes\n' > "$BATCH_INPUT"
  echo "  Created batch-input.tsv" | tee -a "$LOG_FILE"
fi

# Get next available ID
NEXT_ID=1
if [[ -f "$BATCH_INPUT" ]]; then
  MAX_ID=$(tail -n +2 "$BATCH_INPUT" | awk -F'\t' 'NF>0 && $1~/^[0-9]+$/ {if($1+0>max) max=$1+0} END{print max+0}')
  NEXT_ID=$((MAX_ID + 1))
fi

# Parse URLs from pipeline.md (lines starting with http)
ADDED=0
if [[ -f "$PIPELINE_FILE" ]]; then
  while IFS= read -r line; do
    # Match lines that are URLs (start with http) not already in batch-input
    if [[ "$line" =~ ^https?:// ]]; then
      url=$(echo "$line" | awk '{print $1}')
      # Skip if already in batch-input
      if grep -qF "$url" "$BATCH_INPUT" 2>/dev/null; then
        continue
      fi
      printf '%s\t%s\t%s\t%s\n' "$NEXT_ID" "$url" "auto-scan-${DATE}" "" >> "$BATCH_INPUT"
      echo "  + Added #$NEXT_ID: $url" | tee -a "$LOG_FILE"
      NEXT_ID=$((NEXT_ID + 1))
      ADDED=$((ADDED + 1))
    fi
  done < "$PIPELINE_FILE"
fi

echo "  $ADDED new URLs added to batch-input.tsv" | tee -a "$LOG_FILE"

if [[ $ADDED -eq 0 ]]; then
  echo "" | tee -a "$LOG_FILE"
  echo "[INFO] No new URLs to process. Exiting." | tee -a "$LOG_FILE"
  echo "Done: $(date)" | tee -a "$LOG_FILE"
  exit 0
fi

# Step 3: Run batch evaluation
echo "" | tee -a "$LOG_FILE"
echo "[3/4] Running batch evaluation ($ADDED new offers)..." | tee -a "$LOG_FILE"
bash "$SCRIPT_DIR/batch/batch-runner.sh" "${EXTRA_ARGS[@]}" 2>&1 | tee -a "$LOG_FILE"

# Step 4: Merge tracker + verify
echo "" | tee -a "$LOG_FILE"
echo "[4/4] Merging tracker and verifying pipeline..." | tee -a "$LOG_FILE"
node "$SCRIPT_DIR/merge-tracker.mjs" 2>&1 | tee -a "$LOG_FILE"
node "$SCRIPT_DIR/verify-pipeline.mjs" 2>&1 | tee -a "$LOG_FILE" || true

echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo " Done: $(date)" | tee -a "$LOG_FILE"
echo " Log: $LOG_FILE" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
