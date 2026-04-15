#!/usr/bin/env bash
set -euo pipefail

PR_NUMBER="${PR_NUMBER:?}"
BRANCH="${BRANCH:?}"
VERSION="${VERSION:?}"
DRY_RUN="${DRY_RUN:?}"
GH_TOKEN="${GH_TOKEN:?}"

if [ "$DRY_RUN" = "true" ]; then
  echo "🧪 DRY RUN MODE - Closing PR instead of merging"
  echo ""
  echo "Would merge: PR #$PR_NUMBER for version $VERSION"
  echo "Instead: Closing PR and cleaning up branch"
  echo ""

  # Close PR with a comment
  echo "📝 Closing PR #$PR_NUMBER..."
  gh pr close "$PR_NUMBER" --comment "🧪 Dry run completed successfully. PR closed without merging."

  # Delete the branch
  echo "🧹 Deleting branch $BRANCH..."
  git push origin --delete "$BRANCH" || echo "Branch may already be deleted"

  echo "✅ Dry run completed successfully!"
  echo "action_taken=closed" >> "$GITHUB_OUTPUT"
else
  echo "🚀 PRODUCTION MODE - Merging PR"
  echo ""
  echo "Action: Merging PR #$PR_NUMBER for version $VERSION"
  echo ""

  gh pr merge "$PR_NUMBER" --squash --delete-branch

  echo "✅ PR #$PR_NUMBER merged and branch deleted"
  echo "action_taken=merged" >> "$GITHUB_OUTPUT"
fi
