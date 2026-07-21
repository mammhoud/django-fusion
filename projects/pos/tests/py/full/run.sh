#!/usr/bin/env bash
# ============================================================================
# POS — run pos-full sidecar tests from their original location
# ============================================================================
# The original test files live at pos-full/sidecar/tests/ and must be run
# from that directory to avoid pytest-django conflicts with the root
# pyproject.toml (which sets DJANGO_SETTINGS_MODULE).
#
# Usage:
#   bash py/full/run.sh                    — all tests (except rust_db)
#   bash py/full/run.sh -k "test_product"  — filtered
# ============================================================================

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"  # projects/pos/
SIDECAR_FULL="$ROOT/pos-full/sidecar"
cd "$SIDECAR_FULL"

EXTRA_ARGS=("$@")
if [ ${#EXTRA_ARGS[@]} -eq 0 ]; then
    EXTRA_ARGS=("-k" "not rust_db")
fi

echo "▸ Running pos-full tests from $SIDECAR_FULL"
echo "  pytest tests/ ${EXTRA_ARGS[*]}"
echo ""

# Clear DJANGO_SETTINGS_MODULE to avoid pytest-django loading root settings
unset DJANGO_SETTINGS_MODULE
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/ \
    -v --tb=short --no-header \
    "${EXTRA_ARGS[@]}"
