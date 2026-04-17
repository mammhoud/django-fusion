from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)

from core.conf import app_settings
from django_rseal.pipelines.models import DefaultBase, TemplateRenderMixin

from .managers import BaseInvitationManager

try:
    from django.urls import reverse
except ImportError:
    from django.urls import reverse


# ------------------------------------------------------------------
# ENHANCED INVITATION MODEL WITH TEMPLATE RENDERING
# ------------------------------------------------------------------
class Invitation(DefaultBase, TemplateRenderMixin):
    """
    Example of an enhanced invitation model using the mixins.
    """

    email = models.EmailField(
        verbose_name=_("Email"),
        max_length=app_settings.EMAIL_MAX_LENGTH,
    )

    key = models.CharField(
        max_length=64,
        unique=True,
        verbose_name=_("Invitation Key"),
    )

    accepted = models.BooleanField(
        default=False,
        verbose_name=_("Accepted"),
    )

    accepted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Accepted At"),
    )

    expires_at = models.DateTimeField(
        verbose_name=_("Expires At"),
    )

    inviter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_invitations",
        verbose_name=_("Inviter"),
    )


    # Template to use for invitation emails
    # email_template = models.ForeignKey(
    #     "pipelines.EmailTemplate",
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name="invitations",
    #     verbose_name=_("Email Template"),
    #     help_text=_("Template to use for invitation emails"),
    # )
    objects = BaseInvitationManager()

    class Meta:
        verbose_name = _("Invitation")
        verbose_name_plural = _("Invitations")
        ordering = ["-created_at"]

    def __str__(self):
        status = _("Accepted") if self.accepted else _("Pending")
        return f"{self.email} ({status})"

    def get_email_context(self):
        """Get email context specific to invitations."""
        context = super().get_email_context()
        context.update(
            {
                "invitation": self,
                "invite_url": self.get_invite_url(),
                "inviter": self.inviter,
                "expiry_date": self.expires_at.strftime("%Y-%m-%d"),
                "days_remaining": (self.expires_at - timezone.now()).days,
            }
        )
        return context

    def send_invitation_email(self, request=None):
        """Send invitation email using template."""
        # Determine which template to use
        if self.email_template:
            template = self.email_template
        else:
            # Use default invitation template
            from .models import EmailTemplate

            template = EmailTemplate.get_default_for_type("invitation")

        # Get email context
        context = self.get_email_context()
        if request:
            context["request"] = request

        # Send email
        return self.send_template_email(
            template_name=template,
            recipients=[self.email],
            context=context,
            use_template_object=True,
            from_email=app_settings.INVITATION_FROM_EMAIL,
            reply_to=app_settings.INVITATION_REPLY_TO,
        )

    def get_invite_url(self):
        """Generate invitation URL."""
        from django.urls import reverse

        return reverse("invitations:accept", kwargs={"key": self.key})

    def is_expired(self):
        """Check if invitation is expired."""
        return timezone.now() > self.expires_at

    def can_resend(self):
        """Check if invitation can be resent."""
        if self.accepted or self.is_expired():
            return False

        # Don't resend too frequently (minimum 6 hours between sends)
        if hasattr(self, "last_sent") and self.last_sent:
            time_since_last_send = timezone.now() - self.last_sent
            return time_since_last_send.total_seconds() > 21600  # 6 hours

        return True

    # Wagtail admin panels
    content_panels = [
        MultiFieldPanel(
            [
                FieldPanel("email"),
                FieldPanel("inviter"),
                FieldPanel("expires_at"),
            ],
            heading=_("Invitation Details"),
        ),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading=_("Content")),
            ObjectList(DefaultBase.promote_panels, heading=_("Promote")),
            ObjectList(DefaultBase.settings_panels, heading=_("Settings")),
        ]
    )
