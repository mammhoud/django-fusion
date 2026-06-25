"""
models/communication.py
-----------------------

Enhanced Communication & Notification System integrated with Twilio (and extendable to others).

Supports:
- Customer management
- Call and conference logs
- Unified Notification model (SMS, Email, Voice)
- Linkage to Integration model for external API configuration
"""

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from twilio.rest import Client



# ---------------------------------------------------------------------
# CALL MODEL
# ---------------------------------------------------------------------
class Call(models.Model):
    """
    Represents a call made to a customer via Twilio or other integrated systems.
    """

    customer = models.ForeignKey(getattr(settings, 'PROFILE_MODEL', 'auth.User'), on_delete=models.CASCADE, related_name="calls")
    integration = models.ForeignKey(
        "CI.Integration",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="calls",
        verbose_name=_("Integration"),
        help_text=_("Reference to the integration used (e.g., Twilio Voice API)."),
    )
    call_sid = models.CharField(_("Call SID"), max_length=255, unique=True)
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        _("Status"),
        max_length=50,
        default="initiated",
        help_text=_("Call status such as initiated, in-progress, or completed."),
    )

    class Meta:
        app_label = "CI"
        verbose_name = _("Call")
        verbose_name_plural = _("Calls")
        ordering = ["-started_at"]

    def __str__(self):
        return f"Call with {self.customer.name} ({self.call_sid})"

    # -------------------------------------------------------
    # CALL CONTROL METHODS
    # -------------------------------------------------------
    def make_call(self):
        """
        Make an outbound call using the linked integration (Twilio).
        """
        if not self.integration or self.integration.integration_type != "twilio":
            return "Integration not configured for Twilio calls."

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        call = client.calls.create(
            from_=settings.TWILIO_PHONE_NUMBER,
            to=self.customer.phone,
            url="http://example.com/twiml",
        )
        self.call_sid = call.sid
        self.status = "in-progress"
        self.save()
        return call.sid

    def end_call(self):
        """Mark the call as ended."""
        self.ended_at = timezone.now()
        self.status = "completed"
        self.save()
