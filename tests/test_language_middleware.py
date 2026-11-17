"""Regression tests for ``DefaultLanguageMiddleware``'s response side.

These pin the three behaviours the middleware must keep after the
"view persisted a preference mid-request" fix:

1. A view that writes the session language (``set_language_api``) wins — the
   response cookie carries the value the view chose, not the pre-view one.
2. A request-scoped ``?lang=`` override is not answered with the stored
   preference's cookie: the override renders *and* persists, exactly as it did
   before the fix (the first version of the fix compared the session with the
   resolved language, so every override was pinned back to the stored value).
3. A first visit (no cookie, no session) normalizes the default, while a
   request whose session already matches the resolved language does not
   re-issue the cookie (responses stay cookie-stable).

Run with::

    cd libs/django-fusion && uv run pytest tests/test_language_middleware.py -v
"""

from __future__ import annotations

import pytest
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, override_settings

from django_fusion.core.middlewares.language import (
    DefaultLanguageMiddleware,
    language_cookie_name,
    language_session_key,
)

LANGUAGES = [("en", "English"), ("fr", "French"), ("ar", "Arabic")]


class FakeSession(dict):
    """Minimal session stand-in — the middleware only reads/writes/marks."""

    modified = False


def _run(*, session: FakeSession | None = None, cookies: dict | None = None, params: dict | None = None, view_persists: str | None = None):
    request = RequestFactory().get("/contact/", params or {})
    if session is not None:
        request.session = session
    request.COOKIES.update(cookies or {})

    def view(req):
        if view_persists is not None:
            req.session[language_session_key()] = view_persists
            req.session.modified = True
        return HttpResponse("ok")

    response = DefaultLanguageMiddleware(view)(request)
    return request, response


def _cookie_value(response):
    cookie = response.cookies.get(language_cookie_name())
    return cookie.value if cookie is not None else None


@override_settings(
    LANGUAGES=LANGUAGES,
    FUSION_LANGUAGES=LANGUAGES,
    LANGUAGE_CODE="en",
    LANGUAGE_COOKIE_NAME="django_language",
)
class TestLanguageMiddlewareResponse(SimpleTestCase):
    def test_view_persisted_language_wins_over_pre_view_language(self):
        session = FakeSession({language_session_key(): "ar"})
        _request, response = _run(session=session, view_persists="fr")

        # The response body was already rendered in the pre-view language;
        # the cookie is what carries the switch into the next request.
        assert _cookie_value(response) == "fr"

    def test_query_override_is_not_pinned_back_to_the_session(self):
        session = FakeSession({language_session_key(): "ar"})
        request, response = _run(session=session, params={"lang": "fr"})

        assert request.LANGUAGE_CODE == "fr"
        assert _cookie_value(response) == "fr"
        assert session[language_session_key()] == "fr"

    def test_query_override_beats_a_cookie_choice_and_becomes_the_session(self):
        session = FakeSession()
        _request, response = _run(
            session=session, cookies={language_cookie_name(): "ar"}, params={"lang": "fr"}
        )

        assert _cookie_value(response) == "fr"
        assert session[language_session_key()] == "fr"

    def test_first_visit_writes_the_default_cookie(self):
        _request, response = _run(session=FakeSession())

        assert _cookie_value(response) == "en"

    def test_matching_session_does_not_reissue_the_cookie(self):
        session = FakeSession({language_session_key(): "ar"})
        _request, response = _run(session=session)

        assert _cookie_value(response) is None
