from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.lms'
    label = "alliance"
    verbose_name = _("LMS Module")

    def ready(self):
        """Register signals when app is ready."""
        import www.apps.lms.signals  # noqa: F401

        from . import admin  # noqa: F401
