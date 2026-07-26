"""
Data Contact API — inquiries management, mark-as-read.

Extends the existing contact submit endpoint in ``apis.py`` with
admin-only inquiry listing and mark-read functionality.
"""

from __future__ import annotations

import json
import logging

from www.api.data.helpers import paginate_queryset, parse_body, get_current_user, get_image_url, get_user_display_name
from www.auth import TokenAuthBackend, auth_required

logger = logging.getLogger(__name__)


def register_handlers(bolt):
    """Register contact handlers on the given BoltAPI instance."""

    # ── GET /apis/contact/inquiries — list contact inquiries (staff only) ──
    @bolt.get("/contact/inquiries", **auth_required())
    def list_inquiries(request):
        """GET /apis/contact/inquiries — List contact form submissions (staff only)."""
        user = get_current_user(request)
        if user is None or not user.is_staff:
            return {"status": "error", "message": "Permission denied"}, 403

        submissions = _get_submissions(request)

        # Handle both QuerySet and list results
        is_queryset = hasattr(submissions, "count")
        if is_queryset:
            items, pagination = paginate_queryset(submissions, request, default_per_page=20)
            data = [_serialize_submission(s) for s in items]
        else:
            items = submissions
            data = items
            total = len(items) if isinstance(items, list) else 0
            pagination = {"page": 1, "per_page": 20, "total": total, "total_pages": max(1, total // 20 + (1 if total % 20 else 0)) if total else 0}

        return {"status": "success", "data": data, "pagination": pagination}

    # ── POST /apis/contact/inquiries/<pk>/mark-read — mark inquiry as read ──
    @bolt.post("/contact/inquiries/<int:pk>/mark-read", **auth_required())
    def mark_inquiry_read(request, pk):
        """POST /apis/contact/inquiries/<pk>/mark-read — Mark inquiry as read (staff only)."""
        user = get_current_user(request)
        if user is None or not user.is_staff:
            return {"status": "error", "message": "Permission denied"}, 403

        try:
            from plugins.accounts.models.forms.submission import FormSubmission
            submission = FormSubmission.objects.get(pk=pk, form_type="contact")
            if hasattr(submission, "is_read"):
                submission.is_read = True
                submission.save(update_fields=["is_read"])
            return {"status": "success", "message": "Marked as read"}
        except Exception:
            return {"status": "error", "message": "Inquiry not found"}, 404


# ═══════════════════════════════════════════════════════════════════════
# Internal helpers
# ═══════════════════════════════════════════════════════════════════════


def _get_submissions(request):
    """Get contact form submissions from available models."""
    try:
        from plugins.accounts.models.forms.submission import FormSubmission
        return FormSubmission.objects.filter(form_type="contact").order_by("-created_at")
    except Exception as exc:
        logger.warning("Contact submission backend not available: %s", exc)
        return []


def _serialize_submission(sub) -> dict:
    """Serialize a FormSubmission into the inquiry response shape."""
    try:
        raw = json.loads(sub.data) if isinstance(sub.data, str) else sub.data
    except Exception:
        raw = {}

    return {
        "id": sub.id,
        "name": raw.get("name", ""),
        "email": raw.get("email", ""),
        "subject": raw.get("subject", ""),
        "message": raw.get("message", ""),
        "is_read": getattr(sub, "is_read", False),
        "created_at": (
            sub.created_at.isoformat()
            if hasattr(sub, "created_at") and sub.created_at
            else ""
        ),
    }
