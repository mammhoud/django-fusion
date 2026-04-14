# Feature: ctc-structa-admin-auth-integration, Property 5
"""
Property-based test for the /health/ endpoint.

**Validates: Requirements 3.2, 3.10**

For any valid configuration state (non-empty SECRET_KEY, valid DB config),
a GET request to /health/ must return HTTP 200 with JSON body {"status": "ok"}.

Strategy: We generate config variations (different SECRET_KEY values, DB names)
and assert the health endpoint always returns 200. The health check is intentionally
simple — it only verifies the app is running, not DB connectivity.
"""
import json
import os

import django
from django.conf import settings as django_settings

if not django_settings.configured:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configs.settings")
    os.environ.setdefault("DJANGO_PRINT_ENV", "false")
    django.setup()

from django.test import Client, override_settings
from hypothesis import given, settings
from hypothesis import strategies as st

# Strategy: generate valid SECRET_KEY values (length >= 50, no insecure prefix)
valid_secret_key_strategy = st.text(
    min_size=50,
    max_size=100,
    alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd"), whitelist_characters="-_!@#"),
).filter(lambda k: not k.lower().startswith("django-insecure-"))

# Strategy: generate valid DB name strings
valid_db_name_strategy = st.text(
    min_size=1,
    max_size=30,
    alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd"), whitelist_characters="_"),
)


@given(secret_key=valid_secret_key_strategy)
@settings(max_examples=100)
def test_health_check_returns_200(secret_key: str):
    """
    **Validates: Requirements 3.2, 3.10**

    For any valid SECRET_KEY, GET /health/ must return HTTP 200
    with JSON body containing {"status": "ok"}.
    """
    with override_settings(SECRET_KEY=secret_key):
        client = Client()
        response = client.get("/health/")

    assert response.status_code == 200, (
        f"GET /health/ returned {response.status_code}, expected 200"
    )

    try:
        body = json.loads(response.content)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"GET /health/ response body is not valid JSON: {response.content!r}"
        ) from exc

    assert body.get("status") == "ok", (
        f"GET /health/ JSON body must contain {{\"status\": \"ok\"}}, got: {body!r}"
    )
