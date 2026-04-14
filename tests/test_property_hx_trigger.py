# Feature: ctc-structa-admin-auth-integration, Property 3
"""
Property-based test for HX-Trigger header on HTMX form responses.

**Validates: Requirements 10.5, 10.8**

For any HTMX form submission (with HX-Request header) to AllauthLoginView or
AllauthSignupView — whether the form is valid or invalid — the response must
include an HX-Trigger header whose value is valid JSON containing
showNotification.message and showNotification.type.

Strategy: We test the view methods (form_valid / form_invalid) directly using
RequestFactory, mocking PageHandler and render_fragment to avoid the full
django_grep template stack. The property under test is the HX-Trigger header
logic in trigger_notification(), which is called unconditionally on every
HTMX response path.
"""
import json
import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

from django.http import HttpResponse
from django.test import RequestFactory

from hypothesis import given, settings
from hypothesis import strategies as st

# ---------------------------------------------------------------------------
# Stub out django_osoul.comp.site.PageHandler before importing allauth_views.
# This avoids pulling in the full django_grep model registry.
# ---------------------------------------------------------------------------

_stub_module = ModuleType("django_osoul.comp.site")


class _StubPageHandler:
    """Minimal PageHandler stub: provides setup() and strategy attribute."""

    template_name: str = ""
    fragment_template: str = ""
    page_title: str = ""

    def setup(self, request, *args, **kwargs):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        self.strategy = "fragment" if request.META.get("HTTP_HX_REQUEST") else "full"

    def dispatch(self, request, *args, **kwargs):
        return HttpResponse(status=200)

    def get_context_data(self, **kwargs):
        return kwargs

    def render_fragment(self, request, context, **kwargs):
        return HttpResponse(status=200)

    def render_layout(self, context):
        return HttpResponse(status=200)


_stub_module.PageHandler = _StubPageHandler  # type: ignore[attr-defined]

# Inject the stub into sys.modules so that allauth_views.py picks it up
sys.modules.setdefault("django_grep", ModuleType("django_grep"))
sys.modules.setdefault("django_osoul.comp", ModuleType("django_osoul.comp"))
sys.modules["django_osoul.comp.site"] = _stub_module

# Now we can safely import the views
from apps.handlers.registration.allauth_views import AllauthLoginView, AllauthSignupView  # noqa: E402
from apps.handlers.registration.views import trigger_notification  # noqa: E402

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

factory = RequestFactory()


def _make_htmx_post(url: str, data: dict) -> "django.http.HttpRequest":
    """Create a POST request with HX-Request header set."""
    request = factory.post(url, data=data)
    request.META["HTTP_HX_REQUEST"] = "true"
    request.session = {}
    request.user = MagicMock()
    request.user.is_authenticated = False
    return request


def _assert_hx_trigger_valid(response: HttpResponse, context: str = "") -> None:
    """Assert HX-Trigger header is present and contains showNotification payload."""
    assert "HX-Trigger" in response, (
        f"HX-Trigger header missing from HTMX response. {context}"
    )
    raw = response["HX-Trigger"]
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"HX-Trigger header is not valid JSON: {raw!r}. {context}"
        ) from exc

    assert "showNotification" in payload, (
        f"HX-Trigger JSON missing 'showNotification' key. Got: {payload}. {context}"
    )
    notification = payload["showNotification"]
    assert "message" in notification, (
        f"showNotification missing 'message' field. Got: {notification}. {context}"
    )
    assert "type" in notification, (
        f"showNotification missing 'type' field. Got: {notification}. {context}"
    )
    assert isinstance(notification["message"], str) and notification["message"], (
        f"showNotification.message must be a non-empty string. Got: {notification['message']!r}"
    )
    assert notification["type"] in ("success", "error", "warning", "info"), (
        f"showNotification.type must be one of success/error/warning/info. "
        f"Got: {notification['type']!r}"
    )


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# Invalid login form data — always triggers form_invalid
invalid_login_data_strategy = st.one_of(
    st.just({}),
    st.fixed_dictionaries({"login": st.just(""), "password": st.just("")}),
    st.fixed_dictionaries({"login": st.emails(), "password": st.just("")}),
    st.fixed_dictionaries({"login": st.just(""), "password": st.text(min_size=1)}),
)

# Invalid signup form data — always triggers form_invalid
invalid_signup_data_strategy = st.one_of(
    st.just({}),
    st.fixed_dictionaries({
        "username": st.just(""),
        "email": st.just(""),
        "password1": st.just(""),
        "password2": st.just(""),
    }),
    st.fixed_dictionaries({"email": st.emails()}),
)

# Valid login form data (for form_valid path)
valid_login_data_strategy = st.fixed_dictionaries(
    {
        "login": st.emails(),
        "password": st.text(min_size=8, max_size=64).filter(lambda s: s.strip()),
    }
)

# Valid signup form data (for form_valid path)
valid_signup_data_strategy = st.fixed_dictionaries(
    {
        "username": st.text(
            min_size=3,
            max_size=20,
            alphabet=st.characters(whitelist_categories=("Ll", "Lu", "Nd")),
        ).filter(lambda s: s.strip()),
        "email": st.emails(),
        "password1": st.text(min_size=10, max_size=64).filter(lambda s: s.strip()),
    }
)


# ---------------------------------------------------------------------------
# Property 3a: HX-Trigger on invalid login form submissions (form_invalid path)
# ---------------------------------------------------------------------------


@given(form_data=invalid_login_data_strategy)
@settings(max_examples=100)
def test_hx_trigger_on_invalid_login(form_data: dict):
    """
    **Validates: Requirements 10.5, 10.8**

    For any invalid HTMX POST to AllauthLoginView, the response must include
    an HX-Trigger header with valid JSON containing showNotification.message
    and showNotification.type.
    """
    request = _make_htmx_post("/allauth/login/", form_data)

    # Patch allauth's LoginView.post to call form_invalid directly
    # (avoids DB auth while exercising our form_invalid override)
    with patch("allauth.account.views.LoginView.post") as mock_post:
        # Simulate allauth calling form_invalid by invoking it directly
        view = AllauthLoginView()
        view.setup(request)

        # Build a mock form with errors (simulates invalid submission)
        mock_form = MagicMock()
        mock_form.errors = {"login": ["This field is required."]}

        response = view.form_invalid(mock_form)

    _assert_hx_trigger_valid(
        response,
        context=f"form_data={form_data!r}, view=AllauthLoginView, form_invalid path",
    )


# ---------------------------------------------------------------------------
# Property 3b: HX-Trigger on invalid signup form submissions (form_invalid path)
# ---------------------------------------------------------------------------


@given(form_data=invalid_signup_data_strategy)
@settings(max_examples=100)
def test_hx_trigger_on_invalid_signup(form_data: dict):
    """
    **Validates: Requirements 10.5, 10.8**

    For any invalid HTMX POST to AllauthSignupView, the response must include
    an HX-Trigger header with valid JSON containing showNotification.message
    and showNotification.type.
    """
    request = _make_htmx_post("/allauth/signup/", form_data)

    view = AllauthSignupView()
    view.setup(request)

    mock_form = MagicMock()
    mock_form.errors = {"email": ["Enter a valid email address."]}

    response = view.form_invalid(mock_form)

    _assert_hx_trigger_valid(
        response,
        context=f"form_data={form_data!r}, view=AllauthSignupView, form_invalid path",
    )


# ---------------------------------------------------------------------------
# Property 3c: HX-Trigger on valid login (form_valid path)
# ---------------------------------------------------------------------------


@given(form_data=valid_login_data_strategy)
@settings(max_examples=100)
def test_hx_trigger_on_valid_login_form_valid_path(form_data: dict):
    """
    **Validates: Requirements 10.5, 10.8**

    When AllauthLoginView.form_valid() is called on an HTMX request, the
    response must include an HX-Trigger header with valid JSON containing
    showNotification.message and showNotification.type.
    """
    request = _make_htmx_post("/allauth/login/", form_data)

    view = AllauthLoginView()
    view.setup(request)

    mock_form = MagicMock()
    mock_form.errors = {}
    mock_form.cleaned_data = form_data

    # Patch super().form_valid to avoid allauth DB operations
    with patch("allauth.account.views.LoginView.form_valid", return_value=HttpResponse(status=200)):
        response = view.form_valid(mock_form)

    _assert_hx_trigger_valid(
        response,
        context=f"form_data={form_data!r}, view=AllauthLoginView, form_valid path",
    )


# ---------------------------------------------------------------------------
# Property 3d: HX-Trigger on valid signup (form_valid path)
# ---------------------------------------------------------------------------


@given(form_data=valid_signup_data_strategy)
@settings(max_examples=100)
def test_hx_trigger_on_valid_signup_form_valid_path(form_data: dict):
    """
    **Validates: Requirements 10.5, 10.8**

    When AllauthSignupView.form_valid() is called on an HTMX request, the
    response must include an HX-Trigger header with valid JSON containing
    showNotification.message and showNotification.type.
    """
    request = _make_htmx_post("/allauth/signup/", form_data)

    view = AllauthSignupView()
    view.setup(request)

    mock_form = MagicMock()
    mock_form.errors = {}
    mock_form.cleaned_data = {
        **form_data,
        "email": form_data.get("email", "test@example.com"),
    }

    with (
        patch("allauth.account.views.SignupView.form_valid", return_value=HttpResponse(status=200)),
    ):
        response = view.form_valid(mock_form)

    _assert_hx_trigger_valid(
        response,
        context=f"form_data={form_data!r}, view=AllauthSignupView, form_valid path",
    )
