#!/usr/bin/env bash
set -euo pipefail

PR_NUMBER="${PR_NUMBER:?}"
GH_TOKEN="${GH_TOKEN:?}"

echo "📝 Approving PR #$PR_NUMBER..."
gh pr review "$PR_NUMBER" --approve --body "Auto-approved by release automation 🤖"
echo "✅ PR approved successfully"
