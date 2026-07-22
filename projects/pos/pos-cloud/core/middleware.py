"""POS Cloud — Middleware to inject the sync-events WebSocket script
into the analytics dashboard pages so live sync events are received
without requiring a manual template override."""

from __future__ import annotations

from django.http import HttpResponse

_SCRIPT_TAG = '<script src="/static/js/bolt-sync-events.js" defer></script>'

# Only inject on dashboard root pages (not every sub-page / API call).
_DASHBOARD_PREFIXES = ("/apis", "/admin/")


class BoltSyncEventsMiddleware:
    """Injects the WebSocket event listener script into the analytics dashboard."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only touch HTML responses on dashboard / admin paths.
        if not any(request.path.startswith(p) for p in _DASHBOARD_PREFIXES):
            return response

        content_type = response.get("Content-Type", "")
        if "text/html" not in content_type:
            return response

        # Don't consume streaming responses.
        if hasattr(response, "streaming_content"):
            return response

        # Decode, inject, re-encode.
        try:
            content = response.content.decode(response.charset or "utf-8")
        except (UnicodeDecodeError, LookupError):
            return response  # Non-text content — leave untouched

        if "</body>" in content:
            content = content.replace("</body>", f"{_SCRIPT_TAG}\n</body>")
        else:
            content += f"\n{_SCRIPT_TAG}"

        # Build a fresh response to avoid issues with streaming responses.
        return HttpResponse(
            content,
            status=response.status_code,
            headers={k: v for k, v in response.items() if k != "Content-Type"},
            content_type=content_type,
        )
