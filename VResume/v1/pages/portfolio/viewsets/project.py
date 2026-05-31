"""
Project Snippet ViewSet
Manages reusable project snippets for portfolio
"""
from django.utils.translation import gettext_lazy as _
from wagtail.admin.ui.tables import BooleanColumn

from core.snippets import BaseSnippetViewSet
from pages.portfolio.models import Project


class ProjectViewSet(BaseSnippetViewSet):
    """
    Project Snippet ViewSet
    Manages reusable project snippets for portfolio
    
    Features:
    - Rich content with HTML support
    - Video embedding (YouTube, Vimeo)
    - Technology tagging
    - Featured project support
    - Date tracking
    - Multi-field admin panels
    - CSV export
    - Duplicate action
    
    Menu: Portfolio > Projects
    """
    model = Project
    icon = "folder"
    menu_label = _("Projects")
    menu_name = "projects"
    menu_group = "portfolio"
    menu_order = 120

    list_display = [
        "title",
        "category",
        BooleanColumn("is_active", label=_("Active")),
        "date_completed",
    ]
    list_filter = ["category", "is_active", "date_completed"]
    search_fields = ["title", "description", "body", "category"]
    ordering = ["-date_completed", "-created_at"]
