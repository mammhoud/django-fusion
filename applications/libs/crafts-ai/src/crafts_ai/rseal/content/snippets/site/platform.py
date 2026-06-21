# wagtail_hooks.py
from django.utils.translation import gettext_lazy as _

from crafts_ai.content.models import TechBridges
from crafts_ai.content.snippets.base import BaseSnippetViewSet


class TechBridgesViewSet(BaseSnippetViewSet):
    """
    Custom ViewSet for TechBridges with enhanced functionality.
    """
    model = TechBridges
    icon = "cog"  # Wagtail icon name
    menu_label = _("Tech Bridges")
    menu_name = "site-settings"
    menu_order = 1000
    ordering = ["language", "-active"]
