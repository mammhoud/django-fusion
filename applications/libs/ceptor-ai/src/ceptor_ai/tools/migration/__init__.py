"""Import-path migration utilities.

Provides rule-based classification of legacy import paths and generates
step-by-step migration plans for moving symbols to canonical locations.

Usage::

    from ceptor_ai.tools.migration import classify_import, migration_plan
    from ceptor_ai.tools.migration import RSEAL_IMPORT_RULES, ImportRule, MigrationItem
"""

from .inventory import RSEAL_IMPORT_RULES, ImportRule, classify_import
from .plan import MigrationItem, migration_plan

__all__ = [
    "ImportRule",
    "MigrationItem",
    "RSEAL_IMPORT_RULES",
    "classify_import",
    "migration_plan",
]
