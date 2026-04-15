#!/usr/bin/env bash
set -euo pipefail

TAG_NAME="${TAG_NAME:?}"
GH_TOKEN="${GH_TOKEN:?}"
RUN_ID="${RUN_ID:-}"

echo "🧪 DRY RUN MODE - Starting cleanup"
echo ""

# Require provided workflow run id from the push step
if [[ -z "$RUN_ID" ]] || [[ "$RUN_ID" == "null" ]]; then
  echo "❌ Missing publish workflow run id for cleanup"
  exit 1
fi

echo "✅ Using provided publish workflow run: $RUN_ID"
echo "⏳ Waiting 30 seconds for workflow jobs to initialize..."
sleep 30

echo "🛑 Canceling workflow run..."
if gh run cancel "$RUN_ID"; then
  echo "✅ Workflow canceled"
else
  echo "⚠️  Could not cancel workflow (may have already completed)"
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
