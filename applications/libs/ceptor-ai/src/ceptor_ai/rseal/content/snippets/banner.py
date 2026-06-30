"""
AnnouncementBanner SnippetViewSet for Wagtail admin.
Registered via wagtail_hooks.py in TechBridgesSnippetGroup.
"""
from django.utils.translation import gettext_lazy as _
from wagtail.snippets.views.snippets import SnippetViewSet

from ceptor_ai.content.models import AnnouncementBanner


class AnnouncementBannerViewSet(SnippetViewSet):
    """
    Admin interface for managing announcement banners.
    """
    model = AnnouncementBanner

    menu_label = _("Banners")
    menu_icon = "bullhorn"
    menu_order = 200
    add_to_admin_menu = False  # Part of TechBridgesSnippetGroup
    list_display = ["name", "marquee_text", "show_discount", "is_active", "updated_at"]
    list_filter = ["is_active", "show_discount"]
    search_fields = ["name", "marquee_text"]
