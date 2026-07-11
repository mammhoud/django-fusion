#!/usr/bin/env bash
# check_boundaries.sh — Verify package boundary rules for venv/libs
# Rules:
#   django-fusion core (excl. comp/blocks, comp/templatetags): NO wagtail, celery, ceptor_ai
#   ceptor-ai: NO django imports

set -euo pipefail

LIBS="$(cd "$(dirname "$0")/../.." && pwd)/core/libs"
ERRORS=0

echo "=== Checking django-fusion boundaries (no wagtail/celery/ceptor_ai) ==="
OSOUL="$LIBS/django-fusion/src/django_fusion"
# comp/blocks and comp/templatetags are Wagtail UI components — wagtail imports are expected there
VIOLATIONS=$(grep -rn --include="*.py" \
  -e "^from wagtail" -e "^import wagtail" \
  -e "^from celery" -e "^import celery" \
  -e "^from ceptor_ai" -e "^import ceptor_ai" \
  "$OSOUL" 2>/dev/null \
  | grep -v "__pycache__" \
  | grep -v "/comp/blocks/" \
  | grep -v "/comp/templatetags/" \
  || true)

if [ -n "$VIOLATIONS" ]; then
  echo "FAIL: django-fusion boundary violations:"
  echo "$VIOLATIONS"
  ERRORS=$((ERRORS + 1))
else
  echo "PASS: django-fusion has no boundary violations"
fi

echo ""
echo "=== Checking ceptor-ai boundaries (no django imports) ==="
CRAFTS_AI="$LIBS/ceptor-ai/src/ceptor_ai"
VIOLATIONS=$(grep -rn --include="*.py" \
  -e "^from django" -e "^import django" \
  "$CRAFTS_AI" 2>/dev/null | grep -v "__pycache__" || true)

if [ -n "$VIOLATIONS" ]; then
  echo "FAIL: ceptor-ai boundary violations:"
  echo "$VIOLATIONS"
  ERRORS=$((ERRORS + 1))
else
  echo "PASS: ceptor-ai has no Django imports"
fi

echo ""
if [ "$ERRORS" -eq 0 ]; then
  echo "✅ All boundary checks passed"
  exit 0
else
  echo "❌ $ERRORS boundary check(s) failed"
  exit 1
fi
