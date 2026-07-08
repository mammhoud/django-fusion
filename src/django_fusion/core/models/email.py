"""
Email models for django-fusion.

Provides models for email templates, logs, and user groups for email distribution.
"""

import hashlib
import json
import logging
from datetime import timedelta

from django.db import models
from django.utils import timezone

logger = logging.getLogger(__name__)


class EmailLog(models.Model):
    """
    Audit trail for all email sending activities.

    Tracks delivery status, retries, and errors.
    """

    class Status(models.TextChoices):
        QUEUED = 'queued', 'Queued'
        SENDING = 'sending', 'Sending'
        SENT = 'sent', 'Sent'
        FAILED = 'failed', 'Failed'
        BOUNCED = 'bounced', 'Bounced'

    # Core fields
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    recipient = models.EmailField(db_index=True)
    subject = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.QUEUED,
        db_index=True
    )

    # Template and content
    template_used = models.CharField(max_length=255, blank=True)
    message_body = models.TextField(blank=True)

    # Error tracking
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    last_retry_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='email_logs'
    )
    group_name = models.CharField(max_length=100, blank=True)
    task_id = models.CharField(max_length=255, blank=True, db_index=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    # Security fields
    invitation_token = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        default=None,
        unique=True,
        db_index=True,
        help_text="Secure token for invitation links"
    )
    token_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Token expiration time (default: 7 days)"
    )

    class Meta:
        app_label = 'django_fusion'
        db_table = 'email_log'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['status', 'timestamp']),
            models.Index(fields=['recipient', 'timestamp']),
            models.Index(fields=['task_id']),
            models.Index(fields=['recipient', 'status', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.recipient} - {self.subject} ({self.status})"

    def mark_sent(self):
        """Mark email as successfully sent."""
        self.status = self.Status.SENT
        self.sent_at = timezone.now()
        self.save(update_fields=['status', 'sent_at', 'updated_at'])

    def mark_failed(self, error_message: str):
        """Mark email as failed with error message."""
        self.status = self.Status.FAILED
        self.error_message = error_message
        self.save(update_fields=['status', 'error_message', 'updated_at'])

    def increment_retry(self):
        """Increment retry count and update timestamp."""
        self.retry_count += 1
        self.last_retry_at = timezone.now()
        self.save(update_fields=['retry_count', 'last_retry_at', 'updated_at'])


class EmailTemplate(models.Model):
    """
    Enhanced email template for reusable email content.

    Supports both simple and advanced usage:
    - Simple: Just name, subject, html_content (backward compatible)
    - Advanced: Scheduling, versioning, multiple sources, metrics, etc.
    """

    # ============================================================================
    # BASIC FIELDS (Original Simple Model - Backward Compatible)
    # ============================================================================
    name = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="Template name for internal reference"
    )

    subject = models.CharField(
        max_length=255,
        help_text="Email subject (for simple usage, use subject_template for dynamic content)"
    )

    html_content = models.TextField(
        help_text="HTML email content"
    )

    text_content = models.TextField(
        blank=True,
        help_text="Plain text fallback content"
    )

    description = models.TextField(
        blank=True,
        help_text="Template description"
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this template can be used"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ============================================================================
    # ADVANCED FIELDS (From Pipelines Model)
    # ============================================================================

    # Scheduling
    go_live_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Schedule template to become active at this date/time"
    )

    expire_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Schedule template to expire at this date/time"
    )

    # Template Source Configuration
    TEMPLATE_SOURCE_CHOICES = [
        ("inline", "Inline Content"),
        ("file", "Uploaded Files"),
        ("path", "Template Path"),
        ("external", "External URL"),
    ]

    template_source = models.CharField(
        max_length=20,
        choices=TEMPLATE_SOURCE_CHOICES,
        default="inline",
        help_text="Where the template content comes from"
    )

    template_path = models.CharField(
        max_length=255,
        blank=True,
        help_text="Django template path (e.g., 'emails/newsletter.html')"
    )

    external_url = models.URLField(
        blank=True,
        help_text="External URL to fetch template from"
    )

    # Subject & Preview (Enhanced)
    subject_template = models.CharField(
        max_length=255,
        blank=True,
        help_text="Subject template with variables like {{ title }}, {{ user_name }}"
    )

    preview_text = models.CharField(
        max_length=255,
        blank=True,
        help_text="Preview text shown in email clients"
    )

    # Template Files
    html_file = models.FileField(
        upload_to="email_templates/html/%Y/%m/%d/",
        blank=True,
        null=True,
        help_text="Upload HTML template file"
    )

    css_file = models.FileField(
        upload_to="email_templates/css/%Y/%m/%d/",
        blank=True,
        null=True,
        help_text="Upload CSS stylesheet file"
    )

    css_content = models.TextField(
        blank=True,
        help_text="Inline CSS styles"
    )

    # Template Metadata
    TEMPLATE_TYPE_CHOICES = [
        ("invitation", "Invitation"),
        ("notification", "Notification"),
        ("newsletter", "Newsletter"),
        ("transactional", "Transactional"),
        ("welcome", "Welcome"),
        ("password_reset", "Password Reset"),
        ("order_confirmation", "Order Confirmation"),
        ("system_alert", "System Alert"),
        ("campaign", "Campaign"),
        ("promotional", "Promotional"),
        ("abandoned_cart", "Abandoned Cart"),
        ("receipt", "Receipt"),
        ("feedback", "Feedback"),
        ("announcement", "Announcement"),
    ]

    template_type = models.CharField(
        max_length=50,
        choices=TEMPLATE_TYPE_CHOICES,
        default="notification",
        help_text="Template category"
    )

    LANGUAGE_CHOICES = [
        ("en", "English"),
        ("es", "Spanish"),
        ("fr", "French"),
        ("de", "German"),
        ("it", "Italian"),
        ("pt", "Portuguese"),
        ("ru", "Russian"),
        ("zh", "Chinese"),
        ("ja", "Japanese"),
        ("ar", "Arabic"),
        ("ko", "Korean"),
        ("hi", "Hindi"),
        ("tr", "Turkish"),
        ("nl", "Dutch"),
        ("pl", "Polish"),
    ]

    language = models.CharField(
        max_length=10,
        default="en",
        choices=LANGUAGE_CHOICES,
        help_text="Template language"
    )

    version = models.PositiveIntegerField(
        default=1,
        help_text="Template version number"
    )

    # Status & Behavior
    is_default = models.BooleanField(
        default=False,
        help_text="Mark as default template for this type"
    )

    is_system = models.BooleanField(
        default=False,
        help_text="System templates cannot be deleted"
    )

    is_draft = models.BooleanField(
        default=False,
        help_text="Draft templates are not available for use"
    )

    # Email Settings
    reply_to_email = models.EmailField(
        blank=True,
        help_text="Reply-to address"
    )

    from_email = models.EmailField(
        blank=True,
        help_text="Sender email address"
    )

    from_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Sender display name"
    )

    unsubscribe_url = models.URLField(
        blank=True,
        help_text="Unsubscribe link"
    )

    # Categorization & Tagging
    category = models.CharField(
        max_length=100,
        blank=True,
        help_text="Category for grouping templates"
    )

    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Tags for filtering and organizing"
    )

    slug = models.SlugField(
        max_length=200,
        blank=True,
        help_text="URL-friendly identifier"
    )

    # Caching & Performance
    cache_key = models.CharField(
        max_length=100,
        blank=True,
        help_text="Auto-generated cache key"
    )

    last_rendered = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When template was last rendered"
    )

    render_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times template has been rendered"
    )

    # Performance Metrics
    open_rate = models.FloatField(
        default=0.0,
        help_text="Historical open rate percentage"
    )

    click_rate = models.FloatField(
        default=0.0,
        help_text="Historical click rate percentage"
    )

    conversion_rate = models.FloatField(
        default=0.0,
        help_text="Historical conversion rate percentage"
    )

    bounce_rate = models.FloatField(
        default=0.0,
        help_text="Historical bounce rate percentage"
    )

    class Meta:
        app_label = 'django_fusion'
        db_table = 'email_template'
        ordering = ['template_type', 'name', 'version']
        indexes = [
            models.Index(fields=['template_type', 'is_active']),
            models.Index(fields=['language', 'is_active']),
            models.Index(fields=['is_default', 'is_active']),
            models.Index(fields=['template_source']),
            models.Index(fields=['cache_key']),
            models.Index(fields=['go_live_at']),
            models.Index(fields=['expire_at']),
            models.Index(fields=['category']),
            models.Index(fields=['is_draft', 'is_active']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["template_type", "language", "version"],
                condition=models.Q(is_default=True),
                name="unique_default_template_per_type_language_version",
            )
        ]

    def __str__(self):
        if self.template_source == "path" and self.template_path:
            return f"{self.name} ({self.template_path})"
        return f"{self.name} ({self.get_template_type_display()} - {self.get_language_display()})"

    def save(self, *args, **kwargs):
        """Enhanced save with validation and auto-population."""
        # Backward compatibility: copy subject to subject_template if not set
        if not self.subject_template and self.subject:
            self.subject_template = self.subject

        # Ensure only one template is marked as default per type and language
        if self.is_default and not self.is_system:
            EmailTemplate.objects.filter(
                template_type=self.template_type,
                language=self.language,
                is_default=True,
            ).exclude(pk=self.pk).update(is_default=False)

        # Validate scheduling
        if self.go_live_at and self.expire_at and self.go_live_at >= self.expire_at:
            raise ValueError("go_live_at must be before expire_at")

        # Auto-generate slug from name if not set
        if not self.slug and self.name:
            from django.utils.text import slugify
            self.slug = slugify(self.name)

        # Generate cache key
        self.cache_key = self._generate_cache_key()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Prevent deletion of system templates."""
        if self.is_system:
            raise models.ProtectedError("Cannot delete system templates.", [self])
        super().delete(*args, **kwargs)

    def _generate_cache_key(self):
        """Generate a unique cache key for this template."""
        template_data = {
            "id": str(self.id) if self.id else "",
            "name": self.name,
            "template_source": self.template_source,
            "template_path": self.template_path,
            "version": self.version,
            "updated_at": str(self.updated_at) if self.updated_at else "",
        }
        data_str = json.dumps(template_data, sort_keys=True)
        return f"template_{hashlib.md5(data_str.encode()).hexdigest()}"

    @property
    def is_live(self):
        """Check if template is currently live based on scheduling."""
        now = timezone.now()

        if self.is_draft:
            return False
        if not self.is_active:
            return False
        if self.go_live_at and now < self.go_live_at:
            return False
        if self.expire_at and now > self.expire_at:
            return False

        return True

    @property
    def scheduled_status(self):
        """Get human-readable scheduling status."""
        now = timezone.now()

        if self.is_draft:
            return "Draft"
        if not self.is_active:
            return "Inactive"
        if self.go_live_at and now < self.go_live_at:
            days_until = (self.go_live_at - now).days
            return f"Scheduled (in {days_until} days)"
        if self.expire_at and now > self.expire_at:
            return "Expired"
        if self.go_live_at and self.expire_at:
            days_left = (self.expire_at - now).days
            return f"Active ({days_left} days left)"
        return "Active"

    @classmethod
    def get_default_for_type(cls, template_type, language="en", include_scheduled=True):
        """Get default template for a specific type and language."""
        from django.db.models import Q

        try:
            qs = cls.objects.filter(
                template_type=template_type,
                language=language,
                is_default=True,
                is_active=True,
                is_draft=False,
            )

            if not include_scheduled:
                now = timezone.now()
                qs = qs.filter(
                    Q(go_live_at__isnull=True) | Q(go_live_at__lte=now),
                    Q(expire_at__isnull=True) | Q(expire_at__gte=now),
                )

            return qs.first()
        except cls.DoesNotExist:
            return None


class UserGroup(models.Model):
    """
    User groups for targeted email distribution.
    Users can belong to multiple groups.
    """

    name = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True)
    score = models.IntegerField(default=0)
    users = models.ManyToManyField('auth.User', related_name='email_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'django_fusion'
        db_table = 'user_group'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_recipients(self):
        """Get all email addresses in this group."""
        return list(self.users.values_list('email', flat=True))


__all__ = ['EmailLog', 'EmailTemplate', 'UserGroup']
