"""
Data Events API — detail, upcoming filter, registration.

Extends the existing event endpoints in ``apis.py`` (which provide
basic listing) with additional detail and registration endpoints.
"""

from __future__ import annotations

import logging

from django.utils import timezone

from www.api.data.helpers import paginate_queryset, parse_body, get_current_user, get_image_url, get_user_display_name
from www.auth import TokenAuthBackend, auth_required

logger = logging.getLogger(__name__)


def register_handlers(bolt):
    """Register event handlers on the given BoltAPI instance."""

    # ── GET /apis/events/<pk> — single event detail ──
    @bolt.get("/events/<int:pk>")
    def get_event(request, pk):
        """GET /apis/events/<pk> — Single event detail."""
        try:
            from plugins.accounts.models import Event as EventModel
            event = EventModel.objects.get(pk=pk, is_active=True)
        except Exception:
            try:
                from www.content.models.blog import Event as EventModel
                event = EventModel.objects.get(pk=pk, is_published=True)
            except Exception:
                return {"status": "error", "message": "Event not found"}, 404

        return {"status": "success", "data": _serialize_event(event)}

    # ── GET /apis/events/upcoming — upcoming events ──
    @bolt.get("/events/upcoming")
    def list_upcoming_events(request):
        """GET /apis/events/upcoming — Upcoming (future) events, max 6."""
        try:
            from plugins.accounts.models import Event as EventModel
            events = EventModel.objects.filter(
                is_active=True, is_visible=True,
                start_date__gte=timezone.now(),
            ).order_by("start_date")[:6]
        except Exception as exc:
            logger.warning("Upcoming events (plugins.accounts) failed: %s", exc)
            try:
                from www.content.models.blog import Event as EventModel
                events = EventModel.objects.filter(
                    is_published=True,
                    event_date__gte=timezone.now(),
                ).order_by("event_date")[:6]
            except Exception as exc2:
                logger.warning("Upcoming events (blog) also failed: %s", exc2)
                events = []

        data = [_serialize_event(e) for e in events]
        return {"status": "success", "count": len(data), "results": data}

    # ── POST /apis/events/register — register for an event ──
    @bolt.post("/events/register")
    def register_for_event(request):
        """POST /apis/events/register — Register for an event."""
        body = parse_body(request)
        event_id = body.get("event_id")
        full_name = body.get("full_name", "")
        email = body.get("email", "")
        phone = body.get("phone", "")

        if not event_id or not full_name or not email:
            return {"status": "error", "message": "event_id, full_name, and email are required"}, 400

        try:
            from plugins.accounts.models import Event as EventModel
            event = EventModel.objects.get(pk=event_id, is_active=True)
        except Exception:
            return {"status": "error", "message": "Event not found"}, 404

        registration_data = {
            "event": event.id,
            "event_title": event.title,
            "full_name": full_name,
            "email": email,
            "phone": phone or "",
            "is_attended": False,
            "registered_at": timezone.now().isoformat(),
        }

        # Try saving registration if the model exists
        try:
            from plugins.accounts.models import EventRegistration
            reg = EventRegistration.objects.create(
                event=event,
                full_name=full_name,
                email=email,
                phone=phone or "",
            )
            registration_data["id"] = reg.id
            registration_data["registered_at"] = (
                reg.created_at.isoformat() if hasattr(reg, "created_at") and reg.created_at
                else timezone.now().isoformat()
            )
        except Exception:
            registration_data["id"] = 0

        return {"status": "success", "data": registration_data}


# ═══════════════════════════════════════════════════════════════════════
# Internal helpers
# ═══════════════════════════════════════════════════════════════════════


def _serialize_event(event) -> dict:
    """Serialize an event instance into the response shape matching DRF EventSerializer."""
    return {
        "id": event.pk,
        "title": event.title,
        "slug": getattr(event, "slug", ""),
        "description": getattr(event, "description", ""),
        "short_description": getattr(event, "short_description", "")
            or (getattr(event, "description", "")[:200] if getattr(event, "description", None) else ""),
        "featured_image": getattr(event, "image_url", "")
            or get_image_url(getattr(event, "image", None))
            or "",
        "start_date": (
            event.start_date.isoformat()
            if hasattr(event, "start_date") and event.start_date
            else (
                event.event_date.isoformat()
                if hasattr(event, "event_date") and event.event_date
                else ""
            )
        ),
        "end_date": (
            event.end_date.isoformat()
            if hasattr(event, "end_date") and event.end_date
            else ""
        ),
        "location": getattr(event, "location", ""),
        "is_online": getattr(event, "is_online", False),
        "meeting_url": getattr(event, "meeting_url", ""),
        "capacity": int(getattr(event, "capacity", 0) or getattr(event, "max_participants", 0) or 0),
        "registered_count": int(getattr(event, "registered_count", 0) or 0),
        "price": float(getattr(event, "price", 0)) if hasattr(event, "price") else 0,
        "is_free": getattr(event, "price", 0) == 0 if hasattr(event, "price") else True,
        "organizer": getattr(event, "speaker_name", "") or getattr(event, "organizer", ""),
        "status": getattr(event, "status", "upcoming") or "upcoming",
        "is_published": getattr(event, "is_published", True),
        "created_at": (
            event.created_at.isoformat()
            if hasattr(event, "created_at") and event.created_at
            else ""
        ),
    }
