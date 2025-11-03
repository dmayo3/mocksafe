# Release Process Documentation

This document outlines the complete release process for MockSafe.

## Automated Release Process (Recommended)

As of December 2024, MockSafe uses an automated GitHub Actions workflow to streamline the release process.

### Quick Start

1. **Trigger the Release Workflow:**
   ```bash
   # For standard releases:
   gh workflow run release.yaml --field bump_type=<patch|minor|major>

   # For prerelease versions:
   gh workflow run release.yaml --field bump_type=<patch|minor|major> --field prerelease_type=<beta|rc>

   # For custom version:
   gh workflow run release.yaml --field custom_version=X.Y.Z
   ```

2. **Review and Merge the PR:**
   - The workflow automatically creates a release PR
   - Review the version changes
   - Ensure all CI checks pass
   - Approve and merge the PR

3. **Continue with Manual Steps:**
   - After PR merge, continue with [Step 10](#4-tagging-and-release) of the manual process
   - Tag creation and deployment still require manual steps

### Automated Workflow Details

The automated workflow handles:
- ✅ Version bumping using `bumpver`
- ✅ Creating a release branch
- ✅ Committing version changes
- ✅ Creating a pull request with proper labels
- ✅ Providing a release checklist in the PR

**Version Bump Options:**
- **bump_type**: `patch`, `minor`, or `major` (required)
- **prerelease_type**: `none`, `beta`, or `rc` (optional, defaults to `none`)
- **custom_version**: Override with specific version string (optional)

The bump type and prerelease type are orthogonal, allowing combinations like:
- `bump_type=minor` → 1.2.0 → 1.3.0
- `bump_type=minor` + `prerelease_type=beta` → 1.2.0 → 1.3.0-beta
- `bump_type=patch` + `prerelease_type=rc` → 1.2.0 → 1.2.1-rc

## Manual Release Process (Fallback)

If the automated workflow is unavailable or for special cases, follow the manual process below.

## Prerequisites

Before starting a release, ensure you have:

- [ ] `gh` CLI tool installed and authenticated
- [ ] `bumpver` package installed
- [ ] All planned features and fixes merged into `main`
- [ ] Access to ReadTheDocs admin panel

## Manual Release Process Steps

### 1. Preparation

**Note:** Steps 1-9 are now automated by the Release Process workflow. Skip to [Step 10](#4-tagging-and-release) if using automation.

1. **Create a fresh branch from latest origin/main:**
   ```bash
   git fetch origin
   git checkout main
   git pull origin main
   git checkout -b release-vX.Y.Z  # Use appropriate version number
   ```

### 2. Version Bumping

2. **Test version bump (dry run):**
   ```bash
   bumpver update [--major|--minor|--patch] [--tag TAG] --no-commit --no-tag-commit --dry
   ```

3. **Review the output** to ensure it looks correct. Check that all files are updated appropriately.

4. **Apply version bump:**
   ```bash
   bumpver update [--major|--minor|--patch] [--tag TAG] --no-commit --no-tag-commit
   ```

5. **Commit the changes:**
   ```bash
   git add .
   git commit -m "Bump version U.V.W -> X.Y.Z"
   ```

### 3. Pull Request Process

6. **Push branch and create PR:**
   ```bash
   git push origin release-vX.Y.Z
   gh pr create --title "Release vX.Y.Z" --body "Version bump for vX.Y.Z release. Closes #[issue-number]"
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
    git tag X.Y.Z
    git push origin X.Y.Z
    ```

11. **Trigger publish workflow on the tag:**
    ```bash
    gh workflow run publish.yaml --ref X.Y.Z
    ```

12. **Monitor and approve deployment:**
    ```bash
    # Check workflow status
    gh run list --workflow=publish.yaml --limit 3

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
    - **PyPI Package**: https://pypi.org/project/mocksafe/X.Y.Z/
    - **TestPyPI Package**: https://test.pypi.org/project/mocksafe/X.Y.Z/
    - **ReadTheDocs**: https://mocksafe.readthedocs.io/en/X.Y.Z/

14. **Create GitHub Release:**
    ```bash
    gh release create X.Y.Z \
      --title "Release vX.Y.Z" \
      --notes "[Release notes content]" \
      [--prerelease]  # Use for beta/rc releases
    ```

### 6. Milestone Management

15. **Close the milestone:**
    ```bash
    # Find milestone number
    gh api repos/dmayo3/mocksafe/milestones --jq '.[] | select(.title=="vX.Y") | .number'

    # Close milestone
    gh api repos/dmayo3/mocksafe/milestones/[NUMBER] --method PATCH --field state=closed
    ```

## Known Issues and Manual Tasks

### 1. PyPI Documentation Link Issue

**Problem**: The "Docs: Read The Docs" link on the PyPI package page may point to an older version.

**Current Status**: Requires investigation and should be tracked as a separate issue.

### 2. ReadTheDocs Version Activation

**Problem**: New version builds need to be manually enabled in ReadTheDocs admin panel.

**Manual Steps Required**:
1. Go to ReadTheDocs admin panel
2. Navigate to the project settings
3. Find the new version
4. Manually activate/enable it

**Note**: Automation opportunities should be tracked as separate issues.

## Environment IDs for Deployment Approval

For reference, the environment IDs used in the approval process:
- **TestPyPI Environment ID**: `3609739890`
- **PyPI Environment ID**: `3609764890`

*Note: These IDs may change if environments are recreated.*

## Troubleshooting

### Branch Protection Issues

If you encounter "Branch 'main' is not allowed to deploy to pypi" errors:
- Ensure you're running the publish workflow against a **tag**, not the main branch
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
- If you lack permissions, request help from someone who can approve deployments

## Process Improvements

Future improvements should be tracked as GitHub Issues with appropriate labels and milestones assigned.

Potential areas for improvement include workflow automation, documentation updates, and tooling enhancements.

## Workflow Files Reference

- **`.github/workflows/release.yaml`**: Automated release process workflow (version bump & PR creation)
- **`.github/workflows/publish.yaml`**: Package publishing workflow (formerly release.yaml)
- **`.github/workflows/mocksafe.yml`**: CI/CD checks for PRs

## Release History

- **v0.10.0-beta**: Released on 2025-09-16, first release using this documented process
- **TBD**: First release using automated workflow

---

*This document should be updated after each release to capture any new learnings or process changes.*
