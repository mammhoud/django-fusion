import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AppsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    label = "apps_core"
    verbose_name = _("Module Common Settings")

    def ready(self):
        with contextlib.suppress(ImportError):
            import apps.core.signals  # noqa: F401

