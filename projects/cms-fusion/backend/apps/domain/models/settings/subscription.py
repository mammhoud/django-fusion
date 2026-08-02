from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel

from django_fusion.models.default import DefaultBase
from django_fusion.models.settings import AbstractNewsletterSubscription


class NewsletterSubscription(DefaultBase, AbstractNewsletterSubscription):
    """Tracks user newsletter subscriptions and preferences."""

    person = models.ForeignKey(
        getattr(settings, "PROFILE_MODEL", "auth.User"),
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

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("email"),
                FieldRowPanel(
                    [FieldPanel("subscription_type"), FieldPanel("preferred_format")]
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

    class Meta:
        app_label = "shared"
        verbose_name = _("Newsletter Subscription")
        verbose_name_plural = _("Newsletter Subscriptions")
        unique_together = ["email", "subscription_type"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email} ({self.get_subscription_type_display()})"
