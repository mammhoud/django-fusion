#!/bin/bash
# Makefile Validation and Testing Script
# Validates all Makefile targets and ensures they can be executed

set -e

echo "=========================================="
echo "Makefile Validation Script"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
SKIPPED=0

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to log success
success() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

# Function to log failure
failure() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

# Function to log skip
skip() {
    echo -e "${YELLOW}○${NC} $1"
    ((SKIPPED++))
}

# Function to log info
info() {
    echo -e "${BLUE}→${NC} $1"
}

# Function to log section
section() {
    echo ""
    echo -e "${CYAN}==========================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}==========================================${NC}"
}

# Function to test a make target
test_make_target() {
    local website=$1
    local target=$2
    local description=$3
    local expected_exit=${4:-0}

    info "Testing: WEBSITE=$website make $target"

    if [ "$expected_exit" == "0" ]; then
        if make --dry-run -C /data/coolify/applications WEBSITE="$website" "$target" >/dev/null 2>&1; then
            success "$description (WEBSITE=$website)"
        else
            failure "$description (WEBSITE=$website)"
        fi
    else
        if make --dry-run -C /data/coolify/applications WEBSITE="$website" "$target" >/dev/null 2>&1; then
            failure "$description (should have failed)"
        else
            success "$description (expected failure)"
        fi
    fi
}

# Check dependencies
section "Checking Dependencies"

if command_exists make; then
    success "make is installed"
else
    failure "make is not installed"
fi

if command_exists python3; then
    success "python3 is installed"
else
    failure "python3 is not installed"
fi

if command_exists docker; then
    success "docker is installed"
else
    skip "docker is not installed (skipping docker tests)"
fi

if command_exists uv; then
    success "uv is installed"
else
    skip "uv is not installed (skipping uv commands)"
fi

# Validate main Makefile structure
section "Validating Main Makefile"

if [ -f "/data/coolify/applications/Makefile" ]; then
    success "Main Makefile exists"
else
    failure "Main Makefile not found"
    exit 1
fi

# Show make targets
info "Available make targets:"
make -C /data/coolify/applications show-targets 2>/dev/null || echo "  (show-targets command not available)"

# Validate website aliases
section "Validating Website Aliases"

for alias in ctc ctc-research ctc-research.com ctc-website; do
    info "Testing alias: $alias"
    result=$(make -C /data/coolify/applications WEBSITE="$alias" show-vars 2>/dev/null | grep "SITE=" | cut -d'=' -f2)
    if [ "$result" == "ctc-research" ]; then
        success "Alias '$alias' resolves to ctc-research"
    else
        failure "Alias '$alias' should resolve to ctc-research, got '$result'"
    fi
done

for alias in structa lms-demo lms core structa.cloud; do
    info "Testing alias: $alias"
    result=$(make -C /data/coolify/applications WEBSITE="$alias" show-vars 2>/dev/null | grep "SITE=" | cut -d'=' -f2)
    if [ "$result" == "lms-demo" ]; then
        success "Alias '$alias' resolves to lms-demo"
    else
        failure "Alias '$alias' should resolve to lms-demo, got '$result'"
    fi
done

for alias in vresume VResume resume vresume.structa.cloud; do
    info "Testing alias: $alias"
    result=$(make -C /data/coolify/applications WEBSITE="$alias" show-vars 2>/dev/null | grep "SITE=" | cut -d'=' -f2)
    if [ "$result" == "vresume" ]; then
        success "Alias '$alias' resolves to vresume"
    else
        failure "Alias '$alias' should resolve to vresume, got '$result'"
    fi
done

# Validate Django sites
section "Validating Django Sites"

for site in ctc-research lms-demo vresume; do
    if [ -d "/data/coolify/applications/$site" ]; then
        success "Site directory exists: $site"
    else
        failure "Site directory not found: $site"
    fi

    if [ -f "/data/coolify/applications/$site/manage.py" ]; then
        success "manage.py exists: $site"
    else
        failure "manage.py not found: $site"
    fi

    if [ -f "/data/coolify/applications/$site/Makefile" ]; then
        success "Makefile exists: $site"
    else
        failure "Makefile not found: $site"
    fi
done

# Validate sub-Makefiles
section "Validating Sub-Makefiles"

for site in ctc-research lms-demo VResume; do
    makefile="/data/coolify/applications/$site/Makefile"
    if [ -f "$makefile" ]; then
        success "Sub-Makefile exists: $site"

        # Check if help target exists
        if grep -q "help:" "$makefile"; then
            success "help target exists in $site/Makefile"
        else
            failure "help target not found in $site/Makefile"
        fi
    else
        failure "Sub-Makefile not found: $site"
    fi
done

# Summary
section "Validation Summary"

echo ""
echo -e "${CYAN}Results:${NC}"
echo -e "${GREEN}Passed:${NC} $PASSED"
echo -e "${RED}Failed:${NC} $FAILED"
echo -e "${YELLOW}Skipped:${NC} $SKIPPED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All critical validations passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some validations failed. Please review.${NC}"
    exit 1
fi
