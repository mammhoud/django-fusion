#!/usr/bin/env bash
# ============================================================================
# POS — run formint-pos backend tests from their original location
# ============================================================================
# formint-pos is the merged package (pos-full + pos-solo). Its backend uses
# Django's test runner (Django Ninja API + Unfold admin + HTMX fragments).
#
# Usage:
#   bash py/formint/run.sh                    — all formint tests
#   bash py/formint/run.sh -v 2               — verbose
#   bash py/formint/run.sh --tag=admin        — filtered via manage.py test
# ============================================================================

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"  # projects/pos/
BACKEND="$ROOT/formint-pos/backend"

if [ ! -d "$BACKEND/.venv" ]; then
    echo "✗ formint-pos backend venv not found at $BACKEND/.venv"
    echo "  Create it first:"
    echo "    cd $BACKEND && python3 -m venv .venv && . .venv/bin/activate && pip install -e ."
    exit 1
fi

cd "$BACKEND"

EXTRA_ARGS=("$@")
if [ ${#EXTRA_ARGS[@]} -eq 0 ]; then
    EXTRA_ARGS=("-v" "1")
fi

echo "▸ Running formint-pos tests from $BACKEND"
echo "  manage.py test formint ${EXTRA_ARGS[*]}"
echo ""

# Clear DJANGO_SETTINGS_MODULE so only config.settings is used
unset DJANGO_SETTINGS_MODULE
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python3 manage.py test formint "${EXTRA_ARGS[@]}"
