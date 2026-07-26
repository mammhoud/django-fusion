import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "plugins.accounts"
    label = "accounts"
    verbose_name = _("Module Common Settings")

    def ready(self):
        from . import admin  # noqa: F401
        from .startup import run_startup_checks
        run_startup_checks()

        # Registration signals (merged from plugins.accounts.registration)
        from . import signals  # noqa: F401

        # Registration admin (user admin override)
        from .admin.registration import register_user_admin
        register_user_admin()

        with contextlib.suppress(ImportError):
            import www.apps.accounts.signals
