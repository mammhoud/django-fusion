"""
Wagtail hooks for Portfolio application.
Registers all portfolio snippet viewsets.
"""

from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSetGroup

from .viewsets import (
    PortfolioTagViewSet,
    ProjectViewSet,
)


class PortfolioSnippetGroup(SnippetViewSetGroup):
    """
    Group all portfolio-related snippet viewsets
    under a single admin menu section.
    """

    menu_label = "Portfolio"
    menu_icon = "folder-open-inverse"
    menu_order = 200
    items = (
        PortfolioTagViewSet,
        ProjectViewSet,
    )


register_snippet(PortfolioSnippetGroup)