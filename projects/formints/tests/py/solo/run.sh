#!/usr/bin/env bash
# ============================================================================
# POS — run merged server tests (alias for py/full — pos-solo merged)
# ============================================================================
# pos-solo was merged into formint-pos; its unique test (test_ws_client.py)
# lives with the combined suite at formint-pos/server/tests/. This wrapper is
# kept as an alias so existing CI/docs invocations keep working.
#
# Usage:
#   bash py/solo/run.sh              — all tests
#   bash py/solo/run.sh -k "product" — filtered
# ============================================================================

set -euo pipefail

exec bash "$(dirname "$0")/full/run.sh" "$@"
