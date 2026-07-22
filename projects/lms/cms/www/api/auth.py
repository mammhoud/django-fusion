"""
Auth API — login, register, logout, profile, password reset (bolt-pattern adapter).

Matches the RTK Query slice at: store/api/endpoints/auth.ts
"""

import json
import logging

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User

from www.api.data_adapter import bolt_view, login_required, parse_body
from www.content.models.others import Token

logger = logging.getLogger(__name__)


def _serialize_user(user: User) -> dict:
    """Serialize a User to the frontend-expected format."""
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": "instructor" if user.groups.filter(name="Instructors").exists() else "student",
        "avatar": "",
        "bio": getattr(user, "bio", ""),
        "date_joined": user.date_joined.isoformat(),
        "last_login": user.last_login.isoformat() if user.last_login else None,
    }


@bolt_view
def login_view(request):
    """POST /api/auth/login/ — Authenticate and return an API token."""
    body = parse_body(request)
    if not body:
        return {"status": "error", "message": "Invalid request body"}, 400

    username = body.get("username", "").strip()
    password = body.get("password", "")

    if not username or not password:
        return {"status": "error", "message": "Username and password are required"}, 400

    user = authenticate(request, username=username, password=password)
    if user is None:
        return {"status": "error", "message": "Invalid credentials"}, 401

    token_obj, raw_token = Token.from_django_fusion_pattern(
        user, token_type="access", category="api"
    )

    return {
        "status": "success",
        "token": raw_token,
        "user": _serialize_user(user),
    }


@bolt_view
def register_view(request):
    """POST /api/auth/register/ — Create a new user account and return token."""
    body = parse_body(request)
    if not body:
        return {"status": "error", "message": "Invalid request body"}, 400

    username = body.get("username", "").strip()
    email = body.get("email", "").strip()
    password = body.get("password", "")
    password2 = body.get("password2", "")
    first_name = body.get("first_name", "").strip()
    last_name = body.get("last_name", "").strip()
    role = body.get("role", "student")

    # Validation
    errors = {}
    if not username:
        errors["username"] = "Username is required"
    if User.objects.filter(username=username).exists():
        errors["username"] = "Username already taken"
    if not email:
        errors["email"] = "Email is required"
    elif User.objects.filter(email=email).exists():
        errors["email"] = "Email already registered"
    if not password:
        errors["password"] = "Password is required"
    elif len(password) < 8:
        errors["password"] = "Password must be at least 8 characters"
    if password != password2:
        errors["password2"] = "Passwords do not match"
    if role not in ("student", "instructor"):
        errors["role"] = "Role must be 'student' or 'instructor'"

    if errors:
        return {"status": "error", "errors": errors}, 400

    user = User.objects.create_user(
        username=username, email=email, password=password,
        first_name=first_name, last_name=last_name,
    )

    from django.contrib.auth.models import Group
    group_name = "Instructors" if role == "instructor" else "Students"
    group, _ = Group.objects.get_or_create(name=group_name)
    user.groups.add(group)

    token_obj, raw_token = Token.from_django_fusion_pattern(
        user, token_type="access", category="api"
    )

    return {
        "status": "success",
        "token": raw_token,
        "user": _serialize_user(user),
    }, 201


@bolt_view
def logout_view(request):
    """POST /api/auth/logout/ — Invalidate the current API token."""
    if hasattr(request, "auth_token") and request.auth_token:
        try:
            request.auth_token.delete()
        except Exception:
            pass
    return {"status": "success", "message": "Logged out successfully"}


@bolt_view
@login_required
def profile_view(request):
    """GET/PATCH /api/auth/profile/ — Get or update current user profile."""
    if request.method == "PATCH":
        body = parse_body(request)
        if not body:
            return {"status": "error", "message": "Invalid request body"}, 400

        user = request.user
        allowed_fields = {"first_name", "last_name", "email", "bio"}
        for field in allowed_fields:
            if field in body:
                setattr(user, field, body[field])
        user.save(update_fields=[f for f in allowed_fields if f in body])

    return {"status": "success", **_serialize_user(request.user)}


@bolt_view
def password_reset_view(request):
    """POST /api/auth/password-reset/ — Send password reset email."""
    body = parse_body(request)
    if not body:
        return {"status": "error", "message": "Invalid request body"}, 400

    email = body.get("email", "").strip()
    if not email:
        return {"status": "error", "message": "Email is required"}, 400

    form = PasswordResetForm({"email": email})
    if form.is_valid():
        form.save(
            request=request,
            use_https=request.is_secure(),
            email_template_name="registration/password_reset_email.html",
        )

    return {
        "status": "success",
        "message": "If an account with that email exists, a password reset link has been sent.",
    }


@bolt_view
@login_required
def change_password_view(request):
    """POST /api/auth/change-password/ — Change password for authenticated user."""
    body = parse_body(request)
    if not body:
        return {"status": "error", "message": "Invalid request body"}, 400

    old_password = body.get("old_password", "")
    new_password = body.get("new_password", "")

    if not request.user.check_password(old_password):
        return {"status": "error", "message": "Current password is incorrect"}, 400

    if len(new_password) < 8:
        return {"status": "error", "message": "New password must be at least 8 characters"}, 400

    request.user.set_password(new_password)
    request.user.save(update_fields=["password"])
    from django.contrib.auth import update_session_auth_hash
    update_session_auth_hash(request, request.user)

    return {"status": "success", "message": "Password changed successfully"}
