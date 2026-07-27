"""Pages app configuration for CMS Fusion."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PagesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.pages.pages"
    verbose_name = _("Fusion CMS Pages")
    label = "fusion_pages"

    def ready(self):
        from apps.pages.pages import models  # noqa: F401
        from apps.pages.pages import wagtail_hooks  # noqa: F401
