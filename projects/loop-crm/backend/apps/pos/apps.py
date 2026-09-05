from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.pos"
    label = "pos"
    verbose_name = _("POS ingestion")
