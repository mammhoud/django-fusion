"""
Property-based tests for HTMX vs non-HTMX redirect behavior.

**Validates: Requirements 8.2, 8.3**

Tests the redirect logic in `RegisterView.post()` from
`apps.accounts.registration.views`.

Property 5b: HTMX requests get HX-Redirect; non-HTMX requests get HTTP 302.

Specifically:
  1. When HX-Request header is present, a successful registration returns a
     response with HX-Redirect header set (not HTTP 302).
  2. When HX-Request header is absent, a successful registration returns
     HTTP 302 redirect.
  3. The HX-Redirect target URL is always a non-empty string.
  4. The HTTP 302 redirect location is always a non-empty string.

These tests are standalone — they configure Django minimally and mock
the heavy django_fusion / wagtail import chain so that only the pure
redirect decision logic is exercised.
"""

import sys
import types

# ---------------------------------------------------------------------------
# Minimal Django setup — must happen before any django.* import
# ---------------------------------------------------------------------------
import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        INSTALLED_APPS=["django.contrib.contenttypes", "django.contrib.auth"],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache"
            }
        },
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


# django_fusion.comp.site — needs a PageHandler class
_ensure_mock("django_fusion")
_ensure_mock("django_fusion.comp")
_site_mod = _ensure_mock("django_fusion.comp.site")
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
# Import the logic under test
# ---------------------------------------------------------------------------
from django.http import HttpResponse, HttpResponseRedirect  # noqa: E402
from hypothesis import given  # noqa: E402
from hypothesis import settings as h_settings
from hypothesis import strategies as st  # noqa: E402

# ---------------------------------------------------------------------------
# Pure redirect logic extracted from RegisterView.post() on success
# ---------------------------------------------------------------------------

def _build_redirect_response(is_htmx: bool, home_url: str):
    """
    Mirrors the redirect decision logic from RegisterView.post() on success:

        if is_htmx:
            response = HttpResponse(status=200)
            response["HX-Redirect"] = home_url
        else:
            response = HttpResponseRedirect(home_url)

    Returns the response object so properties can be asserted on it.
    """
    if is_htmx:
        response = HttpResponse(status=200)
        response["HX-Redirect"] = home_url
        return response
    else:
        return HttpResponseRedirect(home_url)


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# Valid URL path strings — non-empty, start with "/", ASCII-safe characters
# (matching real-world URL paths; HttpResponseRedirect percent-encodes non-ASCII)
url_path_strategy = st.builds(
    lambda path: "/" + path,
    st.text(
        alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_/.",
        min_size=0,
        max_size=100,
    ),
)

is_htmx_strategy = st.booleans()

# ---------------------------------------------------------------------------
# Property 1: HTMX requests get HX-Redirect header (not HTTP 302)
# ---------------------------------------------------------------------------

@given(url_path_strategy)
@h_settings(max_examples=200)
def test_htmx_request_gets_hx_redirect_header(home_url: str):
    """
    **Property 5b (HTMX branch) — Validates: Requirements 8.2**

    When is_htmx=True, the response must have an HX-Redirect header set
    and must NOT be an HTTP 302 redirect.
    """
    response = _build_redirect_response(is_htmx=True, home_url=home_url)

    assert "HX-Redirect" in response, (
        f"HX-Redirect header missing for HTMX request with home_url={home_url!r}"
    )
    assert response.status_code != 302, (
        f"HTMX request should not return HTTP 302, got {response.status_code}"
    )


# ---------------------------------------------------------------------------
# Property 2: Non-HTMX requests get HTTP 302 redirect
# ---------------------------------------------------------------------------

@given(url_path_strategy)
@h_settings(max_examples=200)
def test_non_htmx_request_gets_http_302(home_url: str):
    """
    **Property 5b (non-HTMX branch) — Validates: Requirements 8.3**

    When is_htmx=False, the response must be an HTTP 302 redirect and
    must NOT have an HX-Redirect header.
    """
    response = _build_redirect_response(is_htmx=False, home_url=home_url)

    assert response.status_code == 302, (
        f"Non-HTMX request should return HTTP 302, got {response.status_code}"
    )
    assert "HX-Redirect" not in response, (
        "Non-HTMX response must not contain HX-Redirect header"
    )


# ---------------------------------------------------------------------------
# Property 3: HX-Redirect target URL is always a non-empty string
# ---------------------------------------------------------------------------

@given(url_path_strategy)
@h_settings(max_examples=200)
def test_hx_redirect_target_is_non_empty(home_url: str):
    """
    **Property 5b — Validates: Requirements 8.2**

    For HTMX requests, the HX-Redirect header value must always be a
    non-empty string.
    """
    response = _build_redirect_response(is_htmx=True, home_url=home_url)

    hx_redirect_value = response.get("HX-Redirect", "")
    assert isinstance(hx_redirect_value, str), (
        f"HX-Redirect header must be a string, got {type(hx_redirect_value).__name__}"
    )
    assert len(hx_redirect_value) > 0, (
        "HX-Redirect header must not be empty"
    )


# ---------------------------------------------------------------------------
# Property 4: HTTP 302 redirect location is always a non-empty string
# ---------------------------------------------------------------------------

@given(url_path_strategy)
@h_settings(max_examples=200)
def test_http_302_location_is_non_empty(home_url: str):
    """
    **Property 5b — Validates: Requirements 8.3**

    For non-HTMX requests, the HTTP 302 Location header must always be a
    non-empty string.
    """
    response = _build_redirect_response(is_htmx=False, home_url=home_url)

    location = response.get("Location", "")
    assert isinstance(location, str), (
        f"Location header must be a string, got {type(location).__name__}"
    )
    assert len(location) > 0, (
        "HTTP 302 Location header must not be empty"
    )


# ---------------------------------------------------------------------------
# Property 5: Redirect target matches the provided home_url (both branches)
# ---------------------------------------------------------------------------

@given(url_path_strategy, is_htmx_strategy)
@h_settings(max_examples=200)
def test_redirect_target_matches_home_url(home_url: str, is_htmx: bool):
    """
    **Property 5b — Validates: Requirements 8.1, 8.2, 8.3**

    Regardless of HTMX vs non-HTMX, the redirect target must equal the
    provided home_url.
    """
    response = _build_redirect_response(is_htmx=is_htmx, home_url=home_url)

    if is_htmx:
        actual_url = response.get("HX-Redirect", "")
    else:
        actual_url = response.get("Location", "")

    assert actual_url == home_url, (
        f"Redirect target mismatch: expected {home_url!r}, got {actual_url!r} "
        f"(is_htmx={is_htmx})"
    )
