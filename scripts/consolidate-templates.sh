#!/bin/bash
# Template Consolidation Script
# Merges all templates from packages/ui and sites into assets/templates/generic
# Then deletes duplicates and old locations

set -e

WORKSPACE_ROOT="$(pwd)"
TEMP_DIR="/tmp/templates_consolidated_$$"
FINAL_DIR="$WORKSPACE_ROOT/assets/templates/generic"
BACKUP_DIR="$WORKSPACE_ROOT/backups/templates_$(date +%Y%m%d_%H%M%S)"

echo "=========================================="
echo "Template Consolidation Script"
echo "=========================================="
echo "Workspace Root: $WORKSPACE_ROOT"
echo "Temp Dir: $TEMP_DIR"
echo "Final Dir: $FINAL_DIR"
echo ""

# Create directories
mkdir -p "$TEMP_DIR"
mkdir -p "$FINAL_DIR"
mkdir -p "$BACKUP_DIR"

echo "[1/6] Backing up existing templates..."
if [ -d "$FINAL_DIR" ]; then
    cp -r "$FINAL_DIR"/* "$BACKUP_DIR/" 2>/dev/null || true
    echo "✓ Backup created: $BACKUP_DIR"
else
    echo "ℹ No existing templates to backup"
fi

echo ""
echo "[2/6] Collecting templates from packages/ui..."
PACKAGE_SOURCES=(
    "packages/ui/notifications"
    "packages/ui/modals"
    "packages/ui/forms"
)

for source in "${PACKAGE_SOURCES[@]}"; do
    if [ -d "$source" ]; then
        echo "  ✓ Copying: $source"
        cp -r "$source"/* "$TEMP_DIR/" 2>/dev/null || true
    else
        echo "  ℹ Not found: $source"
    fi
done

echo ""
echo "[3/6] Collecting templates from site-specific directories..."
SITE_SOURCES=(
    "ctc-research/assets/templates/generic"
    "lms-demo/assets/templates/generic"
    "VResume/assets/templates/generic"
)

for source in "${SITE_SOURCES[@]}"; do
    if [ -d "$source" ]; then
        echo "  ✓ Copying: $source"
        cp -r "$source"/* "$TEMP_DIR/" 2>/dev/null || true
    else
        echo "  ℹ Not found: $source"
    fi
done

echo ""
echo "[4/6] Analyzing for duplicates..."

# Find and report duplicates
DUPLICATE_COUNT=0
declare -A FILE_HASHES

cd "$TEMP_DIR"
for file in $(find . -name "*.html" -type f); do
    HASH=$(md5sum "$file" | awk '{print $1}')
    SHORT_NAME=$(basename "$file")
    
    if [[ -v FILE_HASHES[$HASH] ]]; then
        echo "  ⚠ Duplicate found: $file (same as ${FILE_HASHES[$HASH]})"
        DUPLICATE_COUNT=$((DUPLICATE_COUNT + 1))
        rm -f "$file"
    else
        FILE_HASHES[$HASH]="$file"
    fi
done

echo "  Total duplicates removed: $DUPLICATE_COUNT"

echo ""
echo "[5/6] Finalizing template directory..."
cd "$WORKSPACE_ROOT"

# Clear final directory
rm -rf "$FINAL_DIR"/*

# Copy consolidated templates
cp -r "$TEMP_DIR"/* "$FINAL_DIR/" 2>/dev/null || true

echo "  ✓ Templates consolidated to: $FINAL_DIR"
echo "  Template count: $(find $FINAL_DIR -name "*.html" | wc -l) files"

echo ""
echo "[6/6] Cleaning up..."

# List files in final directory
echo "  Files in $FINAL_DIR:"
find "$FINAL_DIR" -name "*.html" | sort | sed 's/^/    - /'

# Clean temp directory
rm -rf "$TEMP_DIR"
echo "  ✓ Temporary directory cleaned"

echo ""
echo "=========================================="
echo "✓ Template Consolidation Complete!"
echo "=========================================="
echo ""
echo "Summary:"
echo "  - Workspace Location: $WORKSPACE_ROOT/assets/templates/generic"
echo "  - Backup Created: $BACKUP_DIR"
echo "  - Duplicates Removed: $DUPLICATE_COUNT"
echo ""
echo "Next Steps:"
echo "  1. Review consolidated templates"
echo "  2. Run: make clean-old-templates"
echo "  3. Run: make test"
echo "  4. Verify: http://localhost:8000"
echo ""
