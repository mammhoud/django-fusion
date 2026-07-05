from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Integration(models.Model):
    """
    Represents a system integration configuration.

    This model manages connections to known external services
    such as Twilio, Stripe, PayPal, or custom APIs.

    Each integration type (e.g. Twilio, Stripe) can have
    specific endpoint categories (e.g. messaging, payments, webhooks).
    """

    # ---------------------------------------------------------------------
    # INTEGRATION TYPES (Specific Systems)
    # ---------------------------------------------------------------------
    class IntegrationType(models.TextChoices):
        TWILIO = "twilio", _("Twilio (Messaging API)")
        STRIPE = "stripe", _("Stripe (Payment Processor)")
        PAYPAL = "paypal", _("PayPal (Payment Gateway)")
        GOOGLE = "google", _("Google (OAuth / APIs)")
        AWS = "aws", _("Amazon Web Services (S3, SNS, etc.)")
        SLACK = "slack", _("Slack (Messaging / Webhooks)")
        ZOHO = "zoho", _("Zoho (CRM / Accounting)")
        HUBSPOT = "hubspot", _("HubSpot (CRM / Marketing)")
        QUICKBOOKS = "quickbooks", _("QuickBooks (Accounting)")
        CUSTOM = "custom", _("Custom Integration")

    # ---------------------------------------------------------------------
    # ENDPOINT TYPES (Specific API Sections)
    # ---------------------------------------------------------------------
    class EndpointType(models.TextChoices):
        # Twilio Endpoints
        SMS = "sms", _("Messaging / SMS")
        VOICE = "voice", _("Voice / Calls")
        WHATSAPP = "whatsapp", _("WhatsApp Messaging")
        VIDEO = "video", _("Video API")

        # Stripe / PayPal Endpoints
        PAYMENTS = "payments", _("Payments / Charges")
        INVOICES = "invoices", _("Invoices / Billing")
        CUSTOMERS = "customers", _("Customer Profiles")
        SUBSCRIPTIONS = "subscriptions", _("Subscriptions / Plans")

        # Generic Endpoints
        AUTH = "auth", _("Authentication / OAuth")
        WEBHOOK = "webhook", _("Webhook Endpoint")
        SYNC = "sync", _("Data Synchronization")
        REPORTS = "reports", _("Analytics / Reports")
        CALLBACK = "callback", _("Callback or Redirect")
        HEALTH = "health", _("Health Check / Ping")
        CUSTOM = "custom", _("Custom Endpoint")

    # ---------------------------------------------------------------------
    # CORE FIELDS
    # ---------------------------------------------------------------------
    name = models.CharField(
        _("Integration Name"),
        max_length=100,
        help_text=_("Human-readable name of the integration (e.g. Twilio Messaging)."),
    )
    external_id = models.CharField(
        _("External ID"),
        max_length=255,
        blank=True,
        help_text=_("Unique identifier from the external system (if available)."),
    )
    integration_type = models.CharField(
        max_length=20,
        choices=IntegrationType.choices,
        default=IntegrationType.CUSTOM,
        verbose_name=_("Integration Type"),
        help_text=_("Select which platform or service this integration connects to."),
    )
    endpoint_type = models.CharField(
        max_length=20,
        choices=EndpointType.choices,
        default=EndpointType.CUSTOM,
        verbose_name=_("Endpoint Type"),
        help_text=_("Type of endpoint or API section this configuration handles."),
    )

    api_endpoint = models.URLField(
        _("API Endpoint"),
        blank=True,
        help_text=_("Base URL for the endpoint, e.g., https://api.twilio.com/v1/messages"),
    )
    api_key = models.CharField(
        _("API Key / Token"),
        max_length=255,
        blank=True,
        help_text=_("API key or authentication token used for access."),
    )
    metadata = models.JSONField(
        _("Metadata"),
        blank=True,
        null=True,
        help_text=_("Additional configuration or credentials as JSON."),
    )

    # ---------------------------------------------------------------------
    # STATUS AND TRACKING
    # ---------------------------------------------------------------------
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active"),
        help_text=_("Indicates whether this integration is currently enabled."),
    )
    last_sync_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Last Sync At"),
        help_text=_("When the last synchronization or update occurred."),
    )
    sync_status = models.CharField(
        max_length=20,
        choices=[
            ("success", _("Success")),
            ("error", _("Error")),
            ("pending", _("Pending")),
            ("never", _("Never Synced")),
        ],
        default="never",
        verbose_name=_("Sync Status"),
        help_text=_("The current synchronization status."),
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        app_label = "CI"
        verbose_name = _("Integration")
        verbose_name_plural = _("Integrations")
        unique_together = ["name", "integration_type", "endpoint_type"]
        indexes = [
            models.Index(fields=["integration_type", "is_active"]),
            models.Index(fields=["name"]),
            models.Index(fields=["sync_status"]),
        ]
        ordering = ["-updated_at", "name"]

    def __str__(self):
        return f"{self.name} ({self.integration_type} - {self.endpoint_type})"

    # ---------------------------------------------------------------------
    # METHODS
    # ---------------------------------------------------------------------
    def mark_synced(self, success=True):
        """Mark the integration as synced and update sync status."""
        self.last_sync_at = timezone.now()
        self.sync_status = "success" if success else "error"
        self.save(update_fields=["last_sync_at", "sync_status", "updated_at"])

    def activate(self):
        """Enable this integration."""
        self.is_active = True
        self.save(update_fields=["is_active", "updated_at"])

    def deactivate(self):
        """Disable this integration."""
        self.is_active = False
        self.save(update_fields=["is_active", "updated_at"])

    def status_display(self):
        """Return a human-readable sync status."""
        return {
            "success": _("Last sync succeeded."),
            "error": _("Last sync failed."),
            "pending": _("Sync pending."),
            "never": _("Never synced."),
        }.get(self.sync_status, _("Unknown status."))

    def sync_required(self):
        """Determine if sync should be retried."""
        return self.is_active and self.sync_status != "success"
