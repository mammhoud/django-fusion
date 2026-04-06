import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PagesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.pages"
    label = "pages"
    verbose_name = _("Landing Pages")

    def ready(self):
        with contextlib.suppress(ImportError):
            pass
            # import apps.pages.signals.default
            # import apps.pages.signals.user
