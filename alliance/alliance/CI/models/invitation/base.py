import datetime
from typing import Any, Dict, Optional

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

from alliance.CI.adapters import get_invitations_adapter
from alliance.CI.adapters import InvitationEmailHandler
from django_grep.pipelines.signals import invitations
from alliance.conf import EmailSendingStrategy, app_settings

from .managers import BaseInvitationManager

try:
    from django.urls import reverse
except ImportError:
    from django.urls import reverse


class AbstractBaseInvitation(models.Model):
    """
    Abstract base for invitation system.
    Provides common fields and interface for invitation workflows.
    """

    email = models.EmailField(
        verbose_name=_("Email"),
        db_index=True,
        max_length=app_settings.EMAIL_MAX_LENGTH,
    )
    accepted = models.BooleanField(verbose_name=_("Accepted"), default=False)
    key = models.CharField(verbose_name=_("Key"), max_length=64, unique=True)
    sent = models.DateTimeField(verbose_name=_("Sent"), null=True, blank=True)
    expires_at = models.DateTimeField(verbose_name=_("Expires At"), null=True, blank=True)

    inviter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Inviter"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="sent_invitations",
    )

    created = models.DateTimeField(
        verbose_name=_("created"), default=timezone.now
    )

    objects = BaseInvitationManager()

    class Meta:
        abstract = True
        ordering = ["-sent"]
        verbose_name = _("Base Invitation")
        verbose_name_plural = _("Base Invitations")

    @classmethod
    def create(cls, email, inviter=None, **kwargs):
        """
        Create and persist a new invitation with a unique key and expiration date.
        """
        key = get_random_string(64).lower()
        expires_at = timezone.now() + timezone.timedelta(
            days=kwargs.get('validity_days', app_settings.INVITATION_EXPIRY)
        )

        invitation = cls.objects.create(
            email=email,
            inviter=inviter,
            key=key,
            expires_at=expires_at,
            sent=timezone.now(),
            **kwargs,
        )
        return invitation

    def key_expired(self):
        """
        Determine if the invitation key has expired.
        """
        if self.expires_at:
            return timezone.now() > self.expires_at
        # Fallback to old behavior if expires_at is not set
        if self.sent:
            expiration_date = self.sent + datetime.timedelta(
                days=app_settings.INVITATION_EXPIRY,
            )
            return expiration_date <= timezone.now()
        return False

    def get_invite_url(self, request=None):
        """
        Generate the invitation URL.
        """
        if request:
            current_site = get_current_site(request)
            invite_url = reverse(
                app_settings.CONFIRMATION_URL_NAME, args=[self.key]
            )
            return request.build_absolute_uri(invite_url)
        else:
            # Without request, construct URL from settings
            site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
            invite_path = reverse(
                app_settings.CONFIRMATION_URL_NAME, args=[self.key]
            )
            return f"{site_url}{invite_path}"

    def send_invitation(self, request=None, **kwargs):
        """
        Send invitation email to the recipient.
        """
        if request:
            # Traditional method with request
            current_site = get_current_site(request)
            invite_url = reverse(
                app_settings.CONFIRMATION_URL_NAME, args=[self.key]
            )
            invite_url = request.build_absolute_uri(invite_url)
            ctx = kwargs
            ctx.update(
                {
                    "invite_url": invite_url,
                    "site_name": current_site.name,
                    "email": self.email,
                    "key": self.key,
                    "inviter": self.inviter,
                },
            )

            email_template = "invitations/email/email_invite"

            try:
                adapter = get_invitations_adapter()
                if hasattr(adapter, 'send_mail'):
                    adapter.send_mail(email_template, self.email, ctx)
                else:
                    # Fallback to email handler
                    self._send_invitation_email(ctx)
            except Exception:
                # Fallback to email handler
                self._send_invitation_email(ctx)
        else:
            # Without request object
            ctx = kwargs.copy() if kwargs else {}
            ctx.update({
                "email": self.email,
                "key": self.key,
                "inviter": self.inviter,
            })
            self._send_invitation_email(ctx)

        self.sent = timezone.now()
        self.save(update_fields=["sent"])

        # Send signal
        invitations.invite_url_sent.send(
            sender=self.__class__,
            instance=self,
            invite_url_sent=self.get_invite_url(request),
            inviter=self.inviter,
        )

        return True

    def _send_invitation_email(self, context: Optional[Dict[str, Any]] = None):
        """Internal method to send invitation email using email handler"""
        if not app_settings.SEND_INVITATION_EMAIL:
            return True

        # Add default context
        if context is None:
            context = {}

        # Add invitation-specific context
        context.update({
            'invitation': self,
            'expiry_days': app_settings.INVITATION_EXPIRY,
            'subject': app_settings.INVITATION_EMAIL_SUBJECT,
        })

        # Add app_settings context
        context.update(app_settings.get_invitation_email_context(self))

        # Use the email handler
        return InvitationEmailHandler.send_invitation_email(self)

    def __str__(self):
        status = _("Accepted") if self.accepted else _("Pending")
        return f"{self.email} ({status})"
