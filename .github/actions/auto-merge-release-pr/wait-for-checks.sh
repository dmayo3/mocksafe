#!/usr/bin/env bash
set -euo pipefail

PR_NUMBER="${PR_NUMBER:?}"
GH_TOKEN="${GH_TOKEN:?}"

echo "📊 Monitoring PR #$PR_NUMBER checks..."

# Maximum wait time: 30 minutes
MAX_WAIT=1800
INTERVAL=30
ELAPSED=0

while [ $ELAPSED -lt $MAX_WAIT ]; do
  # Get check status using correct field names
  # state can be: COMPLETED, PENDING, QUEUED, REQUESTED, WAITING
  CHECK_STATUS=$(gh pr checks "$PR_NUMBER" --json state,name --jq '
    if (any(.[]; .state != "COMPLETED")) then
      "pending"
    elif (all(.[]; .state == "COMPLETED")) then
      "success"
    else
      "failed"
    end
  ')

  echo "Check status: $CHECK_STATUS"

  if [ "$CHECK_STATUS" = "success" ]; then
    echo "✅ All checks completed!"
    echo "checks_passed=true" >> "$GITHUB_OUTPUT"
    exit 0
  elif [ "$CHECK_STATUS" = "failed" ]; then
    echo "❌ Some checks failed"
    echo "checks_passed=false" >> "$GITHUB_OUTPUT"
    exit 1
  else
    echo "⏳ Checks still pending... waiting ${INTERVAL}s"
    sleep $INTERVAL
    ELAPSED=$((ELAPSED + INTERVAL))
  fi
done

echo "⏰ Timeout waiting for checks (max ${MAX_WAIT}s)"
echo "checks_passed=false" >> "$GITHUB_OUTPUT"
exit 1
