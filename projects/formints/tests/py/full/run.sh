#!/usr/bin/env bash
# ============================================================================
# POS — run merged server tests (pos-full + pos-solo absorbed into formint-pos)
# ============================================================================
# pos-full and pos-solo were merged into formint-pos (see the merge commit).
# Their Robyn server now lives at formint-pos/server/ — this wrapper runs
# the combined suite from that single location.
#
# Test-grouping note
# ------------------
# Each server test file bootstraps its own Django settings at import time
# (independent in-memory DBs). Running the whole tests/ directory in ONE
# pytest session lets the first file's `settings.configure()` win and breaks
# the rest (Django settings are process-global). The documented canonical
# invocation is therefore the 3-file subset below; the remaining files run
# as their own groups. See server/ARCHITECTURE.md → Test Results.
#
# Usage:
#   bash py/full/run.sh                    — all groups (rust_db excluded)
#   bash py/full/run.sh -k "test_product"  — filtered (first group)
# ============================================================================

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"  # projects/pos/
SERVER="$ROOT/formint-pos/server"
cd "$SERVER"

PY=python3
if [ -x "$SERVER/.venv/bin/python3" ]; then
    PY="$SERVER/.venv/bin/python3"
fi

EXTRA_ARGS=("$@")
if [ ${#EXTRA_ARGS[@]} -eq 0 ]; then
    EXTRA_ARGS=("-k" "not rust_db")
fi

echo "▸ Running merged server tests from $SERVER"
echo "  python: $PY"
echo ""

# Clear DJANGO_SETTINGS_MODULE to avoid pytest-django loading root settings
unset DJANGO_SETTINGS_MODULE
export PYTHONDONTWRITEBYTECODE=1

# Group 1 — documented canonical subset (server + data-sync + webhook e2e)
echo "── Group 1: test_server + test_data_sync + test_webhook_e2e ──"
"$PY" -m pytest tests/test_server.py tests/test_data_sync.py tests/test_webhook_e2e.py \
    -q --tb=short --no-header "${EXTRA_ARGS[@]}"

# Group 2 — model/unit suites (each file self-bootstraps Django)
echo "── Group 2: unit + model suites (per-file groups) ──"
for f in tests/test_pos_models.py tests/test_extra_models.py tests/test_conftest.py \
         tests/test_fusion_integration.py tests/test_ws_client.py tests/test_bolt_api.py; do
    echo "── $f ──"
    "$PY" -m pytest "$f" -q --tb=short --no-header "${EXTRA_ARGS[@]}"
done

echo ""
echo "✅ All server test groups finished"
