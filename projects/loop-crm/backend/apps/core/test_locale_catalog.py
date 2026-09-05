"""Regression coverage for the shared Loop-CRM gettext catalog contract."""
from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class SharedLocaleCatalogTests(SimpleTestCase):
    def test_shared_catalogs_exist_for_each_advertised_language(self):
        locale_root = Path(settings.LOCALE_PATHS[0])
        for language in ("en", "ar"):
            catalog = locale_root / language / "LC_MESSAGES" / "django.po"
            self.assertTrue(catalog.is_file(), catalog)
            self.assertIn('msgid "Interface language"', catalog.read_text(encoding="utf-8"))

    def test_backend_surface_catalog_contains_core_runtime_copy(self):
        locale_root = Path(settings.LOCALE_PATHS[0])
        english = (locale_root / "en" / "LC_MESSAGES" / "django.po").read_text(encoding="utf-8")
        arabic = (locale_root / "ar" / "LC_MESSAGES" / "django.po").read_text(encoding="utf-8")
        for message in ("Overview", "Workspace", "Billing is not configured."):
            self.assertIn(f'msgid "{message}"', english)
            self.assertIn(f'msgid "{message}"', arabic)
        self.assertIn('msgstr "الفوترة غير مُهيأة."', arabic)


    def test_makefile_targets_shared_locale_root(self):
        makefile = Path(settings.BASE_DIR).parent / "backend" / "Makefile"
        text = makefile.read_text(encoding="utf-8")
        self.assertIn("SHARED_LOCALE_DIR := $(CURDIR)/../../assets/locale", text)
        self.assertIn("makemessages -l en -l ar --no-wrap", text)
        self.assertIn("cp locale/$$lang/LC_MESSAGES/django.po", text)
        self.assertIn("locale-check", text)

    def test_settings_and_catalog_root_are_aligned(self):
        self.assertEqual(
            Path(settings.LOCALE_PATHS[0]),
            Path(settings.BASE_DIR).parents[1] / "assets" / "locale",
        )
        self.assertEqual({code for code, _label in settings.LANGUAGES}, {"en", "ar"})
