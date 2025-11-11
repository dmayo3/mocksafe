#!/usr/bin/env bash
set -euo pipefail

PR_NUMBER="${PR_NUMBER:?}"
GH_TOKEN="${GH_TOKEN:?}"

echo "📊 Monitoring PR #$PR_NUMBER checks..."

# Maximum wait time: 30 minutes
MAX_WAIT=1800
INTERVAL=10
ELAPSED=0
CHECKS_APPEARED=false

while [ $ELAPSED -lt $MAX_WAIT ]; do
  # Get check statuses
  CHECKS_JSON=$(gh pr checks "$PR_NUMBER" --json state,name 2>/dev/null || echo "[]")
  CHECK_COUNT=$(echo "$CHECKS_JSON" | jq 'length')

  if [ "$CHECK_COUNT" -gt 0 ]; then
    CHECKS_APPEARED=true
    echo "Found $CHECK_COUNT checks"

    # Count checks by state
    COMPLETED_COUNT=$(echo "$CHECKS_JSON" | jq '[.[] | select(.state == "COMPLETED")] | length')
    PENDING_COUNT=$(echo "$CHECKS_JSON" | jq '[.[] | select(.state != "COMPLETED")] | length')

    echo "Status: $COMPLETED_COUNT completed, $PENDING_COUNT pending"
    echo "$CHECKS_JSON" | jq -r '.[] | "  \(.state): \(.name)"' || true

    # If all checks are completed, we're done
    if [ "$PENDING_COUNT" -eq 0 ]; then
      echo "✅ All checks completed!"
      echo "checks_passed=true" >> "$GITHUB_OUTPUT"
      exit 0
    fi
  else
    # No checks yet
    if [ "$CHECKS_APPEARED" = false ]; then
      echo "⏳ Waiting for checks to appear..."
    fi
  fi

  sleep $INTERVAL
  ELAPSED=$((ELAPSED + INTERVAL))
done

echo "⏰ Timeout waiting for checks (max ${MAX_WAIT}s)"
echo "checks_passed=false" >> "$GITHUB_OUTPUT"
exit 1
