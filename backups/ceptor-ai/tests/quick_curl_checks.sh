#!/bin/bash
# Quick curl checks for domain reachability
# Tests: HTTP status, CSS loading, no errors, response time

VRESUME="https://vresume.structa.cloud"
CTC="https://ctc-research.com"
STRUCTA="https://structa.cloud"
LMS="https://lms-demo.com"
MEDIA_STRUCTA="https://media.structa.cloud"
MEDIA_CTC="https://media.ctc-research.com"
MEDIA_LMS="https://media.lms-demo.com"
MEDIA_VRESUME="https://media.vresume.structa.cloud"

echo "=================================================="
echo "QUICK DOMAIN REACHABILITY CHECKS"
echo "=================================================="
echo ""

# Function for quick test
quick_test() {
    local name=$1
    local url=$2
    
    echo "Testing: $name"
    echo "URL: $url"
    echo ""
    
    # Test 1: Basic connectivity with status
    echo "1. Connectivity & Status:"
    curl -s -m 10 -o /dev/null -w "   HTTP Status: %{http_code}\n" "$url"
    curl -s -m 10 -o /dev/null -w "   Response Time: %{time_total}s\n" "$url"
    echo ""
    
    # Test 2: Check for CSS
    echo "2. CSS Loading Check:"
    curl -s -m 10 "$url" | grep -c '<link.*stylesheet' && echo "   ✓ Found stylesheet links" || echo "   ✗ No stylesheet links found"
    curl -s -m 10 "$url" | grep -c '<style' && echo "   ✓ Found style tags" || echo "   ✗ No style tags found"
    echo ""
    
    # Test 3: Check for errors
    echo "3. Error Detection:"
    if curl -s -m 10 "$url" | grep -qi "500\|error\|traceback\|syntaxerror"; then
        echo "   ✗ Errors found in response"
    else
        echo "   ✓ No error patterns detected"
    fi
    echo ""
    
    # Test 4: HTML structure
    echo "4. HTML Structure:"
    curl -s -m 10 "$url" | grep -q '<html' && echo "   ✓ HTML tag found" || echo "   ✗ No HTML tag"
    curl -s -m 10 "$url" | grep -q '<head' && echo "   ✓ HEAD tag found" || echo "   ✗ No HEAD tag"
    curl -s -m 10 "$url" | grep -q '<body' && echo "   ✓ BODY tag found" || echo "   ✗ No BODY tag"
    echo ""
    
    # Test 5: Meta tags
    echo "5. Meta Tags:"
    meta_count=$(curl -s -m 10 "$url" | grep -o '<meta' | wc -l)
    echo "   Meta tags found: $meta_count"
    curl -s -m 10 "$url" | grep -q 'viewport' && echo "   ✓ Viewport meta found" || echo "   ✗ No viewport meta"
    echo ""
    
    # Test 6: Content-Type
    echo "6. Content-Type:"
    curl -s -m 10 -I "$url" | grep -i content-type
    echo ""
    
    # Test 7: Server info
    echo "7. Server Info:"
    curl -s -m 10 -I "$url" | grep -i "^server:\|^x-powered-by:"
    echo ""
    
    echo "=================================================="
    echo ""
}

# Run tests
quick_test "VResume" "$VRESUME"
quick_test "CTC Research" "$CTC"
quick_test "Structa Cloud" "$STRUCTA"
quick_test "LMS Demo" "$LMS"
quick_test "Media Structa" "$MEDIA_STRUCTA"
quick_test "Media CTC" "$MEDIA_CTC"
quick_test "Media LMS" "$MEDIA_LMS"
quick_test "Media VResume" "$MEDIA_VRESUME"

echo "✓ Quick checks completed"
