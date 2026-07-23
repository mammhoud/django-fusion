from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AnalyzerAppConfig(AppConfig):
    label = "analyzer"
    name = "django_fusion.analyzer"
    verbose_name = _("Component & Template Analyzer")
