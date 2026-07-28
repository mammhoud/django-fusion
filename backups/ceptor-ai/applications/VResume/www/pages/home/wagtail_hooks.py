from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSetGroup

from .viewsets import (
    SliderViewSet,
    TeamMemberViewSet,
    ServiceViewSet,
)


class HomeAdminGroup(SnippetViewSetGroup):
    menu_label = "Home"
    menu_icon = "home"
    menu_order = 200
    items = (
        SliderViewSet,
        TeamMemberViewSet,
        ServiceViewSet,
    )

register_snippet(HomeAdminGroup)
