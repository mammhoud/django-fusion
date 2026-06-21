"""
Newsletter Subscriber Model
"""
import secrets

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Subscriber(models.Model):
    """
    Newsletter subscriber with double opt-in support.
    """

    STATUS_CHOICES = [
        ("pending", _("Pending Confirmation")),
        ("confirmed", _("Confirmed")),
        ("unsubscribed", _("Unsubscribed")),
        ("bounced", _("Bounced")),
    ]

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

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name=_("Status"),
        db_index=True,
    )

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

    # Source tracking
    source = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name=_("Source"),
        help_text=_("Where the subscriber signed up from"),
    )

    class Meta:
        verbose_name = _("Subscriber")
        verbose_name_plural = _("Subscribers")
        ordering = ["-created_at"]
        db_table = "newsletter_subscriber"
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["confirmation_token"]),
            models.Index(fields=["unsubscribe_token"]),
        ]

    def __str__(self):
        return f"{self.email} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        # Generate tokens if not set
        if not self.confirmation_token:
            self.confirmation_token = self._generate_token()
        if not self.unsubscribe_token:
            self.unsubscribe_token = self._generate_token()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_token() -> str:
        """Generate a secure random token."""
        return secrets.token_urlsafe(32)

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
        Unsubscribe from the newsletter.

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

    @property
    def is_active(self) -> bool:
        """Check if subscriber is active (confirmed and not unsubscribed)."""
        return self.status == "confirmed"
