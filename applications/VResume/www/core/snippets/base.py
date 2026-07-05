<<<<<<< HEAD
"""VResume snippet compatibility imports.

Reusable Wagtail snippet behavior now lives in django-fusion. Keep this module
for existing VResume imports during migration.
"""
=======
"""Compatibility exports for reusable Wagtail snippet helpers."""
>>>>>>> d277962be99bf47e4a7459190c9bc55ed64302e0

from django_fusion.wagtail.viewsets import BaseSnippetViewSet, export_to_csv

__all__ = ["BaseSnippetViewSet", "export_to_csv"]
