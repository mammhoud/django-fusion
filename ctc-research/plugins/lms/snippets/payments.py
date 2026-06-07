"""
Payment Management Snippets for Wagtail Admin

Provides admin views for managing payment transactions, refunds, and webhooks.
"""
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from wagtail.snippets.views.snippets import SnippetViewSet
from wagtail.admin.panels import FieldPanel

from plugins.lms.models import PaymentTransaction, PaymentRefund, PaymentWebhookLog


class PaymentTransactionViewSet(SnippetViewSet):
    """
    Admin management for payment transactions.
    
    Features:
    - View all payment transactions
    - Filter by provider, status, date
    - Search by transaction ID or enrollment email
    - Display payment status with badges
    - View transaction metadata
    - Manual payment status updates (staff only)
    - Export transaction history
    """
    
    model = PaymentTransaction
    menu_label = _("Payment Transactions")
    icon = "credit"
    menu_order = 210
    
    list_display = [
        "transaction_id",
        "enrollment_link",
        "provider_display",
        "amount_display",
        "status_badge",
        "created_at_display",
    ]
    
    list_filter = [
        "provider",
        "status",
        "created_at",
        "webhook_verified",
    ]
    
    search_fields = [
        "transaction_id",
        "enrollment__email",
        "enrollment__name",
    ]
    
    panels = [
        FieldPanel("transaction_id", read_only=True, heading=_("Transaction ID")),
        FieldPanel("provider", read_only=True, heading=_("Provider")),
        FieldPanel("amount", read_only=True, heading=_("Amount")),
        FieldPanel("currency", read_only=True, heading=_("Currency")),
        FieldPanel("status", heading=_("Status")),
        FieldPanel("payment_method", read_only=True, heading=_("Payment Method")),
        FieldPanel("webhook_verified", read_only=True, heading=_("Webhook Verified")),
        FieldPanel("created_at", read_only=True, heading=_("Created")),
        FieldPanel("completed_at", read_only=True, heading=_("Completed")),
    ]
    
    def transaction_id(self, obj):
        """Display transaction ID as link"""
        return format_html(
            '<code style="background: #f0f0f0; padding: 2px 6px; border-radius: 3px;">{}</code>',
            obj.transaction_id
        )
    transaction_id.short_description = _("Transaction ID")
    
    def enrollment_link(self, obj):
        """Display enrollment email or link"""
        if obj.enrollment:
            url = reverse('wagtail_admin_view', args=[
                'lms',
                'courseenrollmentlead',
                obj.enrollment.pk
            ])
            return format_html(
                '<a href="#">{}</a>',
                obj.enrollment.email
            )
        return "—"
    enrollment_link.short_description = _("Enrollment")
    
    def provider_display(self, obj):
        """Display provider name"""
        providers = {
            'stripe': 'Stripe',
            'paypal': 'PayPal',
            'paymo': 'Paymo',
        }
        return providers.get(obj.provider, obj.provider.upper())
    provider_display.short_description = _("Provider")
    
    def amount_display(self, obj):
        """Display amount with currency"""
        return f"${obj.amount} {obj.currency}"
    amount_display.short_description = _("Amount")
    
    def status_badge(self, obj):
        """Display status with badge colors"""
        colors = {
            'pending': '#FFC107',      # Yellow
            'processing': '#17A2B8',   # Blue
            'completed': '#28A745',    # Green
            'failed': '#DC3545',       # Red
            'cancelled': '#6C757D',    # Gray
            'refunded': '#6F42C1',     # Purple
        }
        color = colors.get(obj.status, '#6C757D')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 8px; '
            'border-radius: 3px; font-size: 12px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = _("Status")
    
    def created_at_display(self, obj):
        """Display creation date"""
        return obj.created_at.strftime("%Y-%m-%d %H:%M")
    created_at_display.short_description = _("Created")
    
    @property
    def export_fields(self):
        """Fields to include in CSV export"""
        return [
            'transaction_id',
            'provider',
            'amount',
            'currency',
            'status',
            'payment_method',
            'created_at',
            'completed_at',
        ]


class PaymentRefundViewSet(SnippetViewSet):
    """
    Admin management for payment refunds.
    
    Features:
    - View all refunds
    - Filter by status, date
    - Search by refund ID
    - Display refund status
    - Link to original transaction
    """
    
    model = PaymentRefund
    menu_label = _("Payment Refunds")
    icon = "revert"
    menu_order = 220
    
    list_display = [
        "refund_id",
        "transaction_link",
        "amount_display",
        "status_badge",
        "created_at_display",
    ]
    
    list_filter = [
        "status",
        "created_at",
    ]
    
    search_fields = [
        "refund_id",
        "transaction__transaction_id",
    ]
    
    panels = [
        FieldPanel("refund_id", read_only=True, heading=_("Refund ID")),
        FieldPanel("transaction", read_only=True, heading=_("Original Transaction")),
        FieldPanel("amount", read_only=True, heading=_("Refund Amount")),
        FieldPanel("status", heading=_("Status")),
        FieldPanel("reason", heading=_("Reason")),
        FieldPanel("created_at", read_only=True, heading=_("Created")),
        FieldPanel("completed_at", read_only=True, heading=_("Completed")),
    ]
    
    def refund_id(self, obj):
        """Display refund ID as code"""
        return format_html(
            '<code style="background: #f0f0f0; padding: 2px 6px; border-radius: 3px;">{}</code>',
            obj.refund_id
        )
    refund_id.short_description = _("Refund ID")
    
    def transaction_link(self, obj):
        """Link to original transaction"""
        return format_html(
            '<code>{}</code>',
            obj.transaction.transaction_id[:20]
        )
    transaction_link.short_description = _("Original Transaction")
    
    def amount_display(self, obj):
        """Display refund amount"""
        return f"${obj.amount} {obj.transaction.currency}"
    amount_display.short_description = _("Refund Amount")
    
    def status_badge(self, obj):
        """Display refund status"""
        colors = {
            'pending': '#FFC107',
            'processing': '#17A2B8',
            'completed': '#28A745',
            'failed': '#DC3545',
        }
        color = colors.get(obj.status, '#6C757D')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 8px; '
            'border-radius: 3px; font-size: 12px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = _("Status")
    
    def created_at_display(self, obj):
        """Display creation date"""
        return obj.created_at.strftime("%Y-%m-%d %H:%M")
    created_at_display.short_description = _("Created")


class PaymentWebhookLogViewSet(SnippetViewSet):
    """
    Admin management for payment webhook logs.
    
    Features:
    - View all webhook events
    - Filter by provider, event type
    - Search by event ID
    - Display webhook status
    - View webhook payload
    - Track processing status
    """
    
    model = PaymentWebhookLog
    menu_label = _("Payment Webhooks")
    icon = "list-ul"
    menu_order = 230
    
    list_display = [
        "event_id",
        "provider_display",
        "event_type",
        "verified_badge",
        "processed_badge",
        "created_at_display",
    ]
    
    list_filter = [
        "provider",
        "event_type",
        "verified",
        "processed",
        "created_at",
    ]
    
    search_fields = [
        "event_id",
        "event_type",
    ]
    
    panels = [
        FieldPanel("event_id", read_only=True, heading=_("Event ID")),
        FieldPanel("provider", read_only=True, heading=_("Provider")),
        FieldPanel("event_type", read_only=True, heading=_("Event Type")),
        FieldPanel("verified", read_only=True, heading=_("Verified")),
        FieldPanel("processed", read_only=True, heading=_("Processed")),
        FieldPanel("created_at", read_only=True, heading=_("Created")),
        FieldPanel("processed_at", read_only=True, heading=_("Processed At")),
    ]
    
    def provider_display(self, obj):
        """Display provider name"""
        providers = {
            'stripe': 'Stripe',
            'paypal': 'PayPal',
            'paymo': 'Paymo',
        }
        return providers.get(obj.provider, obj.provider.upper())
    provider_display.short_description = _("Provider")
    
    def verified_badge(self, obj):
        """Display verification status"""
        color = '#28A745' if obj.verified else '#DC3545'
        text = _("Verified") if obj.verified else _("Not Verified")
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 8px; '
            'border-radius: 3px; font-size: 12px;">{}</span>',
            color,
            text
        )
    verified_badge.short_description = _("Verified")
    
    def processed_badge(self, obj):
        """Display processing status"""
        color = '#28A745' if obj.processed else '#FFC107'
        text = _("Processed") if obj.processed else _("Pending")
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 8px; '
            'border-radius: 3px; font-size: 12px;">{}</span>',
            color,
            text
        )
    processed_badge.short_description = _("Processed")
    
    def event_id(self, obj):
        """Display event ID as code"""
        return format_html(
            '<code style="background: #f0f0f0; padding: 2px 6px; border-radius: 3px;">{}</code>',
            obj.event_id[:30]
        )
    event_id.short_description = _("Event ID")
    
    def created_at_display(self, obj):
        """Display creation date"""
        return obj.created_at.strftime("%Y-%m-%d %H:%M:%S")
    created_at_display.short_description = _("Created")


# Export all ViewSets
__all__ = [
    'PaymentTransactionViewSet',
    'PaymentRefundViewSet',
    'PaymentWebhookLogViewSet',
]
