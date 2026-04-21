from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.fields import RichTextField


class AuthEmailTemplate(models.Model):
    class TemplateType(models.TextChoices):
        REGISTRATION_CONFIRMATION = "registration_confirmation", _("Registration Confirmation")
        SIGNIN_SUCCESS = "signin_success", _("Sign-In Success")

    template_type = models.CharField(
        max_length=50,
        choices=TemplateType.choices,
        verbose_name=_("Template Type"),
    )
    subject = models.CharField(max_length=255, verbose_name=_("Subject"))
    body_html = RichTextField(verbose_name=_("Body (HTML)"))
    body_text = models.TextField(
        verbose_name=_("Body (Plain Text)"),
        help_text=_("Used as fallback for email clients that do not render HTML."),
    )
    is_active = models.BooleanField(default=False, verbose_name=_("Active"))

    class Meta:
        verbose_name = _("Auth Email Template")
        verbose_name_plural = _("Auth Email Templates")

    def __str__(self):
        status = "active" if self.is_active else "inactive"
        return f"{self.get_template_type_display()} ({status})"

    def save(self, *args, **kwargs):
        if self.is_active:
            AuthEmailTemplate.objects.filter(
                template_type=self.template_type,
                is_active=True,
            ).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)


class CSVEmailTest(models.Model):
    """Model for tracking CSV-based email testing."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SENT = 'sent', 'Sent'
        FAILED = 'failed', 'Failed'
        SKIPPED = 'skipped', 'Skipped'

    # Test metadata
    test_name = models.CharField(max_length=255, verbose_name=_("Test Name"))
    csv_file = models.CharField(max_length=500, verbose_name=_("CSV File Path"))
    template_dir = models.CharField(max_length=500, verbose_name=_("Template Directory"))

    # Email details
    recipient_email = models.EmailField(verbose_name=_("Recipient Email"))
    recipient_role = models.CharField(max_length=100, verbose_name=_("Recipient Role"))
    email_subject = models.CharField(max_length=255, verbose_name=_("Email Subject"))
    template_used = models.CharField(max_length=255, verbose_name=_("Template Used"))

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_("Status")
    )
    error_message = models.TextField(blank=True, verbose_name=_("Error Message"))

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Sent At"))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Completed At"))

    # Performance metrics
    send_duration_ms = models.FloatField(null=True, blank=True, verbose_name=_("Send Duration (ms)"))

    class Meta:
        verbose_name = _("CSV Email Test")
        verbose_name_plural = _("CSV Email Tests")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['recipient_email', 'created_at']),
            models.Index(fields=['recipient_role', 'created_at']),
        ]

    def __str__(self):
        return f"{self.recipient_email} - {self.test_name} ({self.status})"

    def mark_sent(self, duration_ms: float = None):
        """Mark test as successfully sent."""
        from django.utils import timezone
        self.status = self.Status.SENT
        self.sent_at = timezone.now()
        self.completed_at = timezone.now()
        if duration_ms:
            self.send_duration_ms = duration_ms
        self.save()

    def mark_failed(self, error_message: str, duration_ms: float = None):
        """Mark test as failed with error message."""
        from django.utils import timezone
        self.status = self.Status.FAILED
        self.error_message = error_message
        self.completed_at = timezone.now()
        if duration_ms:
            self.send_duration_ms = duration_ms
        self.save()

    def mark_skipped(self):
        """Mark test as skipped."""
        from django.utils import timezone
        self.status = self.Status.SKIPPED
        self.completed_at = timezone.now()
        self.save()


class CSVEmailTestBatch(models.Model):
    """Model for tracking batch CSV email tests."""

    batch_id = models.CharField(max_length=100, unique=True, verbose_name=_("Batch ID"))
    csv_file = models.CharField(max_length=500, verbose_name=_("CSV File Path"))
    total_emails = models.PositiveIntegerField(verbose_name=_("Total Emails"))
    sent_count = models.PositiveIntegerField(default=0, verbose_name=_("Sent Count"))
    failed_count = models.PositiveIntegerField(default=0, verbose_name=_("Failed Count"))
    skipped_count = models.PositiveIntegerField(default=0, verbose_name=_("Skipped Count"))

    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Started At"))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Completed At"))

    # Results
    results_file = models.CharField(max_length=500, blank=True, verbose_name=_("Results File"))

    class Meta:
        verbose_name = _("CSV Email Test Batch")
        verbose_name_plural = _("CSV Email Test Batches")
        ordering = ['-started_at']

    def __str__(self):
        return f"Batch {self.batch_id} - {self.sent_count}/{self.total_emails} sent"

    def get_success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_emails == 0:
            return 0.0
        return (self.sent_count / self.total_emails) * 100

    def mark_completed(self, results_file: str = None):
        """Mark batch as completed."""
        from django.utils import timezone
        self.completed_at = timezone.now()
        if results_file:
            self.results_file = results_file
        self.save()
