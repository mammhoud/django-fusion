"""
models/interaction/notification.py
------------------------------------

Self-contained Notification model supporting SMS, email, voice, and push.

No external library dependencies beyond Django settings.
"""

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    """Represents a notification sent through a configurable channel."""

    class NotificationType(models.TextChoices):
        SMS = "sms", _("SMS Message")
        EMAIL = "email", _("Email Notification")
        VOICE = "voice", _("Voice Call")
        PUSH = "push", _("Push Notification")

    provider = models.CharField(
        _("Provider"),
        max_length=20,
        default="twilio",
        choices=[("twilio", _("Twilio"))],
        help_text=_("Notification provider (configured via Django settings)."),
    )
    customer = models.ForeignKey(
        getattr(settings, "PROFILE_MODEL", "auth.User"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.SMS,
    )
    message = models.TextField(_("Message Content"))
    subject = models.CharField(_("Subject"), max_length=255, blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        _("Status"),
        max_length=20,
        default="pending",
        help_text=_("Status: pending, sent, failed."),
    )
    response_data = models.JSONField(_("Response Data"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        ordering = ["-created_at"]

    def __str__(self):
        target = self.customer if self.customer else "General"
        return f"{self.get_notification_type_display()} → {target}"

    def send(self):
        """Dispatch the notification via the configured provider."""
        if self.provider == "twilio":
            return self._send_via_twilio()
        self.status = "failed"
        self.save(update_fields=["status"])
        return f"Provider '{self.provider}' not supported."

    def _send_via_twilio(self):
        """Send notification using Twilio API (SMS or Voice)."""
        try:
            from twilio.rest import Client
        except ImportError:
            self.status = "failed"
            self.response_data = {"error": "Twilio library not installed."}
            self.save(update_fields=["status", "response_data"])
            return str(self.response_data)

        sid = getattr(settings, "TWILIO_ACCOUNT_SID", None)
        token = getattr(settings, "TWILIO_AUTH_TOKEN", None)
        from_number = getattr(settings, "TWILIO_PHONE_NUMBER", None)
        if not all([sid, token, from_number]):
            self.status = "failed"
            self.response_data = {"error": "Twilio settings not configured."}
            self.save(update_fields=["status", "response_data"])
            return str(self.response_data)

        to_number = getattr(self.customer, "phone", None) if self.customer else None
        if not to_number:
            self.status = "failed"
            self.response_data = {"error": "Customer has no phone number."}
            self.save(update_fields=["status", "response_data"])
            return str(self.response_data)

        try:
            client = Client(sid, token)
            if self.notification_type == "sms":
                message = client.messages.create(
                    body=self.message,
                    from_=from_number,
                    to=to_number,
                )
                self.status = "sent"
                self.response_data = {"sid": message.sid}
            elif self.notification_type == "voice":
                call = client.calls.create(
                    twiml=f"<Response><Say>{self.message}</Say></Response>",
                    from_=from_number,
                    to=to_number,
                )
                self.status = "sent"
                self.response_data = {"call_sid": call.sid}
            else:
                self.status = "failed"
                self.response_data = {"error": f"Unsupported type: {self.notification_type}"}
        except Exception as e:
            self.status = "failed"
            self.response_data = {"error": str(e)}

        self.sent_at = timezone.now()
        self.save(update_fields=["status", "response_data", "sent_at"])
        return self.response_data
