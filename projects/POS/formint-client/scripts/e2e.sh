#!/usr/bin/env bash
# ============================================================================
# e2e.sh — full-stack end-to-end tests for the Formint Client storefront.
#   · Django backend   → :8075
#   · Astro storefront → :4322 (proxies backend routes)
#   · runs frontend/tests/e2e.test.mjs (node --test)
#
# Reuses already-running servers on :8075/:4322 when present (e.g. during a
# `make stack` session); otherwise boots them and cleans up on exit.
# ============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PIDS=()
BACKEND_URL="http://127.0.0.1:8075/fusion/render-mode/"
ASTRO_URL="http://127.0.0.1:4322/"
BE_LOG=/tmp/fc-e2e-backend.log
AS_LOG=/tmp/fc-e2e-astro.log

log() { printf '\n\033[1;36m▶ %s\033[0m\n' "$*"; }

up() { curl -sf "$1" >/dev/null 2>&1; }

cleanup() {
    if [ "${#PIDS[@]}" -gt 0 ]; then
        log "Stopping e2e servers…"
        for pid in "${PIDS[@]}"; do
            kill "$pid" 2>/dev/null || true
            pkill -P "$pid" 2>/dev/null || true
        done
        wait 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

# ── Seed the DB once (idempotent) ──────────────────────────────────────────
if ! up "$BACKEND_URL"; then
    log "Seeding the demo catalog (make seed)"
    (cd "$ROOT/backend" && make seed >/dev/null)
fi

# ── Boot whatever is not already running ───────────────────────────────────
if ! up "$BACKEND_URL"; then
    log "Starting Django backend → http://localhost:8075"
    (cd "$ROOT/backend" && uv run python manage.py runserver 127.0.0.1:8075 >"$BE_LOG" 2>&1) &
    PIDS+=($!)
fi

if ! up "$ASTRO_URL"; then
    log "Starting Astro storefront → http://localhost:4322"
    (cd "$ROOT/frontend" && pnpm dev >"$AS_LOG" 2>&1) &
    PIDS+=($!)
fi

# ── Wait for readiness (90s) ───────────────────────────────────────────────
log "Waiting for the stack…"
READY=0
for _ in $(seq 1 90); do
    if up "$BACKEND_URL" && up "$ASTRO_URL"; then
        READY=1
        break
    fi
    sleep 1
done

if [ "$READY" -ne 1 ]; then
    echo "✗ Stack did not become ready (backend or Astro on :8075/:4322)." >&2
    echo "── backend log tail ──" >&2
    tail -5 "$BE_LOG" >&2 2>/dev/null || true
    echo "── astro log tail ──" >&2
    tail -5 "$AS_LOG" >&2 2>/dev/null || true
    exit 1
fi

# ── Run ────────────────────────────────────────────────────────────────────
log "Running e2e tests (180s cap)"
(cd "$ROOT/frontend" && timeout 180 pnpm test)
log "E2E suite finished."
