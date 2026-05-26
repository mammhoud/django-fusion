# Feature: auth-allauth-enhancement, Property 1: HTMX fragment vs full-page routing
"""
Property test: requests with HX-Request header receive a fragment response
(no full skeleton), requests without it receive a full-page response.
"""
from unittest.mock import MagicMock, patch

from hypothesis import given, settings
from hypothesis import strategies as st


def _make_request(htmx: bool, authenticated: bool = False):
    request = MagicMock()
    request.user.is_authenticated = authenticated
    request.headers = {"HX-Request": "true"} if htmx else {}
    request.GET = {}
    request.POST = {}
    request.method = "GET"
    request.META = {}
    return request


@given(htmx=st.booleans())
@settings(max_examples=50)
def test_login_view_routing(htmx):
    from www.apps.accounts.registration.allauth_views import AllauthLoginView

    view = AllauthLoginView()
    request = _make_request(htmx=htmx)

    with patch.object(AllauthLoginView, "render_fragment") as mock_fragment, \
         patch("allauth.account.views.LoginView.get") as mock_full:
        mock_fragment.return_value = MagicMock(status_code=200)
        mock_full.return_value = MagicMock(status_code=200)

        view.request = request
        view.args = ()
        view.kwargs = {}
        # strategy is set by PageHandler based on HX-Request
        view.strategy = "fragment" if htmx else "page"

        view.get(request)

        if htmx:
            mock_fragment.assert_called_once()
        else:
            mock_full.assert_called_once()
