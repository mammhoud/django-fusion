#!/usr/bin/env bash
# run_tests.sh — Run all venv/libs test suites
set -euo pipefail

LIBS="$(cd "$(dirname "$0")/.." && pwd)"
ERRORS=0

echo "=== Running django-fusion tests ==="
cd "$LIBS"
if uv run pytest django-fusion/tests/ -v --tb=short -q 2>&1; then
  echo "PASS: django-fusion tests"
else
  echo "FAIL: django-fusion tests"
  ERRORS=$((ERRORS + 1))
fi

echo ""
if [ "$ERRORS" -eq 0 ]; then
  echo "✅ All test suites passed"
  exit 0
else
  echo "❌ $ERRORS test suite(s) failed"
  exit 1
fi
