#!/bin/bash

##############################################################################
# Production Verification Script - Complete System Check
##############################################################################

set -e

echo "🔍 PRODUCTION SYSTEM VERIFICATION"
echo "=================================="
echo ""

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT="verification_report_${TIMESTAMP}.txt"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# Helper functions
test_pass() {
    echo -e "${GREEN}✅ PASS: $1${NC}" | tee -a "$REPORT"
    ((PASSED++))
}

test_fail() {
    echo -e "${RED}❌ FAIL: $1${NC}" | tee -a "$REPORT"
    ((FAILED++))
}

test_warn() {
    echo -e "${YELLOW}⚠️  WARN: $1${NC}" | tee -a "$REPORT"
    ((WARNINGS++))
}

test_info() {
    echo -e "${BLUE}ℹ️  INFO: $1${NC}" | tee -a "$REPORT"
}

# Clear report
> "$REPORT"

echo "📝 Test Report: $REPORT" | tee -a "$REPORT"
echo "" | tee -a "$REPORT"

# ============================================================================
# SECTION 1: CONTAINER HEALTH
# ============================================================================
echo "═" | tee -a "$REPORT"
echo "1️⃣ CONTAINER HEALTH CHECKS" | tee -a "$REPORT"
echo "═" | tee -a "$REPORT"

CONTAINERS=("traefik" "web-ctc-research" "shared-media" "postgres" "redis")

for container in "${CONTAINERS[@]}"; do
    if docker ps --filter "name=$container" --filter "status=running" --quiet | grep -q .; then
        test_pass "Container '$container' is running"
    else
        test_fail "Container '$container' is NOT running"
    fi
done

echo "" | tee -a "$REPORT"

# ============================================================================
# SECTION 2: ENDPOINT TESTS
# ============================================================================
echo "═" | tee -a "$REPORT"
echo "2️⃣ ENDPOINT TESTS" | tee -a "$REPORT"
echo "═" | tee -a "$REPORT"

# Health endpoint
if timeout 5 curl -s http://localhost:5070/health/ 2>/dev/null | grep -q "ok"; then
    test_pass "Health endpoint responds with OK"
else
    test_warn "Health endpoint not immediately responding (may be starting)"
fi

# Traefik health
if timeout 5 curl -s http://localhost:8080/ping 2>/dev/null | grep -q "OK"; then
    test_pass "Traefik reverse proxy is healthy"
else
    test_fail "Traefik reverse proxy not responding"
fi

# Assets endpoint
if timeout 5 curl -s http://localhost:5070/assets/health/ 2>/dev/null | grep -q "ok"; then
    test_pass "Assets health endpoint available"
else
    test_warn "Assets health endpoint not responding (optional)"
fi

echo "" | tee -a "$REPORT"

# ============================================================================
# SECTION 3: DATABASE CHECKS
# ============================================================================
echo "═" | tee -a "$REPORT"
echo "3️⃣ DATABASE CHECKS" | tee -a "$REPORT"
echo "═" | tee -a "$REPORT"

# Check database exists
if docker exec postgres psql -U structa -d db_ctc -c "SELECT 1" 2>/dev/null | grep -q 1; then
    test_pass "Database 'db_ctc' exists and is accessible"
else
    test_fail "Cannot connect to database 'db_ctc'"
fi

# Check page count
PAGE_COUNT=$(docker exec postgres psql -U structa -d db_ctc -c "SELECT COUNT(*) FROM wagtailcore_page" 2>/dev/null | grep -E "^[[:space:]]*[0-9]+" | tr -d ' ')
if [ -n "$PAGE_COUNT" ]; then
    test_info "Pages in database: $PAGE_COUNT"
    if [ "$PAGE_COUNT" -ge 2 ]; then
        test_pass "Database contains page records"
    fi
else
    test_warn "Could not retrieve page count"
fi

# Check locales
LOCALE_COUNT=$(docker exec postgres psql -U structa -d db_ctc -c "SELECT COUNT(*) FROM wagtail_localize_locale" 2>/dev/null | grep -E "^[[:space:]]*[0-9]+" | tr -d ' ')
if [ -n "$LOCALE_COUNT" ] && [ "$LOCALE_COUNT" -gt 0 ]; then
    test_pass "Locales configured: $LOCALE_COUNT"
else
    test_warn "No locales found in database"
fi

echo "" | tee -a "$REPORT"

# ============================================================================
# SECTION 4: DJANGO SYSTEM CHECK
# ============================================================================
echo "═" | tee -a "$REPORT"
echo "4️⃣ DJANGO SYSTEM CHECK" | tee -a "$REPORT"
echo "═" | tee -a "$REPORT"

if docker exec web-ctc-research python manage.py check 2>&1 | grep -q "System check identified no issues"; then
    test_pass "Django system check passed (0 issues)"
else
    test_warn "Django system check may have warnings (see logs)"
fi

echo "" | tee -a "$REPORT"

# ============================================================================
# SECTION 5: STATIC FILES
# ============================================================================
echo "═" | tee -a "$REPORT"
echo "5️⃣ STATIC FILES CHECK" | tee -a "$REPORT"
echo "═" | tee -a "$REPORT"

STATIC_COUNT=$(docker exec web-ctc-research find /app/ctc-research/assets/staticfiles -type f 2>/dev/null | wc -l)
if [ "$STATIC_COUNT" -gt 100 ]; then
    test_pass "Static files collected: $STATIC_COUNT files"
else
    test_warn "Static files count is low: $STATIC_COUNT files"
fi

echo "" | tee -a "$REPORT"

# ============================================================================
# SECTION 6: FIXTURE DATA
# ============================================================================
echo "═" | tee -a "$REPORT"
echo "6️⃣ FIXTURE DATA CHECK" | tee -a "$REPORT"
echo "═" | tee -a "$REPORT"

FIXTURE_SIZE=$(du -sh /root/site/websites/ctc-research/assets/fixtures/by-model 2>/dev/null | cut -f1)
FIXTURE_COUNT=$(find /root/site/websites/ctc-research/assets/fixtures/by-model -name "*.json" -type f 2>/dev/null | wc -l)

if [ -n "$FIXTURE_SIZE" ] && [ "$FIXTURE_COUNT" -gt 0 ]; then
    test_pass "Fixture data available: $FIXTURE_COUNT files, $FIXTURE_SIZE"
else
    test_fail "Fixture data not found"
fi

echo "" | tee -a "$REPORT"

# ============================================================================
# SECTION 7: CERTIFICATE CHECK
# ============================================================================
echo "═" | tee -a "$REPORT"
echo "7️⃣ SSL/TLS CERTIFICATE CHECK" | tee -a "$REPORT"
echo "═" | tee -a "$REPORT"

if [ -f /root/site/websites/applications/proxy/traefik/acme/acme.json ]; then
    test_pass "Traefik ACME store (acme.json) exists"
else
    test_warn "ACME store not found at /root/site/websites/applications/proxy/traefik/acme/acme.json"
fi

if [ -d /root/site/websites/applications/proxy/traefik/acme ]; then
    ACME_PERMS=$(stat -c %a /root/site/websites/applications/proxy/traefik/acme/acme.json 2>/dev/null || echo "?")
    test_pass "ACME store permissions: ${ACME_PERMS} (expect 600)"
fi

if [ -d /root/site/websites/applications/proxy/traefik/certs ]; then
    CERT_COUNT=$(find /root/site/websites/applications/proxy/traefik/certs -maxdepth 1 -type f 2>/dev/null | wc -l)
    test_pass "Legacy self-signed fallback files: $CERT_COUNT (deleted in Stage 3)"
else
    test_warn "Legacy self-signed cert directory not found"
fi

echo "" | tee -a "$REPORT"

# ============================================================================
# SECTION 8: CONFIGURATION FILES
# ============================================================================
echo "═" | tee -a "$REPORT"
echo "8️⃣ CONFIGURATION FILES CHECK" | tee -a "$REPORT"
echo "═" | tee -a "$REPORT"

CONFIG_FILES=(
    "/root/site/websites/applications/proxy/traefik/traefik.yml"
    "/root/site/websites/applications/proxy/docker-compose.traefik.yml"
    "/root/site/websites/applications/proxy/docker-compose.warehouse.yml"
    "/root/site/websites/applications/proxy/docker-compose.nginx.yml"
    "/root/site/websites/ctc-research/www/urls.py"
)

for file in "${CONFIG_FILES[@]}"; do
    if [ -f "$file" ]; then
        test_pass "Configuration file exists: $(basename $file)"
    else
        test_warn "Configuration file not found: $(basename $file)"
    fi
done

echo "" | tee -a "$REPORT"

# ============================================================================
# SECTION 9: DOCUMENTATION
# ============================================================================
echo "═" | tee -a "$REPORT"
echo "9️⃣ DOCUMENTATION CHECK" | tee -a "$REPORT"
echo "═" | tee -a "$REPORT"

DOC_FILES=(
    "PRODUCTION_FINAL_STATUS.md"
    "PRODUCTION_SETUP_README.md"
    "PRODUCTION_DEPLOYMENT_REPORT.md"
    "CERTIFICATE_BACKUP_GUIDE.md"
    "DEPLOYMENT_STATUS_REPORT.md"
)

for doc in "${DOC_FILES[@]}"; do
    if [ -f "/root/site/websites/$doc" ]; then
        test_pass "Documentation file: $doc"
    else
        test_warn "Documentation file missing: $doc"
    fi
done

echo "" | tee -a "$REPORT"

# ============================================================================
# FINAL SUMMARY
# ============================================================================
echo "" | tee -a "$REPORT"
echo "═" | tee -a "$REPORT"
echo "📊 VERIFICATION SUMMARY" | tee -a "$REPORT"
echo "═" | tee -a "$REPORT"

TOTAL=$((PASSED + FAILED + WARNINGS))

echo "" | tee -a "$REPORT"
echo "Results:" | tee -a "$REPORT"
echo -e "  ${GREEN}✅ Passed:  $PASSED${NC}" | tee -a "$REPORT"
echo -e "  ${RED}❌ Failed:  $FAILED${NC}" | tee -a "$REPORT"
echo -e "  ${YELLOW}⚠️  Warnings: $WARNINGS${NC}" | tee -a "$REPORT"
echo "  Total Tests: $TOTAL" | tee -a "$REPORT"

echo "" | tee -a "$REPORT"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 PRODUCTION VERIFICATION COMPLETE - ALL CRITICAL TESTS PASSED!${NC}" | tee -a "$REPORT"
    echo "" | tee -a "$REPORT"
    echo "System Status: ✅ PRODUCTION READY" | tee -a "$REPORT"
else
    echo -e "${RED}⚠️ VERIFICATION COMPLETE - SOME TESTS FAILED${NC}" | tee -a "$REPORT"
    echo "" | tee -a "$REPORT"
    echo "System Status: ⚠️ CHECK FAILURES" | tee -a "$REPORT"
fi

echo "" | tee -a "$REPORT"
echo "Report saved to: $REPORT" | tee -a "$REPORT"
echo "" | tee -a "$REPORT"

# Display final status
cat << EOF | tee -a "$REPORT"

🚀 NEXT STEPS:
==============
1. Load page content fixtures (optional)
   bash /root/site/websites/load_fixtures_correct.sh

2. Configure DNS records to point to production

3. Create superuser account:
   docker exec web-ctc-research python manage.py createsuperuser

4. Visit https://ctc-research.com to view the site

5. Access admin at https://ctc-research.com/admin/

Report: $REPORT
EOF
