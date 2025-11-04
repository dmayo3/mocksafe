#!/usr/bin/env bash
set -euo pipefail

VERSION="${VERSION:?}"
BUMP_TYPE="${BUMP_TYPE:?}"
PRERELEASE_TYPE="${PRERELEASE_TYPE:-none}"
CUSTOM_VERSION="${CUSTOM_VERSION:-N/A}"
BRANCH_NAME="release-v${VERSION}"

PR_BODY_FILE=$(mktemp)
trap 'rm -f "$PR_BODY_FILE"' EXIT

cat > "$PR_BODY_FILE" << 'EOF'
## 🚀 Release v${VERSION}

**Bump:** ${BUMP_TYPE}
**Prerelease:** ${PRERELEASE_TYPE}
**Custom:** ${CUSTOM_VERSION}

### Next Steps
1. Review changes
2. Merge PR
3. Create tag & deploy

### Checklist
- [ ] Version correct
- [ ] Tests pass
- [ ] Breaking changes documented
EOF

export VERSION BUMP_TYPE PRERELEASE_TYPE CUSTOM_VERSION
envsubst < "$PR_BODY_FILE" > "${PR_BODY_FILE}.tmp"
mv "${PR_BODY_FILE}.tmp" "$PR_BODY_FILE"

LABELS="release"
[[ "$VERSION" == *"beta"* || "$VERSION" == *"rc"* ]] && LABELS="$LABELS,prerelease"

PR_URL=$(gh pr create \
    --title "Release v${VERSION}" \
    --body-file "$PR_BODY_FILE" \
    --base main \
    --head "$BRANCH_NAME" \
    --label "$LABELS")

PR_NUMBER="${PR_URL##*/}"

echo "pr_url=$PR_URL"
echo "pr_number=$PR_NUMBER"
