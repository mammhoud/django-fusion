import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ContentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core.content"
    label = "pages"
    verbose_name = _("Content")

    def ready(self):
        with contextlib.suppress(ImportError):
            pass
            # import apps.core.content.signals.default
            # import apps.core.content.signals.user
