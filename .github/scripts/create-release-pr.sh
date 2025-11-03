#!/usr/bin/env bash
set -euo pipefail

# create-release-pr.sh - Create a GitHub PR for the release
# This script expects the following environment variables:
# - VERSION: The new version number
# - BUMP_TYPE: The type of version bump
# - CUSTOM_VERSION: Custom version if provided (optional)
# - GH_TOKEN: GitHub token for authentication

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# Validate required environment variables
if [[ -z "${VERSION:-}" ]]; then
    log_error "VERSION environment variable is required"
    exit 1
fi

if [[ -z "${BUMP_TYPE:-}" ]]; then
    log_error "BUMP_TYPE environment variable is required"
    exit 1
fi

if [[ -z "${GH_TOKEN:-}" ]]; then
    log_error "GH_TOKEN environment variable is required"
    exit 1
fi

# Set defaults for optional variables
CUSTOM_VERSION="${CUSTOM_VERSION:-N/A}"
BRANCH_NAME="release-v${VERSION}"

# Determine if this is a prerelease
PRERELEASE_LABELS=""
if [[ "$VERSION" == *"beta"* ]] || [[ "$VERSION" == *"rc"* ]]; then
    PRERELEASE_LABELS="prerelease"
fi

# Create PR body file to avoid injection issues
PR_BODY_FILE=$(mktemp)
trap 'rm -f "$PR_BODY_FILE"' EXIT

cat > "$PR_BODY_FILE" << 'ENDOFBODY'
## 🚀 Release v${VERSION}

This PR was automatically created by the Release Process workflow.

### Version Bump Details
- **Bump Type:** ${BUMP_TYPE}
- **Custom Version:** ${CUSTOM_VERSION}
- **New Version:** ${VERSION}

### Next Steps
1. Review the version changes in the Files tab
2. Ensure all CI checks pass
3. Approve and merge this PR
4. After merge, create tag and trigger deployment

### Release Checklist
- [ ] Version bump looks correct
- [ ] All tests passing
- [ ] Documentation up to date
- [ ] Breaking changes documented (if any)

---
*Automated by GitHub Actions* 🤖
ENDOFBODY

# Substitute variables safely using envsubst
export VERSION BUMP_TYPE CUSTOM_VERSION
envsubst < "$PR_BODY_FILE" > "${PR_BODY_FILE}.tmp"
mv "${PR_BODY_FILE}.tmp" "$PR_BODY_FILE"

# Build gh command arguments safely
GH_ARGS=(
    "pr" "create"
    "--title" "Release v${VERSION}"
    "--body-file" "$PR_BODY_FILE"
    "--base" "main"
    "--head" "$BRANCH_NAME"
    "--label" "release"
)

# Add prerelease label if applicable
if [[ -n "$PRERELEASE_LABELS" ]]; then
    GH_ARGS+=("--label" "$PRERELEASE_LABELS")
fi

log_info "Creating pull request for version $VERSION..."

# Create the PR and capture the URL
PR_URL=$(gh "${GH_ARGS[@]}") || {
    log_error "Failed to create pull request"
    exit 1
}

# Extract PR number from URL (format: https://github.com/owner/repo/pull/123)
PR_NUMBER="${PR_URL##*/}"

# Validate PR number is actually a number
if ! [[ "$PR_NUMBER" =~ ^[0-9]+$ ]]; then
    log_error "Invalid PR number extracted: $PR_NUMBER"
    exit 1
fi

# Output for GitHub Actions
if [[ -n "${GITHUB_OUTPUT:-}" ]]; then
    echo "pr_url=$PR_URL" >> "$GITHUB_OUTPUT"
    echo "pr_number=$PR_NUMBER" >> "$GITHUB_OUTPUT"
fi

# Print success message
log_info "✅ Successfully created PR #$PR_NUMBER"
log_info "📎 PR URL: $PR_URL"

# Also output to stdout for visibility
echo "pr_url=$PR_URL"
echo "pr_number=$PR_NUMBER"
