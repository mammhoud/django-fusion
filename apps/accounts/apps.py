import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"
    label = "accounts"
    verbose_name = _("Module Common Settings")

    def ready(self):
        from . import admin  # noqa: F401
        from .startup import run_startup_checks
        run_startup_checks()

        with contextlib.suppress(ImportError):
            import apps.accounts.signals
