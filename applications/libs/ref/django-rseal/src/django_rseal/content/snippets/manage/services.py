# Project-specific imports removed - use dependency injection
from django.utils.translation import gettext_lazy as _
from wagtail.admin.ui.tables import BooleanColumn

from ..base import BaseSnippetViewSet


class ServiceViewSet(BaseSnippetViewSet):
    model = Service
    icon = "folder-open-inverse"
    menu_label = _("Services")
    menu_name = "services"
    menu_order = 200

    list_display = [
        "name",
        "category",
        "formatted_price",
        BooleanColumn("is_active", label=_("Active")),
        BooleanColumn("is_visible", label=_("Visible")),
        "created_at",
    ]
    list_filter = ["category", "is_active", "is_visible"]
    search_fields = ["name", "overview", "description", "category"]

    # Optional: Enable ordering by name or date
    ordering = ["name"]
