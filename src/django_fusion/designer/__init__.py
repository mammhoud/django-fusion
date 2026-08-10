"""Backward-compatibility shim — new code should import from django_fusion.plugins.designer."""

from django_fusion.plugins.designer import (
    designer_component_catalog,
    designer_form_scaffold,
    designer_preview,
    designer_table_scaffold,
    designer_validate,
    designer_wagtail_field,
    designer_webapp_enhancement_plan,
    designer_website_audit,
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
