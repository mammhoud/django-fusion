#!/usr/bin/env bash
# ============================================================================
# POS — run merged sidecar tests (pos-full + pos-solo absorbed into formint-pos)
# ============================================================================
# pos-full and pos-solo were merged into formint-pos (see the merge commit).
# Their Robyn sidecar now lives at formint-pos/sidecar/ — this wrapper runs
# the combined suite (pos-full tests + pos-solo's test_ws_client.py) from
# that single location, avoiding pytest-django conflicts with the root
# pyproject.toml (which sets DJANGO_SETTINGS_MODULE).
#
# Usage:
#   bash py/full/run.sh                    — all tests (except rust_db)
#   bash py/full/run.sh -k "test_product"  — filtered
# ============================================================================

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"  # projects/pos/
SIDECAR="$ROOT/formint-pos/sidecar"
cd "$SIDECAR"

EXTRA_ARGS=("$@")
if [ ${#EXTRA_ARGS[@]} -eq 0 ]; then
    EXTRA_ARGS=("-k" "not rust_db")
fi

echo "▸ Running merged sidecar tests from $SIDECAR"
echo "  pytest tests/ ${EXTRA_ARGS[*]}"
echo ""

# Clear DJANGO_SETTINGS_MODULE to avoid pytest-django loading root settings
unset DJANGO_SETTINGS_MODULE
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/ \
    -v --tb=short --no-header \
    "${EXTRA_ARGS[@]}"
