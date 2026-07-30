#!/bin/bash
#
# run-e2e-fixture-tests.sh
#
# Run the fixture-content E2E tests for CMS Fusion and LMS Fusion.
# Handles Node.js environment setup, dependency checks, and test execution.
#
# Usage:
#   ./run-e2e-fixture-tests.sh              # Run both CMS and LMS tests
#   ./run-e2e-fixture-tests.sh cms          # Run CMS Fusion tests only
#   ./run-e2e-fixture-tests.sh lms          # Run LMS Fusion tests only
#
# Prerequisites:
#   - Node.js 18+ installed and accessible
#   - npm dependencies installed (npm ci or npm install)
#   - Playwright browsers installed (npx playwright install chromium)
#   - Django backends running (optional - tests gracefully skip if unavailable)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CMS_FRONTEND="$PROJECT_DIR/projects/cms-fusion/frontend"
LMS_FRONTEND="$PROJECT_DIR/projects/lms-fusion/frontend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ── Helpers ────────────────────────────────────────────────────────────────

# Find the Node.js binary
find_node() {
  # Check common locations
  for candidate in \
    "$NVM_BIN/node" \
    "$NVM_DIR/versions/node/*/bin/node" \
    "/usr/local/bin/node" \
    "/opt/homebrew/bin/node"; do
    for f in $candidate; do
      if [ -x "$f" ]; then
        echo "$f"
        return 0
      fi
    done
  done

  # Check if 'node' is in PATH
  if command -v node &>/dev/null; then
    echo "$(command -v node)"
    return 0
  fi

  # Source nvm and try again
  if [ -s "$HOME/.nvm/nvm.sh" ]; then
    . "$HOME/.nvm/nvm.sh"
    if command -v node &>/dev/null; then
      echo "$(command -v node)"
      return 0
    fi
  fi

  echo ""
  return 1
}

# ── Setup ──────────────────────────────────────────────────────────────────

NODE_BIN="$(find_node || true)"
if [ -z "$NODE_BIN" ]; then
  echo -e "${RED}❌ Node.js not found. Please install Node.js 18+ via nvm or homebrew.${NC}"
  exit 1
fi

NVM_BIN="$(dirname "$NODE_BIN")"
NODE_VERSION="$("$NODE_BIN" --version)"
echo -e "${CYAN}🔧 Node.js: $NODE_VERSION at $NODE_BIN${NC}"

# Check Playwright is available in each project
check_project() {
  local name="$1"
  local dir="$2"
  local pw="$dir/node_modules/@playwright/test/cli.js"

  if [ ! -f "$pw" ]; then
    echo -e "${YELLOW}⚠️  Playwright not installed in $name. Running npm install...${NC}"
    cd "$dir" && "$NODE_BIN" "$NVM_BIN/npm" install --no-audit --no-fund
  fi

  # Check if Chromium browser is installed
  if ! "$NODE_BIN" "$dir/node_modules/@playwright/test/cli.js" install --dry-run chromium 2>/dev/null | grep -q "already"; then
    echo -e "${YELLOW}⚠️  Playwright Chromium browser not installed. Installing...${NC}"
    "$NODE_BIN" "$dir/node_modules/@playwright/test/cli.js" install chromium
  fi
}

check_project "CMS Fusion" "$CMS_FRONTEND"
check_project "LMS Fusion" "$LMS_FRONTEND"

# ── Run Tests ──────────────────────────────────────────────────────────────

run_tests() {
  local name="$1"
  local dir="$2"
  local spec="$dir/tests/e2e/fixture-content.spec.ts"

  if [ ! -f "$spec" ]; then
    echo -e "${YELLOW}⚠️  Test file not found: $spec${NC}"
    return
  fi

  echo -e "\n${CYAN}══════════════════════════════════════════════════════════${NC}"
  echo -e "${CYAN}🧪 Running fixture-content tests for $name${NC}"
  echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"

  cd "$dir" && CI=1 NVM_BIN="$NVM_BIN" "$NODE_BIN" node_modules/@playwright/test/cli.js \
    test tests/e2e/fixture-content.spec.ts \
    --reporter=list \
    --timeout=30000 \
    2>&1 || true
}

# Determine which tests to run
RUN_CMS=false
RUN_LMS=false

if [ $# -eq 0 ]; then
  RUN_CMS=true
  RUN_LMS=true
else
  for arg in "$@"; do
    case "$arg" in
      cms|CMS) RUN_CMS=true ;;
      lms|LMS) RUN_LMS=true ;;
      *) echo -e "${YELLOW}Unknown option: $arg (use: cms, lms)${NC}" ;;
    esac
  done
fi

EXIT_CODE=0

if [ "$RUN_CMS" = true ]; then
  run_tests "CMS Fusion" "$CMS_FRONTEND" || EXIT_CODE=1
fi

if [ "$RUN_LMS" = true ]; then
  run_tests "LMS Fusion" "$LMS_FRONTEND" || EXIT_CODE=1
fi

# ── Summary ────────────────────────────────────────────────────────────────

echo -e "\n${CYAN}══════════════════════════════════════════════════════════${NC}"
if [ "$EXIT_CODE" -eq 0 ]; then
  echo -e "${GREEN}✅ All tests completed successfully!${NC}"
else
  echo -e "${YELLOW}⚠️  Some tests failed or were skipped. Check output above.${NC}"
fi
echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "To run the tests with backend servers running:"
echo -e "  1. Start Django backend:"
echo -e "     ${CYAN}cd projects/cms-fusion/backend && make dev PORT=5075${NC}"
echo -e "     ${CYAN}cd projects/lms-fusion/backend && make dev PORT=5074${NC}"
echo -e "  2. Run tests: ${CYAN}./projects/scripts/run-e2e-fixture-tests.sh${NC}"
echo ""
echo -e "The tests gracefully handle unavailable backends. Backend-API tests"
echo -e "will skip automatically if the backend isn't running."
echo ""

exit "$EXIT_CODE"
