import logging

from allauth.account.adapter import DefaultAccountAdapter
from django.http import HttpRequest

from .emails import send_registration_email
from .tokens import registration_token_generator

logger = logging.getLogger("apps.registration")


class RegistrationAdapter(DefaultAccountAdapter):
    """
    Custom allauth adapter that routes lifecycle events into the
    existing email service.

    Registered in settings as:
        ACCOUNT_ADAPTER = "apps.handlers.registration.adapter.RegistrationAdapter"
    """

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        """
        Override allauth's default confirmation mailer.
        Converts the allauth EmailConfirmationHMAC key into a payload
        compatible with RegistrationTokenGenerator, then calls
        send_registration_email().
        """
        user = emailconfirmation.email_address.user
        allauth_key = emailconfirmation.key

        token = registration_token_generator.make_allauth_compatible_token(
            user, allauth_key
        )

        site_url = self._get_site_url(request)
        from django.urls import reverse
        try:
            confirmation_path = reverse("handlers:create-password", kwargs={"token": token})
        except Exception:
            confirmation_path = f"/auth/create-password/{token}/"
        confirmation_url = f"{site_url}{confirmation_path}"

        send_registration_email(user, confirmation_url)

    def login(self, request, user):
        from django.contrib.auth.signals import user_logged_in
        super().login(request, user)
        user_logged_in.send(sender=user.__class__, request=request, user=user)

    def _get_site_url(self, request: HttpRequest) -> str:
        from django.conf import settings
        url = getattr(settings, "WAGTAILADMIN_BASE_URL", "")
        if not url or url == "https://example.com":
            url = "https://structa.cloud"
        return url.rstrip("/")
