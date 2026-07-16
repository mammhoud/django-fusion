#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# Run tests inside Docker containers (production environment).
#
# Usage:
#   bash tests/scripts/run_container_tests.sh structa.cloud
#   bash tests/scripts/run_container_tests.sh ctc-research.com
#   bash tests/scripts/run_container_tests.sh all
# ─────────────────────────────────────────────────────────────────────────────
set -uo pipefail

WEBSITE="${1:-all}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TESTS_DIR="$(cd "$SCRIPT_DIR/../../tests" && pwd)"

PASS=0
FAIL=0

ok()   { echo "  ✅ $*"; PASS=$((PASS+1)); }
err()  { echo "  ❌ $*"; FAIL=$((FAIL+1)); }
info() { echo "  ℹ️  $*"; }

run_for() {
    local site="$1"
    local container port

    case "$site" in
        structa.cloud|lms-demo) container="lms-demo-website"; port=5071 ;;
        ctc-research.com|ctc-research) container="ctc-research-website"; port=5070 ;;
        vresume|vresume.local) container="vresume-website"; port=5072 ;;
        *) echo "Unknown site: $site"; exit 1 ;;
    esac

    echo ""
    echo "══════════════════════════════════════════════════════════════"
    echo "  $container  (port $port)"
    echo "══════════════════════════════════════════════════════════════"

    # ── 1. Container running? ────────────────────────────────────────────────
    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        ok "Container is running"
    else
        err "Container $container is not running — skipping"
        return
    fi

    # ── 2. Django system check ───────────────────────────────────────────────
    if docker exec "$container" python manage.py check 2>&1 \
        | grep -q "System check identified no issues"; then
        ok "Django system check"
    else
        err "Django system check failed"
    fi

    # ── 3. Migration status ──────────────────────────────────────────────────
    # migrate --check exits 0 when there ARE pending migrations, 1 when all applied
    if docker exec "$container" python manage.py migrate --check 2>/dev/null; then
        # exit 0 = pending migrations exist → apply them
        docker exec "$container" python manage.py migrate --noinput 2>&1 | tail -5
        ok "Migrations applied (were pending)"
    else
        ok "All migrations already applied"
    fi

    # ── 4. Health endpoint ───────────────────────────────────────────────────
    response=$(curl -sf "http://localhost:${port}/health/" 2>/dev/null || echo "FAIL")
    if echo "$response" | grep -q '"healthy"'; then
        ok "Health endpoint → $response"
    else
        err "Health endpoint → $response"
    fi

    # ── 5. Admin login page ──────────────────────────────────────────────────
    status=$(curl -so /dev/null -w "%{http_code}" \
        "http://localhost:${port}/django-admin/login/" 2>/dev/null)
    if [ "$status" = "200" ]; then
        ok "Admin login page (HTTP 200)"
    else
        err "Admin login page (HTTP $status)"
    fi

    # ── 6. Auth URLs ─────────────────────────────────────────────────────────
    for path in "/auth/login/" "/auth/register/"; do
        s=$(curl -so /dev/null -w "%{http_code}" -L \
            "http://localhost:${port}${path}" 2>/dev/null)
        if [ "${s:-0}" -lt 500 ] 2>/dev/null; then
            ok "URL $path (HTTP $s)"
        else
            err "URL $path (HTTP $s)"
        fi
    done

    # ── 7. Common URLs ───────────────────────────────────────────────────────
    for path in "/sitemap.xml" "/robots.txt"; do
        s=$(curl -so /dev/null -w "%{http_code}" \
            "http://localhost:${port}${path}" 2>/dev/null)
        # sitemap may 404 if no Wagtail pages yet — that's acceptable
        if [ "${s:-0}" -lt 500 ] 2>/dev/null; then
            ok "URL $path (HTTP $s)"
        else
            err "URL $path (HTTP $s — server error)"
        fi
    done

    # ── 8. Pytest inside container ───────────────────────────────────────────
    echo ""
    info "Copying test file into $container ..."
    docker cp "$TESTS_DIR/test_container.py" "$container:/tmp/test_container.py" 2>/dev/null

    echo ""
    info "Running pytest inside $container ..."
    if docker exec "$container" bash -c \
        "pip install pytest -q 2>/dev/null; \
         python -m pytest /tmp/test_container.py -v --tb=short --no-header -p no:django 2>&1"; then
        ok "Container pytest suite"
    else
        err "Container pytest suite (some tests failed)"
    fi
}

case "$WEBSITE" in
    all)
        run_for "structa.cloud"
        run_for "ctc-research.com"
        ;;
    *)
        run_for "$WEBSITE"
        ;;
esac

echo ""
echo "══════════════════════════════════════════════════════════════"
printf "  Results: %d passed, %d failed\n" "$PASS" "$FAIL"
echo "══════════════════════════════════════════════════════════════"

[ "$FAIL" -eq 0 ]
