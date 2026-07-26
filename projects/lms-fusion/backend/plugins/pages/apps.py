"""
Pages app configuration — registers FusionPage models for auto-discovery.

When this app is ready, it creates migrations for any new page models and
wires them into Wagtail's page tree.
"""

from django.apps import AppConfig


class PagesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "plugins.pages"
    verbose_name = "Fusion Pages"
    label = "pages"

    def ready(self):
        # Import models to register with Wagtail
        from plugins.pages import models  # noqa: F401

        # Register Wagtail hooks
        from plugins.pages import wagtail_hooks  # noqa: F401
