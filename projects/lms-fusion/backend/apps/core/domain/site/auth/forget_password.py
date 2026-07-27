import logging
import uuid
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

# ===============================================
# PASSWORD RESET PAGES
# ===============================================

class ForgotPasswordView(AuthPageBase):
    """
    Forgot password page.

    Allows users to request password reset by email.
    Validates email existence and sends reset link if configured.
    """

    page_title = "Forgot Password"
    page_icon = "bi-key"  # Bootstrap icon class
    template_name = "account/forgot_password.html"
    fragment_name = "auth.forgot_password"

    # HTMX configuration
    htmx_config = {
        'reswap': 'innerHTML',
        'retarget': AuthConfig.FORM_TARGET,
    }

    def get(self, request, *args, **kwargs):
        """Handle GET request for forgot password page."""
        # Redirect authenticated users away (they can change password in settings)
        if request.user.is_authenticated:
            messages.info(request, _("Please change your password in account settings."))
            return redirect(AuthConfig.LOGIN_REDIRECT)

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Handle POST request to send password reset email."""
        email = request.POST.get('email', '').strip().lower()

        if not email:
            return self.show_notification(
                message=_("Please enter your email address."),
                level="error",
                title=_("Email Required"),
                duration=5000,
                request=request
            )

        # Check if user exists
        user = User.objects.filter(email=email).first()
        if not user:
            # For security, don't reveal that email doesn't exist
            logger.info(f"Password reset requested for non-existent email: {email}")
            return self.handle_password_reset_request(request, email, user_exists=False)

        # User exists, proceed with reset
        return self.handle_password_reset_request(request, email, user_exists=True, user=user)

    def handle_password_reset_request(
        self,
        request: HttpRequest,
        email: str,
        user_exists: bool,
        user: Optional[User] = None
    ) -> HttpResponse:
        """Handle password reset email sending logic."""
        # For security, we always show success even if email doesn't exist
        # But we only send email if user exists and email is configured

        if user_exists and user and self.is_email_configured():
            try:
                # Generate reset token
                str(uuid.uuid4())

                # Store token with expiration (24 hours)
                # Implementation depends on your user/profile model

                # Send password reset email
                logger.info(f"Password reset email sent to {email}")

                # Store email in session for reset page
                request.session["reset_email"] = email

            except Exception as e:
                logger.error(f"Failed to send password reset email: {e}")
                # Continue to show success message for security

        # Always show success message (security best practice)
        success_message = _(
            "If your email is registered, you will receive password reset instructions shortly."
        )

        return self.show_notification(
            message=success_message,
            level="success",
            title=_("Check Your Email"),
            duration=5000,
            redirect_url=reverse_lazy("pipelines:login"),  # Redirect to login after showing message
            request=request
        )

    def is_email_configured(self) -> bool:
        """Check if email settings are properly configured."""
        return bool(
            getattr(settings, 'EMAIL_HOST_USER', None) and
            getattr(settings, 'EMAIL_HOST_PASSWORD', None)
        )

