from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'plugins.lms'
    label = "lms"
    verbose_name = _("LMS Module")

    def ready(self):
        """Register signals when app is ready."""
        try:
            import plugins.lms.signals  # noqa: F401
        except ImportError:
            pass
