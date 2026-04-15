#!/usr/bin/env bash
set -euo pipefail

REF="${REF:?REF is required}"
WORKFLOW_FILE="${WORKFLOW_FILE:-publish.yaml}"
DISCOVER_TIMEOUT_SECONDS="${DISCOVER_TIMEOUT_SECONDS:-120}"
POLL_INTERVAL_SECONDS="${POLL_INTERVAL_SECONDS:-5}"

elapsed=0
run_id=""

echo "⏳ Waiting for dispatched workflow run to appear for ref ${REF}..."

while [ "$elapsed" -lt "$DISCOVER_TIMEOUT_SECONDS" ]; do
  run_id="$(gh run list \
    --workflow "${WORKFLOW_FILE}" \
    --event workflow_dispatch \
    --json databaseId,headBranch,createdAt \
    --limit 50 \
    --jq ".[] | select(.headBranch==\"${REF}\") | .databaseId" | head -n 1 || true)"

  if [ -n "${run_id}" ] && [ "${run_id}" != "null" ]; then
    break
  fi

  sleep "${POLL_INTERVAL_SECONDS}"
  elapsed=$((elapsed + POLL_INTERVAL_SECONDS))
done

if [ -z "${run_id}" ] || [ "${run_id}" = "null" ]; then
  echo "❌ Could not find dispatched workflow run for ref ${REF} within ${DISCOVER_TIMEOUT_SECONDS}s"
  exit 1
fi

run_url="https://github.com/${GITHUB_REPOSITORY}/actions/runs/${run_id}"
echo "✅ Found workflow run: ${run_id}"

echo "run_id=${run_id}" >> "${GITHUB_OUTPUT}"
echo "run_url=${run_url}" >> "${GITHUB_OUTPUT}"
