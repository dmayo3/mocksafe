#!/usr/bin/env bash
set -euo pipefail

RUN_ID="${RUN_ID:?RUN_ID is required}"
GH_TOKEN="${GH_TOKEN:?GH_TOKEN is required}"
POLL_INTERVAL_SECONDS="${POLL_INTERVAL_SECONDS:-5}"

echo "⏳ Waiting for run ${RUN_ID} to complete successfully..."
gh run watch "${RUN_ID}" --exit-status --interval "${POLL_INTERVAL_SECONDS}"

conclusion="$(gh run view "${RUN_ID}" --json conclusion --jq '.conclusion' || true)"
if [ -z "${conclusion}" ] || [ "${conclusion}" = "null" ]; then
  conclusion="unknown"
fi

if [ -n "${GITHUB_OUTPUT:-}" ]; then
  echo "conclusion=${conclusion}" >> "${GITHUB_OUTPUT}"
fi

echo "✅ Workflow completed successfully (conclusion=${conclusion})"
