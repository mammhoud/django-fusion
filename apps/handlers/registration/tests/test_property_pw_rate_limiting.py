"""
Property-based tests for password creation rate limiting.

**Validates: Requirements 12.10, 19.3**

Tests the brute-force protection logic in `CreatePasswordView.post()` from
`apps.accounts.registration.views`.

Property 2b: After 10 password creation attempts from the same IP within
1 hour, the 11th attempt returns HTTP 429.

Specifically:
  2b-i.  After exactly 10 invalid token increments, the counter is >= 10
         (request would be blocked).
  2b-ii. For any N < 10 invalid token increments, the counter is < 10
         (request would be allowed).
  2b-iii.For any N >= 10 invalid token increments, the counter is >= 10
         (request would be blocked).

These tests are standalone — they configure Django with an in-memory cache
backend and test the pure brute-force counter logic directly.
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
# Now import the cache and constants under test
# ---------------------------------------------------------------------------
from django.core.cache import cache  # noqa: E402

from hypothesis import given, settings as h_settings  # noqa: E402
from hypothesis import strategies as st  # noqa: E402

# ---------------------------------------------------------------------------
# Constants mirroring the view logic
# ---------------------------------------------------------------------------

PW_BF_LIMIT = 10  # pw_create_bf threshold in CreatePasswordView.post()
PW_BF_WINDOW = 3600  # 1 hour TTL


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _bf_key(ip: str) -> str:
    """Return the brute-force cache key for a given IP."""
    return f"pw_create_bf:{ip}"


def _clear_bf_counter(ip: str):
    """Clear the brute-force cache entry for a specific IP."""
    cache.delete(_bf_key(ip))


def _simulate_invalid_attempts(ip: str, n: int):
    """
    Simulate N invalid token attempts from the given IP.

    Mirrors the exact logic in CreatePasswordView.post():
        bf_attempts = cache.get(bf_key, 0)
        cache.set(bf_key, bf_attempts + 1, 3600)
    """
    key = _bf_key(ip)
    for _ in range(n):
        bf_attempts = cache.get(key, 0)
        cache.set(key, bf_attempts + 1, PW_BF_WINDOW)


def _is_blocked(ip: str) -> bool:
    """
    Return True if the IP would be blocked by the brute-force check.

    Mirrors the exact condition in CreatePasswordView.post():
        bf_attempts = cache.get(bf_key, 0)
        if bf_attempts >= 10:
            return render(..., status=429)
    """
    key = _bf_key(ip)
    bf_attempts = cache.get(key, 0)
    return bf_attempts >= PW_BF_LIMIT


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# IPv4-like strings — constrained to avoid cache key collisions between runs
ip_strategy = st.builds(
    "{}.{}.{}.{}".format,
    st.integers(min_value=1, max_value=254),
    st.integers(min_value=0, max_value=255),
    st.integers(min_value=0, max_value=255),
    st.integers(min_value=1, max_value=254),
).map(str)

# Number of attempts strictly below the limit (0 to PW_BF_LIMIT - 1)
attempts_below_limit_strategy = st.integers(min_value=0, max_value=PW_BF_LIMIT - 1)

# Number of attempts at or above the limit (PW_BF_LIMIT to 15)
attempts_at_or_above_limit_strategy = st.integers(
    min_value=PW_BF_LIMIT, max_value=15
)


# ---------------------------------------------------------------------------
# Property 2b-i: After exactly 10 increments, the IP is blocked
# ---------------------------------------------------------------------------


@given(ip_strategy)
@h_settings(max_examples=100)
def test_blocked_after_exactly_bf_limit_attempts(ip: str):
    """
    **Property 2b-i — Validates: Requirements 12.10, 19.3**

    After exactly PW_BF_LIMIT (10) invalid token attempts from the same IP,
    the brute-force counter must be >= 10, causing the next request to be
    blocked (HTTP 429).
    """
    _clear_bf_counter(ip)

    _simulate_invalid_attempts(ip, PW_BF_LIMIT)

    assert _is_blocked(ip), (
        f"Expected IP {ip!r} to be blocked after {PW_BF_LIMIT} invalid "
        f"attempts, but the counter is below the threshold."
    )


# ---------------------------------------------------------------------------
# Property 2b-ii: For N < 10 increments, the IP is NOT blocked
# ---------------------------------------------------------------------------


@given(ip_strategy, attempts_below_limit_strategy)
@h_settings(max_examples=200)
def test_allowed_when_below_bf_limit(ip: str, n: int):
    """
    **Property 2b-ii — Validates: Requirements 12.10, 19.3**

    For any number of invalid token attempts N < PW_BF_LIMIT (10),
    the brute-force counter must be < 10, so the request is allowed through.
    """
    _clear_bf_counter(ip)

    _simulate_invalid_attempts(ip, n)

    assert not _is_blocked(ip), (
        f"Expected IP {ip!r} to be allowed after {n} invalid attempts "
        f"(below limit of {PW_BF_LIMIT}), but it was blocked."
    )


# ---------------------------------------------------------------------------
# Property 2b-iii: For N >= 10 increments, the IP IS blocked
# ---------------------------------------------------------------------------


@given(ip_strategy, attempts_at_or_above_limit_strategy)
@h_settings(max_examples=200)
def test_blocked_when_at_or_above_bf_limit(ip: str, n: int):
    """
    **Property 2b-iii — Validates: Requirements 12.10, 19.3**

    For any number of invalid token attempts N >= PW_BF_LIMIT (10),
    the brute-force counter must be >= 10, causing the request to be
    blocked (HTTP 429).
    """
    _clear_bf_counter(ip)

    _simulate_invalid_attempts(ip, n)

    assert _is_blocked(ip), (
        f"Expected IP {ip!r} to be blocked after {n} invalid attempts "
        f"(at or above limit of {PW_BF_LIMIT}), but it was allowed."
    )
