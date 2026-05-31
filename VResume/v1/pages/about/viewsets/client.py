from django.utils.translation import gettext_lazy as _
from wagtail.admin.ui.tables import BooleanColumn
from core.snippets import BaseSnippetViewSet
from pages.about.models import Client


class ClientViewSet(BaseSnippetViewSet):
    model = Client
    icon = "group"
    menu_label = _("Clients")
    menu_order = 200
    list_display = ["name", BooleanColumn("is_active", label=_("Active")), "order"]
    list_filter = ["is_active"]
    search_fields = ["name"]
    ordering = ["order", "name"]
