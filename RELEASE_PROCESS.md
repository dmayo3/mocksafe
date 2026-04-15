# Release Process

This project uses a semi-automated release flow.

## Automated (Recommended)

### CLI

```bash
# Standard release
gh workflow run release.yaml --field bump_type=patch --field dry_run=false

# Minor beta prerelease
gh workflow run release.yaml --field bump_type=minor --field prerelease_type=beta --field dry_run=false

# Custom version
gh workflow run release.yaml --field custom_version=2.0.0 --field dry_run=false
```

### GitHub UI

- Release workflow page: https://github.com/dmayo3/mocksafe/actions/workflows/release.yaml
- Publish workflow page: https://github.com/dmayo3/mocksafe/actions/workflows/publish.yaml
- Releases page: https://github.com/dmayo3/mocksafe/releases

On the release workflow page, click **Run workflow** and set:
- `bump_type` (or `custom_version`)
- `prerelease_type` if needed (`beta` / `rc`)
- `dry_run`:
  - `true` to validate flow without keeping a release tag
  - `false` for real release

## What the automated release does

For non-dry-run:
1. Creates a release PR with version bumps.
2. Waits for checks and merges it.
3. Creates and pushes the release tag (`X.Y.Z` / `X.Y.Z-beta`).
4. Dispatches the publish workflow for that tag and waits for completion.

For dry-run:
1. Creates release PR, validates checks, closes PR.
2. Creates temporary tag.
3. Dispatches publish workflow in `dry_run=true` mode (upload jobs skipped).
4. Waits for success, then deletes the temporary tag.

## Production release approval order (important)

The publish workflow uses environment approvals for package upload jobs.

Recommended order:
1. Let release workflow run through build/verify and TestPyPI.
2. **Before approving PyPI upload**, publish ReadTheDocs for the new version.
3. Approve `pypi` environment in GitHub Actions.
4. Confirm PyPI release is live.

This keeps docs available when the new package version becomes publicly installable.

## ReadTheDocs step (manual)

After tag exists and before PyPI approval:
1. Open ReadTheDocs project admin for `mocksafe`.
2. Activate/build the new version matching the tag (for example `0.11.0-beta`).
3. Verify docs URL:
   - `https://mocksafe.readthedocs.io/en/<version>/`

## GitHub Release notes (manual, recommended)

Create a GitHub Release entry from the existing tag for changelog/communication.

1. Open: https://github.com/dmayo3/mocksafe/releases/new
2. Select existing tag (for example `0.11.0-beta`).
3. Mark as **pre-release** for beta/rc versions.
4. Prefer creating as a **draft** first so you can review before publishing.
5. Include:
   - Highlights
   - Contributor shout-outs (especially new contributors)
   - Docs link for that version
   - PyPI/TestPyPI links
   - Compare link (`previous_tag...new_tag`)

## Manual (Fallback)

Use only if automation is unavailable.

1. Create release branch: `git checkout -b release-vX.Y.Z`
2. Bump version with `bumpver`
3. Commit and push
4. Open PR and merge
5. Tag: `git tag X.Y.Z && git push --tags`
6. Run publish workflow from GitHub UI against the tag
7. Activate/publish ReadTheDocs version
8. Create GitHub Release notes entry