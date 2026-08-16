"""POS Cloud — Django middleware.

* ``BoltSyncEventsMiddleware`` — injects the sync-events WebSocket script
  into the analytics dashboard pages so live sync events are received
  without requiring a manual template override.
* ``ApiAuthMiddleware`` — rewrites the django-fusion ``login_required``
  login redirect on ``/api/*`` viewset paths into a JSON ``401`` so API
  consumers never get bounced to the (nonexistent) ``/accounts/login/``.
"""

from __future__ import annotations

from django.http import HttpResponse, JsonResponse

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


class ApiAuthMiddleware:
    """Return a JSON 401 instead of a login redirect on ``/api/*`` paths.

    django-fusion's CRUD views (``ListModelView``, ``CreateModelView``,
    ``UpdateModelView``, ``DeleteModelView``, ``DetailModelView``) decorate
    ``dispatch`` with Django's ``login_required``. For anonymous callers that
    produces a 302 to ``settings.LOGIN_URL`` (``/accounts/login/``) — a route
    that does not exist in POS Cloud. For a JSON API a redirect is useless,
    so we rewrite it into the same JSON ``401`` the root surface returns:
    ``{"error": "authentication required"}``.

    Only redirects pointing at the login page are rewritten; successful
    post-authentication redirects (e.g. after a create) pass through.
    """

    # ``login_required`` redirect target from django.contrib.auth.
    _LOGIN_REDIRECT_MARKER = "/accounts/login/"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only the API surface cares about JSON auth failures.
        if not request.path.startswith("/api/"):
            return response

        # Only rewrite auth redirects, not ordinary 3xx flows.
        if response.status_code not in (301, 302):
            return response
        if self._LOGIN_REDIRECT_MARKER not in response.get("Location", ""):
            return response

        return JsonResponse({"error": "authentication required"}, status=401)
