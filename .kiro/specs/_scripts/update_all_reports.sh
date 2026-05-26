#!/bin/bash
# Update All Reports Script
# Runs all analysis and verification scripts to update reports

set -e  # Exit on error

echo "========================================="
echo "UPDATING ALL SPEC REPORTS"
echo "========================================="
echo ""

# Get current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"

echo "📊 Step 1: Running spec analysis..."
cd /root/site || exit 1
python3 "$PARENT_DIR/analyze_specs.py"
echo "✅ Spec analysis complete"
echo ""

echo "🔍 Step 2: Verifying task completion..."
cd /root/site || exit 1
python3 "$PARENT_DIR/scripts/verify_task_completion.py"
echo "✅ Task verification complete"
echo ""

echo "📋 Step 3: Checking for missing files..."
# Count missing design.md files
MISSING_DESIGN=$(grep -c "❌ design.md" "$PARENT_DIR/reports/verification_report.md" || true)
if [ "$MISSING_DESIGN" -gt 0 ]; then
    echo "⚠️  Found $MISSING_DESIGN spec(s) missing design.md"
    grep -B2 "❌ design.md" "$PARENT_DIR/reports/verification_report.md" || true
else
    echo "✅ All specs have design.md"
fi
echo ""

echo "📈 Step 4: Generating summary statistics..."
TOTAL_SPECS=$(grep -c "^\`" "$PARENT_DIR/reports/status_report.md" | head -1 || true)
COMPLETED_SPECS=$(grep -c "✅" "$PARENT_DIR/reports/status_report.md" || true)
IN_PROGRESS_SPECS=$(grep -c "🔄" "$PARENT_DIR/reports/status_report.md" || true)
NOT_STARTED_SPECS=$(grep -c "⏳" "$PARENT_DIR/reports/status_report.md" || true)

echo "📊 Summary Statistics:"
echo "  Total Specs: $TOTAL_SPECS"
echo "  ✅ Completed: $COMPLETED_SPECS"
echo "  🔄 In Progress: $IN_PROGRESS_SPECS"
echo "  ⏳ Not Started: $NOT_STARTED_SPECS"
echo ""

echo "📁 Step 5: Checking directory structure..."
echo "Current organization:"
find "$PARENT_DIR" -type f -name "*.md" -o -name "*.py" -o -name "*.sh" -o -name "*.json" | \
    sort | \
    sed "s|$PARENT_DIR/||" | \
    while read -r file; do
        echo "  📄 $file"
    done
echo ""

echo "📄 Step 6: Listing generated reports..."
find "$PARENT_DIR/reports" -type f -name "*.md" -o -name "*.json" | \
    sort | \
    sed "s|$PARENT_DIR/||" | \
    while read -r file; do
        echo "  📊 $file"
    done
echo ""

echo "========================================="
echo "UPDATE COMPLETE"
echo "========================================="
echo ""
echo "📋 Generated Reports:"
echo "  1. $PARENT_DIR/reports/status_report.md"
echo "  2. $PARENT_DIR/reports/verification_report.md"
echo "  3. $PARENT_DIR/reports/specs_pydoc.md"
echo "  4. $PARENT_DIR/reports/specs_status.json"
echo ""
echo "🚀 Next steps:"
echo "  1. Review the reports above"
echo "  2. Address any issues found"
echo "  3. Run organize_specs.py if needed"
echo "  4. Update documentation as necessary"
echo ""
echo "💡 Tip: Run this script regularly to keep reports up to date!"
