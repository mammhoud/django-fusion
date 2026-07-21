#!/usr/bin/env bash
# ============================================================================
# POS — run pos-solo sidecar tests from their original location
# ============================================================================
# Usage:
#   bash py/solo/run.sh              — all tests
#   bash py/solo/run.sh -k "product" — filtered
# ============================================================================

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"  # projects/pos/
SIDECAR_SOLO="$ROOT/pos-solo/sidecar"
cd "$SIDECAR_SOLO"

EXTRA_ARGS=("$@")

echo "▸ Running pos-solo tests from $SIDECAR_SOLO"
echo "  pytest tests/ ${EXTRA_ARGS[*]}"
echo ""

# Clear DJANGO_SETTINGS_MODULE to avoid pytest-django loading root settings
unset DJANGO_SETTINGS_MODULE
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/ \
    -v --tb=short --no-header \
    "${EXTRA_ARGS[@]}"
