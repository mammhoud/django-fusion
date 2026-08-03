"""Smoke tests for the landing Wagtail pages (rendered through the real stack)."""
from django.test import TestCase
from wagtail.models import Page, Site

from apps.landing.models import AboutPage, ContactPage, FaqPage, HomePage, PrivacyPage
from apps.landing.management.commands.seed_landing import Command as SeedCommand


class LandingPagesTestCase(TestCase):
    """Seed the tree and assert every landing page renders with its hero."""

    @classmethod
    def setUpTestData(cls):
        SeedCommand().handle()

    def test_all_pages_render(self):
        expected_hero = {
            "/": b"Learn Without Limits",
            "/about/": b"About Us",
            "/contact/": b"Get in Touch",
            "/faq/": b"Frequently Asked Questions",
            "/privacy/": b"Privacy Policy",
        }
        for path, hero in expected_hero.items():
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200, path)
                self.assertIn(hero, response.content)

    def test_homepage_sections_present(self):
        response = self.client.get("/")
        for marker in (
            b"Features",
            b"Testimonials",
            b"Simple, transparent pricing",
            b"Frequently asked questions",
            b"Start Learning Today",
        ):
            self.assertIn(marker, response.content)

    def test_admin_login_reachable(self):
        response = self.client.get("/admin/login/")
        self.assertEqual(response.status_code, 200)

    def test_site_root_points_at_home(self):
        site = Site.objects.get(hostname="localhost")
        self.assertIsInstance(site.root_page.specific, HomePage)

    def test_landing_models_created(self):
        self.assertTrue(HomePage.objects.exists())
        for model in (AboutPage, ContactPage, FaqPage, PrivacyPage):
            self.assertTrue(model.objects.exists(), model.__name__)

    def test_page_tree(self):
        root = Page.objects.filter(depth=1).first()
        children = {c.slug for c in root.get_children()}
        self.assertEqual(children, {"home"})
        home = HomePage.objects.first()
        self.assertEqual({c.slug for c in home.get_children()}, {"about", "contact", "faq", "privacy"})
