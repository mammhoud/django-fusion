"""Backward-compatibility re-exports for django_fusion.site.pages.

The implementation moved to ``django_fusion.ci.pages``.
"""
from django_fusion.ci.pages import PageCatalog, TemplateRoot  # noqa: F401

__all__ = ["PageCatalog", "TemplateRoot"]
