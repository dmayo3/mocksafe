#!/usr/bin/env bash
set -euo pipefail

BUMP_TYPE="${1:?Usage: $0 <bump_type> <prerelease_type> [custom_version]}"
PRERELEASE_TYPE="${2:-none}"
CUSTOM_VERSION="${3:-}"

if [[ -n "$CUSTOM_VERSION" ]]; then
    NEW_VERSION="$CUSTOM_VERSION"
else
    BUMP_ARGS="--$BUMP_TYPE"
    [[ "$PRERELEASE_TYPE" != "none" ]] && BUMP_ARGS="$BUMP_ARGS --tag $PRERELEASE_TYPE"

    NEW_VERSION=$(bumpver update $BUMP_ARGS --dry --no-commit 2>&1 |
                  grep "^New Version:" |
                  sed 's/New Version:[[:space:]]*//')
fi

echo "version=$NEW_VERSION"

BRANCH_NAME="release-v$NEW_VERSION"
git checkout -b "$BRANCH_NAME"

if [[ -n "$CUSTOM_VERSION" ]]; then
    bumpver update --set-version "$NEW_VERSION" --no-tag-commit
else
    bumpver update $BUMP_ARGS --no-tag-commit
fi

git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"

git add .
git commit -m "chore: bump version to $NEW_VERSION"
git push origin "$BRANCH_NAME"

echo "branch=$BRANCH_NAME"
