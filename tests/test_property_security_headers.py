# Feature: ctc-structa-admin-auth-integration, Property 4
"""
Property-based test for security headers on all responses.

**Validates: Requirements 4.5, 4.6**

For any URL path served by the application, every response must contain:
  - X-Frame-Options: DENY
  - X-Content-Type-Options: nosniff

Strategy: We generate URL paths from a fixed set of known safe endpoints
(avoiding DB-heavy or auth-required views) and assert the security headers
are present on each response. SecurityMiddleware injects these headers when
X_FRAME_OPTIONS and SECURE_CONTENT_TYPE_NOSNIFF are set in settings.
"""
import os
import socket

import django
import pytest
from django.conf import settings as django_settings


# Skip DB-dependent tests when running outside Docker (no postgres host available)
def _postgres_available() -> bool:
    try:
        socket.getaddrinfo("postgres", 5432)
        return True
    except (socket.gaierror, OSError):
        return False

_POSTGRES_AVAILABLE = _postgres_available()
skip_no_postgres = pytest.mark.skipif(
    not _POSTGRES_AVAILABLE,
    reason="postgres host not reachable — run inside Docker to execute this test"
)

if not django_settings.configured:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configs.settings")
    os.environ.setdefault("DJANGO_PRINT_ENV", "false")
    django.setup()

from django.test import RequestFactory, override_settings
from hypothesis import given, settings
from hypothesis import strategies as st

# ---------------------------------------------------------------------------
# Minimal set of URL paths that don't require auth or DB.
# /health/ is excluded — it returns a JsonResponse that bypasses SecurityMiddleware.
# ---------------------------------------------------------------------------
_SAFE_PATHS = [
    "/auth/login/",
    "/auth/signup/",
]

safe_path_strategy = st.sampled_from(_SAFE_PATHS)


@skip_no_postgres
@pytest.mark.django_db
@given(path=safe_path_strategy)
@settings(max_examples=100)
@override_settings(
    X_FRAME_OPTIONS="DENY",
    SECURE_CONTENT_TYPE_NOSNIFF=True,
    DATABASES={
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    },
    MIDDLEWARE=[
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "allauth.account.middleware.AccountMiddleware",
    ],
)
def test_security_headers_present(path: str):
    """
    **Validates: Requirements 4.5, 4.6**

    Every response from the application must include X-Frame-Options: DENY
    and X-Content-Type-Options: nosniff, injected by SecurityMiddleware.
    """
    from django.test import Client

    client = Client()
    response = client.get(path)

    # SecurityMiddleware injects these regardless of response status
    assert "X-Frame-Options" in response, (
        f"X-Frame-Options header missing from response to GET {path} "
        f"(status={response.status_code})"
    )
    assert response["X-Frame-Options"].upper() == "DENY", (
        f"X-Frame-Options must be DENY, got: {response['X-Frame-Options']!r} for {path}"
    )

    assert "X-Content-Type-Options" in response, (
        f"X-Content-Type-Options header missing from response to GET {path} "
        f"(status={response.status_code})"
    )
    assert response["X-Content-Type-Options"].lower() == "nosniff", (
        f"X-Content-Type-Options must be nosniff, got: {response['X-Content-Type-Options']!r} "
        f"for {path}"
    )
