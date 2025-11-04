# Release Process

## Automated (Recommended)

```bash
# Standard release
gh workflow run release.yaml --field bump_type=patch

# With prerelease
gh workflow run release.yaml --field bump_type=minor --field prerelease_type=beta

# Custom version
gh workflow run release.yaml --field custom_version=2.0.0
```

After PR merges, create tag and deploy manually.

## Manual (Fallback)

1. Create release branch: `git checkout -b release-vX.Y.Z`
2. Bump version: `bumpver update --patch`
3. Commit and push
4. Create PR via GitHub
5. After merge:
   - Tag: `git tag vX.Y.Z && git push --tags`
   - Deploy via GitHub Release UI
   - Activate ReadTheDocs version
