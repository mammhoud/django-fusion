"""
Payment Management Snippets for Wagtail Admin

Provides admin views for managing payment transactions, refunds, and webhooks.
Icons use wagtail-font-awesome-svg (solid set).

All list_display entries reference actual model fields or @property methods
decorated with admin_order_field — NOT ViewSet instance methods.
"""
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.views.snippets import SnippetViewSet

from apps.pages.lms.models import PaymentRefund, PaymentTransaction, PaymentWebhookLog


class PaymentTransactionViewSet(SnippetViewSet):
    """Admin view for payment transactions."""

    model = PaymentTransaction
    name = "paymenttransaction"
    menu_label = _("Payment Transactions")
    icon = "wagtailfontawesomesvg/solid/credit-card.svg"
    menu_order = 210

    list_display = [
        "transaction_id",
        "provider",
        "amount",
        "currency",
        "status",
        "webhook_verified",
        "created_at",
    ]
    list_filter = ["provider", "status", "webhook_verified"]
    search_fields = [
        "transaction_id",
        "enrollment__email",
        "enrollment__name",
    ]
    ordering = ["-created_at"]

    panels = [
        FieldPanel("transaction_id", read_only=True),
        FieldPanel("provider", read_only=True),
        FieldPanel("amount", read_only=True),
        FieldPanel("currency", read_only=True),
        FieldPanel("status"),
        FieldPanel("payment_method", read_only=True),
        FieldPanel("webhook_verified", read_only=True),
        FieldPanel("created_at", read_only=True),
        FieldPanel("completed_at", read_only=True),
    ]


class PaymentRefundViewSet(SnippetViewSet):
    """Admin view for payment refunds."""

    model = PaymentRefund
    name = "paymentrefund"
    menu_label = _("Payment Refunds")
    icon = "wagtailfontawesomesvg/solid/rotate-left.svg"
    menu_order = 220

    list_display = [
        "refund_id",
        "amount",
        "status",
        "reason",
        "created_at",
        "completed_at",
    ]
    list_filter = ["status"]
    search_fields = ["refund_id", "transaction__transaction_id"]
    ordering = ["-created_at"]

    panels = [
        FieldPanel("refund_id", read_only=True),
        FieldPanel("transaction", read_only=True),
        FieldPanel("amount", read_only=True),
        FieldPanel("status"),
        FieldPanel("reason"),
        FieldPanel("created_at", read_only=True),
        FieldPanel("completed_at", read_only=True),
    ]


class PaymentWebhookLogViewSet(SnippetViewSet):
    """Admin view for payment webhook logs."""

    model = PaymentWebhookLog
    name = "paymentwebhooklog"
    menu_label = _("Payment Webhooks")
    icon = "wagtailfontawesomesvg/solid/bell.svg"
    menu_order = 230

    list_display = [
        "event_id",
        "provider",
        "event_type",
        "verified",
        "processed",
        "created_at",
    ]
    list_filter = ["provider", "event_type", "verified", "processed"]
    search_fields = ["event_id", "event_type"]
    ordering = ["-created_at"]

    panels = [
        FieldPanel("event_id", read_only=True),
        FieldPanel("provider", read_only=True),
        FieldPanel("event_type", read_only=True),
        FieldPanel("verified", read_only=True),
        FieldPanel("processed", read_only=True),
        FieldPanel("created_at", read_only=True),
        FieldPanel("processed_at", read_only=True),
    ]


__all__ = [
    "PaymentTransactionViewSet",
    "PaymentRefundViewSet",
    "PaymentWebhookLogViewSet",
]
