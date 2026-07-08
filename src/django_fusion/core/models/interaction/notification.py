
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from twilio.rest import Client



# ---------------------------------------------------------------------
# NOTIFICATION MODEL
# ---------------------------------------------------------------------
class Notification(models.Model):
    """
    Represents a notification or message sent through different channels.

    Supports SMS, email, or voice notifications. Each notification
    can be linked to an Integration (Twilio, SendGrid, AWS SNS, etc.)
    and optionally a customer record.
    """

    class NotificationType(models.TextChoices):
        SMS = "sms", _("SMS Message")
        EMAIL = "email", _("Email Notification")
        VOICE = "voice", _("Voice Call")
        PUSH = "push", _("Push Notification")

    customer = models.ForeignKey(
        getattr(settings, 'PROFILE_MODEL', 'auth.User'),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    integration = models.ForeignKey(
        "CI.Integration",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
        verbose_name=_("Integration"),
        help_text=_("The integration used to send this notification (e.g., Twilio, SendGrid)."),
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
        help_text=_("Status of the notification: pending, sent, failed."),
    )
    response_data = models.JSONField(_("Response Data"), blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "CI"
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        ordering = ["-created_at"]

    def __str__(self):
        target = self.customer.name if self.customer else "General"
        return f"{self.get_notification_type_display()} → {target}"

    # -------------------------------------------------------
    # NOTIFICATION SENDING METHODS
    # -------------------------------------------------------
    def send(self):
        """
        Dispatch the notification via the selected integration.
        """
        if not self.integration:
            self.status = "failed"
            self.save()
            return "No integration configured."

        if self.integration.integration_type == "twilio":
            return self._send_via_twilio()
        # Future integrations (SendGrid, AWS SNS, etc.)
        self.status = "failed"
        self.save()
        return f"Unsupported integration type: {self.integration.integration_type}"

    def _send_via_twilio(self):
        """
        Send notification using Twilio API (SMS or Voice).
        """
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            if self.notification_type == "sms":
                message = client.messages.create(
                    body=self.message,
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to=self.customer.phone,
                )
                self.status = "sent"
                self.response_data = {"sid": message.sid}
            elif self.notification_type == "voice":
                call = client.calls.create(
                    twiml=f"<Response><Say>{self.message}</Say></Response>",
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to=self.customer.phone,
                )
                self.status = "sent"
                self.response_data = {"call_sid": call.sid}
            else:
                self.status = "failed"
                self.response_data = {"error": "Unsupported notification type"}
            self.sent_at = timezone.now()
            self.save()
            return self.response_data
        except Exception as e:
            self.status = "failed"
            self.response_data = {"error": str(e)}
            self.save()
            return str(e)
