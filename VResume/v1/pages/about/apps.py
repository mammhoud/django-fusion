from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AboutConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pages.about"
    verbose_name = _("About")
