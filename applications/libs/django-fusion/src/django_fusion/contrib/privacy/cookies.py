"""
Cookie Consent Management
==========================
Shared cookie preferences, detection, and storage for all django_fusion sites.

Provides a ``CookiePreferences`` class that any site can use via the
``CookieConsentMiddleware`` registered in ``configs/base/middlewares.py``.

.. code-block:: python

    from django_fusion.contrib.privacy.cookies import CookiePreferences

    prefs = CookiePreferences.get_preferences(request)
    if prefs.get("analytics"):
        ...  # load analytics
"""

import json
from datetime import datetime


class CookiePreferences:
    """Manages cookie preferences with sensible defaults.

    Cookie categories follow the standard GDPR / ePrivacy taxonomy
    and can be extended or overridden per site.
    """

    COOKIE_NAME = "cookie_consent"
    COOKIE_EXPIRY_DAYS = 365

    #: Cookie categories and their default state.
    CATEGORIES: dict = {
        "essential": {
            "name": "Essential Cookies",
            "description": "Required for basic site functionality. Cannot be disabled.",
            "required": True,
            "default": True,
        },
        "analytics": {
            "name": "Analytics Cookies",
            "description": "Help us understand how you use our site to improve your experience.",
            "required": False,
            "default": False,
        },
        "marketing": {
            "name": "Marketing Cookies",
            "description": "Used to track your activity and show you relevant ads.",
            "required": False,
            "default": False,
        },
        "preferences": {
            "name": "Preference Cookies",
            "description": "Remember your choices and settings for a better experience.",
            "required": False,
            "default": True,
        },
    }

    # ------------------------------------------------------------------
    # Preference helpers
    # ------------------------------------------------------------------

    @staticmethod
    def get_default_preferences() -> dict:
        """Return default cookie preferences (no consent given yet)."""
        return {
            "essential": True,
            "analytics": False,
            "marketing": False,
            "preferences": True,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0",
        }

    @staticmethod
    def parse_cookie(cookie_value: str | None) -> dict:
        """Parse a cookie value (JSON string) back into a preferences dict.

        Falls back to defaults on any parse error.
        """
        try:
            return json.loads(cookie_value) if cookie_value else CookiePreferences.get_default_preferences()
        except (json.JSONDecodeError, TypeError):
            return CookiePreferences.get_default_preferences()

    @staticmethod
    def serialize_preferences(preferences: dict) -> str:
        """Serialize preferences dict to a JSON string for storage."""
        return json.dumps(preferences)

    # ------------------------------------------------------------------
    # Request helpers
    # ------------------------------------------------------------------

    @staticmethod
    def is_first_visit(request) -> bool:
        """Return ``True`` if the user has not yet set cookie preferences."""
        return CookiePreferences.COOKIE_NAME not in request.COOKIES

    @staticmethod
    def get_preferences(request) -> dict:
        """Return the current user's cookie preferences (or defaults)."""
        cookie_value = request.COOKIES.get(CookiePreferences.COOKIE_NAME)
        return CookiePreferences.parse_cookie(cookie_value)

    # ------------------------------------------------------------------
    # Response helpers
    # ------------------------------------------------------------------

    @staticmethod
    def set_preferences_response(response, preferences: dict):
        """Attach cookie preferences to an HTTP response."""
        cookie_value = CookiePreferences.serialize_preferences(preferences)
        response.set_cookie(
            CookiePreferences.COOKIE_NAME,
            cookie_value,
            max_age=CookiePreferences.COOKIE_EXPIRY_DAYS * 24 * 60 * 60,
            secure=True,
            httponly=False,  # Allow JS to read consent state
            samesite="Lax",
        )
        return response
