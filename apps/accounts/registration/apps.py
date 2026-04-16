from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RegistrationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts.registration"
    label = "handlers_registration"
    verbose_name = _("Registration")

    def ready(self):
        import apps.accounts.registration.signals  # noqa: F401
