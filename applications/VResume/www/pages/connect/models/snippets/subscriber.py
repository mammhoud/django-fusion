"""
🔔 Communications Subscriber Model
===================================
Enhanced newsletter subscriber with notification preferences and double opt-in support.
Tracks subscription status, preferences, and engagement metrics.
"""
import secrets

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Subscriber(models.Model):
    """
    📧 Enhanced Newsletter Subscriber Model
    
    Features:
    - Double opt-in confirmation
    - Notification preferences (blog, newsletter, projects)
    - Secure token-based unsubscribe
    - Status tracking (pending, confirmed, unsubscribed, bounced)
    - Source tracking for analytics
    - Engagement metrics
    """
    
    STATUS_CHOICES = [
        ("pending", _("Pending Confirmation")),
        ("confirmed", _("Confirmed")),
        ("unsubscribed", _("Unsubscribed")),
        ("bounced", _("Bounced")),
    ]
    
    # ── Basic Information ──
    email = models.EmailField(
        unique=True,
        verbose_name=_("Email Address"),
        db_index=True,
    )
    
    name = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name=_("Name"),
    )
    
    # ── Status Management ──
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name=_("Status"),
        db_index=True,
    )
    
    # ── Notification Preferences ──
    blog_notifications = models.BooleanField(
        default=True,
        verbose_name=_("Blog Notifications"),
        help_text=_("Receive notifications when new blog posts are published"),
    )
    
    newsletter_notifications = models.BooleanField(
        default=True,
        verbose_name=_("Newsletter Notifications"),
        help_text=_("Receive weekly newsletter updates"),
    )
    
    project_updates = models.BooleanField(
        default=False,
        verbose_name=_("Project Updates"),
        help_text=_("Receive updates about new projects and portfolio items"),
    )
    
    # ── Security Tokens ──
    confirmation_token = models.CharField(
        max_length=64,
        blank=True,
        default="",
        verbose_name=_("Confirmation Token"),
    )
    
    unsubscribe_token = models.CharField(
        max_length=64,
        blank=True,
        default="",
        verbose_name=_("Unsubscribe Token"),
    )
    
    # ── Timestamps ──
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Confirmed At"),
    )
    
    unsubscribed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Unsubscribed At"),
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
    )
    
    # ── Analytics ──
    source = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name=_("Source"),
        help_text=_("Where the subscription was created from (e.g., blog, homepage, footer)"),
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_("IP Address"),
        help_text=_("IP address at time of subscription"),
    )
    
    user_agent = models.TextField(
        blank=True,
        default="",
        verbose_name=_("User Agent"),
        help_text=_("Browser/device information at time of subscription"),
    )
    
    class Meta:
        verbose_name = _("Subscriber")
        verbose_name_plural = _("Subscribers")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["confirmation_token"]),
            models.Index(fields=["unsubscribe_token"]),
            models.Index(fields=["blog_notifications", "status"]),
            models.Index(fields=["newsletter_notifications", "status"]),
        ]
    
    def __str__(self):
        return f"{self.email} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        """Generate tokens if not set."""
        if not self.confirmation_token:
            self.confirmation_token = self._generate_token()
        if not self.unsubscribe_token:
            self.unsubscribe_token = self._generate_token()
        super().save(*args, **kwargs)
    
    @staticmethod
    def _generate_token() -> str:
        """Generate a secure random token."""
        return secrets.token_urlsafe(32)
    
    # ── Status Management Methods ──
    
    def confirm(self) -> bool:
        """
        Confirm the subscription.
        
        Returns:
            True if confirmation was successful, False if already confirmed
        """
        if self.status == "confirmed":
            return False
        
        self.status = "confirmed"
        self.confirmed_at = timezone.now()
        self.save(update_fields=["status", "confirmed_at", "updated_at"])
        return True
    
    def unsubscribe(self) -> bool:
        """
        Unsubscribe from all notifications.
        
        Returns:
            True if unsubscription was successful
        """
        if self.status == "unsubscribed":
            return False
        
        self.status = "unsubscribed"
        self.unsubscribed_at = timezone.now()
        self.save(update_fields=["status", "unsubscribed_at", "updated_at"])
        return True
    
    def mark_bounced(self) -> None:
        """Mark the subscriber as bounced (invalid email)."""
        self.status = "bounced"
        self.save(update_fields=["status", "updated_at"])
    
    def regenerate_tokens(self) -> None:
        """Regenerate confirmation and unsubscribe tokens."""
        self.confirmation_token = self._generate_token()
        self.unsubscribe_token = self._generate_token()
        self.save(update_fields=["confirmation_token", "unsubscribe_token", "updated_at"])
    
    # ── Preference Management Methods ──
    
    def update_preferences(self, blog=None, newsletter=None, projects=None) -> None:
        """
        Update notification preferences.
        
        Args:
            blog (bool, optional): Enable/disable blog notifications
            newsletter (bool, optional): Enable/disable newsletter notifications
            projects (bool, optional): Enable/disable project updates
        """
        if blog is not None:
            self.blog_notifications = blog
        if newsletter is not None:
            self.newsletter_notifications = newsletter
        if projects is not None:
            self.project_updates = projects
        self.save(update_fields=["blog_notifications", "newsletter_notifications", "project_updates", "updated_at"])
    
    # ── Property Methods ──
    
    @property
    def is_active(self) -> bool:
        """Check if subscriber is active (confirmed and not unsubscribed)."""
        return self.status == "confirmed"
    
    @property
    def has_any_notifications_enabled(self) -> bool:
        """Check if any notification type is enabled."""
        return self.blog_notifications or self.newsletter_notifications or self.project_updates
    
    @property
    def days_since_subscription(self) -> int:
        """Get number of days since subscription."""
        return (timezone.now() - self.created_at).days
    
    @property
    def is_recent(self) -> bool:
        """Check if subscription is recent (less than 7 days)."""
        return self.days_since_subscription < 7
