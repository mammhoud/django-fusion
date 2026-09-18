"""
ServiceViewSet: Base class for service snippet viewsets.

Canonical import: from apps.domain.contrib.snippets import ServiceViewSetBase

Projects should subclass this and inject their Service model.
"""

from django.utils.translation import gettext_lazy as _
from wagtail.admin.ui.tables import BooleanColumn

from ..base import BaseSnippetViewSet


class ServiceViewSetBase(BaseSnippetViewSet):
    """
    Base class for service snippet viewsets.

    Projects should subclass this and set the model attribute:

    class ServiceViewSet(ServiceViewSetBase):
        model = Service  # Project-specific Service model
    """
    model = None  # Injected by subclass
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

    ordering = ["name"]
