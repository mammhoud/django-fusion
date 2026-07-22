"""POS Cloud — Core Django app config with django-fusion fragment auto-registration."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "core"
    label = "core"
    verbose_name = "POS Cloud — Branches, Orgs, Leads & Reports"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        """Register django-fusion fragments at startup so
        {% comp "core.tables.*" %} works in templates."""
        from .fragments import tables, modals, reports, layouts, skeletons  # noqa: F401
