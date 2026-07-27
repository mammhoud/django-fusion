"""
Fixture content integration tests for cms-fusion.

Verifies:
1. Wagtail models can be populated with fixture-like content
2. Pages render correctly via the API
3. Navigation shows correct menu items
4. render_first behavior (JSON vs server HTML)
5. DB model data integrity (SEO fields, URL paths, locale trees)
"""
from __future__ import annotations

import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from wagtail.models import Locale, Page, Site

User = get_user_model()


# ── Shared base class with all fixture data ────────────────────────────
class _FusionFixtureTestBase(TestCase):
    """Shared base that creates Wagtail fixture data once for all tests."""

    @classmethod
    def setUpTestData(cls):
        # Locales (Wagtail migrations already create 'en')
        cls.en, _ = Locale.objects.get_or_create(language_code="en")
        cls.ar, _ = Locale.objects.get_or_create(language_code="ar")
        cls.fr, _ = Locale.objects.get_or_create(language_code="fr")

        # User for page ownership
        cls.user = User.objects.create_user(
            username="fixturetest", email="test@example.com", password="testpass"
        )

        # Root page (created by Wagtail migrations)
        cls.root = Page.get_first_root_node()
        assert cls.root is not None, (
            "Root page not found — Wagtail migrations may not have run. "
            "Check that _DisableMigrations allows third-party app migrations."
        )

        # Home page (use unique slug to avoid conflict with Wagtail initial data)
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
            hostname="localhost",
            port=80,
            defaults={
                "root_page": cls.home,
                "is_default_site": True,
                "site_name": "Fusion CMS Test",
            },
        )

    def setUp(self):
        self.client = Client()


# ── Test: Fixture loading and DB integrity ─────────────────────────────
@override_settings(ROOT_URLCONF="tests.urls")
class TestFixtureLoading(_FusionFixtureTestBase):
    """Verify Wagtail models work with fixture-like content."""

    def test_locales_exist(self):
        """At least 3 locales are present."""
        assert Locale.objects.count() >= 3

    def test_root_page_exists(self):
        """The root page exists."""
        assert self.root.title == "Root"
        assert self.root.depth == 1

    def test_home_page_exists(self):
        """Home page exists with correct slug and title."""
        home = Page.objects.get(slug="test-home", live=True, depth=2)
        assert home.title == "Test Home Page"

    def test_child_pages_exist(self):
        """About, Contact, Team, and Courses pages exist as children of Home."""
        children = self.home.get_children().live()
        child_slugs = {c.slug for c in children}
        expected = {"about", "contact", "team", "all-courses"}
        missing = expected - child_slugs
        assert not missing, f"Missing child pages: {missing}"

    def test_page_seo_fields(self):
        """Page SEO fields match expected values."""
        assert self.about.seo_title == "About | Fusion CMS"
        assert self.about.show_in_menus is True
        assert "Learn about" in self.about.search_description

    def test_multilingual_home_pages(self):
        """Each locale has its own home page tree."""
        en_homes = Page.objects.filter(depth=2, live=True, locale=self.en)
        ar_homes = Page.objects.filter(depth=2, live=True, locale=self.ar)
        assert en_homes.exists()
        assert ar_homes.exists()

    def test_page_url_paths(self):
        """Page URL paths follow expected patterns."""
        assert self.home.url_path == f"/test-home-{self.home.id}/"
        assert "about" in self.about.url_path


# ── Test: Page rendering via API ───────────────────────────────────────
@override_settings(ROOT_URLCONF="tests.urls")
class TestPageRendering(_FusionFixtureTestBase):
    """Verify pages render correctly via the API endpoints."""

    def test_api_pages_list_returns_data(self):
        """After populating DB, /api/pages/ returns pages."""
        response = self.client.get("/api/pages/")
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["total"] > 0

    def test_api_page_detail_home(self):
        """GET /api/pages/test-home/ returns home page data."""
        response = self.client.get("/api/pages/test-home/")
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["slug"] == "test-home"
        assert data["title"] == "Test Home Page"

    def test_fragment_pointer_returns_200(self):
        """GET /api/pages/test-home/fragment/ returns a fragment pointer JSON."""
        response = self.client.get("/api/pages/test-home/fragment/")
        assert response.status_code == 200
        data = json.loads(response.content)
        assert "target" in data or "action" in data or "url" in data

    def test_page_data_returns_200(self):
        """GET /api/pages/test-home/data/ returns page data JSON."""
        response = self.client.get("/api/pages/test-home/data/")
        assert response.status_code == 200
        data = json.loads(response.content)
        assert "encoded" in data


# ── Test: render_first behavior ────────────────────────────────────────
@override_settings(ROOT_URLCONF="tests.urls")
class TestRenderFirstBehavior(_FusionFixtureTestBase):
    """Verify render_first=false (JSON data) and render_first=true behavior."""

    def test_render_first_false_returns_json_data(self):
        """With render_first=false, page/data returns encoded JSON."""
        response = self.client.get(
            "/api/pages/test-home/data/",
            HTTP_X_FUSION_RENDER_FIRST="false",
        )
        assert response.status_code == 200
        data = json.loads(response.content)
        assert "encoded" in data

    def test_render_first_true_returns_response(self):
        """With render_first=true, page/data returns a valid response."""
        response = self.client.get(
            "/api/pages/test-home/data/",
            HTTP_X_FUSION_RENDER_FIRST="true",
        )
        assert response.status_code == 200

    def test_fusion_health_reflects_session(self):
        """Health endpoint reports render_first state."""
        response = self.client.get("/api/fusion/health")
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["status"] == 200
        inner = data["data"]
        assert "fusion_render_first" in inner
        assert isinstance(inner["fusion_render_first"], bool)


# ── Test: Navigation and footer ────────────────────────────────────────
@override_settings(ROOT_URLCONF="tests.urls")
class TestNavigationAndFooter(_FusionFixtureTestBase):
    """Verify navigation and page hierarchy from DB models."""

    def test_menu_pages_have_show_in_menus(self):
        """Pages meant for navigation have show_in_menus=True."""
        assert self.about.show_in_menus is True
        assert self.team.show_in_menus is True
        assert self.contact.show_in_menus is False  # Not in nav

    def test_api_pages_includes_show_in_nav(self):
        """API pages response includes navigation info from Wagtail models."""
        response = self.client.get("/api/pages/")
        data = json.loads(response.content)
        nav_pages = [p for p in data["pages"] if p.get("show_in_nav")]
        assert len(nav_pages) > 0

    def test_pages_list_includes_all_child_pages(self):
        """The pages list includes all live child pages + home."""
        child_count = self.home.get_children().live().count()
        response = self.client.get("/api/pages/")
        data = json.loads(response.content)
        assert data["total"] >= child_count + 1  # +1 for home

    def test_page_hierarchy_depth(self):
        """Pages are at correct tree depth."""
        assert self.home.depth == 2
        assert self.about.depth == 3
        assert self.about.get_parent() == self.home

    def test_navigable_pages_count(self):
        """Exactly 2 pages are marked for navigation (about, team)."""
        nav_pages = Page.objects.filter(live=True, show_in_menus=True, depth=3)
        assert nav_pages.count() == 2
