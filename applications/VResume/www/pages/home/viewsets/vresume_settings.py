from django.utils.translation import gettext_lazy as _
from django_fusion.wagtail.viewsets import BaseSnippetViewSet
from pages.home.models import VResumeSettings


class VResumeSettingsViewSet(BaseSnippetViewSet):
    model = VResumeSettings
    icon = "cog"
    menu_label = _("vResume Settings")
    menu_order = 50
