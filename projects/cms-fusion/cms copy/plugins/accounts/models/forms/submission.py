"""
Form Submission Model for tracking contact form submissions.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.models import Page


class FormSubmission(models.Model):
    """
    Stores form submissions for tracking and analytics.

    Attributes:
        form_id: Unique identifier for the form (from ContactFormBlock)
        page: The page where the form was submitted
        data: JSON field containing all form field values
        submitted_at: Timestamp of submission
        ip_address: Client IP address
        user_agent: Client browser user agent
        email_sent: Whether notification email was sent
        email_sent_at: Timestamp when email was sent
    """

    form_id = models.CharField(
        max_length=50,
        verbose_name=_("Form ID"),
        help_text=_("Unique identifier for the form"),
        db_index=True,
    )

    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name="form_submissions",
        verbose_name=_("Page"),
        help_text=_("The page where the form was submitted"),
        null=True,
        blank=True,
    )

    data = models.JSONField(
        verbose_name=_("Form Data"),
        help_text=_("JSON containing all submitted form field values"),
        default=dict,
    )

    submitted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Submitted At"),
        db_index=True,
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_("IP Address"),
    )

    user_agent = models.TextField(
        blank=True,
        default="",
        verbose_name=_("User Agent"),
    )

    email_sent = models.BooleanField(
        default=False,
        verbose_name=_("Email Sent"),
        help_text=_("Whether notification email was sent"),
    )

    email_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Email Sent At"),
    )

    # Optional: Track if submission was processed/read
    is_read = models.BooleanField(
        default=False,
        verbose_name=_("Is Read"),
    )

    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Read At"),
    )

    class Meta:
        verbose_name = _("Form Submission")
        verbose_name_plural = _("Form Submissions")
        ordering = ["-submitted_at"]
        app_label = 'accounts'
        indexes = [
            models.Index(fields=["form_id", "submitted_at"]),
            models.Index(fields=["email_sent"]),
        ]

    def __str__(self):
        return f"{self.form_id} - {self.submitted_at.strftime('%Y-%m-%d %H:%M')}"

    def get_email(self):
        """Extract email from form data if present."""
        return self.data.get("email", "")

    def get_name(self):
        """Extract name from form data if present."""
        return self.data.get("name", "")

    def mark_as_read(self):
        """Mark submission as read."""
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=["is_read", "read_at"])

    def mark_email_sent(self):
        """Mark that notification email was sent."""
        from django.utils import timezone
        self.email_sent = True
        self.email_sent_at = timezone.now()
        self.save(update_fields=["email_sent", "email_sent_at"])
