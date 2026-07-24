from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AnalyzerAppConfig(AppConfig):
    label = "fragments_analyzer"
    name = "django_fusion.fragments.analyzer"
    verbose_name = _("Component & Template Analyzer")
