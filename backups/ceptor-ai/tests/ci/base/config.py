"""
Domain-aware configuration for ctc-research.com CI tests.

All URLs, credentials, and domain constants live here.
Tests import from this module — never hardcode URLs in test files.
"""
from __future__ import annotations


class Domain:
    """Domain and base URL configuration for ctc-research.com."""

    # Production domain
    PRODUCTION = "ctc-research.com"
    PRODUCTION_URL = "https://ctc-research.com"

    # Internal container URL (used by verify_deployment.py)
    INTERNAL = "http://127.0.0.1:5080"

    # Test client base (Django test client uses relative paths)
    BASE = ""  # empty — test client uses relative paths

    @classmethod
    def url(cls, path: str) -> str:
        """Build a full URL for the production domain."""
        return f"{cls.PRODUCTION_URL}{path}"


class AuthURLs:
    """All authentication-related URL paths for ctc-research.com."""

    # Allauth standard paths
    LOGIN = "/accounts/login/"
    LOGOUT = "/accounts/logout/"
    SIGNUP = "/accounts/signup/"
    EMAIL_CONFIRM = "/accounts/confirm-email/"
    EMAIL_MANAGE = "/accounts/email/"
    PASSWORD_RESET = "/accounts/password/reset/"
    PASSWORD_RESET_KEY = "/accounts/password/reset/key/{key}/"
    PASSWORD_CHANGE = "/accounts/password/change/"

    # Custom project paths (crafts_ai pipelines)
    SIGN_IN = "/auth/sign-in/"
    SIGN_UP = "/auth/sign-up/"
    SIGN_OUT = "/auth/sign-out/"
    CREATE_PASSWORD = "/create-password/{token}/"
    REGISTER = "/register/"
    REGISTRATION_SUCCESS = "/registration-success/"

    # Protected pages
    DASHBOARD = "/profile/dashboard/"
    PROFILE = "/profile/profile/"

    # Admin redirects to /auth/sign-in/ in this project
    LOGIN_REDIRECT_PATTERNS = ("login", "sign-in", "signin")

    @classmethod
    def password_reset_key(cls, key: str) -> str:
        return cls.PASSWORD_RESET_KEY.format(key=key)

    @classmethod
    def create_password(cls, token: str) -> str:
        return cls.CREATE_PASSWORD.format(token=token)


class AdminURLs:
    """Admin panel URL paths."""

    INDEX = "/control/"          # Wagtail admin
    DJANGO_ADMIN = "/admin/"     # Django admin (redirects to /control/)
    LOGIN = "/admin/login/"

    # Unfold admin markers expected in response body
    UI_MARKERS = [
        "administration",
        "log out",
        "unfold",
        "site administration",
        "django administration",
    ]


class Credentials:
    """Test credentials used across the test suite."""

    # Primary test account — used for registration/email/login tests
    NEW_USER_EMAIL = "mahmoud.ezzat.moustafa@gmail.com"
    NEW_USER_PASSWORD = "Str0ng!Pass#2024"
    NEW_USER_USERNAME = "ezzat_moustafa"

    # Secondary test account — used for legacy/existing tests
    LEGACY_EMAIL = "admin@example.com"
    LEGACY_PASSWORD = "Str0ng!Pass#2024"
    LEGACY_USERNAME = "mahmoud_ezat"

    # Wrong credentials for negative tests
    WRONG_PASSWORD = "WrongPassword999!"
    WRONG_EMAIL = "nonexistent_xyz_test@example.com"

    # Superuser (from .env / docker-compose)
    SUPERUSER_USERNAME = "admin"
    SUPERUSER_PASSWORD = "mk_pAssWord123"
    SUPERUSER_EMAIL = "admin@example.com"

    # django-fusion BaseTestCase built-in credentials
    BASE_USER_EMAIL = "test@example.com"
    BASE_USER_PASSWORD = "testpass123"
    BASE_ADMIN_EMAIL = "admin@example.com"
    BASE_ADMIN_PASSWORD = "adminpass123"
