"""
Generic Authentication Mixins.

Provides core authentication utilities that are framework-agnostic
(Django/Wagtail independent). These can be used in any Django project.

Components:
- AuthConfig: Centralized authentication configuration
- AuthBaseMixin: Core authentication utilities
- AuthValidatorMixin: Authentication validation utilities
- AuthProcessorMixin: Authentication processing logic

Usage:
    from django_fusion.contrib.auth import AuthConfig, AuthProcessorMixin
"""

import logging
from typing import Any, Dict, Optional

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.models import Group
from django.http import HttpRequest
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)
User = get_user_model()


# ===============================================
# AUTH CONFIGURATION & CONSTANTS
# ===============================================


class AuthConfig:
    """Centralized authentication configuration."""

    # Redirect URLs
    LOGIN_REDIRECT = getattr(settings, "LOGIN_REDIRECT_URL", "/")
    LOGOUT_REDIRECT = getattr(settings, "LOGIN_URL", "/login/")

    # Session settings
    REMEMBER_ME_DURATION = 1209600  # 2 weeks in seconds
    SESSION_DURATION = 0  # Browser session

    # Default group
    DEFAULT_GROUP = "Client"

    # Form targets
    FORM_TARGET = ".fragment--form"
    NOTIFICATION_TARGET = "body"

    # Notification durations
    NOTIFICATION_DURATION_SUCCESS = 3000
    NOTIFICATION_DURATION_ERROR = 5000

    @classmethod
    def get_redirect_url(cls, request: HttpRequest, default: str = None) -> str:
        """Get redirect URL with next parameter support."""
        next_url = request.GET.get("next") or request.POST.get("next", "")
        return next_url or default or cls.LOGIN_REDIRECT


# ===============================================
# CORE AUTH MIXINS (BUSINESS LOGIC ONLY)
# ===============================================


class AuthBaseMixin:
    """Core authentication utilities - no page rendering logic."""

    def extract_form_data(self, request: HttpRequest, fields: list[str]) -> Dict[str, Any]:
        """Extract and clean form data."""
        return {field: request.POST.get(field, "").strip() for field in fields}

    def handle_already_authenticated(self, request: HttpRequest):
        """Redirect authenticated users away from auth pages."""
        redirect_url = AuthConfig.get_redirect_url(request, AuthConfig.LOGIN_REDIRECT)
        return self.show_notification(
            message=_("You are already logged in"),
            level="info",
            title=_("Already Logged In"),
            duration=AuthConfig.NOTIFICATION_DURATION_SUCCESS,
            redirect_url=redirect_url,
            request=request,
        )

    def handle_already_logged_out(self, request: HttpRequest):
        """Redirect logged out users to login."""
        return self.show_notification(
            message=_("You are already logged out"),
            level="info",
            title=_("Already Logged Out"),
            duration=AuthConfig.NOTIFICATION_DURATION_SUCCESS,
            redirect_url=reverse_lazy("pipelines:login"),
            request=request,
        )


class AuthValidatorMixin:
    """Authentication validation utilities."""

    @staticmethod
    def validate_login_data(identifier: str, password: str) -> tuple[bool, Optional[str]]:
        """Validate login form data."""
        if not identifier:
            return False, _("Please enter your email/username.")
        if not password:
            return False, _("Please enter your password.")
        return True, None

    @staticmethod
    def validate_registration_data(
        username: str, email: str, password: str, password_confirm: str
    ) -> tuple[bool, Optional[str]]:
        """Validate registration form data."""
        if not username:
            return False, _("Username is required.")
        if not email:
            return False, _("Email is required.")
        if password != password_confirm:
            return False, _("Passwords do not match.")
        if User.objects.filter(username=username).exists():
            return False, _("Username already exists.")
        if User.objects.filter(email=email).exists():
            return False, _("Email already exists.")
        return True, None

    @staticmethod
    def resolve_identifier(identifier: str) -> Optional[str]:
        """Resolve email or username to username."""
        if not identifier:
            return None

        try:
            # Check if identifier is an email
            if "@" in identifier:
                user = User.objects.filter(email__iexact=identifier).first()
                return user.username if user else None

            # Check if identifier is username
            user = User.objects.filter(username__iexact=identifier).first()
            if user:
                return user.username

            # Fallback: try email as username (case-insensitive)
            user = User.objects.filter(email__iexact=identifier).first()
            return user.username if user else None

        except Exception as e:
            logger.error(f"Error resolving identifier {identifier}: {e}")
            return None


class AuthProcessorMixin(AuthBaseMixin, AuthValidatorMixin):
    """Authentication processing logic."""

    def process_login(self, request: HttpRequest):
        """Process login request."""
        # Extract data
        identifier = request.POST.get("email-username", "").strip()
        password = request.POST.get("password", "")
        remember_me = request.POST.get("remember_me") == "on"
        next_url = request.POST.get("next") or request.GET.get("next", "")

        # Validate
        is_valid, error = self.validate_login_data(identifier, password)
        if not is_valid:
            return self.handle_login_error(request, error or _("Invalid credentials"))

        # Resolve username
        username = self.resolve_identifier(identifier)
        if not username:
            return self.handle_login_error(request, _("User not found"))

        # Authenticate
        user = authenticate(request, username=username, password=password)
        if not user:
            return self.handle_login_error(request, _("Invalid credentials"))

        # Login successful
        return self.handle_login_success(request, user, remember_me, next_url)

    def process_registration(self, request: HttpRequest):
        """Process registration request."""
        # Extract data
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        password_confirm = request.POST.get("password_confirm", "")
        next_url = request.POST.get("next") or request.GET.get("next", "")

        # Validate
        is_valid, error = self.validate_registration_data(
            username, email, password, password_confirm
        )
        if not is_valid:
            return self.handle_registration_error(request, error or _("Registration failed"))

        try:
            # Create user
            user = User.objects.create_user(username=username, email=email, password=password)

            # Assign default group
            group, _ = Group.objects.get_or_create(name=AuthConfig.DEFAULT_GROUP)
            user.groups.add(group)

            # Registration successful
            return self.handle_registration_success(request, user, next_url)

        except Exception as e:
            logger.error(f"Registration error: {e}")
            return self.handle_registration_error(
                request, _("An error occurred during registration. Please try again.")
            )

    def process_logout(self, request: HttpRequest):
        """Process logout request."""
        if not request.user.is_authenticated:
            return self.handle_already_logged_out(request)

        username = request.user.username
        logout(request)
        logger.info(f"User {username} logged out")

        return self.show_notification(
            message=_("You have been logged out successfully"),
            level="success",
            title=_("Logged Out"),
            duration=AuthConfig.NOTIFICATION_DURATION_SUCCESS,
            redirect_url=reverse_lazy("pipelines:login"),
            request=request,
        )

    def handle_login_success(
        self, request: HttpRequest, user: User, remember_me: bool, next_url: str
    ):
        """Handle successful login."""
        # Perform login
        login(request, user)

        # Set session expiry
        request.session.set_expiry(
            AuthConfig.REMEMBER_ME_DURATION if remember_me else AuthConfig.SESSION_DURATION
        )

        # Redirect URL
        redirect_url = next_url or AuthConfig.LOGIN_REDIRECT

        logger.info(f"User {user.username} logged in successfully")

        return self.show_notification(
            message=_("Welcome back, %(username)s!") % {"username": user.username},
            level="success",
            title=_("Login Successful"),
            duration=AuthConfig.NOTIFICATION_DURATION_SUCCESS,
            redirect_url=redirect_url,
            request=request,
        )

    def handle_login_error(self, request: HttpRequest, error_message: str):
        """Handle login error."""
        logger.warning(f"Login failed: {error_message}")

        return self.show_notification(
            message=error_message,
            level="error",
            title=_("Login Failed"),
            duration=AuthConfig.NOTIFICATION_DURATION_ERROR,
            request=request,
            replace_form=False,  # Don't replace form, just show notification
            swap="none",
        )

    def handle_registration_success(
        self, request: HttpRequest, user: User, next_url: str, auto_login: bool = True
    ):
        """Handle successful registration."""
        if auto_login:
            login(request, user)
            message = _("Account created and logged in successfully!")
        else:
            message = _("Account created successfully! Please log in.")

        logger.info(f"New user registered: {user.username} ({user.email})")

        redirect_url = next_url or AuthConfig.LOGIN_REDIRECT

        return self.show_notification(
            message=message,
            level="success",
            title=_("Registration Successful"),
            duration=AuthConfig.NOTIFICATION_DURATION_SUCCESS,
            redirect_url=redirect_url,
            request=request,
        )

    def handle_registration_error(self, request: HttpRequest, error_message: str):
        """Handle registration error."""
        return self.show_notification(
            message=error_message,
            level="error",
            title=_("Registration Failed"),
            duration=AuthConfig.NOTIFICATION_DURATION_ERROR,
            request=request,
            replace_form=False,  # Don't replace form
            swap="none",
        )
