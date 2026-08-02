"""Django REST views for Fusion LMS events API.

Mirrors the courses API pattern (standard Django function-based views that
work with runserver). The frontend ``eventsApi`` (RTK Query) expects a
DRF-style paginated response shape: ``{results: [...], count, next, previous}``.

Mount: /api/events, /api/events/<id>, /api/events/upcoming
"""

from __future__ import annotations

import logging

from django.http import JsonResponse

logger = logging.getLogger(__name__)


def _qp(request, key: str, default: str = "") -> str:
    """Get a query parameter safely."""
    return request.GET.get(key, default)


def _qp_int(request, key: str, default: int = 1) -> int:
    """Get an integer query parameter safely."""
    try:
        return int(_qp(request, key, str(default)))
    except (TypeError, ValueError):
        return default


def _event_to_dict(event) -> dict:
    """Serialize an Event model instance to the frontend Event shape."""
    return {
        "id": event.pk,
        "title": event.title,
        "slug": getattr(event, "slug", "") or "",
        "description": getattr(event, "description", "") or "",
        "short_description": getattr(event, "short_description", "") or "",
        "featured_image": (
            event.featured_image.file.url
            if getattr(event, "featured_image", None)
            else ""
        ),
        "start_date": event.start_date.isoformat() if getattr(event, "start_date", None) else None,
        "end_date": event.end_date.isoformat() if getattr(event, "end_date", None) else None,
        "location": getattr(event, "location", "") or "",
        "is_online": bool(getattr(event, "is_online", False)),
        "meeting_url": getattr(event, "meeting_url", "") or "",
        "capacity": getattr(event, "capacity", 0) or 0,
        "registered_count": getattr(event, "registered_count", 0) or 0,
        "price": float(getattr(event, "price", 0) or 0),
        "is_free": bool(getattr(event, "is_free", False)),
        "organizer": getattr(event, "organizer", "") or "",
        "event_type": getattr(event, "event_type", "") or "",
        "status": getattr(event, "status", "upcoming") or "upcoming",
        "is_visible": bool(getattr(event, "is_visible", True)),
        "created_at": (
            event.created_at.isoformat()
            if getattr(event, "created_at", None)
            else None
        ),
    }


def list_events(request):
    """GET /api/events — Event listing with pagination and status filter."""
    try:
        from apps.handlers.models.manage.event import Event

        qs = Event.objects.filter(is_visible=True, is_active=True).order_by(
            "-start_date"
        )

        status = _qp(request, "status")
        if status and hasattr(Event, "status"):
            qs = qs.filter(status=status)

        page = _qp_int(request, "page", 1)
        per_page = _qp_int(request, "per_page", 12)
        total = qs.count()
        events = qs[(page - 1) * per_page : page * per_page]

        return JsonResponse({
            "results": [_event_to_dict(e) for e in events],
            "count": total,
            "next": None,
            "previous": None,
        })
    except Exception:
        logger.exception("Error listing events")
        return JsonResponse({"results": [], "count": 0, "next": None, "previous": None})


def upcoming_events(request):
    """GET /api/events/upcoming — Upcoming events for home/carousel widgets."""
    try:
        from django.utils import timezone

        from apps.handlers.models.manage.event import Event

        now = timezone.now()
        qs = (
            Event.objects.filter(is_visible=True, is_active=True)
            .filter(start_date__gte=now)
            .order_by("start_date")
        )
        events = list(qs[:6])
        # Frontend declares getUpcomingEvents as Event[] (raw array, not paginated).
        return JsonResponse([_event_to_dict(e) for e in events], safe=False)
    except Exception:
        logger.exception("Error listing upcoming events")
        return JsonResponse({"results": [], "count": 0})


def event_detail(request, pk):
    """GET /api/events/<pk> — Single event detail."""
    try:
        import uuid

        # The Event model uses a UUID primary key — reject malformed keys
        # before querying so they 404 instead of surfacing a 500.
        try:
            uuid.UUID(str(pk))
        except (ValueError, TypeError):
            return JsonResponse({"status": "error", "message": "Event not found"}, status=404)

        from apps.handlers.models.manage.event import Event

        event = Event.objects.filter(pk=pk, is_visible=True, is_active=True).first()
        if event is None:
            return JsonResponse({"status": "error", "message": "Event not found"}, status=404)
        return JsonResponse(_event_to_dict(event))
    except Exception:
        logger.exception("Error loading event detail")
        return JsonResponse({"status": "error", "message": "Internal server error"}, status=500)
