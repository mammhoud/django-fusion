"""django-rseal migration helpers for crafts-ai.

This module keeps framework-agnostic package metadata and import migration
rules in ``crafts_ai``.  Django-specific runtime code should remain in the
``django_rseal`` package until it can be extracted behind explicit adapters.
"""

from .inventory import ImportRule, RSEAL_IMPORT_RULES, classify_import
from .migration import MigrationItem, migration_plan

__all__ = [
    "ImportRule",
    "MigrationItem",
    "RSEAL_IMPORT_RULES",
    "classify_import",
    "migration_plan",
]
