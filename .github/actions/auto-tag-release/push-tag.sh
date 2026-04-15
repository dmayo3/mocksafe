#!/usr/bin/env bash
set -euo pipefail

VERSION="${VERSION:?}"
TAG_NAME="${VERSION}"

echo "🚀 Pushing tag to origin..."
if git push origin "${TAG_NAME}"; then
  echo "pushed=true" >> "$GITHUB_OUTPUT"
  echo "✅ Pushed tag ${TAG_NAME} to origin"
else
  echo "pushed=false" >> "$GITHUB_OUTPUT"
  echo "❌ Failed to push tag ${TAG_NAME}"
  exit 1
fi

echo "tag_name=${TAG_NAME}" >> "$GITHUB_OUTPUT"
echo "run_id=" >> "$GITHUB_OUTPUT"
echo "run_url=" >> "$GITHUB_OUTPUT"
