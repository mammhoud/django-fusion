"""
📧 Email Delivery Model
=======================
Tracks individual email deliveries for campaigns.
Monitors delivery status, engagement (opens/clicks), and bounce information.
"""
import secrets

from django.db import models
from django.utils.translation import gettext_lazy as _


class EmailDelivery(models.Model):
    """
    📧 Email Delivery Tracking Model
    
    Tracks each individual email sent as part of a campaign.
    Monitors:
    - Delivery status (pending, sent, failed, bounced, opened, clicked)
    - Timestamps for each status change
    - Engagement metrics (open_count, click_count)
    - Error information for failed deliveries
    - Bounce type (hard, soft)
    
    Features:
    - Unique tracking token per delivery for open/click tracking
    - Timestamps for all status changes
    - Unique constraint on campaign + subscriber
    """

    STATUS_CHOICES = [
        ("pending", _("Pending")),
        ("sent", _("Sent")),
        ("failed", _("Failed")),
        ("bounced", _("Bounced")),
        ("opened", _("Opened")),
        ("clicked", _("Clicked")),
    ]

    BOUNCE_TYPE_CHOICES = [
        ("hard", _("Hard Bounce")),
        ("soft", _("Soft Bounce")),
    ]

    # ── Relationships ──
    campaign = models.ForeignKey(
        'connect.Campaign',
        on_delete=models.CASCADE,
        related_name='deliveries',
        verbose_name=_("Campaign"),
    )

    subscriber = models.ForeignKey(
        'connect.Subscriber',
        on_delete=models.CASCADE,
        related_name='deliveries',
        verbose_name=_("Subscriber"),
    )

    # ── Tracking ──
    tracking_token = models.CharField(
        max_length=64,
        unique=True,
        verbose_name=_("Tracking Token"),
        help_text=_("Unique token for tracking opens and clicks"),
        db_index=True,
    )

    # ── Status ──
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name=_("Status"),
        db_index=True,
    )

    # ── Timestamps ──
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Sent At"),
    )

    opened_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Opened At"),
    )

    clicked_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Clicked At"),
    )

    bounced_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Bounced At"),
    )

    # ── Engagement Metrics ──
    open_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Open Count"),
        help_text=_("Number of times the email was opened"),
    )

    click_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Click Count"),
        help_text=_("Number of times a link was clicked"),
    )

    # ── Error Information ──
    error_message = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("Error Message"),
        help_text=_("Error message if delivery failed"),
    )

    bounce_type = models.CharField(
        max_length=10,
        choices=BOUNCE_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name=_("Bounce Type"),
        help_text=_("Type of bounce: hard or soft"),
    )

    # ── Audit Trail ──
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
    )

    class Meta:
        app_label = "connect"
        verbose_name = _("Email Delivery")
        verbose_name_plural = _("Email Deliveries")
        ordering = ["-created_at"]
        unique_together = [
            ["campaign", "subscriber"],
        ]
        indexes = [
            models.Index(fields=["tracking_token"]),
            models.Index(fields=["campaign", "status"]),
        ]

    def __str__(self):
        return f"{self.campaign.name} -> {self.subscriber.email} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        """Generate tracking token if not set."""
        if not self.tracking_token:
            self.tracking_token = self._generate_tracking_token()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_tracking_token() -> str:
        """Generate a secure random tracking token."""
        return secrets.token_urlsafe(32)

    # ── Status Management Methods ──

    def mark_sent(self) -> None:
        """Mark the email as sent."""
        from django.utils import timezone

        self.status = "sent"
        self.sent_at = timezone.now()
        self.save(update_fields=["status", "sent_at", "updated_at"])

    def mark_failed(self, error_message: str = "") -> None:
        """Mark the email as failed."""
        from django.utils import timezone

        self.status = "failed"
        self.error_message = error_message
        self.save(update_fields=["status", "error_message", "updated_at"])

    def mark_bounced(self, bounce_type: str = "hard") -> None:
        """Mark the email as bounced."""
        from django.utils import timezone

        self.status = "bounced"
        self.bounced_at = timezone.now()
        self.bounce_type = bounce_type
        self.save(update_fields=["status", "bounced_at", "bounce_type", "updated_at"])

    def record_open(self) -> None:
        """Record an email open event."""
        from django.utils import timezone

        self.status = "opened"
        self.opened_at = timezone.now()
        self.open_count = models.F('open_count') + 1
        self.save(update_fields=["status", "opened_at", "open_count", "updated_at"])
        self.refresh_from_db()

    def record_click(self) -> None:
        """Record a click event."""
        from django.utils import timezone

        if self.status != "clicked":
            self.status = "clicked"
            self.clicked_at = timezone.now()
        self.click_count = models.F('click_count') + 1
        self.save(update_fields=["status", "clicked_at", "click_count", "updated_at"])
        self.refresh_from_db()

    # ── Property Methods ──

    @property
    def is_sent(self) -> bool:
        """Check if email was sent."""
        return self.status in ["sent", "opened", "clicked"]

    @property
    def is_pending(self) -> bool:
        """Check if email is pending."""
        return self.status == "pending"

    @property
    def is_failed(self) -> bool:
        """Check if email delivery failed."""
        return self.status == "failed"

    @property
    def is_bounced(self) -> bool:
        """Check if email bounced."""
        return self.status == "bounced"

    @property
    def was_opened(self) -> bool:
        """Check if email was opened."""
        return self.status in ["opened", "clicked"] and self.open_count > 0

    @property
    def was_clicked(self) -> bool:
        """Check if any link was clicked."""
        return self.status == "clicked" and self.click_count > 0