"""VResume snippet compatibility imports.

Reusable Wagtail snippet behavior now lives in django-osoul. Keep this module
for existing VResume imports during migration.
"""

from django_osoul.wagtail.viewsets import BaseSnippetViewSet, export_to_csv

__all__ = ["BaseSnippetViewSet", "export_to_csv"]
