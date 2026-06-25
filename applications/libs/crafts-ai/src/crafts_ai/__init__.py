"""Merged AI/MCP/customizer toolkit for structa.cloud."""

from .cli import package_info
from .rseal import ImportRule, MigrationItem, RSEAL_IMPORT_RULES, classify_import, migration_plan

__all__ = [
    "ImportRule",
    "MigrationItem",
    "RSEAL_IMPORT_RULES",
    "classify_import",
    "migration_plan",
    "package_info",
]
__version__ = "0.1.0"
