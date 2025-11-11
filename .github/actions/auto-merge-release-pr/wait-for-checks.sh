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
    # States can be: SUCCESS, FAILURE, NEUTRAL, CANCELLED, SKIPPED, TIMED_OUT, ACTION_REQUIRED
    COMPLETED_COUNT=$(echo "$CHECKS_JSON" | jq '[.[] | select(.state == "SUCCESS" or .state == "FAILURE" or .state == "NEUTRAL" or .state == "CANCELLED" or .state == "SKIPPED" or .state == "TIMED_OUT" or .state == "ACTION_REQUIRED")] | length')
    PENDING_COUNT=$(echo "$CHECKS_JSON" | jq '[.[] | select(.state != "SUCCESS" and .state != "FAILURE" and .state != "NEUTRAL" and .state != "CANCELLED" and .state != "SKIPPED" and .state != "TIMED_OUT" and .state != "ACTION_REQUIRED")] | length')
    FAILED_COUNT=$(echo "$CHECKS_JSON" | jq '[.[] | select(.state == "FAILURE" or .state == "TIMED_OUT" or .state == "ACTION_REQUIRED")] | length')

    echo "Status: $COMPLETED_COUNT completed, $PENDING_COUNT pending, $FAILED_COUNT failed"
    echo "$CHECKS_JSON" | jq -r '.[] | "  \(.state): \(.name)"' || true

    # If checks have failed, exit immediately
    if [ "$FAILED_COUNT" -gt 0 ]; then
      echo "❌ Some checks failed"
      echo "checks_passed=false" >> "$GITHUB_OUTPUT"
      exit 1
    fi

    # If all checks are completed successfully, we're done
    if [ "$PENDING_COUNT" -eq 0 ] && [ "$COMPLETED_COUNT" -gt 0 ]; then
      echo "✅ All checks completed successfully!"
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
