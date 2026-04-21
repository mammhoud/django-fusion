# Feature: auth-allauth-enhancement, Property 7: HX-Trigger present on all HTMX form responses
"""
Property test: every HTMX form response from AllauthLoginView and AllauthSignupView
contains an HX-Trigger header with valid JSON including showNotification.message
and showNotification.type.
"""
import json
from unittest.mock import MagicMock, patch

from hypothesis import given, settings
from hypothesis import strategies as st


def _make_htmx_request():
    request = MagicMock()
    request.headers = {"HX-Request": "true"}
    request.GET = {}
    request.POST = {}
    request.method = "POST"
    request.META = {}
    request.user.is_authenticated = False
    return request


@given(
    message=st.text(min_size=1, max_size=200),
    notification_type=st.sampled_from(["success", "error", "warning", "info"]),
)
@settings(max_examples=100)
def test_trigger_notification_header_valid(message, notification_type):
    from www.apps.accounts.registration.views import trigger_notification
    from django.http import HttpResponse

    response = HttpResponse()
    trigger_notification(response, message, notification_type)

    assert "HX-Trigger" in response
    payload = json.loads(response["HX-Trigger"])
    assert "showNotification" in payload
    assert "message" in payload["showNotification"]
    assert "type" in payload["showNotification"]
    assert payload["showNotification"]["message"] == message
    assert payload["showNotification"]["type"] == notification_type


@given(
    form_errors=st.dictionaries(
        keys=st.sampled_from(["email", "password1", "password2"]),
        values=st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=2),
        min_size=1,
    )
)
@settings(max_examples=50)
def test_form_invalid_sets_hx_trigger(form_errors):
    from www.apps.accounts.registration.allauth_views import AllauthLoginView
    from django.http import HttpResponse

    view = AllauthLoginView()
    request = _make_htmx_request()
    view.request = request

    mock_form = MagicMock()
    mock_form.errors = form_errors

    with patch.object(view, "render_fragment") as mock_render, \
         patch("apps.accounts.registration.allauth_views.trigger_notification") as mock_trigger:
        mock_render.return_value = HttpResponse()
        view.form_invalid(mock_form)
        mock_trigger.assert_called_once()
        args = mock_trigger.call_args[0]
        assert args[2] == "error"
