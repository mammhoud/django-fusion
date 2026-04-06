from django.utils.translation import gettext_lazy as _
from wagtail.admin.ui.tables import BooleanColumn

from apps.handlers.models import Service

from ..base import BaseSnippetViewSet


class ServiceViewSet(BaseSnippetViewSet):
    model = Service
    icon = "folder-open-inverse"
    menu_label = _("Services")
    menu_name = "services"
    menu_order = 200
    # add_to_admin_menu = True

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

    # Optional: Custom template overrides (if desired)
    # edit_template_name = "admin/services/edit.html"
    # list_template_name = "admin/services/list.html"

    # # Configure snippets to appear in Wagtail's API (if using wagtail.api.v2)
    # api_fields = [
    #     "name",
    #     "overview",
    #     "description",
    #     "category",
    #     "formatted_price",
    #     "is_active",
    #     "is_visible",
    # ]
