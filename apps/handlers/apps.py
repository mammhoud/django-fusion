import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class HandlersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.handlers"
    label = "handlers"
    verbose_name = _("Module Common Settings")

    def ready(self):
        from .startup import run_startup_checks
        run_startup_checks()

        with contextlib.suppress(ImportError):
            import apps.handlers.signals
