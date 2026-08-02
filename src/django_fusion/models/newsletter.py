"""Reusable newsletter model base for Fusion sites."""

import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_fusion.models.default import DefaultBase


class AbstractNewsletter(DefaultBase):
    """Shared newsletter fields, scheduling, and delivery metrics.

    Site models supply their own Wagtail body/content blocks and admin panels.
    """

    title = models.CharField(max_length=255, verbose_name=_("Newsletter Title"))
    subject = models.CharField(max_length=255, verbose_name=_("Email Subject"))
    preview_text = models.TextField(
        max_length=500,
        blank=True,
        verbose_name=_("Preview Text"),
        help_text=_("Short summary text displayed in some email clients."),
    )
    header_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Header Image"),
    )
    template = models.ForeignKey(
        "shared.EmailTemplate",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Email Template"),
        help_text=_("HTML template for rendering this newsletter."),
    )

    AUDIENCE_CHOICES = [
        ("ALL", _("All Users")),
        ("STUDENTS", _("Students Only")),
        ("INSTRUCTORS", _("Instructors Only")),
        ("ADMINS", _("Administrators Only")),
        ("SPECIFIC", _("Specific Users/Groups")),
    ]
    audience_type = models.CharField(
        max_length=15,
        choices=AUDIENCE_CHOICES,
        default="ALL",
    )
    target_user_levels = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Target User Levels"),
        help_text=_("Comma-separated user levels, e.g. UNDERGRAD,GRADUATE"),
    )

    SCHEDULE_CHOICES = [
        ("DRAFT", _("Save as Draft")),
        ("IMMEDIATE", _("Send Immediately")),
        ("SCHEDULED", _("Schedule for Later")),
        ("TEST", _("Send Test Email")),
    ]
    schedule_type = models.CharField(
        max_length=15,
        choices=SCHEDULE_CHOICES,
        default="DRAFT",
    )
    scheduled_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Scheduled Date"),
    )

    sent_date = models.DateTimeField(null=True, blank=True, editable=False)
    total_recipients = models.PositiveIntegerField(default=0, editable=False)
    open_count = models.PositiveIntegerField(default=0, editable=False)
    click_count = models.PositiveIntegerField(default=0, editable=False)
    track_opens = models.BooleanField(default=True, verbose_name=_("Track Opens"))
    track_clicks = models.BooleanField(default=True, verbose_name=_("Track Clicks"))
    include_unsubscribe = models.BooleanField(
        default=True,
        verbose_name=_("Include Unsubscribe Link"),
    )
    important_announcement = models.BooleanField(default=False)
    show_in_portal = models.BooleanField(default=True)
    test_email_addresses = models.TextField(
        blank=True,
        help_text=_("Comma-separated test email addresses"),
    )
    newsletter_id = models.CharField(max_length=50, unique=True, editable=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.newsletter_id:
            self.newsletter_id = f"NL-{uuid.uuid4().hex[:8].upper()}"
        if self.live and not self.sent_date and self.schedule_type == "IMMEDIATE":
            self.sent_date = timezone.now()
        super().save(*args, **kwargs)

    @property
    def is_sent(self):
        return bool(self.sent_date)

    @property
    def open_rate(self):
        return (self.open_count / self.total_recipients) * 100 if self.total_recipients else 0

    @property
    def click_rate(self):
        return (self.click_count / self.total_recipients) * 100 if self.total_recipients else 0

    @property
    def status(self):
        if not self.live:
            return _("Draft")
        if self.sent_date:
            return _("Sent")
        if self.scheduled_date and self.scheduled_date > timezone.now():
            return _("Scheduled")
        return _("Published")
