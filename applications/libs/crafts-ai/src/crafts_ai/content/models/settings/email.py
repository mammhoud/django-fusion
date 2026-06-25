from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    MultiFieldPanel,
)
from wagtail.contrib.settings.models import BaseGenericSetting


# =======================================
# EMAIL & MARKETING SETTINGS
# =======================================
class EmailSettings(BaseGenericSetting):
    """Global configuration for outgoing emails, newsletters, and tracking."""

    default_from_email = models.EmailField(
        default=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
        verbose_name=_("Default From Email"),
    )
    default_from_name = models.CharField(
        max_length=100,
        default="CTC Hub",
        verbose_name=_("Default From Name"),
    )
    enable_tracking = models.BooleanField(
        default=True,
        verbose_name=_("Enable Tracking"),
        help_text=_("Track email opens and clicks in newsletters."),
    )
    use_marketing_consent = models.BooleanField(
        default=True,
        verbose_name=_("Require Marketing Consent"),
        help_text=_("Only send newsletters to users who opted in."),
    )

    # --- Limits ---
    max_daily_emails = models.PositiveIntegerField(
        default=1000,
        verbose_name=_("Max Daily Emails"),
        help_text=_("Maximum number of emails that can be sent per day."),
    )
    batch_size = models.PositiveIntegerField(
        default=100,
        verbose_name=_("Batch Size"),
        help_text=_("Emails per sending batch."),
    )

    # --- Integrations ---
    smtp_server = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("SMTP Server"),
        help_text=_("Optional custom SMTP host for sending."),
    )
    analytics_provider = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Analytics Provider"),
        help_text=_("Optional service for email analytics (e.g., Mailchimp, Sendgrid)."),
    )

    # --- Language & Status ---
    language = models.CharField(
        max_length=10,
        choices=settings.LANGUAGES,
        default="en",
        verbose_name=_("Language Code"),
        help_text=_("Language code for these settings (e.g., 'en', 'fr')."),
    )
    active = models.BooleanField(
        default=False,
        verbose_name=_("Active"),
        help_text=_(
            "Designates whether these settings are active for this language. Only one active per language."
        ),
    )

    panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("language"),
                        FieldPanel("active"),
                    ]
                ),
            ],
            heading=_("Language Configuration"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("default_from_email"),
                FieldPanel("default_from_name"),
                FieldPanel("enable_tracking"),
                FieldPanel("use_marketing_consent"),
            ],
            heading=_("Email Identity & Consent"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("max_daily_emails"),
                FieldPanel("batch_size"),
                FieldPanel("smtp_server"),
                FieldPanel("analytics_provider"),
            ],
            heading=_("Performance & Integrations"),
        ),
    ]

    class Meta:
        verbose_name = _("Email Settings")
        verbose_name_plural = _("Email Settings")
        constraints = [
            models.UniqueConstraint(
                fields=["language"],
                condition=models.Q(active=True),
                name="unique_active_email_settings_per_language",
            ),
        ]

    def __str__(self):
        status = "✓" if self.active else "✗"
        return f"Email Settings ({self.get_language_display()}) {status}"

    def clean(self):
        """Validate that only one active setting exists per language."""
        from django.core.exceptions import ValidationError

        super().clean()

        if self.active:
            # Check if another active setting exists for the same language
            existing_active = EmailSettings.objects.filter(
                language=self.language, active=True
            ).exclude(pk=self.pk)

            if existing_active.exists():
                raise ValidationError(
                    {
                        "active": f"Another active EmailSettings already exists for language {self.get_language_display()}."
                    }
                )

    def save(self, *args, **kwargs):
        # Ensure only one active setting per language
        if self.active:
            # Deactivate all other settings for this language
            EmailSettings.objects.filter(language=self.language, active=True).exclude(
                pk=self.pk
            ).update(active=False)

        super().save(*args, **kwargs)

    @classmethod
    def get_active_for_language(cls, language_code):
        """Get active email settings for a specific language."""
        try:
            return cls.objects.get(language=language_code, active=True)
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_active_for_request(cls, request):
        """
        Get active email settings for the current request with language fallback.
        """
        # Get language from request
        language = getattr(request, "LANGUAGE_CODE", "en")

        # Try exact language match
        settings = cls.get_active_for_language(language)
        if settings:
            return settings

        # Try language prefix if different from full language code
        if "-" in language:
            language_prefix = language.split("-")[0]
            settings = cls.get_active_for_language(language_prefix)
            if settings:
                return settings

        # Fallback to any active settings (first one)
        try:
            return cls.objects.filter(active=True).first()
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_default(cls):
        """Get the first active settings as default."""
        try:
            return cls.objects.filter(active=True).first()
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_all_active(cls):
        """Get all active email settings."""
        return {
            settings.language: settings
            for settings in cls.objects.filter(active=True).order_by("language")
        }

    def get_sender_identity(self):
        """Return formatted sender identity for email headers."""
        return f"{self.default_from_name} <{self.default_from_email}>"
