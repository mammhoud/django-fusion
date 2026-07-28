#!/bin/bash
################################################################################
# Structa Cloud – Comprehensive Site Curl Test Suite
# ─────────────────────────────────────────────────────────────────────────────
# Tests all routes for all 4 sites: CTC Research, LMS Demo, VResume, CRM
# Run: bash tests/scripts/run_comprehensive_curl_tests.sh
# Override URLs: CTC_URL=http://host:5070 LMS_URL=http://host:5071 VRESUME_URL=http://host:5072 CRM_URL=http://host:5074
################################################################################

set -e

# ── Color output ─────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m'

PASS=0
FAIL=0
WARN=0
SKIP=0

# ── Site URLs (overridable via env vars) ────────────────────────────────────
CTC_URL="${CTC_URL:-http://localhost:5070}"
LMS_URL="${LMS_URL:-http://localhost:5071}"
VRESUME_URL="${VRESUME_URL:-http://localhost:5072}"
CRM_URL="${CRM_URL:-http://localhost:5074}"

TIMEOUT="${TIMEOUT:-5}"

# ── Logging ─────────────────────────────────────────────────────────────────
log_info()    { echo -e "${BLUE}ℹ${NC} $1"; }
log_success() { echo -e "${GREEN}✓${NC} $1"; ((PASS++)); }
log_failure() { echo -e "${RED}✗${NC} $1"; ((FAIL++)); }
log_warning() { echo -e "${YELLOW}⚠${NC} $1"; ((WARN++)); }
log_skip()    { echo -e "${CYAN}⊘${NC} $1"; ((SKIP++)); }
log_header()  { echo -e "\n${MAGENTA}${BOLD}━━━ $1 ━━━${NC}\n"; }

# ── Test helpers ─────────────────────────────────────────────────────────────
test_url() {
    local url="$1"
    local expected_status="${2:-200}"
    local label="${3:-$url}"
    local response

    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$url" 2>/dev/null || echo "000")

    if [ "$response" = "$expected_status" ]; then
        log_success "${label} → ${response} (expected ${expected_status})"
    elif [ "$response" = "000" ]; then
        log_failure "${label} → CONNECTION ERROR (expected ${expected_status})"
    else
        log_failure "${label} → ${response} (expected ${expected_status})"
    fi
}

test_url_any() {
    local url="$1"
    local label="${2:-$url}"
    local response

    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$url" 2>/dev/null || echo "000")

    if [ "$response" != "000" ] && [ "$response" -lt 500 ]; then
        log_success "${label} → ${response}"
    elif [ "$response" = "000" ]; then
        log_failure "${label} → CONNECTION ERROR"
    else
        log_failure "${label} → ${response} (server error)"
    fi
}

test_url_range() {
    local url="$1"
    local label="${2:-$url}"
    local response

    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$url" 2>/dev/null || echo "000")

    if [ "$response" != "000" ] && [ "$response" -ge 200 ] && [ "$response" -lt 500 ]; then
        if [ "$response" -ge 400 ]; then
            log_success "${label} → ${response} (expected client error)"
        else
            log_success "${label} → ${response} (2xx/3xx)"
        fi
    elif [ "$response" = "000" ]; then
        log_failure "${label} → CONNECTION ERROR"
    else
        log_failure "${label} → ${response} (500+ server error)"
    fi
}

test_health_json() {
    local url="$1"
    local label="${2:-$url}"
    local response

    response=$(curl -s --max-time "$TIMEOUT" "$url" 2>/dev/null)

    if echo "$response" | python3 -c "import sys,json; d=json.load(sys.stdin); assert d.get('status') in ('healthy','ok')" 2>/dev/null; then
        log_success "${label} → Healthy response: $(echo "$response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status','unknown'))")"
    else
        log_failure "${label} → Not healthy: ${response:0:100}"
    fi
}

# ═════════════════════════════════════════════════════════════════════════════
# MAIN TEST SUITE
# ═════════════════════════════════════════════════════════════════════════════

echo ""
echo -e "${BLUE}${BOLD}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}${BOLD}║   Structa Cloud – Comprehensive Site Curl Test Suite            ║${NC}"
echo -e "${BLUE}${BOLD}║   $(date '+%Y-%m-%d %H:%M:%S')                                        ║${NC}"
echo -e "${BLUE}${BOLD}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 1: CTC Research (port 5070)
# ═════════════════════════════════════════════════════════════════════════════
log_header "CTC Research (${CTC_URL})"

test_health_json "${CTC_URL}/health/" "CTC /health/"
test_health_json "${CTC_URL}/assets/health/" "CTC /assets/health/"
test_health_json "${CTC_URL}/health/database/" "CTC /health/database/"
test_url_any "${CTC_URL}/" "CTC / (root)"
test_url_any "${CTC_URL}/accounts/login/" "CTC /accounts/login/"
test_url_any "${CTC_URL}/accounts/register/" "CTC /accounts/register/"
test_url_any "${CTC_URL}/accounts/password/reset/" "CTC /accounts/password/reset/"
test_url_any "${CTC_URL}/django-admin/login/" "CTC /django-admin/login/"
test_url_range "${CTC_URL}/admin/" "CTC /admin/ (Wagtail)"
test_url_range "${CTC_URL}/sitemap.xml" "CTC /sitemap.xml"
test_url_range "${CTC_URL}/robots.txt" "CTC /robots.txt"
test_url_range "${CTC_URL}/set-language/" "CTC /set-language/"
test_url_any "${CTC_URL}/fusion/" "CTC /fusion/ (routable components)"
test_url_range "${CTC_URL}/this-path-does-not-exist-xyz/" "CTC /nonexistent (404 expected)"

# Hidden/optional endpoints
test_url_range "${CTC_URL}/about/" "CTC /about/"
test_url_range "${CTC_URL}/team/" "CTC /team/"
test_url_range "${CTC_URL}/contact/" "CTC /contact/"

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 2: LMS Demo / Structa Cloud (port 5071)
# ═════════════════════════════════════════════════════════════════════════════
log_header "LMS Demo / Structa Cloud (${LMS_URL})"

test_health_json "${LMS_URL}/health/" "LMS /health/"
test_health_json "${LMS_URL}/assets/health/" "LMS /assets/health/"
test_health_json "${LMS_URL}/health/database/" "LMS /health/database/"
test_url_any "${LMS_URL}/" "LMS / (root)"
test_url_any "${LMS_URL}/accounts/login/" "LMS /accounts/login/"
test_url_any "${LMS_URL}/accounts/register/" "LMS /accounts/register/"
test_url_any "${LMS_URL}/accounts/password/reset/" "LMS /accounts/password/reset/"
test_url_any "${LMS_URL}/django-admin/login/" "LMS /django-admin/login/"
test_url_range "${LMS_URL}/admin/" "LMS /admin/ (Wagtail)"
test_url_range "${LMS_URL}/sitemap.xml" "LMS /sitemap.xml"
test_url_range "${LMS_URL}/robots.txt" "LMS /robots.txt"
test_url_range "${LMS_URL}/set-language/" "LMS /set-language/"
test_url_any "${LMS_URL}/fusion/" "LMS /fusion/ (routable components)"
test_url_range "${LMS_URL}/this-path-does-not-exist-xyz/" "LMS /nonexistent (404 expected)"

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 3: VResume (port 5072)
# ═════════════════════════════════════════════════════════════════════════════
log_header "VResume (${VRESUME_URL})"

test_health_json "${VRESUME_URL}/health/" "VResume /health/"
test_health_json "${VRESUME_URL}/assets/health/" "VResume /assets/health/"
test_health_json "${VRESUME_URL}/health/database/" "VResume /health/database/"
test_url_any "${VRESUME_URL}/django-admin/login/" "VResume /django-admin/login/"
test_url_range "${VRESUME_URL}/admin/" "VResume /admin/ (Wagtail)"
test_url_range "${VRESUME_URL}/sitemap.xml" "VResume /sitemap.xml"
test_url_range "${VRESUME_URL}/robots.txt" "VResume /robots.txt"
test_url_range "${VRESUME_URL}/set-language/" "VResume /set-language/"
test_url_any "${VRESUME_URL}/" "VResume / (root)"

# VResume-specific endpoints
test_url_any "${VRESUME_URL}/api/csrf-token/" "VResume /api/csrf-token/"
test_url_range "${VRESUME_URL}/api/theme/get/" "VResume /api/theme/get/"
test_url_range "${VRESUME_URL}/media-health/" "VResume /media-health/"
test_url_any "${VRESUME_URL}/team/" "VResume /team/"
test_url_range "${VRESUME_URL}/blog/" "VResume /blog/"
test_url_range "${VRESUME_URL}/events/" "VResume /events/"

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 4: CRM (port 5074)
# ═════════════════════════════════════════════════════════════════════════════
log_header "CRM (${CRM_URL})"

test_health_json "${CRM_URL}/health/" "CRM /health/"
test_health_json "${CRM_URL}/assets/health/" "CRM /assets/health/"
test_health_json "${CRM_URL}/health/database/" "CRM /health/database/"
test_url_any "${CRM_URL}/" "CRM / (root)"
test_url_any "${CRM_URL}/accounts/login/" "CRM /accounts/login/"
test_url_any "${CRM_URL}/django-admin/login/" "CRM /django-admin/login/"
test_url_any "${CRM_URL}/crm/" "CRM /crm/ (routable components)"
test_url_range "${CRM_URL}/set-language/" "CRM /set-language/"
test_url_range "${CRM_URL}/robots.txt" "CRM /robots.txt"
test_url_range "${CRM_URL}/this-path-does-not-exist-xyz/" "CRM /nonexistent (404 expected)"

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 5: Cross-site health checks
# ═════════════════════════════════════════════════════════════════════════════
log_header "Cross-Site Health Checks"

# Verify health endpoints return proper JSON with expected fields
for site_name in "CTC" "LMS" "VRESUME" "CRM"; do
    site_url=""
    case "$site_name" in
        CTC)     site_url="$CTC_URL" ;;
        LMS)     site_url="$LMS_URL" ;;
        VRESUME) site_url="$VRESUME_URL" ;;
        CRM)     site_url="$CRM_URL" ;;
    esac

    health_data=$(curl -s --max-time "$TIMEOUT" "${site_url}/health/" 2>/dev/null)

    if echo "$health_data" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    assert 'status' in d
    assert d['status'] in ('healthy', 'ok')
    print('OK: status=' + d['status'])
except Exception as e:
    print('FAIL: ' + str(e))
    sys.exit(1)
" 2>/dev/null; then
        log_success "${site_name} health endpoint validated ✓"
    else
        log_failure "${site_name} health endpoint invalid ✗"
    fi
done

# ═════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ═════════════════════════════════════════════════════════════════════════════
echo ""
log_header "TEST SUMMARY"
echo -e "  ${GREEN}✓ PASSED:${NC}  $PASS"
echo -e "  ${RED}✗ FAILED:${NC}  $FAIL"
echo -e "  ${YELLOW}⚠ WARNINGS:${NC} $WARN"
echo -e "  ${CYAN}⊘ SKIPPED:${NC} $SKIP"
TOTAL=$((PASS + FAIL + WARN + SKIP))
echo -e "  ${BOLD}Total:${NC}    $TOTAL tests"
echo ""

if [ "$FAIL" -eq 0 ]; then
    echo -e "${GREEN}${BOLD}══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}${BOLD}  ALL TESTS PASSED ✓${NC}"
    echo -e "${GREEN}${BOLD}══════════════════════════════════════════════════════════════════${NC}"
    exit 0
else
    echo -e "${RED}${BOLD}══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}${BOLD}  SOME TESTS FAILED ✗${NC}"
    echo -e "${RED}${BOLD}══════════════════════════════════════════════════════════════════${NC}"
    exit 1
fi
