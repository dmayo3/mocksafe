#!/usr/bin/env bash
set -euo pipefail

VERSION="${VERSION:?}"
GH_TOKEN="${GH_TOKEN:?}"

TAG_NAME="v${VERSION}"

echo "🚀 Pushing tag to origin..."
if git push origin "${TAG_NAME}"; then
  echo "pushed=true" >> "$GITHUB_OUTPUT"
  echo "✅ Pushed tag ${TAG_NAME} to origin"
else
  echo "pushed=false" >> "$GITHUB_OUTPUT"
  echo "❌ Failed to push tag ${TAG_NAME}"
  exit 1
fi

echo "tag_name=${TAG_NAME}" >> "$GITHUB_OUTPUT"

echo "⏳ Waiting for publish workflow to be triggered..."

# Give GitHub a moment to register the tag push
sleep 5

# Wait up to 90 seconds for the workflow to appear
MAX_WAIT=90
INTERVAL=3
ELAPSED=0
RUN_ID=""

while [ $ELAPSED -lt $MAX_WAIT ]; do
  # Look for the most recent publish.yaml workflow run
  RUN_ID=$(gh run list \
    --workflow publish.yaml \
    --status in_progress,queued \
    --json databaseId,createdAt \
    --limit 1 \
    -q '.[0].databaseId' 2>/dev/null || echo "")

  if [ -n "$RUN_ID" ] && [ "$RUN_ID" != "null" ]; then
    echo "✅ Found publish workflow run: ${RUN_ID}"
    echo "run_id=${RUN_ID}" >> "$GITHUB_OUTPUT"

    # Generate URL to the workflow run
    REPO="${GITHUB_REPOSITORY}"
    RUN_URL="https://github.com/${REPO}/actions/runs/${RUN_ID}"
    echo "run_url=${RUN_URL}" >> "$GITHUB_OUTPUT"
    exit 0
  fi

  sleep $INTERVAL
  ELAPSED=$((ELAPSED + INTERVAL))
done

echo "⚠️  Could not locate the triggered workflow run"
echo "run_id=" >> "$GITHUB_OUTPUT"
echo "run_url=" >> "$GITHUB_OUTPUT"
