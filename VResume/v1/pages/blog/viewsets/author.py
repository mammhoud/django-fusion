from django.utils.translation import gettext_lazy as _
from wagtail.admin.ui.tables import BooleanColumn
from core.snippets import BaseSnippetViewSet
from pages.blog.models import BlogAuthor


class BlogAuthorViewSet(BaseSnippetViewSet):
    model = BlogAuthor
    icon = "user"
    menu_label = _("Authors")
    menu_order = 110
    list_display = [
        "name",
        "role",
        BooleanColumn("is_active", label=_("Active")),
        "display_order",
    ]
    list_filter = ["is_active"]
    search_fields = ["name", "role", "bio"]
    ordering = ["display_order", "name"]
