import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ProfileConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.profile"
    label = "profile"
    verbose_name = _("Profile")

    def ready(self):
        from . import signals  # noqa: F401

        with contextlib.suppress(ImportError):
            import www.apps.profile.signals
