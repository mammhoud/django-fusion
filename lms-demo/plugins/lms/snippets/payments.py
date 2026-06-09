"""
Payment admin snippets for the LMS plugin.

Uses Django proxy models so each payment view registers its own
Wagtail snippet without conflicting with the base Enrollment registration.
Icons use wagtail-font-awesome-svg (solid set).
"""

from django.utils.translation import gettext_lazy as _

from plugins.accounts.snippets import BaseSnippetViewSet
from plugins.lms.models import Enrollment


# ---------------------------------------------------------------------------
# Proxy models — each represents a filtered "view" of Enrollment
# ---------------------------------------------------------------------------

class PaymentTransaction(Enrollment):
    """Proxy: all enrollment payment transactions."""

    class Meta:
        proxy = True
        verbose_name = _("Payment Transaction")
        verbose_name_plural = _("Payment Transactions")


class PaymentRefund(Enrollment):
    """Proxy: refunded or failed enrollments."""

    class Meta:
        proxy = True
        verbose_name = _("Payment Refund")
        verbose_name_plural = _("Payment Refunds")


class PaymentWebhookLog(Enrollment):
    """Proxy: pending / unprocessed webhook enrollments."""

    class Meta:
        proxy = True
        verbose_name = _("Payment Webhook Log")
        verbose_name_plural = _("Payment Webhook Logs")


# ---------------------------------------------------------------------------
# ViewSets — registered via PaymentSnippetGroup in wagtail_hooks.py
# ---------------------------------------------------------------------------

class PaymentTransactionViewSet(BaseSnippetViewSet):
    """Admin view for all enrollment payment transactions."""

    model = PaymentTransaction
    name = "paymenttransaction"
    menu_label = _("Transactions")
    icon = "wagtailfontawesomesvg/solid/credit-card.svg"
    menu_order = 300
    list_display = [
        "student",
        "course",
        "amount_paid",
        "payment_status",
        "payment_id",
        "transaction_date",
        "enrolled_at",
    ]
    list_filter = ["payment_status", "course"]
    search_fields = [
        "student__username",
        "student__email",
        "course__title",
        "payment_id",
        "payment_reference",
    ]
    ordering = ["-enrolled_at"]


class PaymentRefundViewSet(BaseSnippetViewSet):
    """Admin view for refunded / failed enrollments."""

    model = PaymentRefund
    name = "paymentrefund"
    menu_label = _("Refunds")
    icon = "wagtailfontawesomesvg/solid/rotate-left.svg"
    menu_order = 310
    list_display = [
        "student",
        "course",
        "amount_paid",
        "payment_status",
        "payment_reference",
        "transaction_date",
    ]
    list_filter = ["payment_status", "course"]
    search_fields = [
        "student__username",
        "student__email",
        "course__title",
        "payment_reference",
    ]
    ordering = ["-transaction_date"]

    def get_queryset(self, request):
        return super().get_queryset(request).filter(
            payment_status__in=["refunded", "failed"]
        )


class PaymentWebhookLogViewSet(BaseSnippetViewSet):
    """Admin view for pending webhook enrollment events."""

    model = PaymentWebhookLog
    name = "paymentwebhooklog"
    menu_label = _("Webhook Log")
    icon = "wagtailfontawesomesvg/solid/bell.svg"
    menu_order = 320
    list_display = [
        "student",
        "course",
        "payment_status",
        "payment_id",
        "payment_reference",
        "enrolled_at",
    ]
    list_filter = ["payment_status"]
    search_fields = [
        "student__username",
        "student__email",
        "payment_id",
        "payment_reference",
    ]
    ordering = ["-enrolled_at"]

    def get_queryset(self, request):
        return super().get_queryset(request).filter(payment_status="pending")
