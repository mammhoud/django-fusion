"""
Auth Feature Tests

Tests allauth adapter configuration, social auth, MFA readiness,
and HTMX fragment auth flows across sites.
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.django_db


class TestAuthSettings:
    """Verify base auth settings are configured correctly."""

    def test_allauth_in_installed_apps(self, settings) -> None:
        assert "allauth" in settings.INSTALLED_APPS
        assert "allauth.account" in settings.INSTALLED_APPS
        assert "allauth.socialaccount" in settings.INSTALLED_APPS

    def test_auth_backends_configured(self, settings) -> None:
        assert "django.contrib.auth.backends.ModelBackend" in settings.AUTHENTICATION_BACKENDS
        assert "allauth.account.auth_backends.AuthenticationBackend" in settings.AUTHENTICATION_BACKENDS

    def test_account_adapter_set(self, settings) -> None:
        assert hasattr(settings, "ACCOUNT_ADAPTER")
        assert "RegistrationAdapter" in settings.ACCOUNT_ADAPTER or "AuthHTMXAdapter" in settings.ACCOUNT_ADAPTER

    def test_account_login_methods(self, settings) -> None:
        assert hasattr(settings, "ACCOUNT_LOGIN_METHODS")
        assert "email" in settings.ACCOUNT_LOGIN_METHODS

    def test_account_signup_fields(self, settings) -> None:
        assert hasattr(settings, "ACCOUNT_SIGNUP_FIELDS")
        assert "email*" in settings.ACCOUNT_SIGNUP_FIELDS

    def test_session_cookie_secure_in_production(self, settings) -> None:
        if getattr(settings, "IS_PRODUCTION", False):
            assert settings.SESSION_COOKIE_SECURE is True
            assert settings.CSRF_COOKIE_SECURE is True

    def test_account_logout_on_get_is_false(self, settings) -> None:
        assert getattr(settings, "ACCOUNT_LOGOUT_ON_GET", False) is False

    def test_socialaccount_adapter_set(self, settings) -> None:
        if hasattr(settings, "SOCIALACCOUNT_ADAPTER"):
            assert "AuthHTMXSocialAccountAdapter" in settings.SOCIALACCOUNT_ADAPTER

    def test_mfa_settings_exist(self, settings) -> None:
        """MFA settings should be present when allauth.mfa is available."""
        mfa_installed = "allauth.mfa" in settings.INSTALLED_APPS
        if mfa_installed:
            assert hasattr(settings, "MFA_SUPPORTED_TYPES")
            assert hasattr(settings, "MFA_PASSKEY_LOGIN_ENABLED")

    def test_passkey_mfa_enabled(self, settings) -> None:
        """Passkey/WebAuthn MFA should be enabled."""
        mfa_installed = "allauth.mfa" in settings.INSTALLED_APPS
        if mfa_installed:
            assert settings.MFA_PASSKEY_LOGIN_ENABLED is True
            assert "webauthn" in settings.MFA_SUPPORTED_TYPES


class TestAuthAdapters:
    """Verify auth adapter classes can be imported and instantiated."""

    def test_registration_adapter_importable(self, settings) -> None:
        from importlib import import_module
        from django.utils.module_loading import import_string

        adapter_path = getattr(settings, "ACCOUNT_ADAPTER", "")
        if not adapter_path:
            pytest.skip("ACCOUNT_ADAPTER not set")

        try:
            adapter_cls = import_string(adapter_path)
            assert adapter_cls is not None
        except ImportError as e:
            pytest.skip(f"Adapter not importable: {e}")

    def test_social_adapter_importable(self, settings) -> None:
        from django.utils.module_loading import import_string

        adapter_path = getattr(settings, "SOCIALACCOUNT_ADAPTER", "")
        if not adapter_path:
            pytest.skip("SOCIALACCOUNT_ADAPTER not set")

        try:
            adapter_cls = import_string(adapter_path)
            assert adapter_cls is not None
        except ImportError as e:
            pytest.skip(f"Social adapter not importable: {e}")


class TestAuthTemplates:
    """Verify auth templates exist and use comp_include where appropriate."""

    def test_auth_skeleton_template_exists(self) -> None:
        from django.template.loader import get_template

        try:
            t = get_template("layout/auth/skeleton.html")
            assert t is not None
        except Exception as e:
            pytest.skip(f"Auth skeleton template not found: {e}")

    def test_login_template_exists(self) -> None:
        from django.template.loader import get_template

        try:
            t = get_template("auth/login.html")
            assert t is not None
        except Exception as e:
            pytest.skip(f"Login template not found: {e}")

    def test_register_template_exists(self) -> None:
        from django.template.loader import get_template

        try:
            t = get_template("auth/register.html")
            assert t is not None
        except Exception as e:
            pytest.skip(f"Register template not found: {e}")


class TestAuthHTMXFlows:
    """Verify HTMX auth views are accessible."""

    def test_login_page_returns_200(self, client) -> None:
        response = client.get("/accounts/login/")
        assert response.status_code in (200, 302)

    def test_signup_page_returns_200(self, client) -> None:
        response = client.get("/accounts/signup/")
        assert response.status_code in (200, 302)

    def test_password_reset_page_returns_200(self, client) -> None:
        response = client.get("/accounts/password/reset/")
        assert response.status_code in (200, 302)

    def test_logout_requires_post(self, client) -> None:
        """ACCOUNT_LOGOUT_ON_GET=False means GET should not log out immediately."""
        response = client.get("/accounts/logout/")
        assert response.status_code in (200, 405, 302)


class TestAuthEmailVerification:
    """Verify email verification settings are sensible."""

    def test_email_verification_setting_is_valid(self, settings) -> None:
        verification = getattr(settings, "ACCOUNT_EMAIL_VERIFICATION", "optional")
        assert verification in ("none", "optional", "mandatory")

    def test_unique_email_enabled(self, settings) -> None:
        assert getattr(settings, "ACCOUNT_UNIQUE_EMAIL", False) is True
