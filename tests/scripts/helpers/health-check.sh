#!/bin/bash
# ============================================================
# Health Check Script
# Tests all health endpoints for the deployed services
# ============================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
CTC_URL="${CTC_URL:-http://localhost:5070}"
STRUCTA_URL="${STRUCTA_URL:-http://localhost:5071}"

echo "============================================================"
echo "Health Check - All Services"
echo "============================================================"
echo ""

# Function to check endpoint
check_endpoint() {
    local url=$1
    local name=$2
    local endpoint=$3

    echo -n "Checking ${name} ${endpoint}... "

    response=$(curl -s -w "\n%{http_code}" "${url}${endpoint}" || echo "000")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ OK${NC} (HTTP $http_code)"
        echo "$body" | jq '.' 2>/dev/null || echo "$body"
        return 0
    elif [ "$http_code" = "503" ]; then
        echo -e "${YELLOW}⚠ DEGRADED${NC} (HTTP $http_code)"
        echo "$body" | jq '.' 2>/dev/null || echo "$body"
        return 1
    else
        echo -e "${RED}✗ FAILED${NC} (HTTP $http_code)"
        echo "$body"
        return 1
    fi
    echo ""
}

# Track failures
failures=0

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "CTC-Research.com Health Checks"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

check_endpoint "$CTC_URL" "CTC" "/health/" || ((failures++))
echo ""
check_endpoint "$CTC_URL" "CTC" "/health/database/" || ((failures++))
echo ""
check_endpoint "$CTC_URL" "CTC" "/health/assets/" || ((failures++))
echo ""
check_endpoint "$CTC_URL" "CTC" "/health/media/" || ((failures++))
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Structa.Cloud Health Checks"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

check_endpoint "$STRUCTA_URL" "Structa" "/health/" || ((failures++))
echo ""
check_endpoint "$STRUCTA_URL" "Structa" "/health/database/" || ((failures++))
echo ""
check_endpoint "$STRUCTA_URL" "Structa" "/health/assets/" || ((failures++))
echo ""
check_endpoint "$STRUCTA_URL" "Structa" "/health/media/" || ((failures++))
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ $failures -eq 0 ]; then
    echo -e "${GREEN}✓ All health checks passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ $failures health check(s) failed${NC}"
    exit 1
fi
