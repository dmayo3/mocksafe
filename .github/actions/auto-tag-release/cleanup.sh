#!/usr/bin/env bash
set -euo pipefail

TAG_NAME="${TAG_NAME:?}"
GH_TOKEN="${GH_TOKEN:?}"

echo "🧪 DRY RUN MODE - Starting cleanup"
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
