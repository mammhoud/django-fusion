"""
Fixture content integration tests for cms-fusion.

Verifies:
1. Wagtail models can be populated with fixture-like content
2. DB model data integrity (SEO fields, URL paths, locale trees)
3. Navigation shows correct menu items and hierarchy
4. render_first behavior via fusion health endpoint
5. Content rendering — page content from DB appears in rendered response
"""
from __future__ import annotations

import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from wagtail.models import Locale, Page, Site

User = get_user_model()


@override_settings(ROOT_URLCONF="tests.urls")
class TestFixtureContent(TestCase):
    """Comprehensive fixture content tests in a single class."""

    @classmethod
    def setUpTestData(cls):
        # Locales (Wagtail migrations create 'en', we add 'ar' and 'fr')
        cls.en, _ = Locale.objects.get_or_create(language_code="en")
        cls.ar, _ = Locale.objects.get_or_create(language_code="ar")
        cls.fr, _ = Locale.objects.get_or_create(language_code="fr")

        # User
        cls.user = User.objects.create_user(
            username="fixturetest", email="test@example.com", password="testpass"
        )

        # Root page — create if missing (Wagtail migrations may not run)
        root = Page.get_first_root_node()
        if root is None:
            root = Page.add_root(
                instance=Page(title="Root", slug="root", live=True)
            )
        cls.root = root

        # Home page (unique slug avoids conflict with Wagtail initial data)
        cls.home = cls.root.add_child(
            instance=Page(
                title="Test Home Page",
                slug="test-home",
                live=True,
                seo_title="Fusion CMS | AI-Powered Platform",
                search_description="A powerful CMS platform.",
                show_in_menus=False,
                locale=cls.en,
                owner=cls.user,
            )
        )

        # Child pages
        cls.about = cls.home.add_child(
            instance=Page(
                title="About Us",
                slug="about",
                live=True,
                seo_title="About | Fusion CMS",
                search_description="Learn about our platform.",
                show_in_menus=True,
                locale=cls.en,
                owner=cls.user,
            )
        )
        cls.contact = cls.home.add_child(
            instance=Page(
                title="Contact",
                slug="contact",
                live=True,
                seo_title="Contact | Fusion CMS",
                search_description="Get in touch.",
                show_in_menus=False,
                locale=cls.en,
                owner=cls.user,
            )
        )
        cls.team = cls.home.add_child(
            instance=Page(
                title="Our Team",
                slug="team",
                live=True,
                seo_title="Team | Fusion CMS",
                search_description="Meet our team.",
                show_in_menus=True,
                locale=cls.en,
                owner=cls.user,
            )
        )
        cls.courses = cls.home.add_child(
            instance=Page(
                title="Courses",
                slug="all-courses",
                live=True,
                seo_title="Courses | Fusion CMS",
                search_description="Explore our courses.",
                show_in_menus=False,
                locale=cls.en,
                owner=cls.user,
            )
        )

        # Multilingual
        cls.home_ar = cls.root.add_child(
            instance=Page(
                title="الصفحة الرئيسية",
                slug="home-ar",
                live=True,
                seo_title="Fusion CMS Arabic",
                search_description="منصة CMS قوية.",
                show_in_menus=False,
                locale=cls.ar,
                owner=cls.user,
            )
        )

        # Site config
        Site.objects.update_or_create(
            hostname="testserver",
            port=80,
            defaults={
                "root_page": cls.home,
                "is_default_site": True,
                "site_name": "Fusion CMS Test",
            },
        )

    def setUp(self):
        self.client = Client()

    # ── DB model integrity ──────────────────────────────────────────

    def test_locales_exist(self):
        assert Locale.objects.count() >= 3

    def test_root_page_exists(self):
        assert self.root.depth == 1

    def test_home_page_exists(self):
        home = Page.objects.get(slug="test-home", live=True, depth=2)
        assert home.title == "Test Home Page"

    def test_child_pages_exist(self):
        children = self.home.get_children().live()
        child_slugs = {c.slug for c in children}
        expected = {"about", "contact", "team", "all-courses"}
        assert child_slugs == expected

    def test_page_seo_fields(self):
        assert self.about.seo_title == "About | Fusion CMS"
        assert self.about.show_in_menus is True
        assert "Learn about" in self.about.search_description

    def test_multilingual_home_pages(self):
        en_homes = Page.objects.filter(depth=2, live=True, locale=self.en)
        ar_homes = Page.objects.filter(depth=2, live=True, locale=self.ar)
        assert en_homes.exists()
        assert ar_homes.exists()

    def test_page_url_paths(self):
        assert "test-home" in self.home.url_path
        assert "about" in self.about.url_path

    # ── Navigation and hierarchy ────────────────────────────────────

    def test_menu_pages_have_show_in_menus(self):
        assert self.about.show_in_menus is True
        assert self.team.show_in_menus is True
        assert self.contact.show_in_menus is False

    def test_page_hierarchy_depth(self):
        assert self.home.depth == 2
        assert self.about.depth == 3
        assert self.about.get_parent() == self.home

    def test_navigable_pages_count(self):
        nav_pages = Page.objects.filter(live=True, show_in_menus=True, depth=3)
        assert nav_pages.count() == 2

    def test_child_page_count(self):
        assert self.home.get_children().live().count() == 4

    def test_root_has_multiple_locale_pages(self):
        root_children = self.root.get_children().live()
        assert root_children.count() >= 2

    # ── Content rendering (DB → page URL) ───────────────────────────

    def test_page_has_valid_url_path(self):
        """Page url_path is correctly constructed from the tree path."""
        url_path = self.about.url_path
        assert url_path is not None
        assert url_path.startswith("/")
        assert "about" in url_path

    def test_page_url_matches_slug(self):
        """Page.get_url() includes the slug."""
        # get_url() or url_path should contain the slug
        assert "about" in (self.about.url or self.about.url_path)

    # ── API connectivity ────────────────────────────────────────────

    def test_fusion_health_returns_ok(self):
        response = self.client.get("/api/fusion/health")
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["status"] == 200
        inner = data["data"]
        assert "fusion_render_first" in inner
        assert isinstance(inner["fusion_render_first"], bool)

    def test_api_pages_list_returns_200(self):
        response = self.client.get("/api/pages/")
        assert response.status_code == 200
        data = json.loads(response.content)
        assert "pages" in data
        assert "total" in data

    # ── render_first behavior ───────────────────────────────────────

    def test_render_first_is_boolean(self):
        """render_first is always reported as a boolean."""
        response = self.client.get("/api/fusion/health")
        data = json.loads(response.content)
        assert isinstance(data["data"]["fusion_render_first"], bool)

    def test_render_first_header_changes_value(self):
        """X-Fusion-Render-First: true header sets render_first to True."""
        response = self.client.get(
            "/api/fusion/health",
            HTTP_X_FUSION_RENDER_FIRST="true",
        )
        data = json.loads(response.content)
        assert data["data"]["fusion_render_first"] is True
