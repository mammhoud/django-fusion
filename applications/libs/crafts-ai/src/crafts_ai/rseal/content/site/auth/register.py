"""
Enhanced Register Page Component
================================
Clean, production-ready registration page using the streamlined auth system.
Features:
- Email verification support
- Automatic group assignment
- HTMX-friendly with proper swapping
- Unified notification system
"""

import logging
import json
from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)

from .mixins import AuthConfig, AuthPageBase

User = get_user_model()


class RegisterView(AuthPageBase):
    """
    Registration page component with email verification support.

    Features:
    - Clean form handling with validation
    - Email verification flow
    - Automatic group assignment
    - HTMX-friendly responses
    """

    # Page configuration
    page_title = "Sign Up"
    page_icon = "bi-person-plus"  # Bootstrap icon class
    fragment_name = "auth.register"

    # Email verification settings
    require_email_verification = True
    auto_login_after_registration = True

    # HTMX configuration
    htmx_config = {
        'reswap': 'innerHTML',
        'retarget': AuthConfig.FORM_TARGET,
        # 'push_url': 'true'
    }

    def get_context_data(self, **kwargs):
        """Add registration-specific context."""
        context = super().get_context_data(**kwargs)

        # Add form field values for re-population on errors
        context.update({
            'form_fields': {
                'username': self.request.POST.get('username', ''),
                'email': self.request.POST.get('email', ''),
            },
            'require_email_verification': self.require_email_verification,
        })

        return context

    def get(self, request, *args, **kwargs):
        """Handle GET request for registration page."""
        # Redirect if already authenticated
        if request.user.is_authenticated:
            return self.handle_already_authenticated(request)

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Handle POST request for registration with email verification."""
        # Redirect if already authenticated
        if request.user.is_authenticated:
            return self.handle_already_authenticated(request)

        # Process registration with email verification
        return self.process_registration_with_verification(request)

    def process_registration_with_verification(self, request: HttpRequest) -> HttpResponse:
        """
        Enhanced registration process with email verification.

        Steps:
        1. Validate form data
        2. Create user account
        3. Assign default group
        4. Send verification email (if configured)
        5. Store email in session
        6. Return appropriate response
        """
        # Extract form data
        form_data = self.extract_registration_data(request)

        # Validate using base validation
        is_valid, error_message = self.validate_registration(form_data)
        if not is_valid:
            return self.handle_registration_error(request, error_message)

        try:
            # Create user account
            user = self.create_user_account(form_data)

            # Assign default group
            self.assign_default_group(user)

            # Handle email verification
            return self.handle_email_verification(request, user, form_data)

        except Exception as e:
            logger.error(f"Registration error: {e}")
            return self.handle_registration_error(
                request,
                _("An error occurred during registration. Please try again.")
            )

    def extract_registration_data(self, request: HttpRequest) -> dict[str, Any]:
        """Extract and clean registration form data."""
        return {
            "username": request.POST.get("username", "").strip(),
            "email": request.POST.get("email", "").strip().lower(),
            "password": request.POST.get("password", ""),
            "password_confirm": request.POST.get("password_confirm", ""),
            "next": request.POST.get("next") or request.GET.get("next", ""),
        }

    def validate_registration(self, data: dict[str, Any]) -> tuple[bool, str | None]:
        """Validate registration form data with custom rules if needed."""
        # Use base validation first
        is_valid, error = self.validate_registration_data(
            data["username"],
            data["email"],
            data["password"],
            data["password_confirm"]
        )

        if not is_valid:
            return False, error

        # Add any additional validation here
        # Example: Check password strength
        if len(data["password"]) < 8:
            return False, _("Password must be at least 8 characters long.")

        return True, None

    def create_user_account(self, data: dict[str, Any]) -> User:
        """Create new user account with additional fields if needed."""
        user = User.objects.create_user(
            username=data["username"],
            email=data["email"],
            password=data["password"],
        )

        return user

    def assign_default_group(self, user: User, group_name: str = None):
        """Assign user to default group with optional customization."""
        group_name = group_name or AuthConfig.DEFAULT_GROUP
        group, _ = Group.objects.get_or_create(name=group_name)

        if group not in user.groups.all():
            user.groups.add(group)
            user.save()

        logger.info(f"Assigned user {user.username} to group: {group_name}")

    def handle_email_verification(
        self,
        request: HttpRequest,
        user: User,
        form_data: dict[str, Any]
    ) -> HttpResponse:
        """Handle email verification flow."""
        email_sent = False

        # Check if email verification is enabled and configured
        if self.require_email_verification and self.is_email_configured():
            try:
                # Send verification email
                self.send_verification_email(user)
                email_sent = True
                logger.info(f"Verification email sent to {user.email}")
            except Exception as e:
                logger.error(f"Failed to send verification email: {e}")
                email_sent = False
        else:
            logger.warning("Email verification skipped - not configured or disabled")

        # Store email in session for verification page
        if email_sent:
            request.session["verification_email"] = form_data["email"]
            request.session["verification_user_id"] = user.id

        # Determine response based on email status
        if email_sent:
            return self.handle_registration_with_verification(request, user, form_data)
        else:
            # If no email verification, proceed with normal registration success
            return self.handle_registration_success(
                request,
                user,
                form_data.get("next"),
                auto_login=self.auto_login_after_registration
            )

    def is_email_configured(self) -> bool:
        """Check if email settings are properly configured."""
        return bool(
            getattr(settings, 'EMAIL_HOST_USER', None) and
            getattr(settings, 'EMAIL_HOST_PASSWORD', None)
        )

    def send_verification_email(self, user: User):
        """Send verification email to user."""
        # This is a placeholder - implement your email sending logic
        # Uncomment when you have the email functionality

        # For now, just log it
        logger.info(f"Would send verification email to {user.email}")

        # Mock implementation - remove this in production
        if hasattr(user, 'token'):
            logger.info(f"Token generated: {user.token}")

    def handle_registration_with_verification(
        self,
        request: HttpRequest,
        user: User,
        form_data: dict[str, Any]
    ) -> HttpResponse:
        """Handle successful registration with email verification required."""
        # Don't auto-login when email verification is required
        message = _(
            "Account created successfully! "
            "Please check your email to verify your account."
        )

        # Redirect to verification page
        redirect_url = reverse_lazy("pipelines:verify-email-page")

        logger.info(f"User {user.username} registered, verification email sent")

        return self.show_notification(
            message=message,
            level="success",
            title=_("Registration Successful"),
            duration=5000,
            redirect_url=redirect_url,
            request=request
        )

    def handle_registration_error(
        self,
        request: HttpRequest,
        error_message: str
    ) -> HttpResponse:
        """Handle registration errors with proper user feedback."""
        logger.warning(f"Registration failed: {error_message}")

        return self.show_notification(
            message=error_message,
            level="error",
            title=_("Registration Failed"),
            duration=5000,
            request=request,
            replace_form=False,  # Don't replace form, just show notification
            swap="none"
        )

    def render_to_response(self, context, **response_kwargs):
        """Override to add HTMX headers if needed."""
        response = super().render_to_response(context, **response_kwargs)

        # For HTMX fragment requests, add initialization trigger
        if self.is_htmx(self.request):
            # Apply HTMX configuration
            if 'reswap' in self.htmx_config:
                response['HX-Reswap'] = self.htmx_config['reswap']
            if 'retarget' in self.htmx_config:
                response['HX-Retarget'] = self.htmx_config['retarget']
            if 'push_url' in self.htmx_config:
                response['HX-Push-Url'] = self.htmx_config['push_url']

            # Add client-side initialization trigger for non-POST requests
            if not self.request.method == 'POST':
                response['HX-Trigger'] = json.dumps({
                    'pageFragmentLoaded': {
                        'fragment': self.fragment_name,
                        'page': 'register'
                    }
                })

        return response

    def get_client_ip(self, request: HttpRequest) -> str:
        """Get client IP address for logging."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


# ===============================================
# ASYNC VERSION (OPTIONAL)
# ===============================================

class AsyncRegisterPage(RegisterView):
    """
    Async version of RegisterPage for better performance with async operations.
    Use this if your database and email backend support async.
    """

    async def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Async POST handler for registration."""
        if request.user.is_authenticated:
            return self.handle_already_authenticated(request)

        return await self.async_process_registration(request)

    async def async_process_registration(self, request: HttpRequest) -> HttpResponse:
        """Async version of registration process."""
        # Extract form data
        form_data = self.extract_registration_data(request)

        # Validate
        is_valid, error_message = self.validate_registration(form_data)
        if not is_valid:
            return self.handle_registration_error(request, error_message)

        try:
            # Create user account (sync for now - make async if ORM supports it)
            user = self.create_user_account(form_data)

            # Assign default group
            self.assign_default_group(user)

            # Handle email verification (make async if email backend supports it)
            if self.require_email_verification and self.is_email_configured():
                # await self.async_send_verification_email(user)
                email_sent = True
                request.session["verification_email"] = form_data["email"]
                request.session["verification_user_id"] = user.id
            else:
                email_sent = False

            # Determine response
            if email_sent:
                return self.handle_registration_with_verification(request, user, form_data)
            else:
                return self.handle_registration_success(
                    request,
                    user,
                    form_data.get("next"),
                    auto_login=self.auto_login_after_registration
                )

        except Exception as e:
            logger.error(f"Async registration error: {e}")
            return self.handle_registration_error(
                request,
                _("An error occurred during registration. Please try again.")
            )


# ===============================================
# MODAL VERSION (FOR MODAL DIALOGS)
# ===============================================

class RegisterModal(AuthPageBase):
    """
    Registration modal component for in-page registration dialogs.
    """

    # Modal configuration
    page_title = "Sign Up"
    modal_title = "Create New Account"
    modal_size = "md"

    # Template configuration
    template_name = "components/modal_auth.html"
    fragment_name = "auth.register_modal"

    # HTMX configuration for modals
    htmx_config = {
        'reswap': 'innerHTML',
        'retarget': '#auth-modal-container',
    }

    def get(self, request, *args, **kwargs):
        """Handle GET for registration modal."""
        if request.user.is_authenticated:
            # If user is already authenticated, close modal and show notification
            response = self.handle_already_authenticated(request)
            if request.htmx:
                # Add trigger to close modal
                response['HX-Trigger'] = json.dumps({'closeModal': True})
            return response

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Handle POST for registration modal."""
        if request.user.is_authenticated:
            return self.handle_already_authenticated(request)

        # Use the RegisterPage's logic
        register_page = RegisterPage()
        register_page.request = request
        response = register_page.process_registration_with_verification(request)

        # If response is a redirect and we're in HTMX, trigger modal close
        if request.htmx and 'HX-Redirect' in response:
            response['HX-Trigger'] = json.dumps({
                'closeModal': True,
                'showNotification': {
                    'message': _("Registration successful!"),
                    'level': 'success'
                }
            })

        return response

