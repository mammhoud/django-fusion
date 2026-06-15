#!/usr/bin/env bash
# Phase 3: Move django_rseal.seeder → django_grep.seeder
# Usage: ./scripts/libs/move_seeder.sh
set -e

LIBS="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/libs"
SRC="$LIBS/django-rseal/src/django_rseal/seeder"
DST="$LIBS/django-grep/src/django_grep/seeder"

echo "=== Moving seeder: django_rseal → django_grep ==="

if [ ! -d "$SRC" ]; then
    echo "ERROR: source $SRC not found"; exit 1
fi

mkdir -p "$DST"
cp "$SRC/seeder.py"     "$DST/seeder.py"
cp "$SRC/guessers.py"   "$DST/guessers.py"
cp "$SRC/providers.py"  "$DST/providers.py"
cp "$SRC/exceptions.py" "$DST/exceptions.py"

# Fix imports inside copied files
sed -i 's/from django_rseal\.seeder/from django_grep.seeder/g' "$DST"/*.py
sed -i 's/import django_rseal\.seeder/import django_grep.seeder/g' "$DST"/*.py

# Write __init__.py
cat > "$DST/__init__.py" << 'INITEOF'
"""
django_grep.seeder
==================
Django ORM seeder — moved from django_rseal.seeder.

Provides Faker-based model seeding for test data generation.
"""
from .exceptions import SeederCommandError, SeederException
from .guessers import FieldTypeGuesser, NameGuesser
from .providers import Provider
from .seeder import ModelSeeder, Seeder

__all__ = [
    "Seeder",
    "ModelSeeder",
    "NameGuesser",
    "FieldTypeGuesser",
    "Provider",
    "SeederException",
    "SeederCommandError",
]
INITEOF

# Replace rseal seeder with deprecation shim
cat > "$SRC/__init__.py" << 'SHIMEOF'
"""Compatibility shim: seeder moved to django_grep.seeder."""
import warnings
warnings.warn(
    "django_rseal.seeder is deprecated. Use django_grep.seeder instead.",
    DeprecationWarning,
    stacklevel=2,
)
from django_grep.seeder import (  # noqa: F401, E402
    FieldTypeGuesser, ModelSeeder, NameGuesser,
    Provider, Seeder, SeederCommandError, SeederException,
)
SHIMEOF

echo "✓ Seeder moved to django_grep.seeder"
echo "✓ Shim written to django_rseal.seeder"
echo ""
echo "Next: run ./scripts/libs/run_tests.sh to verify"
