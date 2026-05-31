#!/usr/bin/env bash
set -euo pipefail
WEBSITE="${1:-all}"
PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"

if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python"
fi

COMMON_ARGS=(tests -k "not hypothesis" --ignore=tests/apps/accounts/registration --ignore=tests/unit/accounts/registration)

case "$WEBSITE" in
  ctc)
    "$PYTHON_BIN" -m pytest "${COMMON_ARGS[@]}" -k "ctc and not hypothesis"
    ;;
  structa)
    "$PYTHON_BIN" -m pytest "${COMMON_ARGS[@]}" -k "structa and not hypothesis"
    ;;
  all)
    "$PYTHON_BIN" -m pytest "${COMMON_ARGS[@]}"
    ;;
  *)
    echo "Usage: $0 [ctc|structa|all]" >&2
    exit 2
    ;;
esac
