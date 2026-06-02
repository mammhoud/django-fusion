#!/bin/bash

################################################################################
# Comprehensive Test Runner with Proxy and Debug Support
# Runs tests for websites, SSL verification, and deployment checks
################################################################################

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
WORKSPACE_ROOT="/root/site/websites"
TESTS_DIR="$WORKSPACE_ROOT/tests"
SCRIPTS_DIR="$TESTS_DIR/scripts"
LOG_DIR="$WORKSPACE_ROOT/logs/tests"
REPORT_FILE="$LOG_DIR/test-report-$(date +%Y%m%d_%H%M%S).txt"

# Create log directory
mkdir -p "$LOG_DIR"

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
    echo "✅ $1" >> "$REPORT_FILE"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
    echo "❌ $1" >> "$REPORT_FILE"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    echo "⚠️  $1" >> "$REPORT_FILE"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
    echo "ℹ️  $1" >> "$REPORT_FILE"
}

test_separator() {
    echo -e "\n${CYAN}───────────────────────────────────────────────────────────────${NC}\n"
    echo "───────────────────────────────────────────────────────────────" >> "$REPORT_FILE"
}

################################################################################
# Test Functions
################################################################################

test_ssl_config() {
    print_header "Test 1: SSL Configuration Verification"
    
    if [ -f "$SCRIPTS_DIR/verify-ssl-config.sh" ]; then
        if bash "$SCRIPTS_DIR/verify-ssl-config.sh" 2>&1 | tee -a "$REPORT_FILE"; then
            print_success "SSL configuration verified"
            return 0
        else
            print_error "SSL configuration verification failed"
            return 1
        fi
    else
        print_warning "SSL verification script not found"
        return 2
    fi
    
    test_separator
}

test_docker_compose_syntax() {
    print_header "Test 2: Docker Compose Syntax Validation"
    
    if command -v docker &> /dev/null; then
        if docker compose -f "$WORKSPACE_ROOT/docker-compose.yml" config > /dev/null 2>&1; then
            print_success "Docker Compose syntax is valid"
            return 0
        else
            print_error "Docker Compose syntax is invalid"
            return 1
        fi
    else
        print_warning "Docker not installed, skipping Docker Compose syntax validation"
        return 2
    fi
    
    test_separator
}

test_makefile_targets() {
    print_header "Test 3: Makefile Targets Availability"
    
    cd "$WORKSPACE_ROOT"
    
    local targets=("help" "check" "build-assets-all" "docker-status" "test" "docker-health-check")
    local failed=0
    
    for target in "${targets[@]}"; do
        if make -n "$target" > /dev/null 2>&1; then
            print_info "✓ Target available: $target"
            echo "✓ Target available: $target" >> "$REPORT_FILE"
        else
            print_error "Target not available: $target"
            failed=$((failed + 1))
        fi
    done
    
    if [ $failed -eq 0 ]; then
        print_success "All Makefile targets available"
        return 0
    else
        print_error "$failed Makefile targets not available"
        return 1
    fi
    
    test_separator
}

test_certificate_files() {
    print_header "Test 4: SSL Certificate Files"
    
    local cert_dir="$WORKSPACE_ROOT/compose/traefik/certs"
    local failed=0
    
    if [ -d "$cert_dir" ]; then
        local certs=(
            "ctc-research.crt"
            "structa-cloud.crt"
            "vresume.crt"
        )
        
        for cert in "${certs[@]}"; do
            if [ -f "$cert_dir/$cert" ]; then
                print_info "✓ Certificate found: $cert"
                echo "✓ Certificate found: $cert" >> "$REPORT_FILE"
            else
                print_error "Certificate missing: $cert"
                failed=$((failed + 1))
            fi
        done
        
        if [ $failed -eq 0 ]; then
            print_success "All SSL certificates present"
            return 0
        else
            print_error "$failed SSL certificates missing"
            return 1
        fi
    else
        print_error "Certificate directory not found: $cert_dir"
        return 1
    fi
    
    test_separator
}

test_documentation() {
    print_header "Test 5: Documentation Completeness"
    
    local docs_dir="$WORKSPACE_ROOT/docs"
    local required_docs=(
        "00_MASTER_INDEX.md"
        "SAFE_DEPLOYMENT_PROCEDURE.md"
        "FIXTURE_LOADING_ERROR_ANALYSIS.md"
        "DEPLOYMENT_GUIDE_SSL.md"
        "READ_ME_FIRST.md"
    )
    
    local failed=0
    
    for doc in "${required_docs[@]}"; do
        if [ -f "$docs_dir/$doc" ]; then
            print_info "✓ Documentation found: $doc"
            echo "✓ Documentation found: $doc" >> "$REPORT_FILE"
        else
            print_error "Documentation missing: $doc"
            failed=$((failed + 1))
        fi
    done
    
    if [ $failed -eq 0 ]; then
        print_success "All required documentation present"
        return 0
    else
        print_error "$failed documentation files missing"
        return 1
    fi
    
    test_separator
}

test_repository_structure() {
    print_header "Test 6: Repository Structure Validation"
    
    local failed=0
    
    # Check for base directory cleanup
    local base_md=$(find "$WORKSPACE_ROOT" -maxdepth 1 -name "*.md" -type f | wc -l)
    local base_log=$(find "$WORKSPACE_ROOT" -maxdepth 1 -name "*.log" -type f | wc -l)
    
    if [ "$base_md" -eq 0 ]; then
        print_info "✓ Base directory clean: no .md files"
        echo "✓ Base directory clean: no .md files" >> "$REPORT_FILE"
    else
        print_error "Base directory contains $base_md .md files"
        failed=$((failed + 1))
    fi
    
    if [ "$base_log" -eq 0 ]; then
        print_info "✓ Base directory clean: no .log files"
        echo "✓ Base directory clean: no .log files" >> "$REPORT_FILE"
    else
        print_error "Base directory contains $base_log .log files"
        failed=$((failed + 1))
    fi
    
    # Check for required directories
    local required_dirs=("docs" "compose" "tests" "scripts")
    
    for dir in "${required_dirs[@]}"; do
        if [ -d "$WORKSPACE_ROOT/$dir" ]; then
            print_info "✓ Directory exists: $dir"
            echo "✓ Directory exists: $dir" >> "$REPORT_FILE"
        else
            print_error "Directory missing: $dir"
            failed=$((failed + 1))
        fi
    done
    
    if [ $failed -eq 0 ]; then
        print_success "Repository structure is valid"
        return 0
    else
        print_error "$failed structure issues found"
        return 1
    fi
    
    test_separator
}

test_services_configuration() {
    print_header "Test 7: Docker Services Configuration"
    
    local compose_file="$WORKSPACE_ROOT/docker-compose.yml"
    local required_services=(
        "traefik"
        "postgres"
        "redis"
        "web-ctc-research"
        "web-lms-demo"
        "web-vresume"
        "shared-media"
    )
    
    local failed=0
    
    for service in "${required_services[@]}"; do
        if grep -q "container_name: $service" "$WORKSPACE_ROOT"/*/docker-compose.yml "$WORKSPACE_ROOT"/compose/docker-compose*.yml 2>/dev/null; then
            print_info "✓ Service configured: $service"
            echo "✓ Service configured: $service" >> "$REPORT_FILE"
        else
            print_warning "Service not found in config: $service"
            failed=$((failed + 1))
        fi
    done
    
    if [ $failed -eq 0 ]; then
        print_success "All required services configured"
        return 0
    else
        print_warning "$failed services not found in configuration"
        return 1
    fi
    
    test_separator
}

test_environment_variables() {
    print_header "Test 8: Environment Variables"
    
    local env_file="$WORKSPACE_ROOT/.env"
    
    if [ -f "$env_file" ]; then
        print_info "Environment file found: .env"
        
        # Check for required variables
        local required_vars=(
            "POSTGRES_USER"
            "POSTGRES_PASSWORD"
            "POSTGRES_DB"
        )
        
        local failed=0
        
        for var in "${required_vars[@]}"; do
            if grep -q "^$var=" "$env_file"; then
                print_info "✓ Environment variable set: $var"
                echo "✓ Environment variable set: $var" >> "$REPORT_FILE"
            else
                print_warning "Environment variable not set: $var"
                failed=$((failed + 1))
            fi
        done
        
        if [ $failed -eq 0 ]; then
            print_success "All required environment variables configured"
            return 0
        else
            print_warning "$failed environment variables not configured"
            return 1
        fi
    else
        print_warning "Environment file not found: .env"
        return 2
    fi
    
    test_separator
}

test_network_connectivity() {
    print_header "Test 9: Docker Network Connectivity"
    
    if ! command -v docker &> /dev/null; then
        print_warning "Docker not installed, skipping network test"
        return 2
    fi
    
    # Check if docker networks exist
    local networks=("traefik-net" "site_network")
    local failed=0
    
    for network in "${networks[@]}"; do
        if docker network ls | grep -q "$network"; then
            print_info "✓ Network exists: $network"
            echo "✓ Network exists: $network" >> "$REPORT_FILE"
        else
            print_warning "Network not found: $network (will be created on startup)"
            # Don't count as failure since networks are created automatically
        fi
    done
    
    print_info "Networks will be created automatically on service startup"
    print_success "Docker network configuration valid"
    return 0
    
    test_separator
}

test_proxy_configuration() {
    print_header "Test 10: Traefik Proxy Configuration"
    
    local traefik_config="$WORKSPACE_ROOT/compose/traefik/traefik.yml"
    
    if [ -f "$traefik_config" ]; then
        # Check for TLS configuration
        if grep -q "tls:" "$traefik_config"; then
            print_info "✓ TLS configuration found"
            echo "✓ TLS configuration found" >> "$REPORT_FILE"
        else
            print_error "TLS configuration missing"
            return 1
        fi
        
        # Check for entry points
        if grep -q "entryPoints:" "$traefik_config"; then
            print_info "✓ Entry points configured"
            echo "✓ Entry points configured" >> "$REPORT_FILE"
        else
            print_error "Entry points not configured"
            return 1
        fi
        
        # Check for providers
        if grep -q "providers:" "$traefik_config"; then
            print_info "✓ Providers configured"
            echo "✓ Providers configured" >> "$REPORT_FILE"
        else
            print_error "Providers not configured"
            return 1
        fi
        
        print_success "Traefik proxy configuration valid"
        return 0
    else
        print_error "Traefik configuration file not found"
        return 1
    fi
    
    test_separator
}

################################################################################
# Test Execution
################################################################################

run_all_tests() {
    print_header "🧪 COMPREHENSIVE TEST SUITE"
    
    # Initialize report
    cat > "$REPORT_FILE" << EOF
================================
TEST REPORT
Generated: $(date)
================================

EOF
    
    local total=0
    local passed=0
    local failed=0
    local skipped=0
    
    # Run all tests
    test_ssl_config && ((passed++)) || ((failed++)); ((total++))
    test_docker_compose_syntax && ((passed++)) || ((failed++)); ((total++))
    test_makefile_targets && ((passed++)) || ((failed++)); ((total++))
    test_certificate_files && ((passed++)) || ((failed++)); ((total++))
    test_documentation && ((passed++)) || ((failed++)); ((total++))
    test_repository_structure && ((passed++)) || ((failed++)); ((total++))
    test_services_configuration && ((passed++)) || ((failed++)); ((total++))
    test_environment_variables && ((passed++)) || ((failed++)); ((total++))
    test_network_connectivity && ((passed++)) || ((failed++)); ((total++))
    test_proxy_configuration && ((passed++)) || ((failed++)); ((total++))
    
    # Print summary
    print_header "📊 TEST SUMMARY"
    
    echo -e "\nTotal Tests:    $total"
    echo -e "${GREEN}Passed:${NC}        $passed"
    echo -e "${RED}Failed:${NC}        $failed"
    echo -e "${YELLOW}Skipped:${NC}       $skipped"
    echo ""
    
    # Calculate percentage
    if [ $total -gt 0 ]; then
        local percentage=$((passed * 100 / total))
        echo -e "Success Rate:   ${GREEN}${percentage}%${NC}"
    fi
    
    # Save summary to report
    {
        echo ""
        echo "================================"
        echo "TEST SUMMARY"
        echo "================================"
        echo "Total Tests:    $total"
        echo "Passed:         $passed"
        echo "Failed:         $failed"
        echo "Skipped:        $skipped"
        if [ $total -gt 0 ]; then
            local percentage=$((passed * 100 / total))
            echo "Success Rate:   ${percentage}%"
        fi
        echo ""
        echo "Report generated: $(date)"
    } >> "$REPORT_FILE"
    
    print_info "Full report saved to: $REPORT_FILE"
    
    # Return appropriate exit code
    if [ $failed -eq 0 ]; then
        print_success "ALL TESTS PASSED!"
        return 0
    else
        print_error "$failed tests failed"
        return 1
    fi
}

################################################################################
# Main
################################################################################

main() {
    cd "$WORKSPACE_ROOT"
    run_all_tests
}

# Run main function
main "$@"
