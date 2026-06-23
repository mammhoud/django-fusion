from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DjangoRsealConfig(AppConfig):
    label = "crafts_ai"
    name = "crafts_ai"
    default_auto_field = "django.db.models.BigAutoField"
    verbose_name = _("Django RSeal")
    verbose_name_plural = _("Django RSeal")

    def ready(self):
        # Import signals to register them with Django's signal dispatcher
        import crafts_ai.user_signals  # noqa: F401

