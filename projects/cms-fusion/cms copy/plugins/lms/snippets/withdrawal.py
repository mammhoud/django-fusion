"""
Withdrawal Management Snippet for Wagtail Admin

Provides admin views for managing instructor withdrawal requests.
Icons use wagtail-font-awesome-svg (solid set).
"""

from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.views.snippets import SnippetViewSet

from plugins.lms.models import Withdrawal


class WithdrawalViewSet(SnippetViewSet):
    """Admin view for instructor withdrawal/payout requests."""

    model = Withdrawal
    name = "withdrawal"
    menu_label = _("Withdrawals")
    icon = "wagtailfontawesomesvg/solid/wallet.svg"
    menu_order = 240

    list_display = [
        "instructor",
        "amount",
        "status",
        "payment_method",
        "created_at",
        "processed_at",
    ]
    list_filter = ["status", "payment_method"]
    search_fields = [
        "instructor__username",
        "instructor__email",
        "instructor__first_name",
        "instructor__last_name",
        "reference",
    ]
    ordering = ["-created_at"]

    panels = [
        FieldPanel("instructor", read_only=True),
        FieldPanel("amount", read_only=True),
        FieldPanel("current_balance", read_only=True),
        FieldPanel("status"),
        FieldPanel("payment_method"),
        FieldPanel("payment_details"),
        FieldPanel("reference"),
        FieldPanel("notes"),
        FieldPanel("processed_by"),
        FieldPanel("created_at", read_only=True),
        FieldPanel("updated_at", read_only=True),
        FieldPanel("processed_at", read_only=True),
    ]


__all__ = [
    "WithdrawalViewSet",
]
