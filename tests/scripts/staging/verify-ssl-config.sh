#!/bin/bash

###############################################################################
# SSL Configuration Verification Script
# Verifies that all SSL certificate configurations are in place
###############################################################################

set -e

echo "======================================================================"
echo "SSL/TLS Configuration Verification"
echo "======================================================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track errors
ERRORS=0
WARNINGS=0

# Functions
check_file() {
    local file=$1
    local description=$2
    
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $description"
        return 0
    else
        echo -e "${RED}✗${NC} $description - FILE NOT FOUND: $file"
        ((ERRORS++))
        return 1
    fi
}

check_permission() {
    local file=$1
    local expected_perm=$2
    local description=$3
    
    if [ -f "$file" ]; then
        local actual_perm=$(stat -c %a "$file")
        if [ "$actual_perm" == "$expected_perm" ]; then
            echo -e "${GREEN}✓${NC} $description (permissions: $actual_perm)"
            return 0
        else
            echo -e "${YELLOW}⚠${NC} $description - Expected: $expected_perm, Got: $actual_perm"
            ((WARNINGS++))
            return 1
        fi
    fi
}

check_contains() {
    local file=$1
    local pattern=$2
    local description=$3
    
    if grep -q "$pattern" "$file" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $description"
        return 0
    else
        echo -e "${RED}✗${NC} $description - Pattern not found in $file"
        ((ERRORS++))
        return 1
    fi
}

# Check certificate files
echo ""
echo "1. Certificate Files Verification"
echo "=================================="

# LE-managed: acme.json is the source of truth (Stage 3+). Until Stage 3
# the self-signed .crt/.key/.pem files in certs/ are still referenced
# via certs.yml as a fallback.
check_file "/root/site/websites/applications/proxy/traefik/acme/acme.json" "Traefik ACME store (acme.json)"
check_permission "/root/site/websites/applications/proxy/traefik/acme/acme.json" "600" "ACME store permissions"

check_file "/root/site/websites/applications/proxy/traefik/certs/ctc-research.crt" "CTC-Research self-signed cert (fallback)"
check_file "/root/site/websites/applications/proxy/traefik/certs/ctc-research.key" "CTC-Research self-signed key (fallback)"

check_file "/root/site/websites/applications/proxy/traefik/certs/structa-cloud.crt" "Structa Cloud self-signed cert (fallback)"
check_file "/root/site/websites/applications/proxy/traefik/certs/structa-cloud.key" "Structa Cloud self-signed key (fallback)"

check_file "/root/site/websites/applications/proxy/traefik/certs/vresume.crt" "VResume self-signed cert (fallback)"
check_file "/root/site/websites/applications/proxy/traefik/certs/vresume.key" "VResume self-signed key (fallback)"

# Check certificate permissions
echo ""
echo "2. Certificate File Permissions"
echo "================================"

# Self-signed keys (fallback) must remain 0600
check_permission "/root/site/websites/applications/proxy/traefik/certs/ctc-research.key" "600" "CTC-Research Key Permissions"
check_permission "/root/site/websites/applications/proxy/traefik/certs/structa-cloud.key" "600" "Structa Cloud Key Permissions"
check_permission "/root/site/websites/applications/proxy/traefik/certs/vresume.key" "600" "VResume Key Permissions"

# Check configuration files
echo ""
echo "3. Configuration Files Verification"
echo "===================================="

check_file "/root/site/websites/applications/proxy/traefik/traefik.yml" "Traefik Static Configuration"
check_file "/root/site/websites/applications/proxy/docker-compose.traefik.yml" "Traefik Docker Compose"
check_file "/root/site/websites/applications/proxy/traefik/dynamic/ctc-research.yml" "CTC-Research Routing Config"
check_file "/root/site/websites/applications/proxy/traefik/dynamic/structa-cloud.yml" "Structa Cloud Routing Config"
check_file "/root/site/websites/applications/proxy/traefik/dynamic/vresume.yml" "VResume Routing Config"

# Check configuration content
echo ""
echo "4. Configuration Content Verification"
echo "======================================"

# Static config: must declare the letsencrypt certificatesResolvers block
# (dnsChallenge + cloudflare). certs.yml self-signed fallback is still
# expected on the host until Stage 3 deletes it.
check_contains "/root/site/websites/applications/proxy/traefik/dynamic.yml" "certificatesResolvers:" "Static config declares certificatesResolvers"
check_contains "/root/site/websites/applications/proxy/traefik/dynamic.yml" "certResolver: letsencrypt" "Static config references 'letsencrypt' resolver"
check_contains "/root/site/websites/applications/proxy/traefik/dynamic.yml" "provider: cloudflare" "Static config uses Cloudflare DNS-01"
check_contains "/root/site/websites/applications/proxy/traefik/dynamic.yml" "dnsChallenge:" "Static config uses DNS-01 challenge"

check_file "/root/site/websites/applications/proxy/traefik/dynamic/certs.yml" "Self-signed certs fallback (deleted in Stage 3)"

check_contains "/root/site/websites/applications/proxy/docker-compose.traefik.yml" "./traefik/certs:/etc/traefik/certs" "Legacy self-signed certs volume mount in compose"
check_contains "/root/site/websites/applications/proxy/docker-compose.traefik.yml" "./acme:/etc/traefik/acme" "ACME store volume mount in compose"
check_contains "/root/site/websites/applications/proxy/docker-compose.traefik.yml" "CF_DNS_API_TOKEN" "Cloudflare token env var passed to proxy"

# Stage 1 of the LE rollout only enables vresume. Stage 2 will add the
# other two sites — re-enable these checks at that point.
# check_contains "/root/site/websites/applications/proxy/traefik/dynamic/ctc-research.yml" "certResolver: letsencrypt" "CTC-Research uses Let's Encrypt cert resolver"
# check_contains "/root/site/websites/applications/proxy/traefik/dynamic/structa-cloud.yml" "certResolver: letsencrypt" "Structa Cloud uses Let's Encrypt cert resolver"
check_contains "/root/site/websites/applications/proxy/traefik/dynamic/vresume.yml" "certResolver: letsencrypt" "VResume uses Let's Encrypt cert resolver (Stage 1)"

# Check base directory cleanup
echo ""
echo "5. Repository Cleanup Verification"
echo "==================================="

if [ $(find /root/site/websites -maxdepth 1 -name "*.md" -type f | wc -l) -eq 0 ]; then
    echo -e "${GREEN}✓${NC} No markdown files in base repository"
else
    echo -e "${YELLOW}⚠${NC} Found markdown files in base repository:"
    find /root/site/websites -maxdepth 1 -name "*.md" -type f -exec echo "  - {}" \;
    ((WARNINGS++))
fi

# Check docs directory
echo ""
echo "6. Documentation Directory Verification"
echo "========================================"

if [ -d "/root/site/websites/docs" ]; then
    echo -e "${GREEN}✓${NC} Documentation directory exists"
    md_count=$(find /root/site/websites/docs -name "*.md" -type f | wc -l)
    echo -e "${GREEN}✓${NC} Found $md_count markdown files in docs/"
else
    echo -e "${RED}✗${NC} Documentation directory not found"
    ((ERRORS++))
fi

check_file "/root/site/websites/docs/00_MASTER_INDEX.md" "Master Index Documentation"
check_file "/root/site/websites/docs/TASK_4_COMPLETION_REPORT.md" "Task 4 Completion Report"
check_file "/root/site/websites/docs/DEPLOYMENT_GUIDE_SSL.md" "SSL Deployment Guide"

# Summary
echo ""
echo "======================================================================"
echo "Verification Summary"
echo "======================================================================"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ ALL CHECKS PASSED${NC}"
    echo ""
    echo "SSL Configuration is ready for deployment!"
    echo ""
    echo "Next steps:"
    echo "  1. Rebuild Traefik: docker compose build traefik"
    echo "  2. Restart Traefik: docker compose restart traefik"
    echo "  3. Verify: docker logs traefik | tail -20"
    echo "  4. Test HTTPS: curl -v https://ctc-research.com"
    exit 0
else
    echo -e "${RED}✗ VERIFICATION FAILED${NC}"
    echo ""
    echo "Errors found: $ERRORS"
    echo "Warnings: $WARNINGS"
    echo ""
    echo "Please review the issues above and correct them before deployment."
    exit 1
fi
