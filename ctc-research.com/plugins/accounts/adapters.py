"""
Custom allauth adapter for HTMX fragment rendering.

Module: plugins.accounts.adapters (ctc-research.com)

This adapter:
- Maps allauth template names to auth/ fragment templates
- Detects HX-Request header for fragment vs full-page response
- Wraps fragments in skeleton for non-HTMX requests
- Adds logout success message via Django messages
- RegistrationAdapter: routes email confirmation into the email service
"""

import logging

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib import messages
from django.http import HttpRequest
from django.template.loader import render_to_string

logger = logging.getLogger("apps.registration")


class AuthHTMXAdapter(DefaultAccountAdapter):
    """
    Custom allauth adapter that:
    - Maps allauth view names to auth/ fragment templates
    - Wraps fragments in auth/skeleton.html for non-HTMX requests
    - Returns bare fragments for HTMX requests
    - Handles logout notification via Django messages
    """

    # Template name mapping: allauth internal name → auth/ fragment path
    TEMPLATE_MAP: dict[str, str] = {
        "account/login.html": "auth/login.html",
        "account/signup.html": "auth/register.html",
        "account/password_reset.html": "auth/forgot_page.html",
        "account/password_reset_from_key.html": "auth/reset_password.html",
        "account/password_reset_from_key_done.html": "auth/password_reset_key_done.html",
        "account/password_reset_done.html": "auth/password_reset_done.html",
        "account/email_confirm.html": "auth/verification_link.html",
        "account/password_change.html": "auth/password_change.html",
        "account/password_set.html": "auth/password_set.html",
        "account/email.html": "auth/email_manage.html",
        "account/signup_closed.html": "auth/signup_closed.html",
        "socialaccount/signup.html": "auth/social_signup.html",
        "socialaccount/connections.html": "auth/social_connections.html",
    }

    SKELETON_TEMPLATE = "layout/auth/skeleton.html"

    def get_template_names(self, view_name: str) -> list[str]:
        """
        Return the auth/ fragment template for the given allauth view name.

        Falls back to allauth's default template resolution if no mapping exists.
        """
        # Get the default template names from parent
        template_names = super().get_template_names(view_name)

        # Map each template to our auth/ fragment if a mapping exists
        mapped_names = []
        for name in template_names:
            if name in self.TEMPLATE_MAP:
                mapped_names.append(self.TEMPLATE_MAP[name])
            else:
                mapped_names.append(name)

        return mapped_names

    def render_response(
        self, request: HttpRequest, template_name: str, context: dict, status=None
    ):
        """
        Render the fragment. For non-HTMX requests, wrap in skeleton.
        For HTMX requests, return the bare fragment.
        """
        # Check if this is an HTMX request
        is_htmx = request.headers.get("HX-Request", False)

        # Render the fragment
        fragment = render_to_string(template_name, context, request)

        if is_htmx:
            # Return bare fragment for HTMX requests
            from django.http import HttpResponse

            response = HttpResponse(fragment)
            if status:
                response.status_code = status
            return response
        else:
            # Wrap in skeleton for non-HTMX requests
            skeleton_context = {
                **context,
                "fragment": fragment,
                "template_name": template_name,
            }
            skeleton = render_to_string(self.SKELETON_TEMPLATE, skeleton_context, request)

            from django.http import HttpResponse

            response = HttpResponse(skeleton)
            if status:
                response.status_code = status
            return response

    def get_logout_redirect_url(self, request: HttpRequest) -> str:
        """Return the URL to redirect to after logout."""
        from django.conf import settings

        return getattr(settings, "ACCOUNT_LOGOUT_REDIRECT_URL", "/")

    def logout(self, request: HttpRequest):
        """Perform logout and add a success message for the redirect page."""
        from django.utils.translation import gettext_lazy as _

        messages.success(request, _("You have been signed out successfully."))
        super().logout(request)


class AuthHTMXSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom social account adapter that uses the same HTMX-aware rendering.
    """

    def is_open_for_signup(self, request: HttpRequest, sociallogin) -> bool:
        """Check if signup is open. Uses the main adapter's setting."""
        adapter = AuthHTMXAdapter(request)
        return adapter.is_open_for_signup(request)

    def pre_social_login(self, request: HttpRequest, sociallogin) -> None:
        """Hook called after a user logs in via social login."""
        # Let the default behavior handle this
        super().pre_social_login(request, sociallogin)


class RegistrationAdapter(DefaultAccountAdapter):
    """
    Custom allauth adapter that routes lifecycle events into the
    existing email service.

    Registered in settings as:
        ACCOUNT_ADAPTER = "plugins.accounts.adapters.RegistrationAdapter"
    """

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        """
        Override allauth's default confirmation mailer.
        Converts the allauth EmailConfirmationHMAC key into a payload
        compatible with RegistrationTokenGenerator, then calls
        send_registration_email().
        """
        from .emails import send_registration_email
        from .tokens import registration_token_generator

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
        url = (
            getattr(settings, "SITE_URL", None)
            or getattr(settings, "WAGTAILADMIN_BASE_URL", None)
            or ""
        )
        if not url or url == "https://example.com":
            url = request.build_absolute_uri("/").rstrip("/")
        return url.rstrip("/")
