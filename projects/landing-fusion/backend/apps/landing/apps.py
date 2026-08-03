from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LandingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.landing"
    label = "landing"
    verbose_name = _("Landing")
