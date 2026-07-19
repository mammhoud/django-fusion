from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CVConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pages.cv"
    verbose_name = _("CV / Resume")
