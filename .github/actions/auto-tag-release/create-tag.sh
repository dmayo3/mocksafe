#!/usr/bin/env bash
set -euo pipefail

VERSION="${VERSION:?}"

TAG_NAME="${VERSION}"

git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"

echo "🏷️  Creating annotated tag: ${TAG_NAME}"
git tag -a "${TAG_NAME}" -m "Release ${TAG_NAME}" || {
  echo "❌ Failed to create tag ${TAG_NAME}"
  exit 1
}

echo "✅ Created annotated tag: ${TAG_NAME}"
echo "tag_name=${TAG_NAME}" >> "$GITHUB_OUTPUT"
