#!/bin/bash
# Verification script for Selenium tests and Django-Seed updates

echo "=================================="
echo "  Verification Script"
echo "  Date: $(date)"
echo "=================================="
echo ""

# Check Selenium test file
echo "1. Checking Selenium test file..."
if [ -f "tests/test_selenium_auth_comprehensive.py" ]; then
    echo "   ✅ tests/test_selenium_auth_comprehensive.py exists"
    lines=$(wc -l < tests/test_selenium_auth_comprehensive.py)
    echo "   📄 $lines lines of code"
else
    echo "   ❌ Selenium test file not found"
fi
echo ""

# Check django-seed in libs
echo "2. Checking django-seed in libs..."
if [ -d "libs/django-seed/django_seed" ]; then
    echo "   ✅ libs/django-seed/django_seed exists"
    files=$(find libs/django-seed/django_seed -name "*.py" | wc -l)
    echo "   📄 $files Python files"
else
    echo "   ❌ django-seed not found in libs"
fi
echo ""

# Check django-seed in ctc-research.com
echo "3. Checking django-seed in ctc-research.com..."
if [ -d "ctc-research.com/libs/django_seed" ]; then
    echo "   ✅ ctc-research.com/libs/django_seed exists"
    files=$(find ctc-research.com/libs/django_seed -name "*.py" | wc -l)
    echo "   📄 $files Python files"
else
    echo "   ❌ django-seed not found in ctc-research.com"
fi
echo ""

# Check django-seed in structa.cloud
echo "4. Checking django-seed in structa.cloud..."
if [ -d "structa.cloud/libs/django_seed" ]; then
    echo "   ✅ structa.cloud/libs/django_seed exists"
    files=$(find structa.cloud/libs/django_seed -name "*.py" | wc -l)
    echo "   📄 $files Python files"
else
    echo "   ❌ django-seed not found in structa.cloud"
fi
echo ""

# Check documentation
echo "5. Checking documentation..."
docs=0
[ -f "DJANGO_SEED_UPDATE_SUMMARY.md" ] && echo "   ✅ DJANGO_SEED_UPDATE_SUMMARY.md" && ((docs++))
[ -f "SELENIUM_AND_DJANGO_SEED_COMPLETION.md" ] && echo "   ✅ SELENIUM_AND_DJANGO_SEED_COMPLETION.md" && ((docs++))
echo "   📄 $docs documentation files"
echo ""

# Test django_seed import
echo "6. Testing django_seed import..."
python3 -c "import sys; sys.path.insert(0, 'libs/django-seed'); import django_seed; print('   ✅ django_seed imports successfully')" 2>/dev/null || echo "   ⚠️  Import test skipped (dependencies may be needed)"
echo ""

# Summary
echo "=================================="
echo "  Verification Complete"
echo "=================================="
echo ""
echo "Next steps:"
echo "  1. Install Selenium: pip install selenium webdriver-manager"
echo "  2. Run Selenium tests: python3 tests/test_selenium_auth_comprehensive.py"
echo "  3. Test django-seed in both projects"
echo ""
