#!/bin/bash
# =============================================================================
# Domain Drift Check — Ensures cms-fusion and precis-main domain code stays in sync
#
# The `apps/core/domain/` directory is intentionally duplicated between
# cms-fusion and precis-main. This script verifies they are identical
# and fails the build if any drift is detected.
#
# Usage:
#   ./applications/scripts/dev/check_domain_drift.sh          # check both
#   ./applications/scripts/dev/check_domain_drift.sh --quiet  # silent on success
#   ./applications/scripts/dev/check_domain_drift.sh --fix    # show diff for manual fix
# =============================================================================
set -euo pipefail

WORKSPACE="$(cd "$(dirname "$0")/../../.." && pwd)"
CMS_DOMAIN="$WORKSPACE/projects/cms-fusion/backend/apps/domain"
LMS_DOMAIN="$WORKSPACE/projects/precis-main/backend/apps/domain"

QUIET=false
SHOW_DIFF=false

for arg in "$@"; do
    case "$arg" in
        --quiet|-q) QUIET=true ;;
        --fix|-f)   SHOW_DIFF=true ;;
    esac
done

# ── Validate directories exist ───────────────────────────────────────────────
if [ ! -d "$CMS_DOMAIN" ]; then
    echo "❌ ERROR: cms-fusion domain directory not found: $CMS_DOMAIN"
    exit 2
fi
if [ ! -d "$LMS_DOMAIN" ]; then
    echo "❌ ERROR: precis-main domain directory not found: $LMS_DOMAIN"
    exit 2
fi

DRIFT_FOUND=false
ISSUES=()

# ── 1. Check for files in one project but not the other ─────────────────────
while IFS= read -r file; do
    lms_file="$LMS_DOMAIN/$file"
    if [ ! -f "$lms_file" ]; then
        DRIFT_FOUND=true
        ISSUES+=("MISSING in precis-main: $file")
    fi
done < <(cd "$CMS_DOMAIN" && find . -name '*.py' -not -path '*__pycache__*' | sort)

while IFS= read -r file; do
    cms_file="$CMS_DOMAIN/$file"
    if [ ! -f "$cms_file" ]; then
        DRIFT_FOUND=true
        ISSUES+=("MISSING in cms-fusion: $file")
    fi
done < <(cd "$LMS_DOMAIN" && find . -name '*.py' -not -path '*__pycache__*' | sort)

# ── 2. Check for content differences in files present in both ────────────────
while IFS= read -r file; do
    if [ -f "$LMS_DOMAIN/$file" ]; then
        if ! diff -q "$CMS_DOMAIN/$file" "$LMS_DOMAIN/$file" > /dev/null 2>&1; then
            DRIFT_FOUND=true
            ISSUES+=("CONTENT DRIFT: $file")
        fi
    fi
done < <(cd "$CMS_DOMAIN" && find . -name '*.py' -not -path '*__pycache__*' | sort)

# ── 3. Report results ────────────────────────────────────────────────────────
if [ "$DRIFT_FOUND" = true ]; then
    echo ""
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║  ❌ DOMAIN DRIFT DETECTED                                        ║"
    echo "║  cms-fusion and precis-main domain code has diverged!             ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "  Affected files (${#ISSUES[@]}):"
    for issue in "${ISSUES[@]}"; do
        echo "    • $issue"
    done
    echo ""
    echo "  ⚠️  apps/core/domain/ must stay identical between cms-fusion and"
    echo "  precis-main. When modifying domain code, apply changes to BOTH"
    echo "  projects before committing."
    echo ""
    echo "  To see exact differences, run:"
    echo "    diff -r projects/cms-fusion/backend/apps/domain \\"
    echo "         projects/precis-main/backend/apps/domain \\"
    echo "         -x '__pycache__' -x '*.pyc'"
    echo ""

    # Show actual diffs when --fix is passed
    if [ "$SHOW_DIFF" = true ]; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "  Detailed diff:"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        diff -r "$CMS_DOMAIN" "$LMS_DOMAIN" -x '__pycache__' -x '*.pyc' || true
        echo ""
    fi

    exit 1
fi

# ── Success ──────────────────────────────────────────────────────────────────
if [ "$QUIET" = false ]; then
    echo "  ✅ Domain drift check passed — cms-fusion and precis-main are in sync"
fi
exit 0
