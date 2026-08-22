"""API v1 deprecation signalling.

Adds ``Deprecation`` and ``Sunset`` headers to every ``/api/v1/`` response
so client code, API consumers, and operator dashboards can see that the
compatibility road is planned for retirement. The canonical Bolt road
(``/bolt/``) and the new named roads (``/apis/``) are the forward paths.

This middleware is deliberately passive: it only adds headers, never blocks
requests. The frontend's ``BoltApiClient`` reads the ``Deprecation`` header and
emits a ``console.warn`` when the fallback road is engaged.
"""

from __future__ import annotations

from typing import Callable

from django.http import HttpRequest, HttpResponse

#: RFC 8594 — a hint for automated consumers that this API is deprecated.
DEPRECATION_HEADER = "Deprecation"

#: RFC 8594 — the date after which the deprecated resource may become
#: unavailable. Set far enough out to give all consumers time to migrate.
#: Format: ``@<unix-timestamp>`` (RFC 7231 IMF-fixdate also accepted).
SUNSET_HEADER = "Sunset"

#: RFC 7234 — a human-readable warning that the resource is deprecated.
#: Format: ``299 - "message"``.
WARNING_HEADER = "Warning"

#: The v1 compatibility road path prefix.
V1_PREFIX = "/api/v1"

#: Sunset date — clients should migrate before this date.
#: 2027-01-01 = 1798761600
SUNSET_UNIX = "1798761600"

#: Warning message (RFC 7234 §5.5, warn-code 299 = "Miscellaneous Persistent Warning").
WARNING_VALUE = (
    '299 - "The /api/v1/ compatibility road is deprecated and will be removed. '
    'Migrate to the canonical /bolt/ road or the named /apis/ endpoints."'
)


def _is_v1_path(path: str) -> bool:
    """Check whether *path* (with leading slash) is on the v1 road."""
    return path.startswith(V1_PREFIX)


class APIV1DeprecationMiddleware:
    """Add deprecation headers to every ``/api/v1/`` response."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        if _is_v1_path(request.path):
            response[DEPRECATION_HEADER] = "true"
            response[SUNSET_HEADER] = f"@{SUNSET_UNIX}"
            response[WARNING_HEADER] = WARNING_VALUE
        return response