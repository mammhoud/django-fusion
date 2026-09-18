"""
QR Menu tests — MenuVersion model + publish_menu_version.

Covers the versioned, localized, publish/preview lifecycle of the QR Menu
(P0) launch feature: defaults, unique (menu, version, locale), publish
increments version numbers, archives prior published versions, and isolates
locales from each other.
"""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _clean_menu(django_bootstrap):
    """Isolate menu tests — wipe menu-related tables before each test."""
    from models.menu import Menu, MenuItem, MenuItemAssignment, MenuVersion
    from models.pos import Category

    MenuVersion.objects.all().delete()
    MenuItemAssignment.objects.all().delete()
    MenuItem.objects.all().delete()
    Menu.objects.all().delete()
    Category.objects.all().delete()
    yield


def _make_menu(name="Main Menu", slug="main-menu", category_factory=None):
    from models.menu import Menu, MenuItem, MenuItemAssignment

    menu = Menu.objects.create(name=name, slug=slug)
    if category_factory is not None:
        cat = category_factory(name="Drinks")
        item = MenuItem.objects.create(
            category=cat, name="Espresso", slug="espresso", price="3.50",
            is_available=True,
        )
        MenuItemAssignment.objects.create(menu=menu, item=item, display_order=0)
    return menu


class TestMenuVersion:
    def test_defaults(self, django_bootstrap, category_factory):
        from models.menu import MenuVersion
        menu = _make_menu(category_factory=category_factory)
        v = MenuVersion.objects.create(menu=menu)
        assert v.version == 1
        assert v.locale == "en"
        assert v.status == "draft"
        assert v.published_at is None
        assert v.preview_token == ""

    def test_str(self, django_bootstrap):
        from models.menu import MenuVersion
        menu = _make_menu()
        v = MenuVersion.objects.create(menu=menu, version=2, locale="fr", status="published")
        assert "Main Menu v2 (fr) [published]" in str(v)

    def test_unique_menu_version_locale(self, django_bootstrap):
        from models.menu import MenuVersion
        menu = _make_menu()
        MenuVersion.objects.create(menu=menu, version=1, locale="en")
        with pytest.raises(Exception):
            MenuVersion.objects.create(menu=menu, version=1, locale="en")


class TestPublishMenuVersion:
    def test_publish_first_version(self, django_bootstrap):
        from models.menu import publish_menu_version
        menu = _make_menu()
        v = publish_menu_version(menu, "en")
        assert v.version == 1
        assert v.status == "published"
        assert v.published_at is not None

    def test_publish_increments_and_archives(self, django_bootstrap):
        from models.menu import MenuVersion, publish_menu_version
        menu = _make_menu()
        v1 = publish_menu_version(menu, "en")
        v2 = publish_menu_version(menu, "en")
        assert v2.version == 2
        v1.refresh_from_db()
        assert v1.status == "archived"
        assert MenuVersion.objects.filter(menu=menu, locale="en", status="published").count() == 1

    def test_locales_are_independent(self, django_bootstrap):
        from models.menu import MenuVersion, publish_menu_version
        menu = _make_menu()
        en = publish_menu_version(menu, "en")
        fr = publish_menu_version(menu, "fr")
        assert en.version == 1
        assert fr.version == 1
        assert MenuVersion.objects.filter(menu=menu, status="published").count() == 2

    def test_default_locale_is_en(self, django_bootstrap):
        from models.menu import publish_menu_version
        menu = _make_menu()
        v = publish_menu_version(menu)
        assert v.locale == "en"
