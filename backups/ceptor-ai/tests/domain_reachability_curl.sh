#!/bin/bash
# Domain Reachability Tests using curl
# Tests VResume and CTC Research domains

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VRESUME_URL="https://vresume.structa.cloud"
CTC_URL="https://ctc-research.com"
STRUCTA_URL="https://structa.cloud"
LMS_URL="https://lms-demo.com"
MEDIA_STRUCTA_URL="https://media.structa.cloud"
MEDIA_CTC_URL="https://media.ctc-research.com"
MEDIA_LMS_URL="https://media.lms-demo.com"
MEDIA_VRESUME_URL="https://media.vresume.structa.cloud"
TIMEOUT=30
OUTPUT_DIR="/tmp/domain_tests"

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "=================================================================="
echo "DOMAIN REACHABILITY TESTS - CURL"
echo "=================================================================="
echo ""

# Function to test domain
test_domain() {
    local domain_name=$1
    local url=$2
    local output_file="$OUTPUT_DIR/${domain_name}_full.html"
    local headers_file="$OUTPUT_DIR/${domain_name}_headers.txt"
    
    echo -e "${BLUE}Testing: $domain_name${NC}"
    echo "URL: $url"
    echo ""
    
    # Test 1: Check connectivity
    echo -e "${YELLOW}[1] Checking connectivity...${NC}"
    if curl -s -m $TIMEOUT -o /dev/null -w "HTTP Status: %{http_code}\n" "$url"; then
        echo -e "${GREEN}✓ Domain is reachable${NC}"
    else
        echo -e "${RED}✗ Domain is not reachable${NC}"
        return 1
    fi
    echo ""
    
    # Test 2: Get full response with headers
    echo -e "${YELLOW}[2] Fetching full response...${NC}"
    curl -s -m $TIMEOUT -i "$url" > "$output_file" 2>&1
    
    if [ -f "$output_file" ]; then
        echo -e "${GREEN}✓ Response saved to: $output_file${NC}"
        
        # Extract headers
        head -n 20 "$output_file" > "$headers_file"
        echo -e "${GREEN}✓ Headers saved to: $headers_file${NC}"
    else
        echo -e "${RED}✗ Failed to fetch response${NC}"
        return 1
    fi
    echo ""
    
    # Test 3: Check HTTP status
    echo -e "${YELLOW}[3] Checking HTTP status code...${NC}"
    http_code=$(curl -s -m $TIMEOUT -o /dev/null -w "%{http_code}" "$url")
    echo "HTTP Status Code: $http_code"
    
    if [ "$http_code" -lt 400 ]; then
        echo -e "${GREEN}✓ Valid status code (< 400)${NC}"
    elif [ "$http_code" -lt 500 ]; then
        echo -e "${YELLOW}⚠ Client error ($http_code)${NC}"
    else
        echo -e "${RED}✗ Server error ($http_code)${NC}"
    fi
    echo ""
    
    # Test 4: Check response time
    echo -e "${YELLOW}[4] Checking response time...${NC}"
    response_time=$(curl -s -m $TIMEOUT -o /dev/null -w "%{time_total}" "$url")
    echo "Response Time: ${response_time}s"
    
    if (( $(echo "$response_time < 5" | bc -l) )); then
        echo -e "${GREEN}✓ Good response time (< 5s)${NC}"
    elif (( $(echo "$response_time < 10" | bc -l) )); then
        echo -e "${YELLOW}⚠ Acceptable response time (< 10s)${NC}"
    else
        echo -e "${RED}✗ Slow response time (>= 10s)${NC}"
    fi
    echo ""
    
    # Test 5: Check for style tags
    echo -e "${YELLOW}[5] Checking for style tags...${NC}"
    style_count=$(grep -c "<style" "$output_file" || true)
    link_count=$(grep -c 'rel="stylesheet"' "$output_file" || true)
    inline_styles=$(grep -o 'style=' "$output_file" | wc -l || true)
    
    echo "Style tags: $style_count"
    echo "Link tags: $link_count"
    echo "Inline styles: $inline_styles"
    
    if [ $((style_count + link_count)) -gt 0 ]; then
        echo -e "${GREEN}✓ CSS found${NC}"
    else
        echo -e "${RED}✗ No CSS found${NC}"
    fi
    echo ""
    
    # Test 6: Check for errors
    echo -e "${YELLOW}[6] Checking for error patterns...${NC}"
    errors=0
    
    if grep -q "500 Server Error" "$output_file" 2>/dev/null; then
        echo -e "${RED}✗ Found: 500 Server Error${NC}"
        ((errors++))
    fi
    
    if grep -q "404 Not Found" "$output_file" 2>/dev/null; then
        echo -e "${RED}✗ Found: 404 Not Found${NC}"
        ((errors++))
    fi
    
    if grep -q "Traceback" "$output_file" 2>/dev/null; then
        echo -e "${RED}✗ Found: Python Traceback${NC}"
        ((errors++))
    fi
    
    if grep -q "SyntaxError\|TypeError\|AttributeError" "$output_file" 2>/dev/null; then
        echo -e "${RED}✗ Found: Python Error${NC}"
        ((errors++))
    fi
    
    if grep -q "<h1>Error</h1>\|<h1>500</h1>" "$output_file" 2>/dev/null; then
        echo -e "${RED}✗ Found: Error page${NC}"
        ((errors++))
    fi
    
    if [ $errors -eq 0 ]; then
        echo -e "${GREEN}✓ No error patterns found${NC}"
    fi
    echo ""
    
    # Test 7: Check for meta tags
    echo -e "${YELLOW}[7] Checking meta tags...${NC}"
    meta_count=$(grep -c "<meta" "$output_file" || true)
    has_viewport=$(grep -c "viewport" "$output_file" || true)
    has_charset=$(grep -c "charset" "$output_file" || true)
    
    echo "Meta tags: $meta_count"
    echo "Viewport: $([ $has_viewport -gt 0 ] && echo 'Yes' || echo 'No')"
    echo "Charset: $([ $has_charset -gt 0 ] && echo 'Yes' || echo 'No')"
    
    if [ $meta_count -gt 0 ]; then
        echo -e "${GREEN}✓ Meta tags found${NC}"
    else
        echo -e "${YELLOW}⚠ No meta tags found${NC}"
    fi
    echo ""
    
    # Test 8: Check for HTML structure
    echo -e "${YELLOW}[8] Checking HTML structure...${NC}"
    has_html=$(grep -c "<html" "$output_file" || true)
    has_head=$(grep -c "<head" "$output_file" || true)
    has_body=$(grep -c "<body" "$output_file" || true)
    has_title=$(grep -c "<title" "$output_file" || true)
    
    echo "Has HTML tag: $([ $has_html -gt 0 ] && echo 'Yes' || echo 'No')"
    echo "Has HEAD tag: $([ $has_head -gt 0 ] && echo 'Yes' || echo 'No')"
    echo "Has BODY tag: $([ $has_body -gt 0 ] && echo 'Yes' || echo 'No')"
    echo "Has TITLE tag: $([ $has_title -gt 0 ] && echo 'Yes' || echo 'No')"
    
    if [ $has_html -gt 0 ] && [ $has_head -gt 0 ] && [ $has_body -gt 0 ]; then
        echo -e "${GREEN}✓ Valid HTML structure${NC}"
    else
        echo -e "${RED}✗ Invalid HTML structure${NC}"
    fi
    echo ""
    
    # Test 9: Check Content-Type
    echo -e "${YELLOW}[9] Checking Content-Type header...${NC}"
    content_type=$(curl -s -m $TIMEOUT -I "$url" | grep -i "Content-Type" | head -1)
    echo "$content_type"
    
    if echo "$content_type" | grep -q "text/html"; then
        echo -e "${GREEN}✓ Valid Content-Type${NC}"
    else
        echo -e "${YELLOW}⚠ Unexpected Content-Type${NC}"
    fi
    echo ""
    
    # Test 10: Check Server header
    echo -e "${YELLOW}[10] Checking Server header...${NC}"
    server=$(curl -s -m $TIMEOUT -I "$url" | grep -i "Server:" | head -1)
    echo "$server"
    echo ""
}

# Function to test paths
test_paths() {
    local domain_name=$1
    local domain_url=$2
    shift 2
    local paths=("$@")
    
    echo -e "${BLUE}Testing paths for: $domain_name${NC}"
    echo ""
    
    for path in "${paths[@]}"; do
        url="$domain_url$path"
        http_code=$(curl -s -m $TIMEOUT -o /dev/null -w "%{http_code}" "$url")
        
        if [ "$http_code" -lt 400 ]; then
            echo -e "${GREEN}✓${NC} $path: $http_code"
        elif [ "$http_code" -lt 500 ]; then
            echo -e "${YELLOW}⚠${NC} $path: $http_code"
        else
            echo -e "${RED}✗${NC} $path: $http_code"
        fi
    done
    echo ""
}

# Main tests
echo -e "${BLUE}========== VRESUME.STRUCTA.CLOUD ==========${NC}"
test_domain "vresume" "$VRESUME_URL"

echo -e "${BLUE}========== CTC-RESEARCH.COM ==========${NC}"
test_domain "ctc" "$CTC_URL"

echo -e "${BLUE}========== STRUCTA.CLOUD ==========${NC}"
test_domain "structa" "$STRUCTA_URL"

echo -e "${BLUE}========== LMS-DEMO.COM ==========${NC}"
test_domain "lms" "$LMS_URL"

echo -e "${BLUE}========== MEDIA.STRUCTA.CLOUD ==========${NC}"
test_domain "media_structa" "$MEDIA_STRUCTA_URL"

echo -e "${BLUE}========== MEDIA.CTC-RESEARCH.COM ==========${NC}"
test_domain "media_ctc" "$MEDIA_CTC_URL"

echo -e "${BLUE}========== MEDIA.LMS-DEMO.COM ==========${NC}"
test_domain "media_lms" "$MEDIA_LMS_URL"

echo -e "${BLUE}========== MEDIA.VRESUME.STRUCTA.CLOUD ==========${NC}"
test_domain "media_vresume" "$MEDIA_VRESUME_URL"

# Test specific paths
echo -e "${BLUE}========== PATH ACCESSIBILITY ==========${NC}"
test_paths "vresume" "$VRESUME_URL" "/" "/blog/" "/contact/" "/admin/"
test_paths "ctc" "$CTC_URL" "/" "/research/" "/about/"
test_paths "structa" "$STRUCTA_URL" "/" "/admin/" "/about/"
test_paths "lms" "$LMS_URL" "/" "/blog/" "/admin/"
test_paths "media_structa" "$MEDIA_STRUCTA_URL" "/" "/static/images/logo.png"
test_paths "media_ctc" "$MEDIA_CTC_URL" "/" "/static/images/logo.png"
test_paths "media_lms" "$MEDIA_LMS_URL" "/" "/static/images/logo.png"
test_paths "media_vresume" "$MEDIA_VRESUME_URL" "/" "/static/images/logo.png"

# Summary
echo ""
echo "=================================================================="
echo "TEST SUMMARY"
echo "=================================================================="
echo "Full responses saved to: $OUTPUT_DIR"
ls -lh "$OUTPUT_DIR"
echo ""
echo -e "${GREEN}✓ All tests completed${NC}"
echo ""
