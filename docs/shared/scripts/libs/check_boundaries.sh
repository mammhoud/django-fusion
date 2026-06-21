#!/usr/bin/env bash
# Verify package boundary rules — no forbidden cross-package imports.
# Usage: ./scripts/libs/check_boundaries.sh
set -e

LIBS="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)/applications/libs"
PASS=0; FAIL=0

check() {
    local pkg="$1" src="$2" forbidden="$3"
    local count
    count=$(grep -rn "$forbidden" "$LIBS/$src" --include="*.py" \
        --exclude-dir=__pycache__ 2>/dev/null | grep -v "^.*#" | wc -l | tr -d ' ')
    if [ "$count" -gt 0 ]; then
        echo "FAIL [$pkg] found $count import(s) of '$forbidden'"
        grep -rn "$forbidden" "$LIBS/$src" --include="*.py" --exclude-dir=__pycache__ | grep -v "^.*#" | head -5
        FAIL=$((FAIL+1))
    else
        echo "PASS [$pkg] no '$forbidden' imports"
        PASS=$((PASS+1))
    fi
}

echo "=== Package Boundary Check ==="
echo ""
echo "--- django-osoul: must not import wagtail/celery/AI/rseal (except comp/) ---"
check "osoul" "django-osoul/src/django_osoul/models" "import wagtail"
check "osoul" "django-osoul/src/django_osoul/models" "from wagtail"
check "osoul" "django-osoul/src/django_osoul/utils" "import wagtail"
check "osoul" "django-osoul/src/django_osoul/utils" "from wagtail"
check "osoul" "django-osoul/src/django_osoul/views" "import wagtail"
check "osoul" "django-osoul/src/django_osoul/views" "from wagtail"
check "osoul" "django-osoul/src" "import celery"
check "osoul" "django-osoul/src" "import openai"
check "osoul" "django-osoul/src" "import anthropic"
check "osoul" "django-osoul/src" "from django_rseal"
check "osoul" "django-osoul/src" "import django_rseal"

echo ""
echo "--- crafts-ai: must not import django ---"
check "crafts_ai" "crafts-ai/src/crafts_ai" "^from django"
check "crafts_ai" "crafts-ai/src/crafts_ai" "^import django"

echo ""
echo "--- django-rseal: must not import django-grep ---"
check "rseal" "django-rseal/src" "from django_grep"
check "rseal" "django-rseal/src" "import django_grep"

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ] && exit 0 || exit 1
