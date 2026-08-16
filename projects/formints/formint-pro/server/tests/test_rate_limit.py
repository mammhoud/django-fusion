"""
API Access (P1) — rate limiting tests.

Covers the sliding-window limiter (pure unit) and the per-key enforcement
surface: the ``ApiKey.rate_limit_per_minute`` field and
``ApiKeyRateLimitMiddleware``.
"""

from __future__ import annotations

import pytest

from formint.rate_limit import (
    ApiKeyRateLimitMiddleware,
    SlidingWindowRateLimiter,
    default_limiter,
)


@pytest.fixture
def _clean_keys(django_bootstrap):
    from models.apikey import ApiKey

    ApiKey.objects.all().delete()
    default_limiter._windows.clear()
    yield
    default_limiter._windows.clear()


class TestSlidingWindowRateLimiter:
    def test_allows_within_limit(self):
        limiter = SlidingWindowRateLimiter()
        for i in range(3):
            allowed, remaining, limit, _ = limiter.check("k", limit=3)
            assert allowed is True
            assert remaining == 2 - i
            assert limit == 3

    def test_blocks_over_limit(self):
        limiter = SlidingWindowRateLimiter()
        for _ in range(2):
            assert limiter.check("k", limit=2)[0] is True
        allowed, remaining, limit, retry_after = limiter.check("k", limit=2)
        assert allowed is False
        assert remaining == 0
        assert limit == 2
        assert retry_after > 0

    def test_evicts_expired_timestamps(self):
        import time

        limiter = SlidingWindowRateLimiter()
        assert limiter.check("k", limit=1, window_seconds=60)[0] is True
        # Manually age the recorded timestamp past the window.
        with limiter._lock:
            for dq in limiter._windows.values():
                for idx in range(len(dq)):
                    dq[idx] -= 61.0
        assert limiter.check("k", limit=1, window_seconds=60)[0] is True

    def test_isolated_per_key(self):
        limiter = SlidingWindowRateLimiter()
        assert limiter.check("a", limit=1)[0] is True
        assert limiter.check("a", limit=1)[0] is False
        assert limiter.check("b", limit=1)[0] is True


class TestApiKeyRateLimitField:
    def test_default_unlimited(self, _clean_keys):
        from models.apikey import ApiKey

        key = ApiKey.create_key(name="k")
        key.save()
        assert key.rate_limit_per_minute is None

    def test_create_key_with_rate_limit(self, _clean_keys):
        from models.apikey import ApiKey

        key = ApiKey.create_key(name="k", rate_limit_per_minute=5)
        key.save()
        assert key.rate_limit_per_minute == 5
        assert ApiKey.lookup_key(key._plaintext).rate_limit_per_minute == 5


class TestRateLimitMiddleware:
    def _request(self, path: str, raw_key: str = ""):
        from django.http import HttpRequest

        request = HttpRequest()
        request.path = path
        request.headers = {"X-API-Key": raw_key} if raw_key else {}
        return request

    def test_skips_non_api_paths(self, _clean_keys):
        mw = ApiKeyRateLimitMiddleware(lambda r: None)
        assert mw._enforce(self._request("/admin/")) is None

    def test_skips_missing_key(self, _clean_keys):
        mw = ApiKeyRateLimitMiddleware(lambda r: None)
        assert mw._enforce(self._request("/api/v1/products/")) is None

    def test_enforces_then_429(self, _clean_keys):
        from models.apikey import ApiKey

        key = ApiKey.create_key(name="k", rate_limit_per_minute=2)
        key.save()

        mw = ApiKeyRateLimitMiddleware(lambda r: None)
        req = self._request("/api/v1/products/", raw_key=key._plaintext)

        first = mw._enforce(req)
        assert isinstance(first, dict)
        assert first["X-RateLimit-Limit"] == "2"
        assert first["X-RateLimit-Remaining"] == "1"

        mw._enforce(req)
        third = mw._enforce(req)
        from django.http import JsonResponse

        assert isinstance(third, JsonResponse)
        assert third.status_code == 429
        assert third["Retry-After"]

    def test_unlimited_key_not_limited(self, _clean_keys):
        from models.apikey import ApiKey

        key = ApiKey.create_key(name="k")  # unlimited
        key.save()
        mw = ApiKeyRateLimitMiddleware(lambda r: None)
        for _ in range(5):
            assert mw._enforce(
                self._request("/api/v1/products/", raw_key=key._plaintext)
            ) is None
