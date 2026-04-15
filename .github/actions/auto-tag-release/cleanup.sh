#!/usr/bin/env bash
set -euo pipefail

TAG_NAME="${TAG_NAME:?}"
GH_TOKEN="${GH_TOKEN:?}"

echo "🧪 DRY RUN MODE - Starting cleanup"
echo ""

# Wait for the workflow run to appear (max 90 seconds)
echo "⏳ Waiting for publish workflow to start (up to 90 seconds)..."
MAX_WAIT=90
INTERVAL=3
ELAPSED=0
RUN_ID=""

while [ $ELAPSED -lt $MAX_WAIT ]; do
  RUN_ID=$(gh run list \
    --workflow publish.yaml \
    --json databaseId,status \
    --jq '.[0].databaseId' 2>/dev/null || echo "")

  if [[ -n "$RUN_ID" ]] && [[ "$RUN_ID" != "null" ]]; then
    echo "✅ Found publish workflow run: $RUN_ID"
    break
  fi

  sleep $INTERVAL
  ELAPSED=$((ELAPSED + INTERVAL))
done

if [[ -n "$RUN_ID" ]] && [[ "$RUN_ID" != "null" ]]; then
  echo "⏳ Waiting 30 seconds for workflow jobs to initialize..."
  sleep 30

  echo "🛑 Canceling workflow run..."
  if gh run cancel "$RUN_ID"; then
    echo "✅ Workflow canceled"
  else
    echo "⚠️  Could not cancel workflow (may have already completed)"
  fi
else
  echo "⚠️  Could not find workflow run (cleanup will continue)"
fi

echo ""
echo "🧹 Deleting tag ${TAG_NAME}..."
if git tag -d "$TAG_NAME" 2>/dev/null && git push origin --delete "$TAG_NAME" 2>/dev/null; then
  echo "✅ Tag deleted"
else
  echo "⚠️  Tag deletion had issues (may already be deleted)"
fi

echo ""
echo "status=tag_deleted" >> "$GITHUB_OUTPUT"
echo "✅ Cleanup completed"
