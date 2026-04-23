# Feature: auth-allauth-enhancement, Property 2: Login redirect honours `next` parameter
"""
Property test: get_success_url returns the `next` param when present,
and falls back to the dashboard URL when absent.
"""
from unittest.mock import MagicMock, patch

from hypothesis import given, settings
from hypothesis import strategies as st


def _make_view_with_next(next_url):
    from www.apps.registration.allauth_views import AllauthLoginView

    view = AllauthLoginView()
    request = MagicMock()
    request.GET = {"next": next_url} if next_url else {}
    request.POST = {}
    view.request = request
    return view


@given(
    next_url=st.text(
        alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="/-_"),
        min_size=1,
        max_size=100,
    ).map(lambda s: f"/{s}")
)
@settings(max_examples=100)
def test_redirect_honours_next(next_url):
    view = _make_view_with_next(next_url)
    result = view.get_success_url()
    assert result == next_url


@settings(max_examples=50)
def test_redirect_falls_back_to_dashboard():
    view = _make_view_with_next(None)
    with patch("apps.accounts.registration.allauth_views.reverse", return_value="/profile/dashboard/"):
        result = view.get_success_url()
    assert result == "/profile/dashboard/"
