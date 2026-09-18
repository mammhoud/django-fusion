from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AttributionConfig(AppConfig):
    name = "apps.attribution"
    label = "attribution"
    verbose_name = _("Attribution")
