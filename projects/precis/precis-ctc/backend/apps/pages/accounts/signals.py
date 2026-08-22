"""
Accounts signals for precis-lms.com.

Handles email template file uploads and registration lifecycle events.
"""

import logging
import threading

from allauth.account.models import EmailAddress
from allauth.account.signals import user_signed_up
from django.contrib.auth.signals import user_logged_in
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_fusion.models.email import EmailTemplate

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# SIGNUP — send the email-confirmation (create-password) link
# ------------------------------------------------------------------

@receiver(user_signed_up)
def on_user_signed_up(request, user, **kwargs):
    """
    Send the email-confirmation link after signup so new accounts can verify
    their address via the /auth/create-password/ flow (the site's adapter
    routes allauth confirmations through send_registration_email).

    Dispatched asynchronously so the signup response is never delayed by SMTP.
    """
    email = EmailAddress.objects.filter(user=user, primary=True).first()
    if not email or email.verified:
        return

    def _send():
        try:
            email.send_confirmation(request, signup=True)
            logger.info(f"Signup confirmation email sent to {email.email}")
        except Exception as exc:
            logger.error(
                f"Signup confirmation email failed for user_id={user.pk}: {exc}",
                exc_info=True,
            )

    # Defer until the request transaction commits so the background thread's
    # own DB connection can see the freshly-created user/EmailAddress rows.
    transaction.on_commit(
        lambda: threading.Thread(target=_send, daemon=True).start()
    )


# ------------------------------------------------------------------
# REGISTRATION SIGNALS
# ------------------------------------------------------------------

@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
    """
    Send a sign-in success email on the user's first login.
    Dispatched asynchronously so it does not delay the login response.
    last_login is None before the first login; Django sets it after this signal fires.
    """
    if user.last_login is not None:
        return  # not first login

    def _send():
        try:
            from .emails import send_signin_success_email
            send_signin_success_email(user)
        except Exception as exc:
            logger.error(
                f"sign-in success email failed for user_id={user.pk}: {exc}",
                exc_info=True,
            )

    thread = threading.Thread(target=_send, daemon=True)
    thread.start()


# ------------------------------------------------------------------
# EMAIL TEMPLATE SIGNALS
# ------------------------------------------------------------------

@receiver(post_save, sender=EmailTemplate)
def handle_file_uploads(sender, instance, created, **kwargs):
    """
    Automatically update inline content fields when files are uploaded.
    """
    updated = False

    if instance.html_file and instance.html_file.name:
        if instance.update_html_from_file():
            updated = True

    if instance.css_file and instance.css_file.name:
        if instance.update_css_from_file():
            updated = True

    if updated:
        instance.save(update_fields=["html_content", "css_content"])
        logger.info(f"Auto-updated content fields for template: {instance.name}")

    if instance.is_default and not instance.is_system:
        EmailTemplate.objects.filter(
            template_type=instance.template_type,
            language=instance.language,
            is_default=True,
        ).exclude(pk=instance.pk).update(is_default=False)
