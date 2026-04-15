#!/usr/bin/env bash
set -euo pipefail

VERSION="${VERSION:?}"
GH_TOKEN="${GH_TOKEN:?}"
DRY_RUN="${DRY_RUN:-false}"

TAG_NAME="${VERSION}"

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

echo "🚀 Triggering publish workflow explicitly on tag ref: ${TAG_NAME} (dry_run=${DRY_RUN})..."

if gh workflow run publish.yaml --ref "${TAG_NAME}" --field dry_run="${DRY_RUN}"; then
  echo "✅ Publish workflow dispatch requested for ref ${TAG_NAME} (dry_run=${DRY_RUN})"
else
  echo "❌ Failed to dispatch publish workflow for ref ${TAG_NAME}"
  exit 1
fi

echo "⏳ Waiting for publish workflow run to appear..."

MAX_WAIT=90
INTERVAL=3
ELAPSED=0
RUN_ID=""

while [ $ELAPSED -lt $MAX_WAIT ]; do
  RUN_ID=$(gh run list \
    --workflow publish.yaml \
    --status in_progress,queued \
    --json databaseId,createdAt \
    --limit 1 \
    -q '.[0].databaseId' 2>/dev/null || echo "")

  if [ -n "$RUN_ID" ] && [ "$RUN_ID" != "null" ]; then
    echo "✅ Found publish workflow run: ${RUN_ID}"
    echo "run_id=${RUN_ID}" >> "$GITHUB_OUTPUT"

    REPO="${GITHUB_REPOSITORY}"
    RUN_URL="https://github.com/${REPO}/actions/runs/${RUN_ID}"
    echo "run_url=${RUN_URL}" >> "$GITHUB_OUTPUT"

    if [ "$DRY_RUN" = "true" ]; then
      echo "⏳ Dry-run mode: waiting for publish workflow to complete successfully..."
      RUN_WAIT_MAX=1800
      RUN_WAIT_INTERVAL=10
      RUN_WAIT_ELAPSED=0

      while [ $RUN_WAIT_ELAPSED -lt $RUN_WAIT_MAX ]; do
        RUN_STATUS=$(gh run view "$RUN_ID" --json status,conclusion -q '.status' 2>/dev/null || echo "")
        RUN_CONCLUSION=$(gh run view "$RUN_ID" --json status,conclusion -q '.conclusion' 2>/dev/null || echo "")

        if [ "$RUN_STATUS" = "completed" ]; then
          if [ "$RUN_CONCLUSION" = "success" ]; then
            echo "✅ Dry-run publish workflow completed successfully"
            exit 0
          fi

          echo "❌ Dry-run publish workflow finished with conclusion: ${RUN_CONCLUSION}"
          exit 1
        fi

        sleep $RUN_WAIT_INTERVAL
        RUN_WAIT_ELAPSED=$((RUN_WAIT_ELAPSED + RUN_WAIT_INTERVAL))
      done

      echo "❌ Timed out waiting for dry-run publish workflow completion (${RUN_WAIT_MAX}s)"
      exit 1
    fi

    exit 0
  fi

  sleep $INTERVAL
  ELAPSED=$((ELAPSED + INTERVAL))
done

echo "❌ Could not locate the dispatched publish workflow run within ${MAX_WAIT}s"
exit 1
