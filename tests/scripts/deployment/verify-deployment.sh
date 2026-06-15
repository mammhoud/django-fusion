#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

WORKSPACE="/root/site/websites"
PASSED=0
FAILED=0

log_pass() { echo -e "${GREEN}✓${NC} $1"; PASSED=$((PASSED+1)); }
log_fail() { echo -e "${RED}✗${NC} $1"; FAILED=$((FAILED+1)); }
log_header() { echo -e "\n${BLUE}=== $1 ===${NC}\n"; }

# ==============================================================================
# Check 1: Bundle Files
# ==============================================================================
log_header "Checking Bundle Files"

[ -f "$WORKSPACE/ctc-research/assets/bundles/ctc-research/bundles.json" ] && log_pass "Bundle: ctc-research" || log_fail "Bundle: ctc-research"
[ -f "$WORKSPACE/lms-demo/assets/bundles/lms-demo/bundles.json" ] && log_pass "Bundle: lms-demo" || log_fail "Bundle: lms-demo"
[ -f "$WORKSPACE/VResume/assets/bundles/vresume/bundles.json" ] && log_pass "Bundle: VResume" || log_fail "Bundle: VResume"

# ==============================================================================
# Check 2: Docker Configuration
# ==============================================================================
log_header "Checking Docker Configuration"

docker compose -f "$WORKSPACE/docker-compose.yml" config > /dev/null 2>&1 && log_pass "Docker Compose config valid" || log_fail "Docker Compose config invalid"

# ==============================================================================
# Check 3: Traefik Configuration
# ==============================================================================
log_header "Checking Traefik Configuration"

[ -f "$WORKSPACE/compose/traefik/traefik.yml" ] && log_pass "traefik.yml exists" || log_fail "traefik.yml missing"
[ -f "$WORKSPACE/compose/traefik/dynamic/media-servers.yml" ] && log_pass "media-servers.yml exists" || log_fail "media-servers.yml missing"

# ==============================================================================
# Check 4: Media Server Configuration
# ==============================================================================
log_header "Checking Media Server Configuration"

grep -q "location /health/" "$WORKSPACE/compose/nginx/nginx.conf" && log_pass "Nginx health endpoint configured" || log_fail "Nginx health endpoint missing"
grep -q "media.structa.cloud" "$WORKSPACE/compose/traefik/dynamic/media-servers.yml" && log_pass "Media domains configured" || log_fail "Media domains not configured"

# ==============================================================================
# Check 5: Entry Points
# ==============================================================================
log_header "Checking JavaScript Entry Points"

[ -f "$WORKSPACE/ctc-research/assets/static/js/app.js" ] && log_pass "CTC entry point exists" || log_fail "CTC entry point missing"
[ -f "$WORKSPACE/lms-demo/assets/static/js/app.js" ] && log_pass "LMS entry point exists" || log_fail "LMS entry point missing"
[ -f "$WORKSPACE/VResume/assets/static/js/static.js" ] && log_pass "VResume entry point exists" || log_fail "VResume entry point missing"

# ==============================================================================
# Check 6: Usecase Configs
# ==============================================================================
log_header "Checking Usecase Configurations"

[ -f "$WORKSPACE/ctc-research/assets/static/js/usecase-config.js" ] && log_pass "CTC config exists" || log_fail "CTC config missing"
[ -f "$WORKSPACE/lms-demo/assets/static/js/usecase-config.js" ] && log_pass "LMS config exists" || log_fail "LMS config missing"
[ -f "$WORKSPACE/VResume/assets/static/js/usecases/config.js" ] && log_pass "VResume config exists" || log_fail "VResume config missing"

# ==============================================================================
# Check 7: Assets Structure
# ==============================================================================
log_header "Checking Assets Directory Structure"

[ -d "$WORKSPACE/assets/static/js/core" ] && log_pass "core directory exists" || log_fail "core directory missing"
[ -d "$WORKSPACE/assets/static/js/utility" ] && log_pass "utility directory exists" || log_fail "utility directory missing"
[ -d "$WORKSPACE/assets/static/js/theme" ] && log_pass "theme directory exists" || log_fail "theme directory missing"
[ -d "$WORKSPACE/assets/static/js/modules" ] && log_pass "modules directory exists" || log_fail "modules directory missing"
[ -d "$WORKSPACE/assets/static/js/plugins" ] && log_pass "plugins directory exists" || log_fail "plugins directory missing"

# ==============================================================================
# Check 8: Certificates
# ==============================================================================
log_header "Checking Certificate System"

[ -f "$WORKSPACE/compose/traefik/cert-backup.sh" ] && log_pass "Cert backup script exists" || log_fail "Cert backup script missing"
[ -d "$WORKSPACE/compose/traefik/acme" ] && log_pass "ACME directory exists" || log_fail "ACME directory missing"

# ==============================================================================
# Summary
# ==============================================================================
log_header "Deployment Verification Summary"

total=$((PASSED + FAILED))
percentage=$((PASSED * 100 / total))

echo "✅ Passed:  $PASSED/$total"
echo "❌ Failed:  $FAILED/$total"
echo "📊 Score:   $percentage%"

[ $FAILED -eq 0 ] && echo -e "\n${GREEN}✅ All checks passed! Ready for deployment.${NC}" && exit 0
echo -e "\n${RED}❌ Some checks failed.${NC}" && exit 1
