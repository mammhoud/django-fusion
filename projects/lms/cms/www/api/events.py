"""
Events API — list and detail (bolt-pattern adapter).

Matches the RTK Query slice at: store/api/endpoints/events.ts
"""

import logging

from django.shortcuts import get_object_or_404

from www.api.data_adapter import (
    bolt_view,
    paginate_queryset,
    get_image_url,
    get_user_display_name,
    paginated_response,
)

logger = logging.getLogger(__name__)


def _serialize_event(event) -> dict:
    """Serialize an Event to the frontend-expected format."""
    return {
        "id": event.id,
        "title": event.title,
        "slug": getattr(event, "slug", ""),
        "short_description": (
            getattr(event, "short_description", "")
            or (
                getattr(event, "description", "")[:200]
                if getattr(event, "description", None)
                else ""
            )
        ),
        "description": getattr(event, "description", ""),
        "image": getattr(event, "image_url", "") or "",
        "start_date": (
            event.start_date.isoformat()
            if hasattr(event, "start_date") and event.start_date
            else ""
        ),
        "end_date": (
            event.end_date.isoformat()
            if hasattr(event, "end_date") and event.end_date
            else ""
        ),
        "location": getattr(event, "location", ""),
        "is_online": getattr(event, "is_online", False),
        "is_free": getattr(event, "price", 0) == 0 if hasattr(event, "price") else True,
        "price": float(getattr(event, "price", 0)) if hasattr(event, "price") else 0,
        "capacity": getattr(event, "capacity", 0)
        or getattr(event, "max_participants", 0)
        or 0,
        "registered_count": getattr(event, "registered_count", 0) or 0,
        "status": getattr(event, "status", "upcoming") or "upcoming",
        "category": getattr(event, "category", "")
        or getattr(event, "event_type", "")
        or "",
        "speaker_name": getattr(event, "speaker_name", ""),
        "speaker_role": getattr(event, "speaker_role", ""),
        "created_at": (
            event.created_at.isoformat()
            if hasattr(event, "created_at") and event.created_at
            else None
        ),
    }


def _get_events(request):
    """Try Event model from plugins, return empty if not available."""
    try:
        from plugins.accounts.models import Event

        queryset = Event.objects.filter(is_active=True, is_visible=True)
        status = request.GET.get("status", "").strip()
        if status == "upcoming":
            from django.utils import timezone

            queryset = queryset.filter(start_date__gte=timezone.now())
        elif status == "past":
            from django.utils import timezone

            queryset = queryset.filter(start_date__lt=timezone.now())
        return queryset.order_by("start_date")
    except Exception:
        return []


@bolt_view
def event_list(request):
    """GET /api/events/ — List upcoming and past events."""
    events = _get_events(request)
    items, pagination = (
        paginate_queryset(events, request)
        if hasattr(events, "count")
        else ([], {"page": 1, "per_page": 20, "total": 0, "total_pages": 0})
    )
    return paginated_response(
        items, pagination, request, [_serialize_event(e) for e in items]
    )


@bolt_view
def event_detail(request, pk):
    """GET /api/events/<pk>/ — Get single event details."""
    try:
        from plugins.accounts.models import Event

        event = get_object_or_404(Event, pk=pk, is_active=True)
    except Exception:
        return {"status": "error", "message": "Event not found"}, 404

    data = _serialize_event(event)
    return {"status": "success", "data": data}
