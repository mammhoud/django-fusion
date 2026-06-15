#!/usr/bin/env bash
# Run the centralized test suite from django-grep.
# Usage: ./scripts/libs/run_tests.sh [pytest-args]
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
GREP_DIR="$REPO_ROOT/libs/django-grep"

echo "=== django-grep centralized test suite ==="
cd "$GREP_DIR"

# Activate venv if present
if [ -f "$REPO_ROOT/libs/.venv/bin/activate" ]; then
    source "$REPO_ROOT/libs/.venv/bin/activate"
fi

exec python -m pytest tests/ "$@"
