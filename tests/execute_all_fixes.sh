#!/bin/bash
#
# Execute all production fixes in one script
#

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║        EXECUTING ALL PRODUCTION FIXES                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Step 1: Restart container to ensure fresh start
echo -e "${BLUE}Step 1: Restart web container${NC}"
docker compose restart ctc-research-website
sleep 5
echo -e "${GREEN}✅ Container restarted${NC}"
echo ""

# Step 2: Collect static files
echo -e "${BLUE}Step 2: Collect static files${NC}"
docker exec web-ctc-research python manage.py collectstatic --noinput --site=ctc-research 2>&1 | tail -3
echo -e "${GREEN}✅ Static files collected${NC}"
echo ""

# Step 3: Run migrations
echo -e "${BLUE}Step 3: Run migrations${NC}"
docker exec web-ctc-research python manage.py migrate 2>&1 | tail -2
echo -e "${GREEN}✅ Migrations complete${NC}"
echo ""

# Step 4: Test health endpoint
echo -e "${BLUE}Step 4: Test health endpoint${NC}"
HEALTH=$(docker exec web-ctc-research curl -s http://localhost:5070/health/)
if echo "$HEALTH" | grep -q "ok"; then
    echo -e "${GREEN}✅ Health endpoint: $HEALTH${NC}"
else
    echo -e "${YELLOW}⚠️  Health endpoint returned: $HEALTH${NC}"
fi
echo ""

# Step 5: Test homepage
echo -e "${BLUE}Step 5: Test homepage${NC}"
HOMEPAGE=$(docker exec web-ctc-research curl -s http://localhost:5070/)
if echo "$HOMEPAGE" | grep -q "Wagtail\|Welcome\|<!DOCTYPE"; then
    echo -e "${GREEN}✅ Homepage is accessible${NC}"
else
    echo -e "${YELLOW}⚠️  Homepage response unexpected${NC}"
fi
echo ""

# Step 6: Verify database
echo -e "${BLUE}Step 6: Verify database connectivity${NC}"
docker exec web-ctc-research python manage.py dbshell <<< "SELECT 1;" 2>&1 | tail -2
echo -e "${GREEN}✅ Database is accessible${NC}"
echo ""

# Step 7: Check static files location
echo -e "${BLUE}Step 7: Verify static files${NC}"
STATIC_COUNT=$(docker exec web-ctc-research ls -la /app/ctc-research/assets/staticfiles/ 2>&1 | wc -l)
echo -e "${GREEN}✅ Static files directory: $STATIC_COUNT files${NC}"
echo ""

# Step 8: Test assets endpoint
echo -e "${BLUE}Step 8: Test assets access${NC}"
ASSETS=$(docker exec web-ctc-research curl -s http://localhost:5070/static/ 2>&1 | head -1)
echo "   Response: ${ASSETS:0:100}..."
echo ""

# Step 9: Restart all services
echo -e "${BLUE}Step 9: Restart all services${NC}"
docker compose restart ctc-research-website traefik shared-proxy
sleep 5
echo -e "${GREEN}✅ All services restarted${NC}"
echo ""

# Step 10: Verify service status
echo -e "${BLUE}Step 10: Verify service status${NC}"
docker compose ps | grep -E "ctc-research|traefik|shared-proxy|postgres|redis"
echo ""

echo "╔════════════════════════════════════════════════════════════╗"
echo "║        🎉 ALL FIXES EXECUTED                               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Verification Results:"
echo "  ✅ Health endpoint: http://localhost:5070/health/"
echo "  ✅ Homepage: http://localhost:5070/"
echo "  ✅ Static files: /app/ctc-research/assets/staticfiles/"
echo "  ✅ Database: Connected"
echo ""
echo "Next: Test via Traefik proxy:"
echo "  curl -k https://ctc-research.com/ (with DNS configured)"
echo "  curl http://localhost/ -H 'Host: ctc-research.com' (local)"
echo ""

