#!/usr/bin/env bash
set -euo pipefail

# version-bump.sh - Handle version bumping for MockSafe releases
# Usage: ./version-bump.sh <bump_type> <prerelease_type> [custom_version]

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# Function to validate version format
validate_version() {
    local version=$1
    if [[ ! "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-z]+(\.[0-9]+)?)?$ ]]; then
        log_error "Invalid version format: $version"
        log_error "Expected format: X.Y.Z or X.Y.Z-tag or X.Y.Z-tag.N"
        return 1
    fi
    return 0
}

# Parse arguments
BUMP_TYPE="${1:-}"
PRERELEASE_TYPE="${2:-none}"
CUSTOM_VERSION="${3:-}"

if [[ -z "$BUMP_TYPE" ]]; then
    log_error "Usage: $0 <bump_type> <prerelease_type> [custom_version]"
    log_error "bump_type: patch, minor, major"
    log_error "prerelease_type: none, beta, rc"
    exit 1
fi

# Get current version from pyproject.toml
log_info "Getting current version..."
CURRENT_VERSION=$(python -c "
import tomllib
with open('pyproject.toml', 'rb') as f:
    data = tomllib.load(f)
    print(data['tool']['bumpver']['current_version'])
" 2>/dev/null) || {
    log_error "Failed to read current version from pyproject.toml"
    exit 1
}

log_info "Current version: $CURRENT_VERSION"

# Determine the new version
if [[ -n "$CUSTOM_VERSION" ]]; then
    log_info "Using custom version: $CUSTOM_VERSION"

    # Validate custom version format
    if ! validate_version "$CUSTOM_VERSION"; then
        exit 1
    fi

    NEW_VERSION="$CUSTOM_VERSION"
else
    log_info "Calculating version for bump type: $BUMP_TYPE with prerelease: $PRERELEASE_TYPE"

    # Parse current version (remove any existing prerelease tags)
    BASE_VERSION="${CURRENT_VERSION%%-*}"
    IFS='.' read -r MAJOR MINOR PATCH <<< "$BASE_VERSION"

    # Validate bump type
    case "$BUMP_TYPE" in
        major)
            NEW_MAJOR=$((MAJOR + 1))
            NEW_MINOR=0
            NEW_PATCH=0
            ;;
        minor)
            NEW_MAJOR=$MAJOR
            NEW_MINOR=$((MINOR + 1))
            NEW_PATCH=0
            ;;
        patch)
            NEW_MAJOR=$MAJOR
            NEW_MINOR=$MINOR
            NEW_PATCH=$((PATCH + 1))
            ;;
        *)
            log_error "Invalid bump type: $BUMP_TYPE"
            log_error "Valid types: patch, minor, major"
            exit 1
            ;;
    esac

    # Build base version
    NEW_VERSION="${NEW_MAJOR}.${NEW_MINOR}.${NEW_PATCH}"

    # Add prerelease suffix if specified
    if [[ "$PRERELEASE_TYPE" != "none" ]]; then
        case "$PRERELEASE_TYPE" in
            beta|rc)
                NEW_VERSION="${NEW_VERSION}-${PRERELEASE_TYPE}"
                log_info "Adding $PRERELEASE_TYPE prerelease tag"
                ;;
            *)
                log_error "Invalid prerelease type: $PRERELEASE_TYPE"
                log_error "Valid types: none, beta, rc"
                exit 1
                ;;
        esac
    fi

    log_info "Calculated new version: $NEW_VERSION"
fi

# Validate the determined version
if ! validate_version "$NEW_VERSION"; then
    exit 1
fi

# Output the version for GitHub Actions
echo "version=$NEW_VERSION"

# Create release branch
BRANCH_NAME="release-v$NEW_VERSION"
log_info "Creating branch: $BRANCH_NAME"

if ! git checkout -b "$BRANCH_NAME"; then
    log_error "Failed to create branch: $BRANCH_NAME"
    exit 1
fi

# Apply version bump
log_info "Applying version bump to $NEW_VERSION..."

if [[ -n "$CUSTOM_VERSION" ]]; then
    # For custom version, use --set-version
    if ! bumpver update --set-version "$NEW_VERSION" --no-tag-commit; then
        log_error "Failed to apply version bump"
        exit 1
    fi
else
    # For standard bumps, use the appropriate flag
    case "$BUMP_TYPE" in
        major|minor|patch)
            BUMP_CMD="bumpver update --$BUMP_TYPE --no-tag-commit"
            ;;
        beta|rc)
            BUMP_CMD="bumpver update --tag $BUMP_TYPE --no-tag-commit"
            ;;
    esac

    if ! eval "$BUMP_CMD"; then
        log_error "Failed to apply version bump"
        exit 1
    fi
fi

# Show what changed
log_info "Files modified:"
git diff --name-only

# Configure git for commit
git config user.name "github-actions[bot]"
git config user.email "github-actions[bot]@users.noreply.github.com"

# Commit changes
log_info "Committing version changes..."
git add .

COMMIT_MSG="chore: bump version to $NEW_VERSION

Automated version bump via GitHub Actions workflow.
Bump type: $BUMP_TYPE"

if [[ -n "$CUSTOM_VERSION" ]]; then
    COMMIT_MSG="$COMMIT_MSG
Custom version: $CUSTOM_VERSION"
fi

git commit -m "$COMMIT_MSG"

# Push branch
log_info "Pushing branch: $BRANCH_NAME"
if ! git push origin "$BRANCH_NAME"; then
    log_error "Failed to push branch"
    exit 1
fi

# Output success information
log_info "✅ Successfully created release branch: $BRANCH_NAME"
log_info "✅ Version bumped to: $NEW_VERSION"

# Set outputs for GitHub Actions
echo "branch=$BRANCH_NAME" >> "${GITHUB_OUTPUT:-/dev/stdout}"
echo "version=$NEW_VERSION" >> "${GITHUB_OUTPUT:-/dev/stdout}"
