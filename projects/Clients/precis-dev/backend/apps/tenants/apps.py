"""Default config for the tenants app.

Wires the ``post_save`` signal so provisioning fires when a registration
is approved via the Django admin."""

from django.apps import AppConfig


class TenantsConfig(AppConfig):
    name = "apps.tenants"
    default_auto_field = "django.db.models.BigAutoField"
    verbose_name = "Tenants"

    def ready(self):
        from . import signals  # noqa: F401 — register post_save handler