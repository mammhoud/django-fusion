#!/bin/bash
# Simple script to manage organized specs

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CATEGORIES=("auth" "docs" "integration" "fixes" "modernization" "features")

print_help() {
    echo "Spec Management Script"
    echo "======================"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  list [category]    List all specs or specs in a category"
    echo "  check              Check for duplicates and suggest categories"
    echo "  stats              Show statistics about specs"
    echo "  help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 list            # List all specs"
    echo "  $0 list auth       # List auth specs"
    echo "  $0 check           # Check for duplicates"
    echo "  $0 stats           # Show statistics"
}

list_specs() {
    local category="$1"

    if [[ -n "$category" ]]; then
        if [[ ! -d "$BASE_DIR/$category" ]]; then
            echo "Error: Category '$category' not found"
            echo "Available categories: ${CATEGORIES[*]}"
            return 1
        fi

        echo "Specs in category '$category':"
        echo "=============================="
        find "$BASE_DIR/$category" -maxdepth 1 -type d -name "[!.]*" | while read -r dir; do
            if [[ "$dir" != "$BASE_DIR/$category" ]]; then
                spec_name=$(basename "$dir")
                echo "  • $spec_name"
            fi
        done
    else
        echo "All Specs by Category:"
        echo "======================"
        for cat in "${CATEGORIES[@]}"; do
            if [[ -d "$BASE_DIR/$cat" ]]; then
                count=$(find "$BASE_DIR/$cat" -maxdepth 1 -type d -name "[!.]*" | grep -v "^$BASE_DIR/$cat$" | wc -l)
                echo ""
                echo "$cat ($count specs):"
                find "$BASE_DIR/$cat" -maxdepth 1 -type d -name "[!.]*" | while read -r dir; do
                    if [[ "$dir" != "$BASE_DIR/$cat" ]]; then
                        spec_name=$(basename "$dir")
                        echo "  • $spec_name"
                    fi
                done
            fi
        done
    fi
}

check_duplicates() {
    echo "Running duplicate check..."
    echo ""
    python3 "$BASE_DIR/check-duplicates.py"
}

show_stats() {
    echo "Spec Statistics"
    echo "================"
    echo ""

    total_specs=0
    total_files=0

    for cat in "${CATEGORIES[@]}"; do
        if [[ -d "$BASE_DIR/$cat" ]]; then
            spec_count=$(find "$BASE_DIR/$cat" -maxdepth 1 -type d -name "[!.]*" | grep -v "^$BASE_DIR/$cat$" | wc -l)
            file_count=$(find "$BASE_DIR/$cat" -type f \( -name "*.md" -o -name "*.py" -o -name "*.sh" -o -name "*.json" \) | wc -l)

            echo "$cat:"
            echo "  • Specs: $spec_count"
            echo "  • Files: $file_count"

            total_specs=$((total_specs + spec_count))
            total_files=$((total_files + file_count))
        fi
    done

    echo ""
    echo "Totals:"
    echo "  • Categories: ${#CATEGORIES[@]}"
    echo "  • Specs: $total_specs"
    echo "  • Files: $total_files"
    echo ""

    # Check for incomplete specs
    echo "Incomplete Specs (missing key files):"
    incomplete_found=0
    for cat in "${CATEGORIES[@]}"; do
        if [[ -d "$BASE_DIR/$cat" ]]; then
            find "$BASE_DIR/$cat" -maxdepth 1 -type d -name "[!.]*" | while read -r dir; do
                if [[ "$dir" != "$BASE_DIR/$cat" ]]; then
                    spec_name=$(basename "$dir")

                    # Check for key files
                    has_requirements=0
                    has_design=0
                    has_tasks=0

                    [[ -f "$dir/requirements.md" ]] && has_requirements=1
                    [[ -f "$dir/design.md" ]] && has_design=1
                    [[ -f "$dir/tasks.md" ]] && has_tasks=1
                    [[ -f "$dir/bugfix.md" ]] && has_requirements=1  # bugfix.md serves as requirements

                    if [[ $has_requirements -eq 0 ]] || [[ $has_design -eq 0 ]] || [[ $has_tasks -eq 0 ]]; then
                        echo "  • $cat/$spec_name"
                        incomplete_found=1
                    fi
                fi
            done
        fi
    done

    if [[ $incomplete_found -eq 0 ]]; then
        echo "  None - all specs appear complete! ✅"
    fi
}

# Main command handling
case "${1:-help}" in
    list)
        list_specs "${2:-}"
        ;;
    check)
        check_duplicates
        ;;
    stats)
        show_stats
        ;;
    help|--help|-h)
        print_help
        ;;
    *)
        echo "Unknown command: $1"
        echo ""
        print_help
        exit 1
        ;;
esac
