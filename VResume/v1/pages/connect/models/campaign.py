"""
📧 Campaign Model for Email Marketing
======================================
Manages email campaigns with scheduling, targeting, and analytics.
Tracks campaign status, delivery metrics, and engagement rates.
"""
import secrets
from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Campaign(models.Model):
    """
    📧 Email Campaign Model
    
    Manages email campaigns with:
    - Campaign content (name, subject, body, preview)
    - Targeting (subscribers M2M relationship)
    - Scheduling (scheduled_at, sent_at)
    - Status tracking (draft, scheduled, sending, sent, paused, failed)
    - Analytics (total_sent, total_opened, total_clicked, total_bounced)
    - Audit trail (created_by, created_at, updated_at)
    
    Features:
    - Calculate open rate and click rate as properties
    - Schedule campaigns for later sending
    - Mark campaign status transitions
    - Cancel campaigns
    - Blog post integration for newsletter campaigns
    """
    
    STATUS_CHOICES = [
        ("draft", _("Draft")),
        ("scheduled", _("Scheduled")),
        ("sending", _("Sending")),
        ("sent", _("Sent")),
        ("paused", _("Paused")),
        ("failed", _("Failed")),
    ]
    
    # ── Campaign Content ──
    name = models.CharField(
        max_length=255,
        verbose_name=_("Campaign Name"),
        help_text=_("Internal name for the campaign"),
        db_index=True,
    )
    
    subject = models.CharField(
        max_length=255,
        verbose_name=_("Email Subject"),
        help_text=_("Subject line for the email"),
    )
    
    preview_text = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Preview Text"),
        help_text=_("Preview text shown in email clients (max 255 chars)"),
    )
    
    body = models.TextField(
        verbose_name=_("Email Body"),
        help_text=_("HTML content of the email"),
    )
    
    # ── Blog Integration ──
    blog_post = models.ForeignKey(
        'blog.BlogPage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='campaigns',
        verbose_name=_("Blog Post"),
        help_text=_("Associated blog post for newsletter campaigns"),
    )
    
    # ── Targeting ──
    subscribers = models.ManyToManyField(
        'connect.Subscriber',
        related_name='campaigns',
        verbose_name=_("Subscribers"),
        help_text=_("Subscribers to send this campaign to"),
    )
    
    # ── Status & Timing ──
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
        help_text=_("When the campaign should be sent"),
    )
    
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Sent At"),
        help_text=_("When the campaign was sent"),
    )
    
    # ── Analytics ──
    total_sent = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Total Sent"),
        help_text=_("Number of emails sent"),
    )
    
    total_opened = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Total Opened"),
        help_text=_("Number of emails opened"),
    )
    
    total_clicked = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Total Clicked"),
        help_text=_("Number of emails with clicks"),
    )
    
    total_bounced = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Total Bounced"),
        help_text=_("Number of emails bounced"),
    )
    
    # ── Audit Trail ──
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='campaigns_created',
        verbose_name=_("Created By"),
        help_text=_("User who created the campaign"),
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
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["scheduled_at", "status"]),
            models.Index(fields=["created_by", "created_at"]),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
    
    # ── Analytics Properties ──
    
    @property
    def open_rate(self) -> Decimal:
        """
        Calculate the open rate as a percentage.
        
        Returns:
            Decimal: Open rate percentage (0-100), or 0 if no emails sent
        """
        if self.total_sent == 0:
            return Decimal("0.00")
        
        rate = (Decimal(self.total_opened) / Decimal(self.total_sent)) * Decimal("100")
        return rate.quantize(Decimal("0.01"))
    
    @property
    def click_rate(self) -> Decimal:
        """
        Calculate the click rate as a percentage.
        
        Returns:
            Decimal: Click rate percentage (0-100), or 0 if no emails sent
        """
        if self.total_sent == 0:
            return Decimal("0.00")
        
        rate = (Decimal(self.total_clicked) / Decimal(self.total_sent)) * Decimal("100")
        return rate.quantize(Decimal("0.01"))
    
    @property
    def bounce_rate(self) -> Decimal:
        """
        Calculate the bounce rate as a percentage.
        
        Returns:
            Decimal: Bounce rate percentage (0-100), or 0 if no emails sent
        """
        if self.total_sent == 0:
            return Decimal("0.00")
        
        rate = (Decimal(self.total_bounced) / Decimal(self.total_sent)) * Decimal("100")
        return rate.quantize(Decimal("0.01"))
    
    @property
    def is_scheduled(self) -> bool:
        """Check if campaign is scheduled for later sending."""
        return self.status == "scheduled" and self.scheduled_at is not None
    
    @property
    def is_sending(self) -> bool:
        """Check if campaign is currently sending."""
        return self.status == "sending"
    
    @property
    def is_sent(self) -> bool:
        """Check if campaign has been sent."""
        return self.status == "sent"
    
    @property
    def is_draft(self) -> bool:
        """Check if campaign is in draft status."""
        return self.status == "draft"
    
    @property
    def is_paused(self) -> bool:
        """Check if campaign is paused."""
        return self.status == "paused"
    
    @property
    def is_failed(self) -> bool:
        """Check if campaign failed."""
        return self.status == "failed"
    
    @property
    def can_be_sent(self) -> bool:
        """Check if campaign can be sent (is in draft or paused status)."""
        return self.status in ["draft", "paused"]
    
    @property
    def can_be_scheduled(self) -> bool:
        """Check if campaign can be scheduled (is in draft status)."""
        return self.status == "draft"
    
    @property
    def can_be_paused(self) -> bool:
        """Check if campaign can be paused (is sending)."""
        return self.status == "sending"
    
    @property
    def can_be_cancelled(self) -> bool:
        """Check if campaign can be cancelled (is draft or scheduled)."""
        return self.status in ["draft", "scheduled"]
    
    @property
    def subscriber_count(self) -> int:
        """Get the number of subscribers targeted by this campaign."""
        return self.subscribers.count()
    
    # ── Status Management Methods ──
    
    def schedule(self, scheduled_at: timezone.datetime) -> bool:
        """
        Schedule the campaign for later sending.
        
        Args:
            scheduled_at (datetime): When to send the campaign
            
        Returns:
            bool: True if scheduling was successful, False otherwise
            
        Raises:
            ValueError: If scheduled_at is in the past or campaign cannot be scheduled
        """
        if not self.can_be_scheduled:
            raise ValueError(
                f"Cannot schedule campaign in {self.get_status_display()} status. "
                f"Only draft campaigns can be scheduled."
            )
        
        if scheduled_at <= timezone.now():
            raise ValueError("Scheduled time must be in the future")
        
        self.status = "scheduled"
        self.scheduled_at = scheduled_at
        self.save(update_fields=["status", "scheduled_at", "updated_at"])
        return True
    
    def mark_sending(self) -> bool:
        """
        Mark the campaign as currently sending.
        
        Returns:
            bool: True if status change was successful, False otherwise
        """
        if not self.can_be_sent:
            raise ValueError(
                f"Cannot mark campaign as sending from {self.get_status_display()} status. "
                f"Only draft or paused campaigns can be sent."
            )
        
        self.status = "sending"
        self.save(update_fields=["status", "updated_at"])
        return True
    
    def mark_sent(self) -> bool:
        """
        Mark the campaign as sent.
        
        Returns:
            bool: True if status change was successful, False otherwise
        """
        if self.status != "sending":
            raise ValueError(
                f"Cannot mark campaign as sent from {self.get_status_display()} status. "
                f"Only sending campaigns can be marked as sent."
            )
        
        self.status = "sent"
        self.sent_at = timezone.now()
        self.save(update_fields=["status", "sent_at", "updated_at"])
        return True
    
    def mark_failed(self, reason: str = "") -> bool:
        """
        Mark the campaign as failed.
        
        Args:
            reason (str, optional): Reason for failure
            
        Returns:
            bool: True if status change was successful, False otherwise
        """
        if self.status not in ["sending", "scheduled"]:
            raise ValueError(
                f"Cannot mark campaign as failed from {self.get_status_display()} status. "
                f"Only sending or scheduled campaigns can fail."
            )
        
        self.status = "failed"
        self.save(update_fields=["status", "updated_at"])
        return True
    
    def pause(self) -> bool:
        """
        Pause the campaign (only works for sending campaigns).
        
        Returns:
            bool: True if pause was successful, False otherwise
        """
        if not self.can_be_paused:
            raise ValueError(
                f"Cannot pause campaign in {self.get_status_display()} status. "
                f"Only sending campaigns can be paused."
            )
        
        self.status = "paused"
        self.save(update_fields=["status", "updated_at"])
        return True
    
    def cancel(self) -> bool:
        """
        Cancel the campaign (only works for draft or scheduled campaigns).
        
        Returns:
            bool: True if cancellation was successful, False otherwise
        """
        if not self.can_be_cancelled:
            raise ValueError(
                f"Cannot cancel campaign in {self.get_status_display()} status. "
                f"Only draft or scheduled campaigns can be cancelled."
            )
        
        self.status = "draft"
        self.scheduled_at = None
        self.save(update_fields=["status", "scheduled_at", "updated_at"])
        return True
    
    # ── Analytics Update Methods ──
    
    def increment_sent(self, count: int = 1) -> None:
        """
        Increment the total_sent counter.
        
        Args:
            count (int): Number to increment by (default: 1)
        """
        self.total_sent = models.F('total_sent') + count
        self.save(update_fields=["total_sent", "updated_at"])
        self.refresh_from_db()
    
    def increment_opened(self, count: int = 1) -> None:
        """
        Increment the total_opened counter.
        
        Args:
            count (int): Number to increment by (default: 1)
        """
        self.total_opened = models.F('total_opened') + count
        self.save(update_fields=["total_opened", "updated_at"])
        self.refresh_from_db()
    
    def increment_clicked(self, count: int = 1) -> None:
        """
        Increment the total_clicked counter.
        
        Args:
            count (int): Number to increment by (default: 1)
        """
        self.total_clicked = models.F('total_clicked') + count
        self.save(update_fields=["total_clicked", "updated_at"])
        self.refresh_from_db()
    
    def increment_bounced(self, count: int = 1) -> None:
        """
        Increment the total_bounced counter.
        
        Args:
            count (int): Number to increment by (default: 1)
        """
        self.total_bounced = models.F('total_bounced') + count
        self.save(update_fields=["total_bounced", "updated_at"])
        self.refresh_from_db()
    
    # ── Utility Methods ──
    
    def get_summary(self) -> dict:
        """
        Get a summary of campaign metrics.
        
        Returns:
            dict: Dictionary containing campaign summary data
        """
        return {
            "id": self.id,
            "name": self.name,
            "status": self.get_status_display(),
            "subscriber_count": self.subscriber_count,
            "total_sent": self.total_sent,
            "total_opened": self.total_opened,
            "total_clicked": self.total_clicked,
            "total_bounced": self.total_bounced,
            "open_rate": float(self.open_rate),
            "click_rate": float(self.click_rate),
            "bounce_rate": float(self.bounce_rate),
            "created_at": self.created_at.isoformat(),
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
        }
