"""Pages app configuration for CMS Fusion."""

from django.apps import AppConfig


class PagesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "plugins.pages"
    verbose_name = "Fusion CMS Pages"
    label = "fusion_pages"

    def ready(self):
        from plugins.pages import models  # noqa: F401
        from plugins.pages import wagtail_hooks  # noqa: F401
