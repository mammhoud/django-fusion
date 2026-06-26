"""
Email models for Django Relay.

Provides models for tracking email logs and templates.
"""

import secrets
from datetime import timedelta

from django.db import models
from django.utils import timezone


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
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
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
        app_label = 'crafts_ai'
        db_table = 'email_log'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['status', 'timestamp']),
            models.Index(fields=['recipient', 'timestamp']),
            models.Index(fields=['task_id']),
            # Composite index for email log queries
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

    def generate_invitation_token(self, expires_in_days: int = 7) -> str:
        """
        Generate a secure invitation token.

        Args:
            expires_in_days: Number of days until token expires (default: 7)

        Returns:
            The generated token
        """
        self.invitation_token = secrets.token_urlsafe(32)
        self.token_expires_at = timezone.now() + timedelta(days=expires_in_days)
        self.save(update_fields=['invitation_token', 'token_expires_at', 'updated_at'])
        return self.invitation_token

    def is_token_valid(self) -> bool:
        """Check if invitation token is still valid."""
        if not self.invitation_token or not self.token_expires_at:
            return False
        return timezone.now() < self.token_expires_at

    def invalidate_token(self):
        """Invalidate the invitation token."""
        self.invitation_token = None
        self.token_expires_at = None
        self.save(update_fields=['invitation_token', 'token_expires_at', 'updated_at'])


class EmailTemplate(models.Model):
    """
    Enhanced email template for reusable email content.

    Supports both simple and advanced usage:
    - Simple: Just name, subject, html_content (backward compatible)
    - Advanced: Scheduling, versioning, multiple sources, metrics, etc.

    This model was enhanced by merging features from the pipelines EmailTemplate.
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
        app_label = 'crafts_ai'
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
        import hashlib
        import json

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

    # ============================================================================
    # PROPERTIES
    # ============================================================================

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

    @property
    def time_until_live(self):
        """Get time until template goes live (if scheduled)."""
        if self.go_live_at and timezone.now() < self.go_live_at:
            return self.go_live_at - timezone.now()
        return None

    @property
    def time_until_expire(self):
        """Get time until template expires (if scheduled)."""
        if self.expire_at and timezone.now() < self.expire_at:
            return self.expire_at - timezone.now()
        return None

    # ============================================================================
    # SCHEDULING METHODS
    # ============================================================================

    def schedule_for(self, go_live_at=None, expire_at=None):
        """Schedule template activation and expiration."""
        if go_live_at:
            self.go_live_at = go_live_at
        if expire_at:
            self.expire_at = expire_at
        self.save()

    def activate_immediately(self):
        """Activate template immediately (clear scheduling)."""
        self.go_live_at = None
        self.expire_at = None
        self.is_active = True
        self.is_draft = False
        self.save()

    def expire_immediately(self):
        """Expire template immediately."""
        self.expire_at = timezone.now()
        self.save()

    def mark_as_draft(self):
        """Mark template as draft."""
        self.is_draft = True
        self.save()

    def publish(self):
        """Publish template (clear draft status)."""
        self.is_draft = False
        self.save()

    # ============================================================================
    # PERFORMANCE METRICS METHODS
    # ============================================================================

    def update_metrics(self, opens=0, clicks=0, conversions=0, bounces=0, deliveries=0):
        """Update template performance metrics."""
        if deliveries > 0:
            self.open_rate = (opens / deliveries) * 100
            self.click_rate = (clicks / deliveries) * 100
            self.conversion_rate = (conversions / deliveries) * 100
            self.bounce_rate = (bounces / deliveries) * 100

        self.save(update_fields=["open_rate", "click_rate", "conversion_rate", "bounce_rate"])

    def reset_metrics(self):
        """Reset all performance metrics to zero."""
        self.open_rate = 0.0
        self.click_rate = 0.0
        self.conversion_rate = 0.0
        self.bounce_rate = 0.0
        self.save(update_fields=["open_rate", "click_rate", "conversion_rate", "bounce_rate"])

    # ============================================================================
    # CLASS METHODS
    # ============================================================================

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
            # Fallback to any active template of this type and language
            try:
                qs = cls.objects.filter(
                    template_type=template_type,
                    language=language,
                    is_active=True,
                    is_draft=False,
                ).order_by("-is_default", "-version", "-created_at")

                if not include_scheduled:
                    now = timezone.now()
                    qs = qs.filter(
                        Q(go_live_at__isnull=True) | Q(go_live_at__lte=now),
                        Q(expire_at__isnull=True) | Q(expire_at__gte=now),
                    )

                return qs.first()
            except cls.DoesNotExist:
                return None

    @classmethod
    def get_live_templates(cls, template_type=None, language=None):
        """Get all live templates, optionally filtered by type and language."""
        from django.db.models import Q

        now = timezone.now()

        qs = cls.objects.filter(is_active=True, is_draft=False).filter(
            Q(go_live_at__isnull=True) | Q(go_live_at__lte=now),
            Q(expire_at__isnull=True) | Q(expire_at__gte=now),
        )

        if template_type:
            qs = qs.filter(template_type=template_type)

        if language:
            qs = qs.filter(language=language)

        return qs.order_by("template_type", "name")

    @classmethod
    def find_for_object(cls, obj, template_type=None, language=None, include_scheduled=True):
        """
        Find the appropriate template for a model object.

        Infers template_type from the object's model name if not provided.
        Infers language from ``obj.language`` if available.
        """
        if not template_type:
            model_name = obj._meta.model_name.lower()
            if "invitation" in model_name:
                template_type = "invitation"
            elif "newsletter" in model_name:
                template_type = "newsletter"
            elif "user" in model_name:
                template_type = "welcome"
            else:
                template_type = "notification"

        if not language and hasattr(obj, "language"):
            language = obj.language

        return cls.get_default_for_type(template_type, language or "en", include_scheduled)

    @classmethod
    def cleanup_expired(cls):
        """Deactivate expired templates."""
        import logging
        logger = logging.getLogger(__name__)

        now = timezone.now()
        expired = cls.objects.filter(
            is_active=True,
            expire_at__lt=now,
            expire_at__isnull=False,
        )

        count = expired.count()
        expired.update(is_active=False)

        logger.info(f"Deactivated {count} expired email templates")
        return count

    @classmethod
    def activate_scheduled(cls):
        """Activate templates that have reached their go_live_at date."""
        import logging
        logger = logging.getLogger(__name__)

        now = timezone.now()
        scheduled = cls.objects.filter(
            is_active=False,
            go_live_at__lte=now,
            go_live_at__isnull=False,
        )

        count = scheduled.count()
        scheduled.update(is_active=True)

        logger.info(f"Activated {count} scheduled email templates")
        return count

    # ============================================================================
    # FILE UPLOAD HANDLING METHODS
    # ============================================================================

    def update_html_from_file(self):
        """Read HTML file content and update the html_content field."""
        import logging
        logger = logging.getLogger(__name__)

        if self.html_file and self.html_file.name:
            try:
                self.html_file.open("rb")
                raw = self.html_file.read()
                content = raw.decode("utf-8") if isinstance(raw, bytes) else raw
                self.html_content = content
                logger.info(f"Updated HTML content from file for template: {self.name}")
                return True
            except Exception as e:
                logger.error(f"Failed to read HTML file for template {self.name}: {str(e)}")
                return False
            finally:
                if hasattr(self.html_file, "close"):
                    self.html_file.close()
        return False

    def update_css_from_file(self):
        """Read CSS file content and update the css_content field."""
        import logging
        logger = logging.getLogger(__name__)

        if self.css_file and self.css_file.name:
            try:
                self.css_file.open("rb")
                raw = self.css_file.read()
                content = raw.decode("utf-8") if isinstance(raw, bytes) else raw
                self.css_content = content
                logger.info(f"Updated CSS content from file for template: {self.name}")
                return True
            except Exception as e:
                logger.error(f"Failed to read CSS file for template {self.name}: {str(e)}")
                return False
            finally:
                if hasattr(self.css_file, "close"):
                    self.css_file.close()
        return False

    def create_file_from_content(self, file_type="html"):
        """Create a physical file from inline content."""
        from django.core.files.base import ContentFile

        if file_type == "html" and self.html_content and not self.html_file:
            filename = f"{self.slug or self.name.lower().replace(' ', '_')}.html"
            self.html_file.save(filename, ContentFile(self.html_content.encode("utf-8")), save=False)
            return True
        elif file_type == "css" and self.css_content and not self.css_file:
            filename = f"{self.slug or self.name.lower().replace(' ', '_')}.css"
            self.css_file.save(filename, ContentFile(self.css_content.encode("utf-8")), save=False)
            return True
        return False

    def get_active_html(self, use_files=True):
        """Get HTML content — from uploaded file if available, else inline."""
        if use_files and self.html_file and self.html_file.name:
            try:
                self.html_file.open("r")
                content = self.html_file.read()
                if isinstance(content, bytes):
                    content = content.decode("utf-8")
                return content
            except Exception:
                return self.html_content
            finally:
                if hasattr(self.html_file, "close"):
                    self.html_file.close()
        return self.html_content

    def get_active_css(self, use_files=True):
        """Get CSS content — from uploaded file if available, else inline."""
        if use_files and self.css_file and self.css_file.name:
            try:
                self.css_file.open("r")
                content = self.css_file.read()
                if isinstance(content, bytes):
                    content = content.decode("utf-8")
                return content
            except Exception:
                return self.css_content
            finally:
                if hasattr(self.css_file, "close"):
                    self.css_file.close()
        return self.css_content

    @property
    def has_files(self):
        """Check if template has uploaded files."""
        return bool(self.html_file or self.css_file)

    @property
    def has_inline_content(self):
        """Check if template has inline content."""
        return bool(self.html_content or self.css_content or self.text_content)

    @property
    def is_scheduled(self):
        """Check if template has scheduling configured."""
        return bool(self.go_live_at or self.expire_at)

    @property
    def schedule_summary(self):
        """Get a human-readable schedule summary."""
        if not self.go_live_at and not self.expire_at:
            return "No scheduling"
        parts = []
        if self.go_live_at:
            parts.append(f"Goes live: {self.go_live_at.strftime('%Y-%m-%d %H:%M')}")
        if self.expire_at:
            parts.append(f"Expires: {self.expire_at.strftime('%Y-%m-%d %H:%M')}")
        return " | ".join(parts)

    @property
    def template_display_path(self):
        """Display the template source in a user-friendly way."""
        if self.template_source == "path" and self.template_path:
            return self.template_path
        elif self.template_source == "external" and self.external_url:
            return self.external_url
        elif self.template_source == "file" and self.has_files:
            return "Uploaded Files"
        return "Inline Content"

    # ============================================================================
    # TEMPLATE RENDERING METHODS
    # ============================================================================

    def get_rendered_content(self, context=None, use_cache=True, validate_live=True):
        """
        Render the template with context based on template_source.

        Returns a dict with keys: html, css, text, subject, preview_text.
        """
        if validate_live and not self.is_live:
            raise ValueError(
                f"Template is not currently live. Status: {self.scheduled_status}"
            )

        if context is None:
            context = {}

        if use_cache:
            cached = self._get_cached_rendering(context)
            if cached:
                return cached

        # Merge default context with caller-supplied context
        merged = self.get_default_context()
        merged.update(context)

        if self.template_source == "path" and self.template_path:
            content = self._render_from_template_path(merged)
        elif self.template_source == "external" and self.external_url:
            content = self._render_from_external_url(merged)
        elif self.template_source == "file" and self.has_files:
            content = self._render_from_files(merged)
        else:
            content = self._render_from_inline(merged)

        self._update_render_stats()

        if use_cache:
            self._cache_rendering(content, context)

        return content

    def render_for_email(self, context=None, validate_live=True):
        """
        Render template and return a dict ready for email sending.

        Returns: subject, html, text, preview_text, from_email, from_name, reply_to
        """
        from django.conf import settings as django_settings

        rendered = self.get_rendered_content(context, validate_live=validate_live)

        final_html = rendered["html"]
        if rendered.get("css"):
            final_html = self._insert_css_into_html(final_html, rendered["css"])

        return {
            "subject": rendered["subject"],
            "html": final_html,
            "text": rendered["text"],
            "preview_text": rendered.get("preview_text", ""),
            "from_email": self.from_email or getattr(django_settings, "DEFAULT_FROM_EMAIL", ""),
            "from_name": self.from_name,
            "reply_to": self.reply_to_email,
        }

    def render_for_object(self, obj, context=None, validate_live=True):
        """
        Render template for a specific model object.

        If the object has a ``get_email_context()`` method its result is merged
        into the context before rendering.
        """
        if context is None:
            context = {}

        if hasattr(obj, "get_email_context"):
            context.update(obj.get_email_context())

        context["object"] = obj
        context["obj"] = obj

        return self.render_for_email(context, validate_live=validate_live)

    # ------------------------------------------------------------------
    # Internal rendering helpers
    # ------------------------------------------------------------------

    def _render_from_template_path(self, context):
        """Render from a Django template path."""
        from django.template.loader import render_to_string

        try:
            html_content = render_to_string(self.template_path, context)
            css_path = self.template_path.replace(".html", ".css")
            css_content = ""
            try:
                css_content = render_to_string(css_path, context)
            except Exception:
                css_content = self.css_content

            return {
                "html": html_content,
                "css": css_content,
                "text": self.text_content or self._generate_text_from_html(html_content),
                "subject": self._replace_placeholders(
                    self.subject_template or self.subject, context
                ),
                "preview_text": self.preview_text,
            }
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(
                f"Failed to render template from path {self.template_path}: {e}"
            )
            return self._render_from_inline(context)

    def _render_from_external_url(self, context):
        """Fetch template from an external URL and render it."""
        import requests
        from django.template import Context, Template

        try:
            response = requests.get(self.external_url, timeout=10)
            response.raise_for_status()
            template = Template(response.text)
            html_content = template.render(Context(context))

            return {
                "html": html_content,
                "css": self.css_content,
                "text": self.text_content or self._generate_text_from_html(html_content),
                "subject": self._replace_placeholders(
                    self.subject_template or self.subject, context
                ),
                "preview_text": self.preview_text,
            }
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(
                f"Failed to fetch template from URL {self.external_url}: {e}"
            )
            return self._render_from_inline(context)

    def _render_from_files(self, context):
        """Render from uploaded HTML/CSS files."""
        rendered_html = self._replace_placeholders(self.get_active_html(), context)
        rendered_css = self._replace_placeholders(self.get_active_css(), context)

        return {
            "html": rendered_html,
            "css": rendered_css,
            "text": self.text_content or self._generate_text_from_html(rendered_html),
            "subject": self._replace_placeholders(
                self.subject_template or self.subject, context
            ),
            "preview_text": self.preview_text,
        }

    def _render_from_inline(self, context):
        """Render from inline html_content / css_content / text_content."""
        return {
            "html": self._replace_placeholders(self.html_content, context),
            "css": self._replace_placeholders(self.css_content, context),
            "text": self._replace_placeholders(self.text_content, context),
            "subject": self._replace_placeholders(
                self.subject_template or self.subject, context
            ),
            "preview_text": self.preview_text,
        }

    def _replace_placeholders(self, content, context):
        """Render a string as a Django template with the given context."""
        if not content:
            return content or ""
        from django.template import Context, Template
        from django.template.exceptions import TemplateSyntaxError

        # First, do simple placeholder substitution for all {{ key }} patterns
        # This prevents CSS curly braces from being interpreted as Django template tags
        processed_content = content
        for key, value in context.items():
            # Match {{ key }}, {{key}}, {{ key }} patterns
            patterns = [
                f"{{{{ {key} }}}}",  # {{ key }}
                f"{{{{{key}}}}}",    # {{key}}
            ]
            for pattern in patterns:
                processed_content = processed_content.replace(pattern, str(value))

        # Check if there are any Django template tags ({% %})
        has_template_tags = '{%' in processed_content and '%}' in processed_content

        if not has_template_tags:
            # No template tags, return the processed content directly
            return processed_content

        # Try to render any remaining template syntax
        try:
            return Template(processed_content).render(Context(context))
        except TemplateSyntaxError as e:
            # Template syntax error - return the processed content as-is
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Template syntax error: {e}. Returning processed content.")
            return processed_content
        except Exception:
            # For other exceptions, re-raise as these indicate real problems
            raise

    def _generate_text_from_html(self, html_content):
        """Strip HTML tags to produce a plain-text fallback."""
        try:
            from bs4 import BeautifulSoup
            return BeautifulSoup(html_content, "html.parser").get_text(separator="\n", strip=True)
        except ImportError:
            import re
            text = re.sub(r"<[^>]*>", " ", html_content)
            return re.sub(r"\s+", " ", text).strip()

    def _insert_css_into_html(self, html, css):
        """Inject a <style> block into the HTML <head>."""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            head = soup.find("head")
            if not head:
                head = soup.new_tag("head")
                if soup.html:
                    soup.html.insert(0, head)
            style_tag = soup.new_tag("style")
            style_tag.string = css
            head.append(style_tag)
            return str(soup)
        except Exception:
            return f"<style>{css}</style>\n{html}"

    def _update_render_stats(self):
        """Increment render_count and update last_rendered timestamp."""
        self.last_rendered = timezone.now()
        self.render_count += 1
        self.save(update_fields=["last_rendered", "render_count"])

    def _get_cached_rendering(self, context):
        """Return cached rendering result if available."""
        from django.core.cache import cache
        return cache.get(f"{self.cache_key}_ctx_{self._get_context_hash(context)}")

    def _cache_rendering(self, content, context):
        """Store rendering result in cache."""
        from django.conf import settings as django_settings
        from django.core.cache import cache

        timeout = getattr(django_settings, "EMAIL_TEMPLATE_CACHE_TIMEOUT", 3600)
        cache.set(
            f"{self.cache_key}_ctx_{self._get_context_hash(context)}",
            content,
            timeout,
        )

    def _get_context_hash(self, context):
        """Stable hash of a context dict for cache keying."""
        import hashlib
        import json
        return hashlib.md5(json.dumps(context, sort_keys=True, default=str).encode()).hexdigest()

    def get_default_context(self):
        """Build the default template context from site settings and this template."""
        from django.conf import settings as django_settings

        site_name = getattr(django_settings, "SITE_NAME", "")
        site_url = getattr(django_settings, "SITE_URL", "")

        # Try to get Wagtail site info if available
        try:
            from wagtail.models import Site
            current_site = Site.find_for_request(None)
            if current_site:
                site_name = current_site.site_name or site_name
                site_url = current_site.root_url or site_url
        except Exception:
            pass

        return {
            "site_name": site_name,
            "site_url": site_url,
            "current_year": timezone.now().year,
            "unsubscribe_url": self.unsubscribe_url or "#",
            "template_name": self.name,
            "template_type": self.get_template_type_display(),
            "template": self,
            "go_live_at": self.go_live_at,
            "expire_at": self.expire_at,
            "is_live": self.is_live,
        }


class UserRole(models.Model):
    """
    Role assignment for users with hierarchical permissions.
    Supports multiple roles per user.
    """

    class Role(models.TextChoices):
        SUPERVISOR = 'supervisor', 'Supervisor'
        MANAGER = 'manager', 'Manager'
        INSTRUCTOR = 'instructor', 'Instructor'
        CONTENT_MANAGER = 'content_manager', 'Content Manager'

    # Role hierarchy (higher number = higher privilege)
    ROLE_HIERARCHY = {
        Role.SUPERVISOR: 4,
        Role.MANAGER: 3,
        Role.INSTRUCTOR: 2,
        Role.CONTENT_MANAGER: 1,
    }

    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='roles'
    )
    role = models.CharField(
        max_length=50,
        choices=Role.choices,
        db_index=True
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_roles'
    )

    class Meta:
        app_label = 'crafts_ai'
        db_table = 'user_role'
        unique_together = [['user', 'role']]
        ordering = ['user', '-role']

    def __str__(self):
        return f"{self.user.email} - {self.get_role_display()}"

    @classmethod
    def get_highest_role(cls, user):
        """Get the highest role for a user based on hierarchy."""
        user_roles = cls.objects.filter(user=user).values_list('role', flat=True)
        if not user_roles:
            return None

        highest = max(user_roles, key=lambda r: cls.ROLE_HIERARCHY.get(r, 0))
        return highest

    @classmethod
    def has_permission(cls, user, required_role):
        """Check if user has required role or higher."""
        user_highest = cls.get_highest_role(user)
        if not user_highest:
            return False

        user_level = cls.ROLE_HIERARCHY.get(user_highest, 0)
        required_level = cls.ROLE_HIERARCHY.get(required_role, 0)
        return user_level >= required_level


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
        app_label = 'crafts_ai'
        db_table = 'user_group'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_recipients(self):
        """Get all email addresses in this group."""
        return list(self.users.values_list('email', flat=True))


__all__ = ['EmailLog', 'EmailTemplate', 'UserRole', 'UserGroup']
