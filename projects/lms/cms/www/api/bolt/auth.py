"""
Bolt Auth API — login, register, logout, profile, password reset, change password.

Extends the existing bolt auth endpoints in ``apis.py`` with additional
profile management and password change/reset actions that existed only in DRF.
"""

from __future__ import annotations

import json
import logging

from www.auth import TokenAuthBackend, extract_bearer_token, authenticate_request
from www.api.bolt.helpers import parse_body, get_current_user, get_image_url, get_user_display_name

logger = logging.getLogger(__name__)


def register_handlers(bolt):
    """Register auth handlers on the given BoltAPI instance."""

    # ── GET /apis/auth/profile — current user profile ──
    @bolt.get("/auth/profile", auth=[TokenAuthBackend()])
    def get_profile(request):
        """GET /apis/auth/profile — Return authenticated user's full profile."""
        user = get_current_user(request)
        if user is None:
            return {"status": "error", "message": "Unauthorized"}, 401
        return _serialize_user_profile(user)

    # ── PATCH /apis/auth/profile — update profile ──
    @bolt.patch("/auth/profile", auth=[TokenAuthBackend()])
    def update_profile(request):
        """PATCH /apis/auth/profile — Update current user's profile fields."""
        user = get_current_user(request)
        if user is None:
            return {"status": "error", "message": "Unauthorized"}, 401

        body = parse_body(request)

        # Build update_fields dynamically so bio is saved when present
        update_fields = []
        for field in ["first_name", "last_name", "email"]:
            if field in body and body[field] is not None:
                setattr(user, field, str(body[field]).strip())
                update_fields.append(field)

        bio_val = body.get("bio")
        if bio_val is not None and hasattr(user, "bio"):
            user.bio = bio_val
            update_fields.append("bio")

        if update_fields:
            user.save(update_fields=update_fields)

        return _serialize_user_profile(user)

    # ── POST /apis/auth/password-reset — send reset email ──
    @bolt.post("/auth/password-reset")
    def password_reset(request):
        """POST /apis/auth/password-reset — Send password reset email."""
        body = parse_body(request)
        email = body.get("email", "")

        if not email:
            return {"status": "error", "message": "Email is required"}, 400

        from django.contrib.auth.forms import PasswordResetForm
        form = PasswordResetForm({"email": email})
        if form.is_valid():
            form.save(
                request=request,
                use_https=request.is_secure() if hasattr(request, "is_secure") else False,
                email_template_name="registration/password_reset_email.html",
            )

        # Always return success to avoid leaking user existence
        return {
            "status": "success",
            "message": "If an account with that email exists, a password reset link has been sent.",
        }

    # ── POST /apis/auth/change-password — change password ──
    @bolt.post("/auth/change-password", auth=[TokenAuthBackend()])
    def change_password(request):
        """POST /apis/auth/change-password — Change current user's password."""
        user = get_current_user(request)
        if user is None:
            return {"status": "error", "message": "Unauthorized"}, 401

        body = parse_body(request)
        old_password = body.get("old_password", "")
        new_password = body.get("new_password", "")

        if not old_password or not new_password:
            return {"status": "error", "message": "old_password and new_password are required"}, 400

        if len(new_password) < 8:
            return {"status": "error", "message": "New password must be at least 8 characters"}, 400

        if not user.check_password(old_password):
            return {"status": "error", "message": "Current password is incorrect"}, 400

        user.set_password(new_password)
        user.save(update_fields=["password"])

        return {"status": "success", "message": "Password changed successfully"}


# ═══════════════════════════════════════════════════════════════════════
# Internal helpers
# ═══════════════════════════════════════════════════════════════════════


def _serialize_user_profile(user) -> dict:
    """Serialize a User into a full profile response compatible with the DRF UserSerializer shape."""
    from www.api.bolt.helpers import get_image_url, get_user_display_name

    # Determine role from groups
    role = "student"
    try:
        if user.groups.filter(name="Instructors").exists():
            role = "instructor"
    except Exception:
        pass

    # Get bio if available
    bio = ""
    if hasattr(user, "bio"):
        bio = user.bio if user.bio else ""

    return {
        "status": "success",
        "data": {
            "id": user.pk,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": role,
            "avatar": "",
            "bio": bio,
            "date_joined": user.date_joined.isoformat() if user.date_joined else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
        },
    }
