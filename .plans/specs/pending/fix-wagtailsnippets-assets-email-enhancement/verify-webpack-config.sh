#!/bin/bash
# Webpack Configuration Verification Script
# Tests that webpack builds correctly and generates proper asset paths

set -e

echo "=========================================="
echo "Webpack Configuration Verification"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Check if webpack config files exist
echo "Test 1: Checking webpack configuration files..."
if [ -f "structa.cloud/webpack/main.config.js" ]; then
    echo -e "${GREEN}✓${NC} structa.cloud/webpack/main.config.js exists"
else
    echo -e "${RED}✗${NC} structa.cloud/webpack/main.config.js missing"
    exit 1
fi

if [ -f "ctc-research.com/webpack/main.config.js" ]; then
    echo -e "${GREEN}✓${NC} ctc-research.com/webpack/main.config.js exists"
else
    echo -e "${RED}✗${NC} ctc-research.com/webpack/main.config.js missing"
    exit 1
fi

echo ""

# Test 2: Check if node_modules are installed
echo "Test 2: Checking npm dependencies..."
if [ -d "structa.cloud/node_modules" ]; then
    echo -e "${GREEN}✓${NC} structa.cloud node_modules exists"
else
    echo -e "${YELLOW}⚠${NC} structa.cloud node_modules missing, installing..."
    cd structa.cloud && npm install && cd ..
fi

echo ""

# Test 3: Build webpack bundles
echo "Test 3: Building webpack bundles..."
cd structa.cloud
if npm run build:dev > /tmp/webpack-build.log 2>&1; then
    echo -e "${GREEN}✓${NC} Webpack build successful"
else
    echo -e "${RED}✗${NC} Webpack build failed"
    echo "Build log:"
    cat /tmp/webpack-build.log
    exit 1
fi
cd ..

echo ""

# Test 4: Check if bundles.json was created
echo "Test 4: Checking bundles.json..."
if [ -f "structa.cloud/assets/bundles/bundles.json" ]; then
    echo -e "${GREEN}✓${NC} bundles.json created"

    # Check if public paths are correct
    if grep -q '"publicPath": "/static/' structa.cloud/assets/bundles/bundles.json; then
        echo -e "${GREEN}✓${NC} Public paths are correct (/static/)"
    else
        echo -e "${RED}✗${NC} Public paths are incorrect"
        echo "Expected: /static/"
        echo "Found:"
        grep '"publicPath"' structa.cloud/assets/bundles/bundles.json | head -3
        exit 1
    fi
else
    echo -e "${RED}✗${NC} bundles.json not created"
    exit 1
fi

echo ""

# Test 5: Check if CSS bundles were created
echo "Test 5: Checking CSS bundles..."
if ls structa.cloud/assets/bundles/css/*.css > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} CSS bundles created"
    ls -lh structa.cloud/assets/bundles/css/*.css | head -3
else
    echo -e "${RED}✗${NC} CSS bundles not created"
    exit 1
fi

echo ""

# Test 6: Check if JS bundles were created
echo "Test 6: Checking JS bundles..."
if ls structa.cloud/assets/bundles/*.js > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} JS bundles created"
    ls -lh structa.cloud/assets/bundles/*.js | head -3
else
    echo -e "${RED}✗${NC} JS bundles not created"
    exit 1
fi

echo ""

# Test 7: Check nginx configuration
echo "Test 7: Checking nginx configuration..."
if [ -f "structa.cloud/compose/nginx/nginx.conf" ]; then
    echo -e "${GREEN}✓${NC} nginx.conf exists"

    # Check for MIME types
    if grep -q "application/javascript" structa.cloud/compose/nginx/nginx.conf; then
        echo -e "${GREEN}✓${NC} MIME types configured"
    else
        echo -e "${YELLOW}⚠${NC} MIME types not found in nginx.conf"
    fi

    # Check for try_files directive
    if grep -q "try_files" structa.cloud/compose/nginx/nginx.conf; then
        echo -e "${GREEN}✓${NC} try_files directive configured"
    else
        echo -e "${YELLOW}⚠${NC} try_files directive not found"
    fi
else
    echo -e "${RED}✗${NC} nginx.conf missing"
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}All tests passed!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Test in Docker: docker-compose up --build"
echo "2. Access https://structa.cloud and check browser console"
echo "3. Verify no 502 errors for static assets"
echo ""
