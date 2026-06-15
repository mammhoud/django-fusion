from django.utils.translation import gettext_lazy as _
from wagtail.admin.ui.tables import BooleanColumn
from core.snippets import BaseSnippetViewSet
from pages.home.models import Service


class ServiceViewSet(BaseSnippetViewSet):
    model = Service
    icon = "folder-open-inverse"
    menu_label = _("Services")
    menu_order = 300
    list_display = ["name", BooleanColumn("is_active", label=_("Active")), "order"]
    list_filter = ["is_active"]
    search_fields = ["name", "description"]
    ordering = ["order", "name"]
