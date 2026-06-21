"""
Portfolio Tag Snippet ViewSet
Manages tags for portfolio projects
"""
from django.utils.translation import gettext_lazy as _
from wagtail.admin.ui.tables import BooleanColumn

from django_osoul.wagtail.viewsets import BaseSnippetViewSet
from pages.portfolio.models import PortfolioTag


class PortfolioTagViewSet(BaseSnippetViewSet):
    """
    Portfolio Tag Snippet ViewSet
    Manages tags for portfolio projects
    
    Features:
    - Color coding for visual distinction
    - Icon support (Bootstrap icons)
    - Active status control
    - CSV export
    - Duplicate action
    
    Menu: Portfolio > Tags
    """
    model = PortfolioTag
    icon = "tag"
    menu_label = _("Portfolio Tags")
    menu_name = "portfolio_tags"
    menu_group = "portfolio"
    menu_order = 100

    list_display = [
        "name",
        "slug",
        BooleanColumn("is_active", label=_("Active")),
    ]
    list_filter = ["is_active"]
    search_fields = ["name", "description"]
    ordering = ["name"]
