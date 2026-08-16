from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BrandingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.pages.branding"
    label = "branding"
    verbose_name = _("Branding")
