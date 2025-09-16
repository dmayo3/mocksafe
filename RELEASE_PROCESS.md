# Release Process Documentation

This document outlines the complete release process for MockSafe, based on the successful v0.10.0-beta release and the procedures defined in Issue #90.

## Prerequisites

Before starting a release, ensure you have:

- [ ] Write access to the repository
- [ ] `gh` CLI tool installed and authenticated
- [ ] `bumpver` package installed
- [ ] All planned features and fixes merged into `main`
- [ ] Access to PyPI and TestPyPI (for manual artifact review)
- [ ] Access to ReadTheDocs admin panel

## Release Process Steps

### 1. Preparation

1. **Create a fresh branch from latest origin/main:**
   ```bash
   git fetch origin
   git checkout main
   git pull origin main
   git checkout -b release-vX.Y.Z-beta  # or appropriate version
   ```

### 2. Version Bumping

2. **Test version bump (dry run):**
   ```bash
   bumpver update --minor --tag beta --no-commit --no-tag-commit --dry
   ```

3. **Review the output** to ensure it looks correct. Check that all files are updated appropriately.

4. **Apply version bump:**
   ```bash
   bumpver update --minor --tag beta --no-commit --no-tag-commit
   ```

5. **Commit the changes:**
   ```bash
   git add .
   git commit -m "Bump version X.Y.Z-beta -> X.Y.Z-beta"
   ```

### 3. Pull Request Process

6. **Push branch and create PR:**
   ```bash
   git push origin release-vX.Y.Z-beta
   gh pr create --title "Release vX.Y.Z-beta" --body "Version bump for vX.Y.Z-beta release. Closes #[issue-number]"
   ```

7. **Wait for GitHub Actions checks to pass** - Monitor the PR status.

8. **Request PR review** (if not self-approving).

9. **Merge to main** using squash merge:
   ```bash
   gh pr merge [PR-NUMBER] --squash --delete-branch
   ```

### 4. Tagging and Release

⚠️ **IMPORTANT**: Tag creation must happen BEFORE triggering release workflows, as PyPI deployment is restricted to tags only, not the main branch.

10. **Update local main and create tag:**
    ```bash
    git checkout main
    git pull origin main
    git tag X.Y.Z-beta
    git push origin X.Y.Z-beta
    ```

11. **Trigger release workflow on the tag:**
    ```bash
    gh workflow run release.yaml --ref X.Y.Z-beta
    ```

12. **Monitor and approve deployment:**
    ```bash
    # Check workflow status
    gh run list --workflow=release.yaml --limit 3

    # View specific run
    gh run view [RUN-ID]

    # Check for pending deployments
    gh api repos/dmayo3/mocksafe/actions/runs/[RUN-ID]/pending_deployments

    # Approve deployments (if needed)
    gh api repos/dmayo3/mocksafe/actions/runs/[RUN-ID]/pending_deployments \
      --method POST \
      --field environment_ids[]=[TESTPYPI-ENV-ID] \
      --field environment_ids[]=[PYPI-ENV-ID] \
      --field state=approved \
      --field comment="Approved via automated release process"
    ```

### 5. Manual Review and Documentation

13. **Manual artifact review** - Check the following URLs:
    - **PyPI Package**: https://pypi.org/project/mocksafe/X.Y.Z-betaN/
    - **TestPyPI Package**: https://test.pypi.org/project/mocksafe/X.Y.Z-betaN/
    - **ReadTheDocs**: https://mocksafe.readthedocs.io/en/X.Y.Z-beta/

14. **Create GitHub Release:**
    ```bash
    gh release create X.Y.Z-beta \
      --title "Release vX.Y.Z-beta" \
      --notes "[Release notes content]" \
      --prerelease
    ```

### 6. Milestone Management

15. **Close the milestone:**
    ```bash
    # Find milestone number
    gh api repos/dmayo3/mocksafe/milestones --jq '.[] | select(.title=="vX.Y beta") | .number'

    # Close milestone
    gh api repos/dmayo3/mocksafe/milestones/[NUMBER] --method PATCH --field state=closed
    ```

## Known Issues and Manual Tasks

### 1. PyPI Documentation Link Issue

**Problem**: The "Docs: Read The Docs" link on the PyPI package page may point to an older version (e.g., 0.6 instead of the current release).

**Current Status**: Not easily fixable post-release. This appears to be cached or configured somewhere in the package metadata.

**For Next Release**: Investigate if this can be fixed in `pyproject.toml` or another configuration file before release.

### 2. ReadTheDocs Version Activation

**Problem**: New version builds need to be manually enabled in ReadTheDocs admin panel.

**Manual Steps Required**:
1. Go to ReadTheDocs admin panel
2. Navigate to the project settings
3. Find the new version (X.Y.Z-beta)
4. Manually activate/enable it

**Automation Opportunity**: Investigate ReadTheDocs API for automatic version activation.

## Environment IDs for Deployment Approval

For reference, the environment IDs used in the approval process:
- **TestPyPI Environment ID**: `3609739890`
- **PyPI Environment ID**: `3609764890`

*Note: These IDs may change if environments are recreated.*

## Troubleshooting

### Branch Protection Issues

If you encounter "Branch 'main' is not allowed to deploy to pypi" errors:
- Ensure you're running the release workflow against a **tag**, not the main branch
- Use `--ref X.Y.Z-beta` when triggering the workflow

### Pre-commit Hook Failures

If pre-commit hooks fail during the commit process:
- Review the failures and fix any code formatting issues
- Most issues can be auto-fixed by running the hooks again
- In rare cases, use `--no-verify` (not recommended)

### Workflow Permission Issues

If deployment approval fails:
- Verify you have admin access to the repository
- Check that the GitHub CLI is authenticated with appropriate permissions
- The authenticated user must be listed as a reviewer in the environment protection rules

## Future Improvements

**📋 See Issue #95** for comprehensive automation enhancement tracking and implementation plan.

### Automation Opportunities

1. **ReadTheDocs Integration**: Investigate API-based version activation (tracked in #95)
2. **PyPI Documentation Links**: Research fixing documentation URL references (tracked in #95)
3. **Release Notes Generation**: Consider automated changelog generation (tracked in #95)
4. **Milestone Management**: Could be automated based on version tags (tracked in #95)
5. **Deployment Approval Automation**: Streamline manual deployment approval process (tracked in #95)
6. **Workflow Consolidation**: Combine version bump, tagging, and release into single workflow (tracked in #95)

### Process Improvements

1. **Release Checklist**: Create a GitHub issue template for releases
2. **Notification System**: Set up notifications for release completion
3. **Rollback Procedures**: Document rollback steps for failed releases

## Release History

- **v0.10.0-beta**: Released on 2025-09-16, first release using this documented process

---

*This document should be updated after each release to capture any new learnings or process changes.*
