#!/usr/bin/env bash
# Phase 3: Move ceptor_ai.seeder → django_fusion.seeder
# Usage: ./scripts/libs/move_seeder.sh
set -e

LIBS="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/libs"
SRC="$LIBS/ceptor-ai/src/ceptor_ai/seeder"
DST="$LIBS/django-fusion/src/django_fusion/seeder"

echo "=== Moving seeder: ceptor_ai → django_fusion ==="

if [ ! -d "$SRC" ]; then
    echo "ERROR: source $SRC not found"; exit 1
fi

mkdir -p "$DST"
cp "$SRC/seeder.py"     "$DST/seeder.py"
cp "$SRC/guessers.py"   "$DST/guessers.py"
cp "$SRC/providers.py"  "$DST/providers.py"
cp "$SRC/exceptions.py" "$DST/exceptions.py"

# Fix imports inside copied files
sed -i 's/from ceptor_ai\.seeder/from django_fusion.seeder/g' "$DST"/*.py
sed -i 's/import ceptor_ai\.seeder/import django_fusion.seeder/g' "$DST"/*.py

# Write __init__.py
cat > "$DST/__init__.py" << 'INITEOF'
"""
django_fusion.seeder
==================
Django ORM seeder — moved from ceptor_ai.seeder.

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
"""Compatibility shim: seeder moved to django_fusion.seeder."""
import warnings
warnings.warn(
    "ceptor_ai.seeder is deprecated. Use django_fusion.seeder instead.",
    DeprecationWarning,
    stacklevel=2,
)
from django_fusion.seeder import (  # noqa: F401, E402
    FieldTypeGuesser, ModelSeeder, NameGuesser,
    Provider, Seeder, SeederCommandError, SeederException,
)
SHIMEOF

echo "✓ Seeder moved to django_fusion.seeder"
echo "✓ Shim written to ceptor_ai.seeder"
echo ""
echo "Next: run ./scripts/libs/run_tests.sh to verify"
