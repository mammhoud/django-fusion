"""
Account adapter for django_fusion.

Provides enhanced allauth adapter with basic functionality.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.signals import user_signed_up
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

if TYPE_CHECKING:  # pragma: no cover
    from django.http import HttpRequest


class AccountAdapter(DefaultAccountAdapter):
    """
    Enhanced account adapter with basic functionality.
    """

    # ------------------------------------------------------------------
    # REGISTRATION CONTROLS
    # ------------------------------------------------------------------

    def is_open_for_signup(self, request: HttpRequest) -> bool:
        """
        Determine if signup is open.
        """
        # Bypass for social authentication if configured
        if request.path.startswith('/accounts/social/'):
            if getattr(settings, 'SOCIALACCOUNT_ALLOW_REGISTRATION', True):
                return True

        # Fall back to global registration setting
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    # ------------------------------------------------------------------
    # REDIRECTS & URLS
    # ------------------------------------------------------------------

    def get_login_redirect_url(self, request):
        """
        Customize login redirect URL based on user status.
        """
        # Redirect new users to complete profile
        if request.user.date_joined > timezone.now() - timezone.timedelta(days=1):
            return getattr(
                settings,
                'NEW_USER_REDIRECT_URL',
                reverse('complete_profile') if hasattr(self, 'reverse') else '/profile/complete/'
            )

        return super().get_login_redirect_url(request)

    # ------------------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------------------

    def clean_email(self, email):
        """
        Validate email against rules.
        """
        cleaned_email = super().clean_email(email)

        # Check if email is on blacklist
        email_blacklist = getattr(settings, 'EMAIL_BLACKLIST', [])
        if cleaned_email in email_blacklist:
            from django.core.exceptions import ValidationError
            raise ValidationError("This email address is not allowed.")

        # Check whitelist if enabled
        email_whitelist = getattr(settings, 'EMAIL_WHITELIST', [])
        if email_whitelist and cleaned_email not in email_whitelist:
            from django.core.exceptions import ValidationError
            raise ValidationError("This email address is not allowed.")

        return cleaned_email

    # ------------------------------------------------------------------
    # SIGNALS
    # ------------------------------------------------------------------

    def get_user_signed_up_signal(self):
        """
        Return the user_signed_up signal.
        """
        return user_signed_up
