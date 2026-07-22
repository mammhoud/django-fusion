#!/usr/bin/env bash
set -euo pipefail
WEBSITE="${1:-all}"
PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"

if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python"
fi

COMMON_ARGS=(../../tests/websites/test_cross_site_smoke.py --confcutdir=../../tests/websites -k "not hypothesis")

case "$WEBSITE" in
  ctc)
    "$PYTHON_BIN" -m pytest "${COMMON_ARGS[@]}" -k "ctc or shared"
    ;;
  structa)
    "$PYTHON_BIN" -m pytest "${COMMON_ARGS[@]}" -k "structa or shared"
    ;;
  vresume)
    "$PYTHON_BIN" -m pytest "${COMMON_ARGS[@]}" -k "vresume or shared"
    ;;
  all)
    "$PYTHON_BIN" -m pytest "${COMMON_ARGS[@]}"
    ;;
  *)
    echo "Usage: $0 [ctc|structa|vresume|all]" >&2
    exit 2
    ;;
esac
