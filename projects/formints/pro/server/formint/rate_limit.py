"""
Formint — sliding-window API-key rate limiting.

P1 "API Access" pillar: enforces a per-key requests-per-minute limit on the
``/api/v1/`` and ``/api-keys/`` surfaces (and any other path registered via
``RATE_LIMITED_PATHS``). The limiter is an in-memory sliding window for
single-node deployments, behind a small interface so a Redis backend can be
swapped in for multi-node/cloud without touching the middleware.

Exposed pieces
--------------
* ``SlidingWindowRateLimiter`` — thread-safe sliding-window counter.
* ``ApiKeyRateLimitMiddleware`` — Django middleware that reads ``X-API-Key``,
  looks up the ``ApiKey``, and enforces its ``rate_limit_per_minute``.
* ``default_limiter`` — module-level limiter instance shared across requests.

Rate-limit headers (set on every rate-limited request)::

    X-RateLimit-Limit      e.g. 60
    X-RateLimit-Remaining  e.g. 59
    X-RateLimit-Reset      seconds until the window resets
    Retry-After            seconds (only on 429)

Register in ``MIDDLEWARE`` after the session/auth middleware (needs nothing
from auth — the key is read from the header — but before the views).
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque
from typing import Deque

from django.http import HttpRequest, JsonResponse

# Paths whose requests are rate-limited when an API key is supplied.
RATE_LIMITED_PATHS = ("/api/v1/", "/api-keys/", "/api/")


class SlidingWindowRateLimiter:
    """Thread-safe in-memory sliding-window counter.

    ``check()`` records the request when allowed and returns the remaining
    budget plus the seconds until the window rolls over.  The implementation
    uses ``time.monotonic`` timestamps so wall-clock jumps (NTP, DST) do not
    skew the window.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._windows: dict[str, Deque[float]] = defaultdict(deque)

    def check(
        self,
        key: str,
        limit: int,
        window_seconds: float = 60.0,
    ) -> tuple[bool, int, int, int]:
        """Check (and, if allowed, record) one request for ``key``.

        Returns ``(allowed, remaining, limit, retry_after_seconds)``.
        ``retry_after_seconds`` is meaningful only when ``allowed`` is False.
        """
        now = time.monotonic()
        with self._lock:
            window = self._windows[key]
            # Evict timestamps outside the current window.
            cutoff = now - window_seconds
            while window and window[0] <= cutoff:
                window.popleft()

            if len(window) >= limit:
                oldest = window[0]
                retry_after = max(1, int(window_seconds - (now - oldest)) + 1)
                return False, 0, limit, retry_after

            window.append(now)
            remaining = limit - len(window)
            return True, remaining, limit, int(window_seconds)


# Module-level limiter shared by the middleware across all requests in a
# process. A Redis-backed implementation would swap this for a client that
# uses INCR + EXPIRE (or a sorted set) keyed by the ApiKey prefix.
default_limiter = SlidingWindowRateLimiter()


def _is_rate_limited_path(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in RATE_LIMITED_PATHS)


class ApiKeyRateLimitMiddleware:
    """Enforce per-key rate limits on API paths.

    Reads ``X-API-Key`` from the request; if it resolves to a valid
    ``ApiKey`` with ``rate_limit_per_minute`` set, enforces the limit.
    Invalid/missing keys are passed through so the (separate) authentication
    layer can reject them with the right status code.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        """Enforce the limit before the view, then annotate the response.

        Returns a 429 immediately when the key is over budget; otherwise
        records the request and attaches the rate-limit headers to the view
        response via a temporary ``request`` attribute.
        """
        enforcement = self._enforce(request)
        if isinstance(enforcement, JsonResponse):
            return enforcement  # 429 — do not call the view

        response = self.get_response(request)
        headers = enforcement or getattr(request, "_rate_limit_headers", None)
        if headers:
            for name, value in headers.items():
                response[name] = value
        return response

    def _enforce(self, request: HttpRequest):
        """Return a 429 response, a headers dict, or ``None`` (no-op)."""
        if not _is_rate_limited_path(request.path):
            return None

        raw_key = request.headers.get("X-API-Key", "")
        if not raw_key:
            return None

        try:
            from models.apikey import ApiKey

            key_obj = ApiKey.lookup_key(raw_key)
        except Exception:  # pragma: no cover — DB not ready during early boot
            return None

        if key_obj is None:
            return None

        limit = key_obj.rate_limit_per_minute
        if not limit:
            return None

        allowed, remaining, limit, retry_after = default_limiter.check(
            key=key_obj.prefix, limit=limit, window_seconds=60.0,
        )

        if not allowed:
            resp = JsonResponse(
                {"error": "rate_limit_exceeded", "message": "Too many requests"},
                status=429,
            )
            resp["Retry-After"] = str(retry_after)
            resp["X-RateLimit-Limit"] = str(limit)
            resp["X-RateLimit-Remaining"] = "0"
            resp["X-RateLimit-Reset"] = str(retry_after)
            return resp

        return {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(retry_after),
        }
