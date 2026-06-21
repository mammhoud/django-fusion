"""
Chat views — JSON endpoint consumed by the bubble.html widget.
"""
from __future__ import annotations

import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .backends import get_reply
from .models import ChatMessage, ChatSession

logger = logging.getLogger(__name__)


@require_POST
def chat_message(request):
    """
    POST /chat/message/
    Body: {"message": "...", "session_id": "..."}
    Returns: {"reply": "..."}
    """
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    message = (body.get("message") or "").strip()
    session_id = (body.get("session_id") or "").strip()

    if not message:
        return JsonResponse({"error": "Empty message"}, status=400)
    if not session_id:
        return JsonResponse({"error": "Missing session_id"}, status=400)

    # Get or create session
    session, _ = ChatSession.objects.get_or_create(
        session_id=session_id,
        defaults={
            "user": request.user if request.user.is_authenticated else None,
            "backend": _resolve_backend(request),
        },
    )

    # Persist user message
    ChatMessage.objects.create(session=session, role=ChatMessage.ROLE_USER, text=message)

    # Get AI reply
    reply = get_reply(session, message)

    # Persist bot reply
    ChatMessage.objects.create(session=session, role=ChatMessage.ROLE_BOT, text=reply)

    return JsonResponse({"reply": reply, "session_id": session_id})


def _resolve_backend(request) -> str:
    """Determine which AI backend to use (from settings or request header)."""
    from django.conf import settings
    return getattr(settings, "RSEAL_CHAT_BACKEND", "echo")
