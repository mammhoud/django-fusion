#!/usr/bin/env bash
# ============================================================================
# POS — Unified Test Runner
# ============================================================================
# Orchestrates all test suites from the unified tests/ directory.
#
# Usage:
#   bash tests/run-all.sh              — run everything (default)
#   bash tests/run-all.sh py           — Python sidecar tests only
#   bash tests/run-all.sh js           — JS vitest tests only
#   bash tests/run-all.sh api          — JS API endpoint tests only
#   bash tests/run-all.sh selenium     — Selenium admin panel tests only
#   bash tests/run-all.sh restart      — kill stale servers, fresh run
#
# Quick:  bash tests/run-all.sh --quick    (skip selenium + api)
# ============================================================================

set -uo pipefail  # NOTE: no set -e — we capture exit codes manually

ROOT="$(cd "$(dirname "$0")/.." && pwd)"          # projects/pos/
SIDECAR_FULL="$ROOT/pos-full/sidecar"
SIDECAR_SOLO="$ROOT/pos-solo/sidecar"
TESTS="$ROOT/tests"

MODE="${1:-all}"
RESTART="${RESTART:-false}"
QUICK="${QUICK:-false}"

PASS=0
FAIL=0

cleanup() {
  echo ""
  echo "═══ Cleanup ═══"
  pkill -f 'manage.py runserver' 2>/dev/null || true
  pkill -f 'python3 server.py' 2>/dev/null || true
  echo "Servers stopped."
}
trap cleanup EXIT

banner() {
  echo ""
  echo "╔══════════════════════════════════════════════════════════╗"
  printf "║  %-52s  ║\n" "$1"
  echo "╚══════════════════════════════════════════════════════════╝"
}

run_py_full() {
  banner "Python: pos-full sidecar"
  bash "$TESTS/py/full/run.sh" 2>&1 | tail -15
  local st=${PIPESTATUS[0]}
  if [ "$st" -eq 0 ]; then
    echo "  ✅ pos-full — PASSED"; PASS=$((PASS + 1))
  else
    echo "  ❌ pos-full — FAILED (exit $st)"; FAIL=$((FAIL + 1))
  fi
}

run_py_solo() {
  banner "Python: pos-solo sidecar"
  bash "$TESTS/py/solo/run.sh" 2>&1 | tail -15
  local st=${PIPESTATUS[0]}
  if [ "$st" -eq 0 ]; then
    echo "  ✅ pos-solo — PASSED"; PASS=$((PASS + 1))
  else
    echo "  ❌ pos-solo — FAILED (exit $st)"; FAIL=$((FAIL + 1))
  fi
}

run_js() {
  banner "JavaScript: vitest (pos-full src/test)"
  cd "$ROOT/pos-full"
  npx vitest run --config "$TESTS/js/vitest.config.ts" 2>&1 | tail -20
  local st=${PIPESTATUS[0]}
  if [ "$st" -eq 0 ]; then
    echo "  ✅ vitest — PASSED"; PASS=$((PASS + 1))
  else
    echo "  ❌ vitest — FAILED (exit $st)"; FAIL=$((FAIL + 1))
  fi
}

# ────────────────────────────────────────────────────────────────────────────
# 4. API — Node.js endpoint tests (requires running sidecar)
# ────────────────────────────────────────────────────────────────────────────
run_api() {
  banner "API: Node.js endpoint tests"

  # Start pos-full sidecar if not running
  if ! curl -sf http://127.0.0.1:8000/ >/dev/null 2>&1; then
    echo "Starting pos-full sidecar on :8000 ..."
    cd "$SIDECAR_FULL"
    rm -f restaurant.db
    python3 manage.py migrate 2>/dev/null
    POS_FULL_ADMIN_EMAIL='admin@pos-full.local' \
      POS_FULL_ADMIN_PASSWORD='admin123' \
      python3 manage.py --ensure-superuser 2>/dev/null || true
    python3 manage.py runserver 0.0.0.0:8000 &>/tmp/pos-api-test.log &
    sleep 4
  fi

  # Seed some test data
  echo "Seeding test data..."
  curl -sf -X POST http://127.0.0.1:8000/pos_full/product/ \
    -H 'Content-Type: application/json' \
    -d '{"name":"API Test Product","price":5.99,"sku":"API-TEST-SEED","category_name":"Test","unit":"unit","is_available":true}' \
    >/dev/null 2>&1 || true

  curl -sf -X POST http://127.0.0.1:8000/pos_full/sale/ \
    -H 'Content-Type: application/json' \
    -d "{\"customer_name\":\"Test Customer\",\"total\":19.99,\"payment_method\":\"cash\",\"status\":\"completed\",\"sale_date\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" \
    >/dev/null 2>&1 || true

  echo "Running API tests..."
  cd "$ROOT"

  echo "--- Products ---"
  POS_API_URL=http://127.0.0.1:8000 node tests/api/test_products.mjs 2>&1

  echo "--- Sales ---"
  POS_API_URL=http://127.0.0.1:8000 node tests/api/test_sales.mjs 2>&1
}

# ────────────────────────────────────────────────────────────────────────────
# 5. SELENIUM — Admin panel browser tests (requires running sidecar + chrom*)
# ────────────────────────────────────────────────────────────────────────────
run_selenium() {
  banner "Selenium: Admin panel browser tests"

  if ! command -v chromium-browser &>/dev/null && ! command -v chromium &>/dev/null && ! command -v google-chrome &>/dev/null; then
    echo "⚠️  Chrome/Chromium not found — skipping selenium tests"
    return 0
  fi

  # Start pos-full sidecar with admin if not running
  if ! curl -sf http://127.0.0.1:8000/ >/dev/null 2>&1; then
    echo "Starting pos-full sidecar on :8000 ..."
    cd "$SIDECAR_FULL"
    rm -f restaurant.db
    python3 manage.py migrate 2>/dev/null
    POS_FULL_ADMIN_EMAIL='admin@pos-full.local' \
      POS_FULL_ADMIN_PASSWORD='admin123' \
      python3 manage.py --ensure-superuser 2>/dev/null || true
    python3 manage.py runserver 0.0.0.0:8000 &>/tmp/pos-selenium-test.log &
    sleep 5
  fi

  cd "$TESTS"
  unset DJANGO_SETTINGS_MODULE
  python3 -m pytest selenium/ -v --tb=short --no-header 2>&1 | tail -30
}

# ════════════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════════════

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         POS — Unified Test Runner                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo "Root: $ROOT"
echo "Mode: $MODE"
echo ""

case "$MODE" in
  all)
    run_py_full
    run_py_solo
    run_js
    [[ "$QUICK" == "true" ]] || run_api
    [[ "$QUICK" == "true" ]] || run_selenium
    ;;
  py)
    run_py_full
    run_py_solo
    ;;
  py-full)
    run_py_full
    ;;
  py-solo)
    run_py_solo
    ;;
  js)
    run_js
    ;;
  api)
    run_api
    ;;
  selenium)
    run_selenium
    ;;
  restart)
    cleanup
    echo "Restarting..."
    exec bash "$0" all
    ;;
  --quick)
    QUICK=true
    run_py_full
    run_py_solo
    run_js
    ;;
  *)
    echo "Unknown mode: $MODE"
    echo "Usage: bash tests/run-all.sh [py|js|api|selenium|restart|--quick]"
    exit 1
    ;;
esac

# ── Summary ──────────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    SUMMARY                                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo "  Suites passed: $PASS"
echo "  Suites failed: $FAIL"
echo ""
if [ "$FAIL" -eq 0 ]; then
  echo "  🎉 All test suites passed!"
else
  echo "  ⚠️  $FAIL suite(s) failed."
fi
echo ""

exit "$FAIL"
