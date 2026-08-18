"""
Reusable Email Configuration model for Django Admin.
Allows runtime email configuration without server restart.
"""
import logging

from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage, get_connection
from django.db import models
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)

CACHE_KEY = "email_config_active"
CACHE_TIMEOUT = 300  # 5 minutes


class EmailConfiguration(models.Model):
    """
    Admin-editable email configuration.
    When active, overrides Django settings at send-time.
    Falls back to settings.py if no active config exists.
    """

    class EmailBackend(models.TextChoices):
        SMTP = "django.core.mail.backends.smtp.EmailBackend", _("SMTP")
        CONSOLE = "django.core.mail.backends.console.EmailBackend", _("Console")
        FILE = "django.core.mail.backends.filebased.EmailBackend", _("File")
        LOCMEM = "django.core.mail.backends.locmem.EmailBackend", _("In-Memory")

    # Connection settings
    email_backend = models.CharField(
        max_length=255,
        choices=EmailBackend.choices,
        default=EmailBackend.SMTP,
        verbose_name=_("Email Backend"),
    )
    email_host = models.CharField(
        max_length=255,
        default="smtp.gmail.com",
        verbose_name=_("SMTP Host"),
    )
    email_port = models.IntegerField(
        default=587,
        verbose_name=_("SMTP Port"),
    )
    email_use_tls = models.BooleanField(
        default=True,
        verbose_name=_("Use TLS"),
    )
    email_use_ssl = models.BooleanField(
        default=False,
        verbose_name=_("Use SSL"),
    )

    # Authentication
    email_host_user = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Username / Email"),
    )
    email_host_password = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Password / App Password"),
        help_text=_("For Gmail, use an App Password."),
    )

    # Sender
    default_from_email = models.EmailField(
        blank=True,
        default="",
        verbose_name=_("Default From Email"),
        help_text=_("If blank, uses the host user email."),
    )

    # State
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("Only one configuration should be active at a time."),
    )
    notes = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Notes"),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "shared"
        verbose_name = _("Email Configuration")
        verbose_name_plural = _("Email Configurations")
        ordering = ["-is_active", "-updated_at"]

    def __str__(self):
        status = "✅" if self.is_active else "❌"
        return f"{status} {self.email_host_user or self.email_host} ({self.email_host}:{self.email_port})"

    def clean(self):
        """Validate TLS/SSL exclusivity."""
        if self.email_use_tls and self.email_use_ssl:
            raise ValidationError(
                _("TLS and SSL cannot both be enabled. Choose one.")
            )

    def save(self, *args, **kwargs):
        # Deactivate other configs if this one is active
        if self.is_active:
            EmailConfiguration.objects.filter(is_active=True).exclude(pk=self.pk).update(
                is_active=False
            )
        # Clear cache
        cache.delete(CACHE_KEY)
        super().save(*args, **kwargs)

    @classmethod
    def get_active(cls):
        """Get active email configuration, with caching."""
        config = cache.get(CACHE_KEY)
        if config is None:
            try:
                config = cls.objects.filter(is_active=True).first()
                if config:
                    cache.set(CACHE_KEY, config, CACHE_TIMEOUT)
            except Exception:
                return None
        return config

    def get_connection(self, fail_silently=False):
        """Get a Django email connection using this configuration."""
        return get_connection(
            backend=self.email_backend,
            host=self.email_host,
            port=self.email_port,
            username=self.email_host_user,
            password=self.email_host_password,
            use_tls=self.email_use_tls,
            use_ssl=self.email_use_ssl,
            fail_silently=fail_silently,
        )

    def send_test_email(self, to_email):
        """Send a test email using this configuration."""
        from_email = self.default_from_email or self.email_host_user
        connection = self.get_connection(fail_silently=False)
        email = EmailMessage(
            subject="[Test] Email Configuration Verification",
            body=(
                "This is a test email from your Django admin email configuration.\n\n"
                f"Host: {self.email_host}\n"
                f"Port: {self.email_port}\n"
                f"TLS: {self.email_use_tls}\n"
                f"SSL: {self.email_use_ssl}\n"
                f"User: {self.email_host_user}\n\n"
                "If you received this, your configuration is working correctly! ✅"
            ),
            from_email=from_email,
            to=[to_email],
            connection=connection,
        )
        return email.send()


def get_email_connection(fail_silently=False):
    """
    Get email connection from DB config if available, otherwise use Django defaults.
    This function should be used instead of Django's default get_connection()
    to support runtime email configuration changes without restart.
    """
    config = EmailConfiguration.get_active()
    if config:
        return config.get_connection(fail_silently=fail_silently)
    return get_connection(fail_silently=fail_silently)
