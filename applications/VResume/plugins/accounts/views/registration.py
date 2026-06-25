"""
Registration Views
==================
Handles the complete email-based registration workflow:
1. Registration form (name + email) → creates inactive user → sends email
2. Password creation form (via token link) → sets password → activates user
"""

import json
import logging

from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django_osoul.site import PageHandler

from ..emails import send_registration_email
from ..forms.registration import PasswordCreationForm, RegistrationForm
from ..tokens import registration_token_generator

logger = logging.getLogger("apps.registration")
User = get_user_model()

# Rate limiting constants
RATE_LIMIT_WINDOW = 3600  # 1 hour
RATE_LIMIT_MAX_ATTEMPTS = 5  # max registrations per IP per hour


def get_client_ip(request) -> str:
    """Extract client IP from request."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def rate_limit_check(request) -> bool:
    """
    Check if the IP has exceeded registration rate limit.
    Returns True if allowed, False if rate limited.
    Fails open on cache errors (allows the request) to avoid blocking
    legitimate users when the cache backend is unavailable.
    """
    ip = get_client_ip(request)
    cache_key = f"reg_rate_limit:{ip}"
    try:
        attempts = cache.get(cache_key, 0)
    except Exception as e:
        logger.warning(
            f"Cache failure in rate_limit_check for IP {ip}: {e} — failing open"
        )
        return True  # fail-open: allow the request
    return attempts < RATE_LIMIT_MAX_ATTEMPTS


def rate_limit_increment(request):
    """Increment the rate limit counter for this IP."""
    ip = get_client_ip(request)
    cache_key = f"reg_rate_limit:{ip}"
    try:
        attempts = cache.get(cache_key, 0)
        cache.set(cache_key, attempts + 1, RATE_LIMIT_WINDOW)
    except Exception as e:
        logger.warning(
            f"Cache failure in rate_limit_increment for IP {ip}: {e} — counter not updated"
        )


def ensure_groups_exist():
    """
    Ensure required groups exist in the system.
    Creates 'Instructor' and 'Content Manager' groups if missing.
    Called via post_migrate signal in HandlersConfig.ready().
    """
    required_groups = ["Instructor", "Content Manager"]
    for group_name in required_groups:
        _group, created = Group.objects.get_or_create(name=group_name)
        if created:
            logger.info(
                f"Created group: {group_name} at {timezone.now().isoformat()}"
            )


def assign_default_group(user):
    """
    Assign user to 'Content Manager' group by default.
    Can be called from invitation flows with a different group by
    calling user.groups.add() directly after registration.
    """
    group, _ = Group.objects.get_or_create(name="Content Manager")
    user.groups.add(group)
    logger.info(
        f"Assigned user {user.email} to group '{group.name}'"
    )


def get_site_url(request=None):
    """Get the base site URL for building confirmation links."""
    site_url = (
        getattr(settings, "SITE_URL", None)
        or getattr(settings, "WAGTAILADMIN_BASE_URL", None)
        or ""
    )
    if not site_url or site_url == "https://example.com":
        if request is not None:
            site_url = request.build_absolute_uri("/").rstrip("/")
        else:
            site_url = ""
    return site_url.rstrip("/")


def trigger_notification(response: HttpResponse, message: str, notification_type: str = "success") -> HttpResponse:
    """
    Add HX-Trigger header to response for client-side notification display.

    Sets: HX-Trigger: {"showNotification": {"message": "...", "type": "..."}}

    The existing notification bundle (assets/static/js/modules/notifications/notification.js)
    listens for HTMX trigger headers and handles the "showNotification" event via
    `processTriggerHeader()`, reading `value.message` and `value.type` fields to
    display toast notifications. Supported types: "success", "error", "warning", "info".

    Args:
        response: Django HttpResponse to modify
        message: Notification message text
        notification_type: One of "success", "error", "warning", "info"

    Returns:
        Modified response with HX-Trigger header set
    """
    response["HX-Trigger"] = json.dumps({
        "showNotification": {
            "message": message,
            "type": notification_type,
        }
    })
    return response


@method_decorator(csrf_protect, name="dispatch")
class RegisterView(PageHandler):
    """
    Step 1: Registration Form

    HTMX-aware view using PageHandler base class.
    - Collects full name + email
    - Creates inactive user
    - Generates secure token
    - Sends confirmation email with password creation link
    - Rate limited to prevent abuse
    - Returns fragment on HTMX requests, full page on non-HTMX
    """

    template_name = "registration/register.html"
    fragment_template = "registration/fragments/register_form.html"
    page_title = "Register"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("handlers:dashboard")
        form = RegistrationForm()
        context = self.get_context_data(request=request, form=form)
        if self.strategy == "fragment":
            return self.render_fragment(request, context)
        return self.render_layout(context)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("handlers:dashboard")

        is_htmx = bool(request.headers.get("HX-Request"))

        # Rate limiting
        if not rate_limit_check(request):
            logger.warning(f"Rate limit exceeded for IP: {get_client_ip(request)}")
            form = RegistrationForm(request.POST)
            context = self.get_context_data(
                request=request,
                form=form,
                error="Too many registration attempts. Please try again later.",
            )
            if is_htmx:
                response = self.render_fragment(request, context)
                trigger_notification(
                    response,
                    "Too many registration attempts. Please try again later.",
                    "error",
                )
            else:
                response = self.render_layout(context)
            response.status_code = 429
            return response

        form = RegistrationForm(request.POST)
        if not form.is_valid():
            logger.info(f"Registration form invalid: {form.errors}")
            context = self.get_context_data(request=request, form=form)
            if is_htmx:
                response = self.render_fragment(request, context)
                trigger_notification(response, "Please correct the highlighted fields.", "error")
                return response
            return self.render_layout(context)

        email = form.cleaned_data["email"]
        full_name = form.cleaned_data["full_name"]

        # Split full name into first/last
        name_parts = full_name.split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        try:
            # Create inactive user
            user = User.objects.create_user(
                username=email,  # Use email as username
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_active=False,
            )
            # Set unusable password initially
            user.set_unusable_password()
            user.save()

            logger.info(
                f"User created (inactive): {email} from IP {get_client_ip(request)}"
            )

            # Assign to Content Manager group by default
            assign_default_group(user)

            # Generate secure token
            token = registration_token_generator.make_token(user)

            # Build confirmation URL
            site_url = get_site_url(request)
            confirmation_path = reverse(
                "handlers:create-password", kwargs={"token": token}
            )
            confirmation_url = f"{site_url}{confirmation_path}"

            # Send confirmation email
            email_sent = send_registration_email(user, confirmation_url)

            # Increment rate limiter after successful registration
            rate_limit_increment(request)

            if email_sent:
                logger.info(f"Registration email sent to {email}")
            else:
                logger.error(f"Failed to send registration email to {email}")

            # Build success response with notification
            home_url = "/"
            if is_htmx:
                # Return success fragment instead of redirect so user sees confirmation
                context = self.get_context_data(
                    request=request,
                    form=form,
                    success=True,
                    email=email,
                )
                response = self.render_fragment(request, context)
                trigger_notification(response, "Account created! Check your email.", "success")
                return response
            else:
                response = HttpResponseRedirect(home_url)
                return response

        except Exception as e:
            logger.error(f"Registration error for {email}: {e}", exc_info=True)
            context = self.get_context_data(
                request=request,
                form=form,
                error="An unexpected error occurred. Please try again.",
            )
            if is_htmx:
                response = self.render_fragment(request, context)
                trigger_notification(
                    response,
                    "An unexpected error occurred. Please try again.",
                    "error",
                )
            else:
                response = self.render_layout(context)
            response.status_code = 500
            return response


@method_decorator(csrf_protect, name="dispatch")
class CreatePasswordView(PageHandler):
    """
    Step 2: Password Creation Page

    HTMX-aware view using PageHandler base class.
    Reached via the email confirmation link.
    - Validates the token
    - Displays password creation form
    - Sets password and activates user atomically
    - Logs user in on success
    - Brute-force protected (pw_create_bf:{ip}, limit 10/hour)
    """

    template_name = "registration/create_password.html"
    fragment_template = "registration/fragments/password_form.html"
    page_title = "Create Password"

    def _get_user_from_token(self, token: str):
        """Validate token and return (user, error_message) tuple."""
        data = registration_token_generator.validate_token(token)
        if data is None:
            return None, "invalid"
        if data.get("expired"):
            return None, "expired"

        uid = data.get("uid")
        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            logger.warning(f"Token references non-existent user_id={uid}")
            return None, "invalid"

        # Verify full token validity (including state hash)
        if not registration_token_generator.check_token(user, token):
            if user.is_active and user.has_usable_password():
                return None, "already_used"
            return None, "invalid"

        return user, None

    def get(self, request, token):
        user, error = self._get_user_from_token(token)

        if error == "expired":
            logger.warning(f"Expired token access from IP {get_client_ip(request)}")
            return render(
                request,
                "registration/token_error.html",
                {
                    "error_type": "expired",
                    "message": "This link has expired. Registration links are valid for 24 hours.",
                },
                status=400,
            )
        elif error == "already_used":
            return render(
                request,
                "registration/token_error.html",
                {
                    "error_type": "already_used",
                    "message": "This account has already been activated. You can log in now.",
                },
                status=400,
            )
        elif error:
            logger.warning(f"Invalid token access from IP {get_client_ip(request)}")
            return render(
                request,
                "registration/token_error.html",
                {
                    "error_type": "invalid",
                    "message": "This link is invalid. Please request a new registration.",
                },
                status=400,
            )

        form = PasswordCreationForm()
        context = self.get_context_data(
            request=request,
            form=form,
            token=token,
            user_email=user.email,
            user_name=user.get_full_name() or user.email,
        )
        if self.strategy == "fragment":
            return self.render_fragment(request, context)
        return self.render_layout(context)

    def post(self, request, token):
        is_htmx = bool(request.headers.get("HX-Request"))

        # Brute-force protection on password creation
        ip = get_client_ip(request)
        bf_key = f"pw_create_bf:{ip}"
        bf_attempts = cache.get(bf_key, 0)
        if bf_attempts >= 10:
            logger.warning(f"Brute force protection triggered for IP {ip}")
            return render(
                request,
                "registration/token_error.html",
                {
                    "error_type": "rate_limited",
                    "message": "Too many attempts. Please try again later.",
                },
                status=429,
            )

        user, error = self._get_user_from_token(token)

        if error:
            # Increment brute-force counter on every invalid token attempt
            cache.set(bf_key, bf_attempts + 1, 3600)
            logger.warning(
                f"Invalid token attempt ({error}) for IP {ip}, "
                f"bf_count={bf_attempts + 1}"
            )
            error_messages = {
                "expired": "This link has expired.",
                "already_used": "This account is already activated.",
                "invalid": "This link is invalid.",
            }
            return render(
                request,
                "registration/token_error.html",
                {
                    "error_type": error,
                    "message": error_messages.get(error, "Invalid request."),
                },
                status=400,
            )

        form = PasswordCreationForm(request.POST)
        if not form.is_valid():
            context = self.get_context_data(
                request=request,
                form=form,
                token=token,
                user_email=user.email,
                user_name=user.get_full_name() or user.email,
            )
            if is_htmx:
                response = self.render_fragment(request, context)
                trigger_notification(response, "Please choose a valid password.", "error")
                return response
            return self.render_layout(context)

        # Set password, activate user, and create profile atomically
        password = form.cleaned_data["password"]
        with transaction.atomic():
            user.set_password(password)
            user.is_active = True
            user.save()
            _ensure_profile_exists(user)

        logger.info(
            f"Password set and account activated for user {user.email} "
            f"from IP {ip}"
        )

        # Log the user in
        try:
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            logger.info(f"User {user.email} logged in after password creation")
        except Exception as e:
            logger.error(f"Auto-login failed for {user.email}: {e}")

        # Redirect to registration success page
        success_url = reverse("handlers:registration-success")
        if is_htmx:
            response = HttpResponse(status=200)
            response["HX-Redirect"] = success_url
            trigger_notification(response, "Password set. You are signed in.", "success")
            return response
        return HttpResponseRedirect(success_url)


class RegistrationSuccessView(View):
    """Display success page after completing registration."""

    def get(self, request):
        return render(request, "registration/success.html", {
            "user": request.user if request.user.is_authenticated else None,
        })


def _ensure_profile_exists(user):
    """Create a Person profile for the user if it doesn't exist."""
    try:
        from crafts_ai.pipelines.models.users.users import Person

        _profile, created = Person.objects.get_or_create(
            user=user,
            defaults={
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "full_name": user.get_full_name(),
                "status": "ACTIVE",
                "is_registered": True,
                "registration_date": timezone.now(),
            },
        )
        if created:
            logger.info(f"Profile created for user {user.email}")
        else:
            logger.debug(f"Profile already exists for user {user.email}")
    except Exception as e:
        logger.warning(f"Could not create profile for {user.email}: {e}")
