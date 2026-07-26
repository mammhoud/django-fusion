from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSetGroup

from .viewsets import (
    TestimonialViewSet,
    ClientViewSet,
)


class AboutAdminGroup(SnippetViewSetGroup):
    menu_label = "About"
    menu_icon = "user"
    menu_order = 300
    items = (
        TestimonialViewSet,
        ClientViewSet,
    )

register_snippet(AboutAdminGroup)
