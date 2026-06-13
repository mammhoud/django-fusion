#!/bin/bash
# Create git tags for rollback points
# Run this script before starting each phase

set -e

echo "Creating rollback point tags..."

# Phase 1
git tag rollback-phase-1-start -m "Rollback point: Before Phase 1 - Analysis and Planning"

# Phase 2
git tag rollback-phase-2-start -m "Rollback point: Before Phase 2 - django_osoul extraction"

# Phase 3
git tag rollback-phase-3-start -m "Rollback point: Before Phase 3 - django_rseal extraction"

# Phase 4
git tag rollback-phase-4-start -m "Rollback point: Before Phase 4 - django_grep extraction"

# Phase 5
git tag rollback-phase-5-start -m "Rollback point: Before Phase 5 - nawaai boundary verification"

# Phase 6
git tag rollback-phase-6-start -m "Rollback point: Before Phase 6 - Domain restructuring"

# Phase 7
git tag rollback-phase-7-start -m "Rollback point: Before Phase 7 - Project simplification"

# Phase 8
git tag rollback-phase-8-start -m "Rollback point: Before Phase 8 - Naming conventions"

# Phase 9
git tag rollback-phase-9-start -m "Rollback point: Before Phase 9 - Templates and static files"

# Phase 10
git tag rollback-phase-10-start -m "Rollback point: Before Phase 10 - Dependency alignment"

# Phase 11
git tag rollback-phase-11-start -m "Rollback point: Before Phase 11 - Code recovery and merging"

# Phase 12
git tag rollback-phase-12-start -m "Rollback point: Before Phase 12 - Parsers and serializers"

# Phase 13
git tag rollback-phase-13-start -m "Rollback point: Before Phase 13 - CI and automation"

# Phase 14
git tag rollback-phase-14-start -m "Rollback point: Before Phase 14 - Documentation"

# Phase 15
git tag rollback-phase-15-start -m "Rollback point: Before Phase 15 - Migration safety"

# Phase 16
git tag rollback-phase-16-start -m "Rollback point: Before Phase 16 - Final validation"

echo "✓ All rollback tags created successfully"
echo ""
echo "To view all tags:"
echo "  git tag -l"
echo ""
echo "To rollback to a specific phase:"
echo "  git checkout <tag>"
echo "  git reset --hard <tag>"
