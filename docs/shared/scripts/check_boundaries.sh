#!/usr/bin/env bash
# check_boundaries.sh — Verify package boundary rules for venv/libs
# Rules:
#   django-osoul core (excl. comp/blocks, comp/templatetags): NO wagtail, celery, django_rseal
#   nawaai: NO django imports

set -euo pipefail

LIBS="$(cd "$(dirname "$0")/.." && pwd)"
ERRORS=0

echo "=== Checking django-osoul boundaries (no wagtail/celery/django_rseal) ==="
OSOUL="$LIBS/django-osoul/src/django_osoul"
# comp/blocks and comp/templatetags are Wagtail UI components — wagtail imports are expected there
VIOLATIONS=$(grep -rn --include="*.py" \
  -e "^from wagtail" -e "^import wagtail" \
  -e "^from celery" -e "^import celery" \
  -e "^from django_rseal" -e "^import django_rseal" \
  "$OSOUL" 2>/dev/null \
  | grep -v "__pycache__" \
  | grep -v "/comp/blocks/" \
  | grep -v "/comp/templatetags/" \
  || true)

if [ -n "$VIOLATIONS" ]; then
  echo "FAIL: django-osoul boundary violations:"
  echo "$VIOLATIONS"
  ERRORS=$((ERRORS + 1))
else
  echo "PASS: django-osoul has no boundary violations"
fi

echo ""
echo "=== Checking nawaai boundaries (no django imports) ==="
NAWAAI="$LIBS/nawaai/crafts_ai"
VIOLATIONS=$(grep -rn --include="*.py" \
  -e "^from django" -e "^import django" \
  "$NAWAAI" 2>/dev/null | grep -v "__pycache__" || true)

if [ -n "$VIOLATIONS" ]; then
  echo "FAIL: nawaai boundary violations:"
  echo "$VIOLATIONS"
  ERRORS=$((ERRORS + 1))
else
  echo "PASS: nawaai has no Django imports"
fi

echo ""
if [ "$ERRORS" -eq 0 ]; then
  echo "✅ All boundary checks passed"
  exit 0
else
  echo "❌ $ERRORS boundary check(s) failed"
  exit 1
fi
