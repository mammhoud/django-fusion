#!/usr/bin/env bash
# ============================================================================
# dev-stack.sh — run the full Formint Client dev stack:
#   · Django backend   → http://localhost:8075
#   · Astro storefront → http://localhost:4322
#   · Vue POS          → http://localhost:1420
#
# Ctrl+C stops every server (cascades to child processes).
# ============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PIDS=()
PORTS=(8075 4322 1420)

log() { printf '\n\033[1;36m▶ %s\033[0m\n' "$*"; }

port_in_use() {
    lsof -iTCP:"$1" -sTCP:LISTEN -P -n 2>/dev/null | grep -q LISTEN
}

# ── Pre-flight: refuse to start when a port is already taken ───────────────
for port in "${PORTS[@]}"; do
    if port_in_use "$port"; then
        echo "✗ Port $port is already in use:" >&2
        lsof -iTCP:"$port" -sTCP:LISTEN -P -n 2>/dev/null | tail -n +1 >&2
        echo "  Stop the process above (or set another port) and re-run." >&2
        exit 1
    fi
done

cleanup() {
    log "Stopping all dev servers…"
    # Kill the tracked subshells, then cascade to any grandchildren.
    for pid in "${PIDS[@]:-}"; do
        kill "$pid" 2>/dev/null || true
        pkill -P "$pid" 2>/dev/null || true
    done
    wait 2>/dev/null || true
    log "Done."
}
trap cleanup EXIT INT TERM

# ── Django backend (:8075) ────────────────────────────────────────────────
log "Starting Django backend → http://localhost:8075"
(cd "$ROOT/backend" && make dev) &
PIDS+=($!)

# ── Astro storefront (:4322) ───────────────────────────────────────────────
log "Starting Astro storefront → http://localhost:4322"
(cd "$ROOT/frontend" && pnpm dev) &
PIDS+=($!)

# ── Vue POS (:1420) ────────────────────────────────────────────────────────
log "Starting Vue POS → http://localhost:1420"
(cd "$ROOT" && pnpm dev) &
PIDS+=($!)

wait
