"""POS Cloud — Core Django app config (domain models + fusion fragments)."""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "apps.core"
    label = "core"
    verbose_name = "POS Cloud — Branches, Orgs, Leads & Reports"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        """Register django-fusion fragments at startup.

        Sync broker handler registration lives in HandlersConfig.ready()
        (it imports apps.domain + apps.handlers, so it belongs to the
        handlers app).
        """
        from apps.handlers.fragments import tables, modals, reports, layouts, skeletons  # noqa: F401
