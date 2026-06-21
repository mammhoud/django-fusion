"""
Property-based tests for HTMX response headers.

**Validates: Requirements 3.3, 7.3, 18.1**

Tests the `trigger_notification()` function from
`apps.accounts.registration.views`.

Property 5: HTMX fragment responses always include HX-Trigger with
notification data.

Specifically:
  5a. For any message and valid notification_type, HX-Trigger header is set.
  5b. The HX-Trigger header value is always valid JSON.
  5c. The JSON always contains showNotification.message and
      showNotification.type fields.
  5d. The message field in the JSON matches the input message.
  5e. The type field in the JSON matches the input notification_type.

These tests are standalone — they configure Django minimally and mock
the heavy django_osoul / wagtail import chain so that only the pure
`trigger_notification` helper is exercised.
"""

import json
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


# django_osoul.comp.site — needs a PageHandler class with a dispatch method
_ensure_mock("django_osoul")
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
# Now import the function under test
# ---------------------------------------------------------------------------
from django.http import HttpResponse  # noqa: E402
from hypothesis import given  # noqa: E402
from hypothesis import settings as h_settings
from hypothesis import strategies as st  # noqa: E402
from plugins.accounts.views.registration import trigger_notification  # noqa: E402

# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

VALID_NOTIFICATION_TYPES = ["success", "error", "warning", "info"]

# Arbitrary text including empty strings, unicode, and special characters
message_strategy = st.text(
    alphabet=st.characters(blacklist_categories=("Cs",)),  # exclude surrogates
    min_size=0,
    max_size=500,
)

notification_type_strategy = st.sampled_from(VALID_NOTIFICATION_TYPES)

# ---------------------------------------------------------------------------
# Property 5a: HX-Trigger header is always set
# ---------------------------------------------------------------------------

@given(message_strategy, notification_type_strategy)
@h_settings(max_examples=200)
def test_hx_trigger_header_always_set(message: str, notification_type: str):
    """
    **Property 5a — Validates: Requirements 3.3, 7.3, 18.1**

    For any message string and any valid notification_type,
    `trigger_notification()` must set the HX-Trigger header on the response.
    """
    response = HttpResponse()
    trigger_notification(response, message, notification_type)

    assert "HX-Trigger" in response, (
        f"HX-Trigger header missing for message={message!r}, "
        f"notification_type={notification_type!r}"
    )


# ---------------------------------------------------------------------------
# Property 5b: HX-Trigger value is always valid JSON
# ---------------------------------------------------------------------------

@given(message_strategy, notification_type_strategy)
@h_settings(max_examples=200)
def test_hx_trigger_value_is_valid_json(message: str, notification_type: str):
    """
    **Property 5b — Validates: Requirements 18.1, 18.5**

    The HX-Trigger header value must always be parseable as valid JSON.
    """
    response = HttpResponse()
    trigger_notification(response, message, notification_type)

    header_value = response["HX-Trigger"]
    try:
        parsed = json.loads(header_value)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"HX-Trigger header is not valid JSON: {header_value!r}. "
            f"Error: {exc}"
        ) from exc

    assert isinstance(parsed, dict), (
        f"Expected JSON object, got {type(parsed).__name__}: {parsed!r}"
    )


# ---------------------------------------------------------------------------
# Property 5c: JSON always contains showNotification.message and .type
# ---------------------------------------------------------------------------

@given(message_strategy, notification_type_strategy)
@h_settings(max_examples=200)
def test_hx_trigger_contains_required_fields(message: str, notification_type: str):
    """
    **Property 5c — Validates: Requirements 7.3, 18.1**

    The parsed HX-Trigger JSON must always contain a 'showNotification' key
    with nested 'message' and 'type' fields.
    """
    response = HttpResponse()
    trigger_notification(response, message, notification_type)

    parsed = json.loads(response["HX-Trigger"])

    assert "showNotification" in parsed, (
        f"'showNotification' key missing from HX-Trigger JSON: {parsed!r}"
    )

    notification = parsed["showNotification"]
    assert isinstance(notification, dict), (
        f"'showNotification' must be a dict, got {type(notification).__name__}"
    )

    assert "message" in notification, (
        f"'message' field missing from showNotification: {notification!r}"
    )
    assert "type" in notification, (
        f"'type' field missing from showNotification: {notification!r}"
    )


# ---------------------------------------------------------------------------
# Property 5d: message field matches input
# ---------------------------------------------------------------------------

@given(message_strategy, notification_type_strategy)
@h_settings(max_examples=200)
def test_hx_trigger_message_matches_input(message: str, notification_type: str):
    """
    **Property 5d — Validates: Requirements 3.3, 7.3**

    The 'message' field in the HX-Trigger JSON must exactly match the
    input message string passed to `trigger_notification()`.
    """
    response = HttpResponse()
    trigger_notification(response, message, notification_type)

    parsed = json.loads(response["HX-Trigger"])
    actual_message = parsed["showNotification"]["message"]

    assert actual_message == message, (
        f"Expected message={message!r}, got {actual_message!r}"
    )


# ---------------------------------------------------------------------------
# Property 5e: type field matches input notification_type
# ---------------------------------------------------------------------------

@given(message_strategy, notification_type_strategy)
@h_settings(max_examples=200)
def test_hx_trigger_type_matches_input(message: str, notification_type: str):
    """
    **Property 5e — Validates: Requirements 7.6, 18.1**

    The 'type' field in the HX-Trigger JSON must exactly match the
    input notification_type passed to `trigger_notification()`.
    """
    response = HttpResponse()
    trigger_notification(response, message, notification_type)

    parsed = json.loads(response["HX-Trigger"])
    actual_type = parsed["showNotification"]["type"]

    assert actual_type == notification_type, (
        f"Expected type={notification_type!r}, got {actual_type!r}"
    )
