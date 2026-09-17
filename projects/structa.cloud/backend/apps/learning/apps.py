from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LearningConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.learning"
    label = "learning"
    verbose_name = _("Learning")

    def ready(self):
        from . import signals  # noqa: F401
