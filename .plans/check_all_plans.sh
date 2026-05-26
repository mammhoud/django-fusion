#!/usr/bin/env bash
set -euo pipefail

# Scans Markdown files under this .plans folder for unchecked tasks (- [ ])
# and generates UNDONE_TASKS.md summarizing them grouped by file.

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUT_FILE="$ROOT_DIR/UNDONE_TASKS.md"

echo "# UNDONE TASKS (generated)" > "$OUT_FILE"
echo "" >> "$OUT_FILE"

TOTAL=0

while IFS= read -r file; do
  count=$(grep -c -E '^\s*-\s*\[ \]' "$file" || true)
  if [ "$count" -gt 0 ]; then
    echo "## ${file#${ROOT_DIR}/} ($count)" >> "$OUT_FILE"
    echo "" >> "$OUT_FILE"
    grep -n -E '^\s*-\s*\[ \]' "$file" | sed -E 's/^[0-9]+://; s/^\s*-\s*\[ \]\s*/- /' >> "$OUT_FILE" || true
    echo "" >> "$OUT_FILE"
    TOTAL=$((TOTAL + count))
  fi
done < <(find "$ROOT_DIR" -type f -name '*.md' | sort)

echo "Generated $OUT_FILE with $TOTAL undone tasks." >&2
exit 0
