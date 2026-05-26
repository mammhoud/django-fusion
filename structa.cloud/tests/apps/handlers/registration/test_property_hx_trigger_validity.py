"""
Property-based tests for HX-Trigger header validity.

**Validates: Requirements 7.3, 18.1, 18.5**

Property 5c: `HX-Trigger` header value is always valid JSON with
`showNotification.message` and `showNotification.type` fields.

Tests the `trigger_notification()` helper from
`apps.accounts.registration.views` using hypothesis to generate
arbitrary message strings and notification types.
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


_ensure_mock("django_grep")
_ensure_mock("django_osoul.comp")
_site_mod = _ensure_mock("django_osoul.comp.site")
if not hasattr(_site_mod, "PageHandler"):

    class _PageHandler:
        def dispatch(self, request, *args, **kwargs):
            pass

    _site_mod.PageHandler = _PageHandler

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
from www.apps.accounts.registration.views import trigger_notification  # noqa: E402

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
# Property 5c: HX-Trigger is valid JSON with showNotification.message + .type
# ---------------------------------------------------------------------------


@given(message_strategy, notification_type_strategy)
@h_settings(max_examples=200)
def test_hx_trigger_header_is_valid_json_with_required_fields(
    message: str, notification_type: str
):
    """
    **Property 5c — Validates: Requirements 7.3, 18.1, 18.5**

    For any message string and any valid notification_type,
    the HX-Trigger header set by `trigger_notification()` must:

    1. Be present on the response.
    2. Be parseable as valid JSON.
    3. Contain a top-level 'showNotification' dict.
    4. Have 'message' and 'type' fields inside 'showNotification'.
    5. Have 'message' equal to the input message.
    6. Have 'type' equal to the input notification_type.
    """
    response = HttpResponse()
    trigger_notification(response, message, notification_type)

    # 1. Header must be present
    assert "HX-Trigger" in response, (
        f"HX-Trigger header missing for message={message!r}, "
        f"notification_type={notification_type!r}"
    )

    header_value = response["HX-Trigger"]

    # 2. Must be valid JSON
    try:
        parsed = json.loads(header_value)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"HX-Trigger header is not valid JSON: {header_value!r}. Error: {exc}"
        ) from exc

    assert isinstance(parsed, dict), (
        f"Expected JSON object at top level, got {type(parsed).__name__}: {parsed!r}"
    )

    # 3. Must contain 'showNotification' key
    assert "showNotification" in parsed, (
        f"'showNotification' key missing from HX-Trigger JSON: {parsed!r}"
    )

    notification = parsed["showNotification"]
    assert isinstance(notification, dict), (
        f"'showNotification' must be a dict, got {type(notification).__name__}"
    )

    # 4. Must have 'message' and 'type' fields
    assert "message" in notification, (
        f"'message' field missing from showNotification: {notification!r}"
    )
    assert "type" in notification, (
        f"'type' field missing from showNotification: {notification!r}"
    )

    # 5. message must match input
    assert notification["message"] == message, (
        f"Expected message={message!r}, got {notification['message']!r}"
    )

    # 6. type must match input
    assert notification["type"] == notification_type, (
        f"Expected type={notification_type!r}, got {notification['type']!r}"
    )
