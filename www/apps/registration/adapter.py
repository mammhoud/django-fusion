import logging

from allauth.account.adapter import DefaultAccountAdapter
from django.http import HttpRequest

from .emails import send_registration_email
from .tokens import registration_token_generator

logger = logging.getLogger("apps.registration")


class RegistrationAdapter(DefaultAccountAdapter):
    """
    Custom allauth adapter that routes lifecycle events into the
    existing email service and rate limiter.

    Registered in settings as:
        ACCOUNT_ADAPTER = "apps.accounts.registration.adapter.RegistrationAdapter"
    """

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        """
        Override allauth's default confirmation mailer.
        Converts the allauth EmailConfirmationHMAC key into a payload
        compatible with RegistrationTokenGenerator, then calls the
        existing send_registration_email().
        """
        user = emailconfirmation.email_address.user
        allauth_key = emailconfirmation.key

        token = registration_token_generator.make_allauth_compatible_token(
            user, allauth_key
        )

        site_url = self._get_site_url(request)
        from django.urls import reverse
        confirmation_path = reverse("handlers:create-password", kwargs={"token": token})
        confirmation_url = f"{site_url}{confirmation_path}"

        send_registration_email(user, confirmation_url)

    def pre_login(self, request, user, **kwargs):
        from .views import rate_limit_check
        if not rate_limit_check(request):
            from allauth.account.adapter import get_adapter
            raise get_adapter().validation_error("too_many_login_attempts")
        return super().pre_login(request, user, **kwargs)

    def pre_signup(self, request, user):
        from .views import rate_limit_check, rate_limit_increment
        if not rate_limit_check(request):
            from allauth.account.adapter import get_adapter
            raise get_adapter().validation_error("too_many_signup_attempts")
        rate_limit_increment(request)
        return super().pre_signup(request, user)

    def _get_site_url(self, request: HttpRequest) -> str:
        from django.conf import settings
        url = getattr(settings, "WAGTAILADMIN_BASE_URL", "")
        if not url or url == "https://example.com":
            url = "https://structa.cloud"
        return url.rstrip("/")
