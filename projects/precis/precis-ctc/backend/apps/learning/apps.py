from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LearningConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.learning'
    # Keep the legacy ``lms`` app label so existing DB tables and
    # migration history (apps.learning/migrations) stay intact.
    label = "lms"
    verbose_name = _("Learning Module")

    def ready(self):
        """Register signals when app is ready."""
        try:
            import apps.learning.signals  # noqa: F401
        except ImportError:
            pass
