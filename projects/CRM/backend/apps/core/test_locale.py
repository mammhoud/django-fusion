"""Focused coverage for the shared locale preference contract."""
from __future__ import annotations

import json
from pathlib import Path

from django.test import TestCase, override_settings

from apps.core.locale_api import locale_api


class LocaleApiTests(TestCase):
    def test_get_lists_supported_languages_and_direction(self):
        response = self.client.get("/apis/core/locale/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["current"], "en")
        self.assertEqual({item["code"] for item in payload["languages"]}, {"en", "ar"})
        self.assertEqual(next(item for item in payload["languages"] if item["code"] == "ar")["direction"], "rtl")

    def test_post_sets_language_cookie_and_rtl_direction(self):
        response = self.client.post(
            "/apis/core/locale/",
            data=json.dumps({"language": "ar"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["current"], "ar")
        self.assertEqual(response.json()["direction"], "rtl")
        self.assertEqual(response.cookies["loop_language"].value, "ar")

    def test_post_rejects_unknown_language(self):
        response = self.client.post(
            "/apis/core/locale/",
            data=json.dumps({"language": "fr"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("language", response.json())

    def test_loop_crm_points_at_shared_workspace_catalog(self):
        from django.conf import settings

        self.assertEqual(
            settings.LOCALE_PATHS,
            [Path(settings.BASE_DIR).parents[1] / "assets" / "locale"],
        )

    @override_settings(LANGUAGES=(("en", "English"),))
    def test_single_language_installation_has_no_selector_requirement(self):
        response = self.client.get("/apis/core/locale/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["languages"]), 1)


class LocaleViewUnitContractTests(TestCase):
    def test_view_rejects_unsupported_methods(self):
        response = self.client.generic("PUT", "/apis/core/locale/")
        self.assertEqual(response.status_code, 405)
