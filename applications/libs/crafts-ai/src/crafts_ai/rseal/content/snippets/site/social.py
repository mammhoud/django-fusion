from django.utils.translation import gettext_lazy as _

from crafts_ai.content.models import GlobalSettings

from ..base import BaseSnippetViewSet


class GlobalSettingsViewSet(BaseSnippetViewSet):
    """Manage simple Person records via the Wagtail Snippet interface."""

    model = GlobalSettings
    menu_label = _("Global Links")
    icon = "globe"
    menu_order = 200
