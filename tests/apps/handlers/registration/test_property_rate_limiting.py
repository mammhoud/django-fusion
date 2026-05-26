"""
Property-based tests for registration rate limiting.

**Validates: Requirements 9.9, 19.3, 19.4**

Tests the `rate_limit_check()` and `rate_limit_increment()` functions from
`apps.accounts.registration.views`.

Property 2: After 5 registration attempts from the same IP within 1 hour,
the 6th attempt returns HTTP 429.

Specifically:
  2a. After exactly 5 increments, `rate_limit_check()` returns False
      (rate limited).
  2b. For any N < 5 increments, `rate_limit_check()` returns True (allowed).
  2c. For any N >= 5 increments, `rate_limit_check()` returns False
      (rate limited).
  2d. When the cache raises an exception, `rate_limit_check()` returns True
      (fail-open).

These tests are standalone — they configure Django with an in-memory cache
backend and test the pure rate-limiting functions directly.
"""

# ---------------------------------------------------------------------------
# Minimal Django setup — must happen before any django.* import
# ---------------------------------------------------------------------------
import sys
import types

import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        },
        SECRET_KEY="test-secret-key-for-property-tests-at-least-50-chars-long!!",
        USE_TZ=True,
    )
    django.setup()

# ---------------------------------------------------------------------------
# Mock the heavy import chain so views.py can be imported without wagtail
# ---------------------------------------------------------------------------


def _ensure_mock(name: str) -> types.ModuleType:
    """Return an existing sys.modules entry or create a new mock module."""
    if name not in sys.modules:
        mod = types.ModuleType(name)
        sys.modules[name] = mod
    return sys.modules[name]


# django_osoul.comp.site — needs a PageHandler class
_ensure_mock("django_grep")
_ensure_mock("django_osoul.comp")
_site_mod = _ensure_mock("django_osoul.comp.site")
if not hasattr(_site_mod, "PageHandler"):

    class _PageHandler:
        def dispatch(self, request, *args, **kwargs):
            pass

    _site_mod.PageHandler = _PageHandler

# registration sub-modules
_emails_mod = _ensure_mock("apps.accounts.registration.emails")
if not hasattr(_emails_mod, "send_registration_email"):
    _emails_mod.send_registration_email = lambda *a, **kw: True

_forms_mod = _ensure_mock("apps.accounts.registration.forms")
if not hasattr(_forms_mod, "RegistrationForm"):
    _forms_mod.RegistrationForm = type("RegistrationForm", (), {})
if not hasattr(_forms_mod, "PasswordCreationForm"):
    _forms_mod.PasswordCreationForm = type("PasswordCreationForm", (), {})

_tokens_mod = _ensure_mock("apps.accounts.registration.tokens")
if not hasattr(_tokens_mod, "registration_token_generator"):
    _tokens_mod.registration_token_generator = object()

# ---------------------------------------------------------------------------
# Now import the functions under test
# ---------------------------------------------------------------------------
from unittest.mock import patch  # noqa: E402

from django.core.cache import cache  # noqa: E402
from hypothesis import given  # noqa: E402
from hypothesis import settings as h_settings
from hypothesis import strategies as st  # noqa: E402
from www.apps.accounts.registration.views import (  # noqa: E402
    RATE_LIMIT_MAX_ATTEMPTS,
    rate_limit_check,
    rate_limit_increment,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_request(ip: str):
    """Create a minimal mock request with the given IP address."""

    class FakeRequest:
        META = {"REMOTE_ADDR": ip}
        headers = {}

    return FakeRequest()


def _clear_cache_for_ip(ip: str):
    """Clear the rate limit cache entry for a specific IP."""
    cache.delete(f"reg_rate_limit:{ip}")


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# IPv4-like strings — use text strategy constrained to valid-looking IPs
# to keep tests focused and avoid cache key collisions between examples
ip_strategy = st.builds(
    "{}.{}.{}.{}".format,
    st.integers(min_value=1, max_value=254),
    st.integers(min_value=0, max_value=255),
    st.integers(min_value=0, max_value=255),
    st.integers(min_value=1, max_value=254),
).map(str)

# Number of attempts below the limit (0 to RATE_LIMIT_MAX_ATTEMPTS - 1)
attempts_below_limit_strategy = st.integers(
    min_value=0, max_value=RATE_LIMIT_MAX_ATTEMPTS - 1
)

# Number of attempts at or above the limit (RATE_LIMIT_MAX_ATTEMPTS to 10)
attempts_at_or_above_limit_strategy = st.integers(
    min_value=RATE_LIMIT_MAX_ATTEMPTS, max_value=10
)

# ---------------------------------------------------------------------------
# Property 2a: After exactly 5 increments, rate_limit_check() returns False
# ---------------------------------------------------------------------------


@given(ip_strategy)
@h_settings(max_examples=100)
def test_rate_limited_after_exactly_max_attempts(ip: str):
    """
    **Property 2a — Validates: Requirements 9.9, 19.3, 19.4**

    After exactly RATE_LIMIT_MAX_ATTEMPTS (5) increments from the same IP,
    `rate_limit_check()` must return False (rate limited).
    """
    _clear_cache_for_ip(ip)
    request = _make_request(ip)

    for _ in range(RATE_LIMIT_MAX_ATTEMPTS):
        rate_limit_increment(request)

    result = rate_limit_check(request)

    assert result is False, (
        f"Expected rate_limit_check() to return False after "
        f"{RATE_LIMIT_MAX_ATTEMPTS} increments for IP {ip!r}, "
        f"but got {result!r}."
    )


# ---------------------------------------------------------------------------
# Property 2b: For N < 5 increments, rate_limit_check() returns True
# ---------------------------------------------------------------------------


@given(ip_strategy, attempts_below_limit_strategy)
@h_settings(max_examples=200)
def test_allowed_when_below_limit(ip: str, n: int):
    """
    **Property 2b — Validates: Requirements 9.9, 19.3**

    For any number of increments N < RATE_LIMIT_MAX_ATTEMPTS (5),
    `rate_limit_check()` must return True (request allowed).
    """
    _clear_cache_for_ip(ip)
    request = _make_request(ip)

    for _ in range(n):
        rate_limit_increment(request)

    result = rate_limit_check(request)

    assert result is True, (
        f"Expected rate_limit_check() to return True after {n} increments "
        f"(below limit of {RATE_LIMIT_MAX_ATTEMPTS}) for IP {ip!r}, "
        f"but got {result!r}."
    )


# ---------------------------------------------------------------------------
# Property 2c: For N >= 5 increments, rate_limit_check() returns False
# ---------------------------------------------------------------------------


@given(ip_strategy, attempts_at_or_above_limit_strategy)
@h_settings(max_examples=200)
def test_rate_limited_when_at_or_above_limit(ip: str, n: int):
    """
    **Property 2c — Validates: Requirements 9.9, 19.3, 19.4**

    For any number of increments N >= RATE_LIMIT_MAX_ATTEMPTS (5),
    `rate_limit_check()` must return False (rate limited).
    """
    _clear_cache_for_ip(ip)
    request = _make_request(ip)

    for _ in range(n):
        rate_limit_increment(request)

    result = rate_limit_check(request)

    assert result is False, (
        f"Expected rate_limit_check() to return False after {n} increments "
        f"(at or above limit of {RATE_LIMIT_MAX_ATTEMPTS}) for IP {ip!r}, "
        f"but got {result!r}."
    )


# ---------------------------------------------------------------------------
# Property 2d: Cache failure → rate_limit_check() returns True (fail-open)
# ---------------------------------------------------------------------------


@given(ip_strategy)
@h_settings(max_examples=50)
def test_fail_open_on_cache_error(ip: str):
    """
    **Property 2d — Validates: Requirements 19.7**

    When the cache raises an exception, `rate_limit_check()` must return
    True (fail-open), allowing the request rather than blocking it.
    This ensures cache failures do not lock out legitimate users.
    """
    request = _make_request(ip)

    with patch(
        "apps.accounts.registration.views.cache.get",
        side_effect=Exception("cache unavailable"),
    ):
        result = rate_limit_check(request)

    assert result is True, (
        f"Expected rate_limit_check() to return True (fail-open) when "
        f"cache raises an exception for IP {ip!r}, but got {result!r}."
    )
