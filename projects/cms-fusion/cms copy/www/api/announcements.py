"""
Announcements API — CRUD endpoints for Wagtail-managed announcements.

Endpoints:
    GET    /apis/announcements/              — List published announcements
    POST   /apis/announcements/create/        — Create announcement (instructor)
    GET    /apis/announcements/<pk>/          — Announcement detail
    PATCH  /apis/announcements/<pk>/update/   — Update announcement (owner)
    DELETE /apis/announcements/<pk>/delete/   — Delete announcement (owner)
"""

import json
import logging

from django.shortcuts import get_object_or_404
from django.utils import timezone

from plugins.lms.models import Announcement
from www.api.data_adapter import (
    bolt_view,
    login_required,
    paginate_queryset,
    parse_body,
    paginated_response,
)

logger = logging.getLogger(__name__)


def _serialize_announcement(a: Announcement) -> dict:
    """Serialize an announcement for the frontend."""
    return {
        "id": a.id,
        "title": a.title,
        "content": a.content,
        "audience": a.audience,
        "link": a.link or "",
        "link_label": a.link_label or "",
        "is_published": a.is_published,
        "published_at": a.published_at.isoformat() if a.published_at else None,
        "created_at": a.created_at.isoformat() if a.created_at else None,
        "updated_at": a.updated_at.isoformat() if a.updated_at else None,
    }


# ── List Announcements ──


@bolt_view
@login_required
def announcement_list(request):
    """GET /apis/announcements/ — List announcements.

    Instructors see all announcements they authored.
    Students see published announcements targeted at 'all' or 'student'.
    Admins see all announcements.
    """
    user = request.user
    is_instructor = user.groups.filter(name="Instructors").exists()
    is_staff = user.is_staff

    if is_staff:
        qs = Announcement.objects.all()
    elif is_instructor:
        qs = Announcement.objects.filter(
            audience__in=["all", "instructor"],
            is_published=True,
        )
    else:
        qs = Announcement.objects.filter(
            audience__in=["all", "student"],
            is_published=True,
        )

    # Optional filters
    audience = request.GET.get("audience")
    if audience:
        qs = qs.filter(audience=audience)

    qs = qs.order_by("sort_order", "-published_at", "-created_at")

    items, pagination = paginate_queryset(qs, request)
    return paginated_response(
        items,
        pagination,
        request,
        [_serialize_announcement(a) for a in items],
    )


# ── Create Announcement ──


@bolt_view
@login_required
def announcement_create(request):
    """POST /apis/announcements/create/ — Create a new announcement (instructor only)."""
    if not request.user.groups.filter(name="Instructors").exists() and not request.user.is_staff:
        return {"status": "error", "message": "Only instructors can create announcements"}, 403

    body = parse_body(request)
    if not body:
        return {"status": "error", "message": "Invalid request body"}, 400

    title = body.get("title", "").strip()
    content = body.get("content", "").strip()
    if not title or not content:
        return {"status": "error", "message": "Title and content are required"}, 400

    publish_now = body.get("publish_now", True)

    announcement = Announcement.objects.create(
        title=title,
        content=content,
        audience=body.get("audience", "all"),
        link=body.get("link", ""),
        link_label=body.get("link_label", ""),
        is_published=publish_now,
        published_at=timezone.now() if publish_now else None,
    )

    return {"status": "success", "data": _serialize_announcement(announcement)}, 201


# ── Announcement Detail ──


@bolt_view
@login_required
def announcement_detail(request, pk):
    """GET /apis/announcements/<pk>/ — Get announcement details."""
    announcement = get_object_or_404(Announcement, pk=pk)
    return {"status": "success", "data": _serialize_announcement(announcement)}


# ── Update Announcement ──


@bolt_view
@login_required
def announcement_update(request, pk):
    """PATCH /apis/announcements/<pk>/update/ — Update an announcement (owner/staff only)."""
    announcement = get_object_or_404(Announcement, pk=pk)

    body = parse_body(request)
    if not body:
        return {"status": "error", "message": "Invalid request body"}, 400

    editable_fields = ["title", "content", "audience", "link", "link_label", "is_published"]
    updated = False
    for field in editable_fields:
        if field in body:
            if field == "is_published" and body[field] and not announcement.published_at:
                announcement.published_at = timezone.now()
            setattr(announcement, field, body[field])
            updated = True

    if not updated:
        return {"status": "error", "message": "No valid fields to update"}, 400

    announcement.save()
    return {"status": "success", "data": _serialize_announcement(announcement)}


# ── Delete Announcement ──


@bolt_view
@login_required
def announcement_delete(request, pk):
    """DELETE /apis/announcements/<pk>/delete/ — Delete an announcement."""
    announcement = get_object_or_404(Announcement, pk=pk)
    announcement.delete()
    return {"status": "success", "message": "Announcement deleted"}
