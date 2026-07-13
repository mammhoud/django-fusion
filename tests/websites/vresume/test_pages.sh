#!/bin/bash
# Backward-compatible shim. The canonical VResume page test lives in the
# workspace test scripts so it can be invoked with `make -C tests/scripts vresume-pages`.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
exec "$WORKSPACE_ROOT/tests/scripts/test_vresume_pages.sh" "$@"
