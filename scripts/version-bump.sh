#!/usr/bin/env bash
set -euo pipefail

BUMP_TYPE="${1:?Usage: $0 <bump_type> <prerelease_type> [custom_version]}"
PRERELEASE_TYPE="${2:-none}"
CUSTOM_VERSION="${3:-}"

# Configure git before any operations
git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"

if [[ -n "$CUSTOM_VERSION" ]]; then
    NEW_VERSION="$CUSTOM_VERSION"
else
    # bumpver handles prerelease versions automatically
    # 0.10.0-beta + --minor = 0.11.0-beta
    NEW_VERSION=$(uvx bumpver update --$BUMP_TYPE --dry --no-commit 2>&1 | grep "^INFO.*New Version:" | sed 's/.*New Version: //')

    # If adding a new prerelease tag to a stable version
    if [[ "$PRERELEASE_TYPE" != "none" ]] && [[ "$NEW_VERSION" != *"-"* ]]; then
        NEW_VERSION="${NEW_VERSION}-${PRERELEASE_TYPE}"
    fi
fi

echo "version=$NEW_VERSION"

BRANCH_NAME="release-v$NEW_VERSION"
git checkout -b "$BRANCH_NAME"

# bumpver will commit the changes itself with --no-tag-commit
# (--no-tag-commit means "don't create a tag", not "don't commit")
uvx bumpver update --set-version "$NEW_VERSION" --no-tag-commit

git push origin "$BRANCH_NAME"

echo "branch=$BRANCH_NAME"
