"""Compatibility shim — ``ceptor_ai.rseal`` is now ``ceptor_ai.tools.migration``.

Import from the canonical path instead::

    from ceptor_ai.tools.migration import classify_import, migration_plan
    from ceptor_ai.tools.migration import RSEAL_IMPORT_RULES, ImportRule, MigrationItem
"""
from __future__ import annotations
from ceptor_ai.tools.migration import (  # noqa: F401
    RSEAL_IMPORT_RULES,
    ImportRule,
    MigrationItem,
    classify_import,
    migration_plan,
)

__all__ = [
    "ImportRule",
    "MigrationItem",
    "RSEAL_IMPORT_RULES",
    "classify_import",
    "migration_plan",
]
