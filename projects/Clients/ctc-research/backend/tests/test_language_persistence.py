"""Language persistence and localized Wagtail API contract tests."""

from __future__ import annotations

from django.conf import settings
from django.test import Client, TestCase, override_settings


@override_settings(ROOT_URLCONF="tests.urls", LANGUAGE_COOKIE_SECURE=False)
class TestLanguagePersistence(TestCase):
    """The frontend selector and backend APIs share one language preference."""

    def test_language_request_writes_session_and_configured_cookie(self):
        client = Client(enforce_csrf_checks=False)

        response = client.post("/i18n/setlang/", {"language": "ar"})

        assert response.status_code == 200
        assert response.json()["language"] == "ar"
        assert response.json()["session_key"] == settings.LANGUAGE_SESSION_KEY
        assert client.cookies[settings.LANGUAGE_COOKIE_NAME].value == "ar"
        assert client.cookies[settings.LANGUAGE_COOKIE_NAME]["path"] == settings.LANGUAGE_COOKIE_PATH
        assert client.cookies[settings.LANGUAGE_COOKIE_NAME]["samesite"] == settings.LANGUAGE_COOKIE_SAMESITE
        assert client.session[settings.LANGUAGE_SESSION_KEY] == "ar"

    def test_next_api_request_uses_the_session_language(self):
        client = Client(enforce_csrf_checks=False)
        client.post("/i18n/setlang/", {"language": "ar"})

        response = client.get("/apis/content/languages/")

        assert response.status_code == 200
        payload = response.json()
        assert payload["language"] == "ar"
        assert payload["default_language"] == settings.LANGUAGE_CODE

    def test_explicit_query_language_overrides_the_saved_session(self):
        client = Client(enforce_csrf_checks=False)
        client.post("/i18n/setlang/", {"language": "ar"})

        response = client.get("/apis/navigation/?lang=fr")

        assert response.status_code == 200
        assert response.json()["language"] == "fr"
        assert client.session[settings.LANGUAGE_SESSION_KEY] == "ar"

    def test_default_language_is_used_without_a_saved_preference(self):
        response = self.client.get("/apis/content/languages/")

        assert response.status_code == 200
        assert response.json()["language"] == settings.LANGUAGE_CODE
