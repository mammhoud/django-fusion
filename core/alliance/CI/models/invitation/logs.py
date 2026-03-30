from django.db import models
from django.utils.translation import gettext_lazy as _

from core.conf import EmailSendingStrategy, app_settings

try:
    from django.urls import reverse
except ImportError:
    from django.urls import reverse



class EmailLog(models.Model):
    """
    Model to log email sending activities.
    """
    invitation = models.ForeignKey(
        "Invitation",
        on_delete=models.CASCADE,
        related_name='email_logs',
        null=True,
        blank=True
    )
    email_address = models.EmailField(
        verbose_name=_("Email Address"),
        max_length=app_settings.EMAIL_MAX_LENGTH,
    )
    subject = models.CharField(
        verbose_name=_("Subject"),
        max_length=200
    )
    email_provider = models.CharField(
        verbose_name=_("Email Provider"),
        max_length=50,
        choices=[(strategy.value, strategy.name) for strategy in EmailSendingStrategy]
    )
    status = models.CharField(
        verbose_name=_("Status"),
        max_length=20,
        choices=[
            ('queued', _('Queued')),
            ('sent', _('Sent')),
            ('failed', _('Failed')),
            ('delivered', _('Delivered')),
            ('bounced', _('Bounced')),
            ('complained', _('Complained')),
        ]
    )
    error_message = models.TextField(
        verbose_name=_("Error Message"),
        blank=True,
        null=True
    )
    sent_at = models.DateTimeField(
        verbose_name=_("Sent At"),
        auto_now_add=True
    )
    delivered_at = models.DateTimeField(
        verbose_name=_("Delivered At"),
        null=True,
        blank=True
    )
    opened_at = models.DateTimeField(
        verbose_name=_("Opened At"),
        null=True,
        blank=True
    )
    clicked_at = models.DateTimeField(
        verbose_name=_("Clicked At"),
        null=True,
        blank=True
    )
    provider_message_id = models.CharField(
        verbose_name=_("Provider Message ID"),
        max_length=200,
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = _("Email Log")
        verbose_name_plural = _("Email Logs")
        ordering = ['-sent_at']
        
        indexes = [
            models.Index(fields=['email_address', 'sent_at']),
            models.Index(fields=['status', 'sent_at']),
            models.Index(fields=['invitation', 'sent_at']),
        ]
    
    def __str__(self):
        return f"{self.email_address} - {self.subject} ({self.status})"

