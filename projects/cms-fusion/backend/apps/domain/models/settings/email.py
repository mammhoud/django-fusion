from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseGenericSetting

from django_fusion.models.settings import AbstractEmailSettings


class EmailSettings(AbstractEmailSettings, BaseGenericSetting):
    """Global configuration for outgoing emails, newsletters, and tracking."""

    # Keep CMS's existing environment-derived sender default while the other
    # shared email fields come from django-fusion.
    default_from_email = models.EmailField(
        default=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
        verbose_name=_("Default From Email"),
    )

    panels = [
        MultiFieldPanel(
            [FieldRowPanel([FieldPanel("language"), FieldPanel("active")])],
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
        app_label = "shared"
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
        from django.core.exceptions import ValidationError

        super().clean()
        if self.active and type(self).objects.filter(
            language=self.language,
            active=True,
        ).exclude(pk=self.pk).exists():
            raise ValidationError(
                {
                    "active": (
                        "Another active EmailSettings already exists for language "
                        f"{self.get_language_display()}."
                    )
                }
            )
