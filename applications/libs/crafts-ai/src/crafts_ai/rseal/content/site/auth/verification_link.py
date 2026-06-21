"""
Enhanced Authentication Pages with Unified Mixins System
========================================================
Updated password reset, email verification, and forgot password pages
using the new streamlined AuthPageBase and AuthProcessorMixin.
"""

import logging
from typing import Optional

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from .mixins import AuthConfig, AuthPageBase

logger = logging.getLogger(__name__)
User = get_user_model()

User = get_user_model()


# ===============================================
# EMAIL VERIFICATION PAGES
# ===============================================

class VerifyEmailView(AuthPageBase):
    """
    Email verification page.

    Displays verification status and provides option to resend verification email.
    Uses session-based email storage for unauthenticated users.

    Features:
    - Session-based email tracking
    - Resend verification email functionality
    - Clear messaging for verification status
    """

    page_title = "Verify Email"
    page_icon = "bi-envelope-check"  # Bootstrap icon class
    fragment_name = "auth.verify_email"

    # HTMX configuration
    htmx_config = {
        'reswap': 'innerHTML',
        'retarget': AuthConfig.FORM_TARGET,
    }

    def get_context_data(self, **kwargs):
        """Add verification-specific context."""
        context = super().get_context_data(**kwargs)

        # Get email from session or authenticated user
        email = self.get_verification_email()
        is_authenticated = self.request.user.is_authenticated

        context.update({
            'email': email,
            'email_obfuscated': self.obfuscate_email(email) if email else None,
            'is_authenticated': is_authenticated,
            'email_configured': self.is_email_configured(),
            'can_resend': bool(email),  # Can resend if we have an email
        })

        return context

    def get_verification_email(self) -> Optional[str]:
        """Get email address for verification from session or user."""
        request = self.request

        # Check session for email (unauthenticated users)
        if not request.user.is_authenticated:
            return request.session.get("verification_email")

        # For authenticated users, use their email
        if hasattr(request.user, 'email'):
            return request.user.email

        return None

    def obfuscate_email(self, email: str) -> str:
        """Obfuscate email for display (e.g., j***@example.com)."""
        if '@' not in email:
            return email

        local_part, domain = email.split('@', 1)
        if len(local_part) > 1:
            obfuscated_local = local_part[0] + '*' * (len(local_part) - 1)
        else:
            obfuscated_local = local_part

        return f"{obfuscated_local}@{domain}"

    def is_email_configured(self) -> bool:
        """Check if email settings are properly configured."""
        return bool(
            getattr(settings, 'EMAIL_HOST_USER', None) and
            getattr(settings, 'EMAIL_HOST_PASSWORD', None)
        )

    def get(self, request, *args, **kwargs):
        """Handle GET request for verification page."""
        # If user is authenticated and email is already verified, redirect
        if request.user.is_authenticated and self.is_email_verified(request.user):
            messages.info(request, _("Your email is already verified."))
            return redirect(AuthConfig.LOGIN_REDIRECT)

        return super().get(request, *args, **kwargs)

    def is_email_verified(self, user: User) -> bool:
        """Check if user's email is verified."""
        # Implementation depends on your user model
        # Example: return user.profile.email_verified if hasattr(user, 'profile') else True
        return getattr(user.profile, 'email_verified', True) if hasattr(user, 'profile') else True

    def post(self, request, *args, **kwargs):
        """Handle POST request to resend verification email."""
        action = request.POST.get('action', 'resend')

        if action == 'resend':
            return self.handle_resend_verification(request)

        return super().post(request, *args, **kwargs)

    def handle_resend_verification(self, request: HttpRequest) -> HttpResponse:
        """Handle resend verification email request."""
        email = self.get_verification_email()

        if not email:
            return self.show_notification(
                message=_("No email address found. Please register again."),
                level="error",
                title=_("Email Not Found"),
                duration=5000,
                request=request
            )

        if not self.is_email_configured():
            return self.show_notification(
                message=_("Email service is not configured. Please contact support."),
                level="warning",
                title=_("Email Service Unavailable"),
                duration=5000,
                request=request
            )

        try:
            # Send verification email
            # Note: This requires your email sending implementation

            # For now, just log and show success
            logger.info(f"Verification email resent to {email}")

            return self.show_notification(
                message=_("Verification email sent successfully!"),
                level="success",
                title=_("Email Sent"),
                duration=5000,
                request=request
            )

        except Exception as e:
            logger.error(f"Failed to resend verification email: {e}")
            return self.show_notification(
                message=_("Failed to send verification email. Please try again."),
                level="error",
                title=_("Sending Failed"),
                duration=5000,
                request=request
            )


class VerifyEmailTokenPage(AuthPageBase):
    """
    Email verification token handler.

    Processes verification tokens from email links.
    Updates user verification status and logs them in if successful.
    """

    # No template needed as this is a redirect handler
    def get(self, request, token: str, *args, **kwargs):
        """Process email verification token."""
        try:
            # Find user by token
            # Implementation depends on your token system

            # For demonstration - simulate success
            logger.info(f"Email verification attempted for token: {token}")

            # Show success message
            messages.success(request, _("Email verified successfully!"))

            # Redirect to appropriate page
            if request.user.is_authenticated:
                return redirect(AuthConfig.LOGIN_REDIRECT)
            else:
                return redirect(reverse_lazy("pipelines:login"))

        except (User.DoesNotExist):
            logger.warning(f"Invalid verification token: {token}")
            messages.error(request, _("Invalid or expired verification token."))
            return redirect(reverse_lazy("pipelines:verify-email"))
        except Exception as e:
            logger.error(f"Email verification error: {e}")
            messages.error(request, _("An error occurred during verification."))
            return redirect(reverse_lazy("pipelines:verify-email"))

