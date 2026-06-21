"""
Newsletter Campaign Model
"""
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from wagtail.fields import RichTextField


class Campaign(models.Model):
    """
    Email campaign for newsletters.
    """

    STATUS_CHOICES = [
        ("draft", _("Draft")),
        ("scheduled", _("Scheduled")),
        ("sending", _("Sending")),
        ("sent", _("Sent")),
        ("cancelled", _("Cancelled")),
    ]

    name = models.CharField(
        max_length=255,
        verbose_name=_("Campaign Name"),
        help_text=_("Internal name for this campaign"),
    )

    subject = models.CharField(
        max_length=255,
        verbose_name=_("Email Subject"),
    )

    preview_text = models.CharField(
        max_length=150,
        blank=True,
        default="",
        verbose_name=_("Preview Text"),
        help_text=_("Text shown in email client preview"),
    )

    content = RichTextField(
        verbose_name=_("Content"),
        help_text=_("Main content of the newsletter"),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name=_("Status"),
        db_index=True,
    )

    scheduled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Scheduled At"),
    )

    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Sent At"),
    )

    # Analytics
    total_sent = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Total Sent"),
    )

    total_opened = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Total Opened"),
    )

    total_clicked = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Total Clicked"),
    )

    total_bounced = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Total Bounced"),
    )

    total_unsubscribed = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Total Unsubscribed"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
    )

    class Meta:
        verbose_name = _("Campaign")
        verbose_name_plural = _("Campaigns")
        ordering = ["-created_at"]
        db_table = "newsletter_campaign"

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    def get_open_rate(self) -> float:
        """Calculate open rate as percentage."""
        if self.total_sent == 0:
            return 0.0
        return round((self.total_opened / self.total_sent) * 100, 2)

    def get_click_rate(self) -> float:
        """Calculate click rate as percentage."""
        if self.total_sent == 0:
            return 0.0
        return round((self.total_clicked / self.total_sent) * 100, 2)

    def get_bounce_rate(self) -> float:
        """Calculate bounce rate as percentage."""
        if self.total_sent == 0:
            return 0.0
        return round((self.total_bounced / self.total_sent) * 100, 2)

    def schedule(self, send_at: timezone.datetime) -> None:
        """Schedule the campaign for sending."""
        self.status = "scheduled"
        self.scheduled_at = send_at
        self.save(update_fields=["status", "scheduled_at", "updated_at"])

    def mark_sending(self) -> None:
        """Mark campaign as currently sending."""
        self.status = "sending"
        self.save(update_fields=["status", "updated_at"])

    def mark_sent(self) -> None:
        """Mark campaign as sent."""
        self.status = "sent"
        self.sent_at = timezone.now()
        self.save(update_fields=["status", "sent_at", "updated_at"])

    def cancel(self) -> None:
        """Cancel the campaign."""
        if self.status in ["draft", "scheduled"]:
            self.status = "cancelled"
            self.save(update_fields=["status", "updated_at"])

    def increment_sent(self) -> None:
        """Increment sent counter."""
        self.total_sent += 1
        self.save(update_fields=["total_sent", "updated_at"])

    def increment_opened(self) -> None:
        """Increment opened counter."""
        self.total_opened += 1
        self.save(update_fields=["total_opened", "updated_at"])

    def increment_clicked(self) -> None:
        """Increment clicked counter."""
        self.total_clicked += 1
        self.save(update_fields=["total_clicked", "updated_at"])
