"""
Partner snippet admin configuration using BaseSnippetViewSet.
"""

from django.utils.translation import gettext_lazy as _
from apps.domain.handlers.models.manage_company import Organization

from ..base import BaseSnippetViewSet


class OrganizationViewSet(BaseSnippetViewSet):
    """Admin interface for Organizations."""

    model = Organization
    menu_label = _("Organizations")
    icon = "group"
    menu_order = 120
    search_fields = ["name", "legal_name", "website"]
    ordering = ["name"]

    list_display = ["name",]
    list_export = ["name", "website"]
    csv_filename = "partners.csv"

    list_actions = ["duplicate", "export_csv"]

    @staticmethod
    def website_link(obj):
        """Display clickable link to organization website."""
        return BaseSnippetViewSet.link_display(obj.website)
    website_link.short_description = _("Website")

    @staticmethod
    def logo_display(obj):
        """Show camera icon if logo is available."""
        return BaseSnippetViewSet.image_display(obj.logo)
    logo_display.short_description = _("Logo")
