#!/usr/bin/env bash
set -euo pipefail

GH_TOKEN="${GH_TOKEN:?GH_TOKEN is required}"
REF="${REF:?REF is required}"
WORKFLOW_FILE="${WORKFLOW_FILE:-publish.yaml}"
DRY_RUN="${DRY_RUN:-false}"
DISPATCHED_AT="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

echo "🚀 Dispatching ${WORKFLOW_FILE} on ref ${REF} (dry_run=${DRY_RUN}) at ${DISPATCHED_AT}..."
gh workflow run "${WORKFLOW_FILE}" --ref "${REF}" --field dry_run="${DRY_RUN}"
echo "✅ Dispatch requested"

if [ -n "${GITHUB_OUTPUT:-}" ]; then
  echo "dispatch_requested=true" >> "${GITHUB_OUTPUT}"
  echo "workflow_file=${WORKFLOW_FILE}" >> "${GITHUB_OUTPUT}"
  echo "ref=${REF}" >> "${GITHUB_OUTPUT}"
  echo "dry_run=${DRY_RUN}" >> "${GITHUB_OUTPUT}"
  echo "dispatched_at=${DISPATCHED_AT}" >> "${GITHUB_OUTPUT}"
fi
