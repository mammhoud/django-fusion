# ctc-research/apps/handlers/registration/signals.py

import logging
import threading

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

logger = logging.getLogger("apps.registration")


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
