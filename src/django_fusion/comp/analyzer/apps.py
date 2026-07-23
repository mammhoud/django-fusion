from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AnalyzerAppConfig(AppConfig):
    label = "comp_analyzer"
    name = "django_fusion.comp.analyzer"
    verbose_name = _("Component & Template Analyzer")
