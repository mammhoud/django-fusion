#!/usr/bin/env bash
# =============================================================================
# Structa Cloud — Database Restore Script
# =============================================================================
# Restores PostgreSQL databases from SQL dumps created by:
#   docker exec postgres pg_dump -U admin -d <db> --clean --if-exists
#
# Usage:
#   bash scripts/restore_databases.sh <backup-dir>
#   bash scripts/restore_databases.sh <backup-dir> --dry-run
#   bash scripts/restore_databases.sh <backup-dir> --force     # skip confirmation
#   bash scripts/restore_databases.sh --latest                  # auto-find latest
#
# Example:
#   bash scripts/restore_databases.sh backups/20260703_000236/
# =============================================================================

set -euo pipefail

# ── Configuration ───────────────────────────────────────────────────────────

# Map backup filenames to target database names
declare -A DB_MAP=(
    ["ctc_db.sql"]="db_ctc"
    ["lms_db.sql"]="db_structa"
    ["vresume_db.sql"]="vresume"
)

# PostgreSQL container and credentials
PG_CONTAINER="${PG_CONTAINER:-postgres}"
PG_USER="${PG_USER:-admin}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ── Help ────────────────────────────────────────────────────────────────────

usage() {
    cat <<EOF
Usage: $(basename "$0") [OPTIONS] <BACKUP_DIR>

Restore PostgreSQL databases from pg_dump SQL files.

OPTIONS:
  --dry-run     Show what would be restored without actually restoring
  --force       Skip confirmation prompt
  --latest      Auto-detect the latest backup directory in backups/
  -h, --help    Show this help message

DATABASE MAPPING:
  ctc_db.sql      → db_ctc       (CTC Research)
  lms_db.sql      → db_structa   (LMS Demo / Structa)
  vresume_db.sql  → vresume      (VResume)

ENVIRONMENT:
  PG_CONTAINER    PostgreSQL container name (default: postgres)
  PG_USER         PostgreSQL user (default: admin)
EOF
    exit "${1:-0}"
}

# ── Argument Parsing ────────────────────────────────────────────────────────

DRY_RUN=false
FORCE=false
BACKUP_DIR=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --latest)
            BACKUP_DIR=$(ls -td backups/*/ 2>/dev/null | head -1)
            if [[ -z "$BACKUP_DIR" ]]; then
                echo -e "${RED}Error: No backup directories found in backups/${NC}"
                exit 1
            fi
            shift
            ;;
        -h|--help)
            usage 0
            ;;
        -*)
            echo -e "${RED}Unknown option: $1${NC}"
            usage 1
            ;;
        *)
            BACKUP_DIR="$1"
            shift
            ;;
    esac
done

if [[ -z "$BACKUP_DIR" ]]; then
    echo -e "${RED}Error: No backup directory specified.${NC}"
    echo "Use --latest to auto-detect, or provide a path."
    usage 1
fi

if [[ ! -d "$BACKUP_DIR" ]]; then
    echo -e "${RED}Error: Backup directory not found: $BACKUP_DIR${NC}"
    exit 1
fi

# ── Validation ──────────────────────────────────────────────────────────────

echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo -e "${CYAN}  Structa Cloud — Database Restore${NC}"
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo ""
echo "Backup directory: $BACKUP_DIR"
echo "PostgreSQL container: $PG_CONTAINER"
echo "PostgreSQL user: $PG_USER"
echo ""

# Check that the PostgreSQL container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${PG_CONTAINER}$"; then
    echo -e "${RED}Error: PostgreSQL container '$PG_CONTAINER' is not running.${NC}"
    echo "Running containers:"
    docker ps --format '  {{.Names}}' 2>/dev/null || echo "  (none)"
    exit 1
fi

# Check each backup file exists
MISSING_FILES=()
for sql_file in "${!DB_MAP[@]}"; do
    if [[ ! -f "$BACKUP_DIR/$sql_file" ]]; then
        MISSING_FILES+=("$sql_file")
    fi
done

if [[ ${#MISSING_FILES[@]} -gt 0 ]]; then
    echo -e "${YELLOW}Warning: Missing backup files:${NC}"
    for f in "${MISSING_FILES[@]}"; do
        echo "  - $f"
    done
    echo ""
fi

# Verify target databases exist
echo "Checking target databases..."
for sql_file in "${!DB_MAP[@]}"; do
    target_db="${DB_MAP[$sql_file]}"
    if docker exec "$PG_CONTAINER" psql -U "$PG_USER" -lqt 2>/dev/null | cut -d '|' -f 1 | grep -qw "$target_db"; then
        echo -e "  ${GREEN}✓${NC} $target_db exists"
    else
        echo -e "  ${YELLOW}⚠${NC} $target_db does NOT exist (will be created during restore)"
    fi
done
echo ""

# ── Confirmation ────────────────────────────────────────────────────────────

if [[ "$DRY_RUN" == true ]]; then
    echo -e "${YELLOW}╔═══════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║  DRY RUN — no changes will be made       ║${NC}"
    echo -e "${YELLOW}╚═══════════════════════════════════════════╝${NC}"
    echo ""
    for sql_file in "${!DB_MAP[@]}"; do
        target_db="${DB_MAP[$sql_file]}"
        if [[ -f "$BACKUP_DIR/$sql_file" ]]; then
            size=$(du -h "$BACKUP_DIR/$sql_file" | cut -f1)
            lines=$(wc -l < "$BACKUP_DIR/$sql_file")
            echo "  Would restore: $sql_file ($size, $lines lines) → $target_db"
        fi
    done
    echo ""
    echo -e "${YELLOW}Dry run complete. Remove --dry-run to execute.${NC}"
    exit 0
fi

if [[ "$FORCE" != true ]]; then
    echo -e "${RED}╔═══════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  WARNING: This will OVERWRITE data!      ║${NC}"
    echo -e "${RED}╚═══════════════════════════════════════════╝${NC}"
    echo ""
    echo "The following restore operations will be performed:"
    for sql_file in "${!DB_MAP[@]}"; do
        target_db="${DB_MAP[$sql_file]}"
        if [[ -f "$BACKUP_DIR/$sql_file" ]]; then
            size=$(du -h "$BACKUP_DIR/$sql_file" | cut -f1)
            echo "  $sql_file ($size) → $target_db"
        fi
    done
    echo ""
    read -r -p "Type 'yes' to confirm restore: " CONFIRM
    if [[ "$CONFIRM" != "yes" ]]; then
        echo "Restore cancelled."
        exit 0
    fi
    echo ""
fi

# ── Restore ─────────────────────────────────────────────────────────────────

echo -e "${CYAN}Starting restore...${NC}"
echo ""

RESTORE_OK=0
RESTORE_FAIL=0

for sql_file in "${!DB_MAP[@]}"; do
    target_db="${DB_MAP[$sql_file]}"

    if [[ ! -f "$BACKUP_DIR/$sql_file" ]]; then
        echo -e "  ${YELLOW}SKIP${NC}  $sql_file — file not found"
        continue
    fi

    size=$(du -h "$BACKUP_DIR/$sql_file" | cut -f1)
    echo -n "  Restoring $sql_file ($size) → $target_db ... "

    # Create a temp file without the \restrict token
    # (pg_dump includes a custom security token that psql can't parse)
    TEMP_SQL=$(mktemp /tmp/restore_XXXXXX.sql)

    # Strip \restrict and \unrestrict lines (custom pg_dump security tokens
    # that standard psql cannot parse; grep needs \\ for literal backslash)
    grep -v '^\\restrict \|^\\unrestrict ' "$BACKUP_DIR/$sql_file" > "$TEMP_SQL"

    # Restore into the target database, capturing stderr for error reporting
    ERROR_LOG=$(mktemp /tmp/restore_error_XXXXXX.log)
    if docker exec -i "$PG_CONTAINER" psql -U "$PG_USER" -d "$target_db" \
        -v ON_ERROR_STOP=1 < "$TEMP_SQL" > /dev/null 2>"$ERROR_LOG"; then
        echo -e "${GREEN}OK${NC}"
        RESTORE_OK=$((RESTORE_OK + 1))
    else
        echo -e "${RED}FAILED${NC}"
        RESTORE_FAIL=$((RESTORE_FAIL + 1))
        # Show the error from the captured log
        echo -e "  ${RED}Error details:${NC}"
        tail -5 "$ERROR_LOG"
    fi

    rm -f "$TEMP_SQL" "$ERROR_LOG"
done

echo ""
echo -e "${CYAN}───────────────────────────────────────────${NC}"
echo -e "  ${GREEN}Restored: $RESTORE_OK${NC}"
if [[ $RESTORE_FAIL -gt 0 ]]; then
    echo -e "  ${RED}Failed: $RESTORE_FAIL${NC}"
fi
echo -e "${CYAN}───────────────────────────────────────────${NC}"

# ── Verify ──────────────────────────────────────────────────────────────────

echo ""
echo "Verifying restored databases..."
for sql_file in "${!DB_MAP[@]}"; do
    target_db="${DB_MAP[$sql_file]}"
    if [[ -f "$BACKUP_DIR/$sql_file" ]]; then
        table_count=$(docker exec "$PG_CONTAINER" psql -U "$PG_USER" -d "$target_db" -tAc \
            "SELECT count(*) FROM pg_stat_user_tables" 2>/dev/null || echo "0")
        echo "  $target_db: $table_count tables"
    fi
done

if [[ $RESTORE_FAIL -gt 0 ]]; then
    echo ""
    echo -e "${RED}Some restores failed. Check the errors above.${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Restore complete.${NC}"
