from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DjangoRsealConfig(AppConfig):
    label = "django_rseal"
    name = "django_rseal"
    default_auto_field = "django.db.models.BigAutoField"
    verbose_name = _("Django RSeal")
    verbose_name_plural = _("Django RSeal")

    def ready(self):
        # Import signals to register them with Django's signal dispatcher
        import django_rseal.user_signals  # noqa: F401

