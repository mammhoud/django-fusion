import logging

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel

from crafts_ai.content.models.default import DefaultBase


class NewsletterSubscription(DefaultBase):
    """
    Tracks user newsletter subscriptions and preferences.
    Supports both authenticated users and guest subscribers.
    """

    # ------------------------------------------------------------------
    # FIELDS
    # ------------------------------------------------------------------
    person = models.ForeignKey(
        getattr(settings, 'PROFILE_MODEL', 'auth.User'),
        on_delete=models.CASCADE,
        related_name="newsletter_subscriptions",
        verbose_name=_("User"),
        null=True,
        blank=True,
        help_text=_("Linked user account (optional for guest subscribers)."),
    )

    email = models.EmailField(
        verbose_name=_("Email Address"),
        help_text=_("Primary contact email for receiving newsletters."),
    )

    is_subscribed = models.BooleanField(
        default=True,
        verbose_name=_("Is Subscribed"),
        help_text=_("Uncheck to unsubscribe from this newsletter type."),
    )

    class SubscriptionType(models.TextChoices):
        ALL = "ALL", _("All Newsletters")
        IMPORTANT = "IMPORTANT", _("Important Announcements Only")
        COURSE = "COURSE", _("Course-related Updates")
        DEPARTMENT = "DEPARTMENT", _("Department News Only")

    subscription_type = models.CharField(
        max_length=20,
        choices=SubscriptionType.choices,
        default=SubscriptionType.ALL,
        verbose_name=_("Subscription Type"),
    )

    class FormatType(models.TextChoices):
        HTML = "HTML", _("HTML")
        TEXT = "TEXT", _("Plain Text")

    preferred_format = models.CharField(
        max_length=10,
        choices=FormatType.choices,
        default=FormatType.HTML,
        verbose_name=_("Preferred Format"),
        help_text=_("Preferred newsletter format."),
    )

    last_sent = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Last Newsletter Sent"),
    )

    unsubscribed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Unsubscribed At"),
        help_text=_("Date and time when user unsubscribed."),
    )

    # ------------------------------------------------------------------
    # WAGTAIL ADMIN PANELS
    # ------------------------------------------------------------------
    panels = [
        MultiFieldPanel(
            [
                FieldPanel("email"),
                FieldRowPanel(
                    [
                        FieldPanel("subscription_type"),
                        FieldPanel("preferred_format"),
                    ]
                ),
            ],
            heading=_("Subscriber Information"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("is_subscribed"),
                FieldPanel("last_sent"),
                FieldPanel("unsubscribed_at"),
            ],
            heading=_("Subscription Status"),
        ),
    ]

    # ------------------------------------------------------------------
    # META
    # ------------------------------------------------------------------
    class Meta:
        verbose_name = _("Newsletter Subscription")
        verbose_name_plural = _("Newsletter Subscriptions")
        unique_together = ["email", "subscription_type"]
        ordering = ["-created_at"]

    # ------------------------------------------------------------------
    # STRING REPRESENTATION
    # ------------------------------------------------------------------
    def __str__(self):
        return f"{self.email} ({self.get_subscription_type_display()})"

    # ------------------------------------------------------------------
    # BUSINESS LOGIC
    # ------------------------------------------------------------------
    def mark_unsubscribed(self):
        """Mark the subscriber as unsubscribed and set timestamp."""
        if self.is_subscribed:
            self.is_subscribed = False
            self.unsubscribed_at = timezone.now()
            self.save(update_fields=["is_subscribed", "unsubscribed_at"])
            logger.info(f"User {self.email} unsubscribed from {self.subscription_type}.")

    def mark_sent(self):
        """Update the timestamp for last newsletter sent."""
        self.last_sent = timezone.now()
        self.save(update_fields=["last_sent"])
