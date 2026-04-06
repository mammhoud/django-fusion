from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class IntegrationConfig(AppConfig):
    name = "alliance.CI"
    default_auto_field = "django.db.models.BigAutoField"
    label = "CI"
    verbose_name = _("CI")
    verbose_name_plural = _("CI")

    def ready(self):
        pass
