"""CTC Research — API Schema app configuration (Pydantic).

Single source of truth for API contracts between
ctc-research (django-bolt) and next-LMS (Next.js).
"""

from django.apps import AppConfig


class SchemaConfig(AppConfig):
    name = "www.schemas"
    label = "schemas"
    verbose_name = "CTC Research API Schemas"
    default_auto_field = "django.db.models.BigAutoField"
