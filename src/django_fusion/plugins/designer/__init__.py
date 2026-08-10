"""Safe, schema-driven design helpers for django-fusion MCP clients.

The designer is intentionally read-only or pure-generation: it can inspect
registered components, suggest Wagtail field definitions, generate form/table
scaffolds, validate drafts, and preview registered templates. It never writes
project files or evaluates client-supplied template source.
"""

from django_fusion.plugins.designer.website import (
    designer_webapp_enhancement_plan,
    designer_website_audit,
)
from django_fusion.plugins.designer.handlers import (
    designer_component_catalog,
    designer_form_scaffold,
    designer_preview,
    designer_table_scaffold,
    designer_validate,
    designer_wagtail_field,
)

__all__ = [
    "designer_component_catalog",
    "designer_form_scaffold",
    "designer_preview",
    "designer_table_scaffold",
    "designer_validate",
    "designer_wagtail_field",
    "designer_webapp_enhancement_plan",
    "designer_website_audit",
]
