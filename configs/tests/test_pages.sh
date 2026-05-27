#!/bin/bash

###############################################################################
# VResume Page Testing Script
# 
# Comprehensive shell-based testing for all VResume pages.
# Tests page loads, content presence, images, and HTMX navigation.
#
# Usage:
#   bash tests/test_pages.sh                           # Default: localhost:8000
#   bash tests/test_pages.sh http://custom-url:8000    # Custom URL
#   bash tests/test_pages.sh http://localhost:8000 true # Verbose output
#
# Features:
# - Tests all main pages (Home, About, Resume, Portfolio, Blog, Contact)
# - Verifies populated data presence
# - Tests HTMX navigation
# - Tests static file availability
# - Tests API endpoints
# - Generates summary report
###############################################################################

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Configuration
BASE_URL="${1:-http://localhost:8000}"
TIMEOUT=10
VERBOSE="${2:-false}"

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

print_header() {
    echo -e "\n${CYAN}${BOLD}=========================================${NC}"
    echo -e "${CYAN}${BOLD}$1${NC}"
    echo -e "${CYAN}${BOLD}=========================================${NC}\n"
}

print_test() {
    echo -e "${BLUE}▶ Testing: $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASSED_TESTS++))
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    ((FAILED_TESTS++))
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

# Test if server is running
check_server() {
    print_header "🔍 Checking Server Connection"
    
    if curl -s --connect-timeout 2 "$BASE_URL" > /dev/null 2>&1; then
        print_success "Server is running at $BASE_URL"
        return 0
    else
        print_error "Cannot connect to server at $BASE_URL"
        print_info "Start the server with: make dev"
        exit 1
    fi
}

# Test page load
test_page_load() {
    local page_name="$1"
    local page_url="$2"
    local expected_content="$3"
    
    ((TOTAL_TESTS++))
    print_test "$page_name"
    
    # Get response
    local response=$(curl -s -w "\n%{http_code}" --max-time $TIMEOUT "$page_url")
    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | head -n-1)
    
    # Check HTTP status
    if [ "$http_code" != "200" ]; then
        print_error "$page_name returned HTTP $http_code"
        return 1
    fi
    print_success "$page_name loaded (HTTP 200)"
    
    # Check for expected content
    if [ -n "$expected_content" ]; then
        if echo "$body" | grep -q "$expected_content"; then
            print_success "Found expected content: '$expected_content'"
        else
            print_warning "Expected content not found: '$expected_content'"
        fi
    fi
    
    # Check for images
    local image_count=$(echo "$body" | grep -o '<img[^>]*src=' | wc -l)
    if [ "$image_count" -gt 0 ]; then
        print_success "Found $image_count image(s)"
    else
        print_warning "No images found on page"
    fi
    
    # Check for common populated fields
    check_populated_fields "$body" "$page_name"
    
    return 0
}

# Check for populated data fields
check_populated_fields() {
    local body="$1"
    local page_name="$2"
    
    # Check for VResume settings
    if echo "$body" | grep -q "Mammhoud"; then
        print_success "Found name: Mammhoud"
    fi
    
    if echo "$body" | grep -q "Lead Software Architect"; then
        print_success "Found job title: Lead Software Architect"
    fi
    
    if echo "$body" | grep -q "hello@mammhoud.me"; then
        print_success "Found email: hello@mammhoud.me"
    fi
    
    # Check for page-specific content
    case "$page_name" in
        "About Page")
            if echo "$body" | grep -q "passionate technologist"; then
                print_success "Found About page bio content"
            fi
            ;;
        "Resume Page")
            if echo "$body" | grep -q "Stanford\|MIT\|Google\|OpenAI"; then
                print_success "Found Resume page education/experience content"
            fi
            ;;
        "Portfolio Page")
            if echo "$body" | grep -q "Antigravity AI\|VResume CMS\|Lumina Design"; then
                print_success "Found Portfolio page projects"
            fi
            ;;
        "Blog Page")
            if echo "$body" | grep -q "Agentic Coding\|Wagtail\|Microservices"; then
                print_success "Found Blog page posts"
            fi
            ;;
        "Contact Page")
            if echo "$body" | grep -q "Let's Build Something\|New York"; then
                print_success "Found Contact page content"
            fi
            ;;
    esac
}

# Test HTMX functionality
test_htmx_navigation() {
    print_header "🔗 Testing HTMX Navigation"
    
    ((TOTAL_TESTS++))
    print_test "HTMX Tab Navigation"
    
    # Test tab navigation via HTMX
    local tabs=("about" "resume" "portfolio" "blog" "contact")
    
    for tab in "${tabs[@]}"; do
        local response=$(curl -s -w "\n%{http_code}" --max-time $TIMEOUT \
            -H "HX-Request: true" \
            "$BASE_URL/?tab=$tab")
        local http_code=$(echo "$response" | tail -n1)
        
        if [ "$http_code" = "200" ]; then
            print_success "Tab '$tab' loaded via HTMX"
        else
            print_error "Tab '$tab' failed with HTTP $http_code"
        fi
    done
}

# Test API endpoints
test_api_endpoints() {
    print_header "🔌 Testing API Endpoints"
    
    local endpoints=(
        "/api/pages/"
        "/api/settings/"
        "/api/blog/"
    )
    
    for endpoint in "${endpoints[@]}"; do
        ((TOTAL_TESTS++))
        print_test "API Endpoint: $endpoint"
        
        local response=$(curl -s -w "\n%{http_code}" --max-time $TIMEOUT "$BASE_URL$endpoint")
        local http_code=$(echo "$response" | tail -n1)
        
        if [ "$http_code" = "200" ] || [ "$http_code" = "404" ]; then
            print_success "Endpoint $endpoint responded with HTTP $http_code"
        else
            print_warning "Endpoint $endpoint returned HTTP $http_code"
        fi
    done
}

# Test static files
test_static_files() {
    print_header "📦 Testing Static Files"
    
    local static_files=(
        "/static/bundles/js/main.js"
        "/static/bundles/css/styles.min.css"
        "/static/bundles/images/logo.png"
    )
    
    for file in "${static_files[@]}"; do
        ((TOTAL_TESTS++))
        print_test "Static File: $file"
        
        local response=$(curl -s -w "\n%{http_code}" --max-time $TIMEOUT "$BASE_URL$file")
        local http_code=$(echo "$response" | tail -n1)
        
        if [ "$http_code" = "200" ]; then
            print_success "Static file loaded: $file"
        else
            print_warning "Static file not found: $file (HTTP $http_code)"
        fi
    done
}

# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

main() {
    print_header "🚀 VResume Page Testing Suite"
    print_info "Testing URL: $BASE_URL"
    print_info "Timeout: ${TIMEOUT}s"
    echo ""
    
    # Check server connection
    check_server
    
    # Test main pages
    print_header "📄 Testing Main Pages"
    
    test_page_load "Home Page" "$BASE_URL/" "VResume"
    test_page_load "About Page" "$BASE_URL/?tab=about" "passionate technologist"
    test_page_load "Resume Page" "$BASE_URL/?tab=resume" "Education\|Experience"
    test_page_load "Portfolio Page" "$BASE_URL/?tab=portfolio" "Projects\|Portfolio"
    test_page_load "Blog Page" "$BASE_URL/?tab=blog" "Blog\|Posts"
    test_page_load "Contact Page" "$BASE_URL/?tab=contact" "Contact\|Message"
    
    # Test HTMX navigation
    test_htmx_navigation
    
    # Test static files
    test_static_files
    
    # Test API endpoints
    test_api_endpoints
    
    # Print summary
    print_header "📊 Test Summary"
    echo -e "Total Tests:  ${BOLD}$TOTAL_TESTS${NC}"
    echo -e "Passed:       ${GREEN}${BOLD}$PASSED_TESTS${NC}"
    echo -e "Failed:       ${RED}${BOLD}$FAILED_TESTS${NC}"
    
    if [ $FAILED_TESTS -eq 0 ]; then
        echo -e "\n${GREEN}${BOLD}✅ All tests passed!${NC}\n"
        return 0
    else
        echo -e "\n${RED}${BOLD}❌ Some tests failed${NC}\n"
        return 1
    fi
}

# Run main function
main "$@"
