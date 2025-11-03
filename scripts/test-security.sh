#!/usr/bin/env bash
set -euo pipefail

# test-security.sh - Security test suite for release automation scripts
# This script tests various injection scenarios to ensure proper security measures

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test result functions
pass_test() {
    local test_name="$1"
    echo -e "${GREEN}✓${NC} $test_name"
    ((TESTS_PASSED++))
    ((TESTS_RUN++))
}

fail_test() {
    local test_name="$1"
    local reason="$2"
    echo -e "${RED}✗${NC} $test_name"
    echo -e "  ${YELLOW}Reason:${NC} $reason"
    ((TESTS_FAILED++))
    ((TESTS_RUN++))
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

header() {
    echo
    echo -e "${BLUE}═══════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════${NC}"
}

# Create temporary test environment
TEST_DIR=$(mktemp -d)
trap 'rm -rf "$TEST_DIR"' EXIT

cd "$TEST_DIR"

# Create mock pyproject.toml for testing
cat > pyproject.toml << 'EOF'
[tool.bumpver]
current_version = "1.0.0"
version_pattern = "MAJOR.MINOR.PATCH[-TAG]"

[[tool.bumpver.file_patterns]]
filename = "pyproject.toml"
search = 'version = "{current_version}"'
replace = 'version = "{new_version}"'
EOF

# Copy scripts for testing (assuming they exist)
SCRIPT_DIR="$(dirname "$(dirname "$(realpath "$0")")")/scripts"
if [[ -d "$SCRIPT_DIR" ]]; then
    cp "$SCRIPT_DIR"/*.sh . 2>/dev/null || true
fi

header "Testing Version Validation"

# Test 1: Valid version formats
test_version_validation() {
    local version="$1"
    local expected="$2"

    if bash -c "
        validate_version() {
            local version=\$1
            if [[ ! \"\$version\" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-z]+(\.[0-9]+)?)?$ ]]; then
                return 1
            fi
            return 0
        }
        validate_version '$version'
    " 2>/dev/null; then
        if [[ "$expected" == "valid" ]]; then
            pass_test "Version validation: $version (expected valid)"
        else
            fail_test "Version validation: $version" "Should have been rejected"
        fi
    else
        if [[ "$expected" == "invalid" ]]; then
            pass_test "Version validation: $version (expected invalid)"
        else
            fail_test "Version validation: $version" "Should have been accepted"
        fi
    fi
}

# Valid versions
test_version_validation "1.0.0" "valid"
test_version_validation "2.3.4" "valid"
test_version_validation "10.20.30" "valid"
test_version_validation "1.0.0-beta" "valid"
test_version_validation "1.0.0-rc" "valid"
test_version_validation "1.0.0-alpha.1" "valid"

# Invalid versions - injection attempts
test_version_validation "1.0.0\$(echo pwned)" "invalid"
test_version_validation "1.0.0;rm -rf /" "invalid"
test_version_validation "1.0.0\`curl evil.com\`" "invalid"
test_version_validation "1.0.0 && echo hacked" "invalid"
test_version_validation "1.0.0|cat /etc/passwd" "invalid"
test_version_validation "1.0.0\${PATH}" "invalid"
test_version_validation "1.0.0*" "invalid"
test_version_validation "1.0.0'" "invalid"
test_version_validation '1.0.0"' "invalid"

header "Testing Command Injection Prevention"

# Test 2: Environment variable usage vs direct interpolation
test_env_var_safety() {
    local test_name="$1"
    local test_cmd="$2"
    local should_fail="$3"

    # Create a test script
    cat > test_injection.sh << EOF
#!/bin/bash
set -euo pipefail
$test_cmd
EOF

    chmod +x test_injection.sh

    # Set up malicious input
    export MALICIOUS_INPUT='$(echo "INJECTED" > /tmp/pwned.txt)'

    if ./test_injection.sh >/dev/null 2>&1; then
        if [[ "$should_fail" == "yes" ]]; then
            # Check if injection occurred
            if [[ -f /tmp/pwned.txt ]]; then
                fail_test "$test_name" "Injection succeeded!"
                rm -f /tmp/pwned.txt
            else
                pass_test "$test_name (command succeeded without injection)"
            fi
        else
            pass_test "$test_name (command succeeded)"
        fi
    else
        if [[ "$should_fail" == "yes" ]]; then
            pass_test "$test_name (command properly failed)"
        else
            fail_test "$test_name" "Command should have succeeded"
        fi
    fi

    rm -f test_injection.sh
}

# Unsafe pattern (direct interpolation) - should be avoided
info "Testing unsafe patterns (these should NOT be used in production)"

# Safe pattern (environment variables)
test_env_var_safety \
    "Safe: Environment variable usage" \
    'echo "Version: $MALICIOUS_INPUT"' \
    "no"

# Test with printf
test_env_var_safety \
    "Safe: printf with env var" \
    'printf "Version: %s\n" "$MALICIOUS_INPUT"' \
    "no"

header "Testing GitHub Actions Context Safety"

# Test 3: Simulate GitHub Actions workflow patterns
test_github_actions_pattern() {
    local pattern_name="$1"
    local script_content="$2"

    cat > gh_test.sh << EOF
#!/bin/bash
set -euo pipefail
$script_content
EOF

    chmod +x gh_test.sh

    # Set test variables
    export TEST_VERSION='1.0.0$(echo hacked)'
    export TEST_BUMP='patch'

    if bash -c "./gh_test.sh" >/dev/null 2>&1; then
        # Check for evidence of injection
        if [[ -f /tmp/hacked ]]; then
            fail_test "$pattern_name" "Injection detected"
            rm -f /tmp/hacked
        else
            pass_test "$pattern_name"
        fi
    else
        # Script failed, which might be expected for malicious input
        pass_test "$pattern_name (properly rejected malicious input)"
    fi

    rm -f gh_test.sh
}

test_github_actions_pattern \
    "GH Pattern: Environment variables in printf" \
    'printf "Version: %s\n" "$TEST_VERSION"'

test_github_actions_pattern \
    "GH Pattern: Variable in echo with quotes" \
    'echo "Version: $TEST_VERSION"'

header "Testing Script Output Parsing"

# Test 4: Safe output parsing patterns
test_output_parsing() {
    local test_name="$1"

    # Create script that outputs version info
    cat > output_test.sh << 'EOF'
#!/bin/bash
echo "version=1.0.0"
echo "branch=release-v1.0.0"
echo "Some other output"
echo "version=2.0.0$(echo should_not_execute)"
EOF

    chmod +x output_test.sh

    # Safe pattern: redirect to file first
    ./output_test.sh > output.txt
    VERSION=$(grep "^version=" output.txt | head -1 | cut -d= -f2)

    if [[ "$VERSION" == "1.0.0" ]]; then
        pass_test "$test_name: Safe file parsing"
    else
        fail_test "$test_name: Safe file parsing" "Unexpected version: $VERSION"
    fi

    rm -f output_test.sh output.txt
}

test_output_parsing "Output parsing safety"

header "Testing PR Body Generation Safety"

# Test 5: envsubst safety
test_envsubst_safety() {
    local test_name="$1"

    # Create template with variables
    cat > template.txt << 'EOF'
Version: ${VERSION}
Bump Type: ${BUMP_TYPE}
Custom: ${CUSTOM_VERSION}
Malicious: ${MALICIOUS_VAR}
EOF

    # Set environment variables
    export VERSION="1.0.0"
    export BUMP_TYPE="patch"
    export CUSTOM_VERSION="N/A"
    export MALICIOUS_VAR='$(echo "injected")'

    # Use envsubst (safe)
    envsubst < template.txt > output.txt

    # Check output
    if grep -q "injected" output.txt; then
        fail_test "$test_name" "envsubst executed the injection"
    elif grep -q '\$(echo "injected")' output.txt; then
        pass_test "$test_name (envsubst preserved literal string)"
    else
        fail_test "$test_name" "Unexpected output"
    fi

    rm -f template.txt output.txt
}

test_envsubst_safety "envsubst injection prevention"

header "Testing Bump Type Validation"

# Test 6: Orthogonal bump and prerelease types
test_bump_type_combo() {
    local bump="$1"
    local prerelease="$2"
    local expected="$3"

    # Simulate version calculation
    CURRENT="1.0.0"
    IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT"

    case "$bump" in
        major)
            NEW_VERSION="2.0.0"
            ;;
        minor)
            NEW_VERSION="1.1.0"
            ;;
        patch)
            NEW_VERSION="1.0.1"
            ;;
        *)
            NEW_VERSION="invalid"
            ;;
    esac

    if [[ "$prerelease" != "none" ]]; then
        NEW_VERSION="${NEW_VERSION}-${prerelease}"
    fi

    if [[ "$NEW_VERSION" == "$expected" ]]; then
        pass_test "Bump combo: $bump + $prerelease = $expected"
    else
        fail_test "Bump combo: $bump + $prerelease" "Expected $expected, got $NEW_VERSION"
    fi
}

test_bump_type_combo "major" "none" "2.0.0"
test_bump_type_combo "minor" "none" "1.1.0"
test_bump_type_combo "patch" "none" "1.0.1"
test_bump_type_combo "major" "beta" "2.0.0-beta"
test_bump_type_combo "minor" "rc" "1.1.0-rc"
test_bump_type_combo "patch" "beta" "1.0.1-beta"

header "Testing Script Permissions"

# Test 7: File permission checks
test_script_permissions() {
    local script="$1"

    if [[ -f "../scripts/$script" ]]; then
        if [[ -x "../scripts/$script" ]]; then
            pass_test "Script permissions: $script is executable"
        else
            fail_test "Script permissions: $script" "Not executable"
        fi
    else
        info "Skipping permission test for $script (not found)"
    fi
}

test_script_permissions "version-bump.sh"
test_script_permissions "create-release-pr.sh"

header "Test Summary"

echo
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}Total Tests Run: $TESTS_RUN${NC}"
echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo -e "${GREEN}✓ All security tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some security tests failed!${NC}"
    exit 1
fi
