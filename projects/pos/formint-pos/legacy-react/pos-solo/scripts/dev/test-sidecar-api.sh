#!/usr/bin/env bash
# ==============================================================================
# POS Solo — Sidecar API Test Script
# ==============================================================================
# Tests the Python/Robyn sidecar API endpoints with curl and validates
# that the seeded database returns the expected data.
#
# Usage:
#   bash scripts/dev/test-sidecar-api.sh              # use running sidecar (or auto-start)
#   bash scripts/dev/test-sidecar-api.sh --no-start   # fail if sidecar not already running
#   PORT=8765 bash scripts/dev/test-sidecar-api.sh    # custom port
#
# Exit codes:
#   0 — all tests passed
#   1 — one or more tests failed
#   2 — sidecar could not be reached
# ==============================================================================

set -euo pipefail

# ── Configuration ───────────────────────────────────────────────────────────

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8766}"
BASE="http://${HOST}:${PORT}"
NO_START="${NO_START:-false}"
SIDECAR_DIR="$(cd "$(dirname "$0")/../../sidecar" && pwd)"
STARTED_BY_US=false
SIDECAR_PID=""

# Accept --no-start flag
for arg in "$@"; do
    case "$arg" in
        --no-start) NO_START=true ;;
        --host=*) HOST="${arg#*=}" ;;
        --port=*) PORT="${arg#*=}" ;;
    esac
done

# ── Colors ──────────────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

PASS="${GREEN}PASS${NC}"
FAIL="${RED}FAIL${NC}"
SKIP="${YELLOW}SKIP${NC}"

passed=0
failed=0
skipped=0

# ── Helpers ─────────────────────────────────────────────────────────────────

_header() {
    echo -e "\n${BOLD}${CYAN}━━━ $1 ━━━${NC}"
}

_pass() {
    echo -e "  ${PASS}  $1"
    ((passed++)) || true
}

_fail() {
    echo -e "  ${FAIL}  $1"
    ((failed++)) || true
}

_skip() {
    echo -e "  ${SKIP}  $1"
    ((skipped++)) || true
}

curl_json() {
    # Fetch JSON from an endpoint, with retries
    local url="$1"
    local max_retries=3
    local output
    for i in {1..$max_retries}; do
        output=$(curl -sf --max-time 5 "$url" 2>/dev/null) && echo "$output" && return 0
        sleep 1
    done
    return 1
}

# ── Start Sidecar (if needed) ───────────────────────────────────────────────

start_sidecar() {
    if curl -sf --max-time 2 "${BASE}/health" > /dev/null 2>&1; then
        echo -e "  Sidecar already running at ${BASE}"
        return 0
    fi

    if [ "$NO_START" = true ]; then
        echo -e "  ${RED}Sidecar not running and --no-start specified — aborting${NC}"
        exit 2
    fi

    echo -e "  Starting sidecar on ${BASE}..."
    python3 "${SIDECAR_DIR}/server.py" --port "$PORT" --host "$HOST" > /tmp/pos-solo-api-test.log 2>&1 &
    SIDECAR_PID=$!
    STARTED_BY_US=true

    # Wait for sidecar to be ready (up to 15s)
    echo -n "  Waiting for sidecar "
    for i in {1..30}; do
        if curl -sf --max-time 2 "${BASE}/health" > /dev/null 2>&1; then
            echo " ready!"
            return 0
        fi
        echo -n "."
        sleep 0.5
    done
    echo ""
    echo -e "  ${RED}Sidecar failed to start within 15s${NC}"
    cat /tmp/pos-solo-api-test.log | tail -20
    exit 2
}

stop_sidecar() {
    if [ "$STARTED_BY_US" = true ] && [ -n "$SIDECAR_PID" ]; then
        echo -e "\n  Stopping sidecar (pid $SIDECAR_PID)..."
        kill "$SIDECAR_PID" 2>/dev/null || true
        wait "$SIDECAR_PID" 2>/dev/null || true
    fi
}

# ── Test Functions ──────────────────────────────────────────────────────────

test_health() {
    _header "Health Check"

    local resp
    resp=$(curl_json "${BASE}/health") || { _fail "Endpoint unreachable"; return; }

    # Validate JSON structure
    local status service version db
    status=$(echo "$resp" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null)
    service=$(echo "$resp" | python3 -c "import sys,json; print(json.load(sys.stdin).get('service',''))" 2>/dev/null)
    version=$(echo "$resp" | python3 -c "import sys,json; print(json.load(sys.stdin).get('version',''))" 2>/dev/null)
    db=$(echo "$resp" | python3 -c "import sys,json; print(json.load(sys.stdin).get('database',''))" 2>/dev/null)

    if [ "$status" = "healthy" ]; then
        _pass "status=healthy"
    else
        _fail "status=${status:-missing}"
    fi

    if [ -n "$service" ]; then
        _pass "service=${service}"
    else
        _fail "service field missing"
    fi

    if [ -n "$version" ]; then
        _pass "version=${version}"
    else
        _fail "version field missing"
    fi

    if [ -n "$db" ] && [ "$db" != "null" ]; then
        _pass "database=${db}"
    else
        _skip "database field empty/null (expected in some configs)"
    fi
}

test_products() {
    _header "Products"

    local resp
    resp=$(curl_json "${BASE}/products?page=1&per_page=50") || { _fail "Endpoint unreachable"; return; }

    # Extract data array
    local items count
    items=$(echo "$resp" | python3 -c "
import sys, json
d = json.load(sys.stdin)
data = d.get('data', d) if isinstance(d, dict) else d
print(json.dumps(data))
" 2>/dev/null)

    count=$(echo "$items" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null)

    if [ "$count" -ge 5 ]; then
        _pass "Found ${count} products (>=5)"
    elif [ "$count" -ge 1 ]; then
        _fail "Only ${count} products (expected >=5 from seed data)"
    else
        _fail "No products found"
    fi

    # Validate seeded product names exist
    local names
    names=$(echo "$items" | python3 -c "
import sys, json
for p in json.load(sys.stdin):
    print(p.get('name', ''))
" 2>/dev/null)

    # Check for known seeded products
    local expected_products=("Cappuccino" "Cheesecake" "Chicken Sandwich" "Chocolate Muffin" "Club Sandwich")
    for expected in "${expected_products[@]}"; do
        if echo "$names" | grep -qF "$expected"; then
            _pass "Product '${expected}' found"
        else
            _fail "Product '${expected}' NOT found"
        fi
    done

    # Validate product schema
    local first_product_keys
    first_product_keys=$(echo "$items" | python3 -c "
import sys, json
items = json.load(sys.stdin)
if items:
    print(','.join(sorted(items[0].keys())))
" 2>/dev/null)

    local required_fields=("id" "name" "price" "sku" "category_id")
    for field in "${required_fields[@]}"; do
        if echo "$first_product_keys" | grep -q "$field"; then
            _pass "Field '${field}' present in product schema"
        else
            _fail "Field '${field}' missing in product schema"
        fi
    done
}

test_categories() {
    _header "Categories"

    local resp
    resp=$(curl_json "${BASE}/categories") || { _fail "Endpoint unreachable"; return; }

    local items count
    items=$(echo "$resp" | python3 -c "
import sys, json
d = json.load(sys.stdin)
data = d if isinstance(d, list) else d.get('data', d)
print(json.dumps(data))
" 2>/dev/null)

    count=$(echo "$items" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null)

    if [ "$count" -ge 4 ]; then
        _pass "Found ${count} categories (>=4)"
    elif [ "$count" -ge 1 ]; then
        _fail "Only ${count} categories (expected >=4 from seed data)"
    else
        _fail "No categories found"
    fi

    local names
    names=$(echo "$items" | python3 -c "
import sys, json
for c in json.load(sys.stdin):
    print(c.get('name', ''))
" 2>/dev/null)

    local expected_categories=("Hot Drinks" "Cold Drinks" "Pastries" "Sandwiches" "Desserts")
    for expected in "${expected_categories[@]}"; do
        if echo "$names" | grep -qF "$expected"; then
            _pass "Category '${expected}' found"
        else
            _fail "Category '${expected}' NOT found"
        fi
    done
}

test_sales() {
    _header "Sales"

    local resp
    resp=$(curl_json "${BASE}/sales?page=1&per_page=10") || { _fail "Endpoint unreachable"; return; }

    local items count
    items=$(echo "$resp" | python3 -c "
import sys, json
d = json.load(sys.stdin)
data = d.get('data', d) if isinstance(d, dict) else d
print(json.dumps(data))
" 2>/dev/null)

    count=$(echo "$items" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null)

    if [ "$count" -ge 1 ]; then
        _pass "Found ${count} sales"
    else
        _fail "No sales found (expected seed data)"
    fi

    # Validate sale has expected fields
    local first_sale_keys
    first_sale_keys=$(echo "$items" | python3 -c "
import sys, json
items = json.load(sys.stdin)
if items:
    print(','.join(sorted(items[0].keys())))
" 2>/dev/null)

    local sale_fields=("id" "total" "status")
    for field in "${sale_fields[@]}"; do
        if echo "$first_sale_keys" | grep -q "$field"; then
            _pass "Field '${field}' present in sale schema"
        else
            _fail "Field '${field}' missing in sale schema"
        fi
    done

    # Check for completed sales
    local completed
    completed=$(echo "$items" | python3 -c "
import sys, json
items = json.load(sys.stdin)
completed = [s for s in items if s.get('status') == 'completed']
print(len(completed))
" 2>/dev/null)

    if [ "$completed" -ge 1 ]; then
        _pass "${completed} completed sale(s) found"
    else
        _fail "No completed sales found"
    fi
}

# ── Main ────────────────────────────────────────────────────────────────────

main() {
    echo -e "${BOLD}${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}${CYAN}║  POS Solo — Sidecar API Test                           ║${NC}"
    echo -e "${BOLD}${CYAN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo -e "  Target: ${BASE}"
    echo ""

    # Ensure sidecar is running
    start_sidecar

    # Trap cleanup on exit (after start so we know SIDECAR_PID is set)
    trap stop_sidecar EXIT

    # Run tests
    test_health
    test_products
    test_categories
    test_sales

    # ── Summary ─────────────────────────────────────────────────────────────
    local total=$((passed + failed + skipped))
    echo ""
    echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "  ${BOLD}Results:${NC} ${GREEN}${passed} passed${NC}, ${RED}${failed} failed${NC}, ${YELLOW}${skipped} skipped${NC} (${total} total)"
    echo ""

    if [ "$failed" -gt 0 ]; then
        echo -e "  ${RED}${BOLD}✗ Some tests FAILED${NC}"
        exit 1
    else
        echo -e "  ${GREEN}${BOLD}✓ All tests passed${NC}"
    fi
}

main "$@"
