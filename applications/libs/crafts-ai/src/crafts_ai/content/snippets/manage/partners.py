"""
Partner snippet admin configuration using BaseSnippetViewSet.
"""

from django.utils.translation import gettext_lazy as _

# Project-specific imports removed - use dependency injection

from ..base import BaseSnippetViewSet


class PartnerViewSet(BaseSnippetViewSet):
    """Admin interface for Partners."""

    model = Partner
    menu_label = _("Partners")
    icon = "group"
    menu_order = 120
    search_fields = ["name", "website_url"]
    ordering = ["name"]

    list_display = ["name",]
    list_export = ["name", "website_url"]
    csv_filename = "partners.csv"

    list_actions = ["duplicate", "export_csv"]

    @staticmethod
    def website_link(obj):
        """Display clickable link to partner website."""
        return BaseSnippetViewSet.link_display(obj.website_url)
    website_link.short_description = _("Website")

    @staticmethod
    def logo_display(obj):
        """Show camera icon if logo is available."""
        return BaseSnippetViewSet.image_display(obj.logo)
    logo_display.short_description = _("Logo")
