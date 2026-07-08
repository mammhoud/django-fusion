"""
Social account adapter for django_fusion.

Provides social account adapter with basic functionality.
"""
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Social account adapter with basic functionality.
    """

    def is_open_for_signup(self, request, sociallogin):
        """
        Allow social signup based on global settings.
        """
        # Fall back to social account settings
        return getattr(settings, "SOCIALACCOUNT_ALLOW_REGISTRATION", True)
