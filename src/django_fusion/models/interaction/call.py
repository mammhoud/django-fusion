"""
models/interaction/call.py
----------------------------

Self-contained Call model for Twilio integration (extendable to other providers).

No external library dependencies beyond Django settings.
"""

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Call(models.Model):
    """Represents a call made to a customer via a voice provider."""

    provider = models.CharField(
        _("Provider"),
        max_length=20,
        default="twilio",
        choices=[("twilio", _("Twilio"))],
        help_text=_("Voice provider (configured via Django settings)."),
    )
    customer = models.ForeignKey(
        getattr(settings, "PROFILE_MODEL", "auth.User"),
        on_delete=models.CASCADE,
        related_name="calls",
    )
    call_sid = models.CharField(_("Call SID"), max_length=255, unique=True)
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        _("Status"),
        max_length=50,
        default="initiated",
        help_text=_("Call status: initiated, in-progress, completed, failed."),
    )

    class Meta:
        verbose_name = _("Call")
        verbose_name_plural = _("Calls")
        ordering = ["-started_at"]

    def __str__(self):
        return f"Call with {self.customer} ({self.call_sid})"

    def make_call(self):
        """Make an outbound call using the configured provider."""
        if self.provider == "twilio":
            return self._make_twilio_call()
        return f"Provider '{self.provider}' not supported."

    def _make_twilio_call(self):
        """Place a call via Twilio API."""
        try:
            from twilio.rest import Client
        except ImportError:
            return "Twilio library not installed."

        sid = getattr(settings, "TWILIO_ACCOUNT_SID", None)
        token = getattr(settings, "TWILIO_AUTH_TOKEN", None)
        from_number = getattr(settings, "TWILIO_PHONE_NUMBER", None)
        if not all([sid, token, from_number]):
            return "Twilio settings not configured."

        client = Client(sid, token)
        to_number = getattr(self.customer, "phone", None)
        if not to_number:
            return "Customer has no phone number."

        call = client.calls.create(
            from_=from_number,
            to=to_number,
            url="http://example.com/twiml",
        )
        self.call_sid = call.sid
        self.status = "in-progress"
        self.save(update_fields=["call_sid", "status"])
        return call.sid

    def end_call(self):
        """Mark the call as ended."""
        self.ended_at = timezone.now()
        self.status = "completed"
        self.save(update_fields=["ended_at", "status"])
