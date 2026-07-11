#!/bin/bash

################################################################################
# Structa Cloud – Complete Domain Integration Test Suite
# ─────────────────────────────────────────────────────────────────────────────
# Tests: Health endpoints, proxy routing, SSL/TLS, databases, configuration
################################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PASS=0
FAIL=0
WARN=0

log_info() {
  echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
  echo -e "${GREEN}✓${NC} $1"
  ((PASS++))
}

log_failure() {
  echo -e "${RED}✗${NC} $1"
  ((FAIL++))
}

log_warning() {
  echo -e "${YELLOW}⚠${NC} $1"
  ((WARN++))
}

section() {
  echo ""
  echo "════════════════════════════════════════════════════════════════"
  echo "$1"
  echo "════════════════════════════════════════════════════════════════"
}

################################################################################
# TEST 1: Container Health
################################################################################

test_container_health() {
  section "TEST 1: Container Health Status"

  local containers=("crm-website" "ctc-research-website" "lms-web" "vresume-web" "default-proxy" "postgres" "default-redis")

  for container in "${containers[@]}"; do
    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
      local status=$(docker inspect "$container" --format='{{.State.Status}}' 2>/dev/null)
      if [ "$status" = "running" ]; then
        log_success "Container running: $container"
      else
        log_failure "Container not running: $container (status: $status)"
      fi
    else
      log_failure "Container not found: $container"
    fi
  done
}

################################################################################
# TEST 2: Direct Health Endpoints
################################################################################

test_direct_endpoints() {
  section "TEST 2: Direct Health Endpoints (Port-based)"

  local endpoints=(
    "http://localhost:5074/health/:CRM"
    "http://localhost:5070/health/:CTC Research"
    "http://localhost:5071/health/:LMS Demo"
    "http://localhost:5072/health/:VResume"
  )

  for endpoint_info in "${endpoints[@]}"; do
    IFS=':' read -r endpoint name <<< "$endpoint_info"
    
    if response=$(curl -s --max-time 5 "$endpoint" 2>/dev/null); then
      if echo "$response" | grep -q "ok\|running"; then
        log_success "Endpoint accessible: $name"
      else
        log_warning "Endpoint response unclear: $name ($response)"
      fi
    else
      log_failure "Endpoint unreachable: $name ($endpoint)"
    fi
  done
}

################################################################################
# TEST 3: Proxy Routing Tests
################################################################################

test_proxy_routing() {
  section "TEST 3: Proxy Routing (HTTP → HTTPS Redirect)"

  local routes=(
    "crm.structa.cloud:CRM"
    "structa.cloud:Structa/LMS Demo"
    "ctc-research.com:CTC Research"
    "vresume.structa.cloud:VResume"
  )

  for route_info in "${routes[@]}"; do
    IFS=':' read -r host name <<< "$route_info"
    
    response=$(curl -s -I -H "Host: $host" http://localhost/ 2>&1 | head -1)
    if echo "$response" | grep -q "308\|301\|302"; then
      location=$(curl -s -I -H "Host: $host" http://localhost/ 2>&1 | grep -i "^Location:" | head -1)
      if echo "$location" | grep -q "https"; then
        log_success "HTTP redirect working: $name → HTTPS"
      else
        log_failure "Redirect not HTTPS: $name"
      fi
    else
      log_failure "No redirect found: $name"
    fi
  done
}

################################################################################
# TEST 4: Database Health
################################################################################

test_database_health() {
  section "TEST 4: Database Health & Integration"

  if ! docker exec postgres pg_isready -U admin -d postgres >/dev/null 2>&1; then
    log_failure "PostgreSQL not responding"
    return
  fi
  log_success "PostgreSQL is responding"

  local databases=("app_db" "db_ctc" "db_structa" "vresume" "db_crm" "blinko" "coder")

  for db in "${databases[@]}"; do
    count=$(docker exec postgres psql -U admin -d "$db" -c "SELECT 1;" 2>&1 | grep -c "1" || echo 0)
    if [ "$count" -gt 0 ]; then
      log_success "Database accessible: $db"
    else
      log_failure "Database not accessible: $db"
    fi
  done

  # Check CRM tables specifically
  table_count=$(docker exec postgres psql -U admin -d db_crm -c "SELECT count(*) as cnt FROM information_schema.tables WHERE table_schema = 'public';" 2>&1 | grep -E "[0-9]+" -o | head -1)
  if [ -n "$table_count" ] && [ "$table_count" -gt 50 ]; then
    log_success "CRM database initialized: $table_count tables"
  else
    log_failure "CRM database not initialized (tables: $table_count)"
  fi
}

################################################################################
# TEST 5: Configuration Files
################################################################################

test_configuration() {
  section "TEST 5: Configuration Files"

  # Check Traefik CRM config exists
  if [ -f "/home/structa.cloud/proxy/traefik/dynamic/crm.yml" ]; then
    log_success "Traefik CRM router config exists"
    if grep -q "crm-website:5074" /home/structa.cloud/proxy/traefik/dynamic/crm.yml; then
      log_success "CRM service endpoint configured correctly"
    else
      log_failure "CRM service endpoint not configured"
    fi
  else
    log_failure "Traefik CRM router config missing"
  fi

  # Check CLI site registry
  if grep -q '"crm".*"crm-website"' /home/structa.cloud/core/cli.py 2>/dev/null; then
    log_success "CRM site registered in CLI"
  else
    log_failure "CRM site not registered in CLI"
  fi

  # Check environment variables
  if grep -q "structa.cloud@gmail.com" /home/structa.cloud/.env 2>/dev/null; then
    log_success "Email updated in root .env"
  else
    log_failure "Email not updated in root .env"
  fi

  if grep -q "structa.cloud@gmail.com" /home/structa.cloud/proxy/.env 2>/dev/null; then
    log_success "Email updated in proxy .env"
  else
    log_failure "Email not updated in proxy .env"
  fi
}

################################################################################
# TEST 6: Site CLI Registration
################################################################################

test_site_registration() {
  section "TEST 6: Site CLI Registration"

  cd /home/structa.cloud/applications

  # Test each site
  local sites=("crm" "ctc-research" "lms-demo" "vresume")

  for site in "${sites[@]}"; do
    if python cli.py sites 2>&1 | grep -q "$site"; then
      log_success "Site registered in CLI: $site"
    else
      log_failure "Site not in CLI registry: $site"
    fi
  done
}

################################################################################
# TEST 7: Traefik Configuration
################################################################################

test_traefik_config() {
  section "TEST 7: Traefik Configuration Status"

  # Check proxy health
  if curl -s http://localhost:8080/ping 2>&1 | grep -q "OK"; then
    log_success "Traefik health check responding"
  else
    log_failure "Traefik health check not responding"
  fi

  # Check router count
  router_count=$(curl -s http://localhost:8080/api/http/routers 2>&1 | grep -o '"name"' | wc -l)
  if [ "$router_count" -gt 0 ]; then
    log_success "Traefik routers loaded: $router_count routers"
  else
    log_failure "No Traefik routers found"
  fi

  # Check for CRM router
  if curl -s http://localhost:8080/api/http/routers 2>&1 | grep -q "crm"; then
    log_success "CRM routers detected in Traefik"
  else
    log_warning "CRM routers not detected in Traefik (may not have been loaded yet)"
  fi
}

################################################################################
# TEST 8: ACME / Let's Encrypt
################################################################################

test_acme_setup() {
  section "TEST 8: ACME / Let's Encrypt Setup"

  if [ -f "/home/structa.cloud/proxy/acme/acme.json" ]; then
    log_success "ACME storage file exists"
    perms=$(stat -c %a /home/structa.cloud/proxy/acme/acme.json)
    if [ "$perms" = "600" ]; then
      log_success "ACME file permissions correct (600)"
    else
      log_failure "ACME file permissions incorrect (${perms}, expected 600)"
    fi
  else
    log_failure "ACME storage file missing"
  fi

  # Check dynamic config
  if [ -f "/home/structa.cloud/proxy/traefik/dynamic.yml" ]; then
    if grep -q "certificatesResolvers:" /home/structa.cloud/proxy/traefik/dynamic.yml; then
      log_success "ACME configuration found in Traefik"
    else
      log_failure "ACME configuration not found"
    fi
  fi

  # Check CRM TLS config
  if grep -q "certResolver: letsencrypt" /home/structa.cloud/proxy/traefik/dynamic/crm.yml; then
    log_success "CRM configured for Let's Encrypt"
  else
    log_failure "CRM not configured for Let's Encrypt"
  fi
}

################################################################################
# TEST 9: Media Server Integration
################################################################################

test_media_server() {
  section "TEST 9: Media Server Integration"

  if curl -s -H "Host: crm.structa.cloud" -I http://localhost/media/ 2>&1 | grep -q "404\|301\|302"; then
    log_success "Media endpoint routing configured"
  else
    log_failure "Media endpoint not responding as expected"
  fi

  if docker ps --format '{{.Names}}' | grep -q "^shared-media$"; then
    log_success "Shared media container running"
  else
    log_failure "Shared media container not running"
  fi
}

################################################################################
# TEST 10: Network Connectivity
################################################################################

test_network_connectivity() {
  section "TEST 10: Network Connectivity"

  # Check if containers can reach each other
  if docker exec crm-website ping -c 1 postgres 2>&1 | grep -q "1 received"; then
    log_success "CRM container can reach database"
  else
    log_failure "CRM container cannot reach database"
  fi

  if docker exec crm-website ping -c 1 default-redis 2>&1 | grep -q "1 received"; then
    log_success "CRM container can reach Redis"
  else
    log_failure "CRM container cannot reach Redis"
  fi

  if docker exec default-proxy curl -s http://crm-website:5074/health/ 2>&1 | grep -q "ok"; then
    log_success "Proxy can reach CRM backend"
  else
    log_failure "Proxy cannot reach CRM backend"
  fi
}

################################################################################
# TEST 11: Site-Specific Django Checks
################################################################################

test_django_checks() {
  section "TEST 11: Django System Checks"

  cd /home/structa.cloud/applications

  local sites=("crm" "ctc-research" "lms-demo" "vresume")

  for site in "${sites[@]}"; do
    if python manage.py --site "$site" check 2>&1 | grep -q "System check identified no issues"; then
      log_success "Django system check passed: $site"
    else
      log_warning "Django system check may have issues: $site"
    fi
  done
}

################################################################################
# SUMMARY
################################################################################

print_summary() {
  echo ""
  section "TEST SUMMARY"
  
  total=$((PASS + FAIL + WARN))
  
  echo ""
  echo "Results:"
  echo "  ${GREEN}✓ PASSED:${NC} $PASS"
  echo "  ${RED}✗ FAILED:${NC} $FAIL"
  echo "  ${YELLOW}⚠ WARNINGS:${NC} $WARN"
  echo "  ${BLUE}━━━━━${NC}"
  echo "  Total: $total tests"
  echo ""

  if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ ALL TESTS PASSED - SYSTEM READY FOR PRODUCTION${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    return 0
  else
    echo -e "${RED}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}✗ SOME TESTS FAILED - REVIEW ABOVE FOR DETAILS${NC}"
    echo -e "${RED}════════════════════════════════════════════════════════════════${NC}"
    return 1
  fi
}

################################################################################
# MAIN
################################################################################

main() {
  echo ""
  echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
  echo -e "${BLUE}║  Structa Cloud – Domain Integration Test Suite                  ║${NC}"
  echo -e "${BLUE}║  Email: structa.cloud@gmail.com                                 ║${NC}"
  echo -e "${BLUE}║  Date: $(date '+%Y-%m-%d %H:%M:%S')                                    ║${NC}"
  echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
  echo ""

  test_container_health
  test_direct_endpoints
  test_proxy_routing
  test_database_health
  test_configuration
  test_site_registration
  test_traefik_config
  test_acme_setup
  test_media_server
  test_network_connectivity
  test_django_checks

  print_summary
}

# Run all tests
main "$@"
exit $?

