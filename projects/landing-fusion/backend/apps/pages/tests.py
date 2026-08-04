"""Smoke tests for the landing Wagtail pages (rendered through the real stack)."""
from django.test import TestCase
from wagtail.models import Page, Site

from apps.pages.models import (
    AboutPage,
    CompanyPage,
    ContactPage,
    FaqPage,
    FeaturesPage,
    HomePage,
    PrivacyPage,
    ProductsPage,
    ProjectsPage,
    ServicesPage,
)
from apps.pages.management.commands.seed_pages import Command as SeedCommand


class LandingPagesTestCase(TestCase):
    """Seed the tree and assert every landing page renders with its hero."""

    @classmethod
    def setUpTestData(cls):
        SeedCommand().handle()

    def test_all_pages_render(self):
        expected_hero = {
            "/": b"Learn Without Limits",
            "/about/": b"About Us",
            "/company/": b"Who We Are",
            "/services/": b"Services",
            "/products/": b"Products",
            "/features/": b"Features",
            "/projects/": b"Projects",
            "/contact/": b"Get in Touch",
            "/faq/": b"Frequently Asked Questions",
            "/privacy/": b"Privacy Policy",
        }
        for path, hero in expected_hero.items():
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200, path)
                self.assertIn(hero, response.content)

    def test_home_is_slim_entry(self):
        """Home renders hero + CTA only — the section stack moved to About."""
        response = self.client.get("/")
        self.assertIn(b"Learn Without Limits", response.content)
        self.assertIn(b"Start Learning Today", response.content)
        for moved in (
            b"Numbers that speak for themselves",
            b"Everything you need to launch",
            b"Loved by teams worldwide",
            b"Simple, transparent pricing",
            b"Frequently asked questions",
        ):
            self.assertNotIn(moved, response.content)

    def test_about_carries_full_document(self):
        """About renders the whole stack: mission, stats, features, pricing, testimonials, faq, cta."""
        response = self.client.get("/about/")
        self.assertEqual(response.status_code, 200)
        for marker in (
            b"Our mission",
            b"Numbers that speak for themselves",
            b"Everything you need to launch",
            b"Simple, transparent pricing",
            b"Loved by teams worldwide",
            b"Frequently asked questions",
            b"Start Learning Today",
        ):
            self.assertIn(marker, response.content)

    def test_products_and_features_carry_full_document(self):
        """Products + Features render the full stack like About: stats, features, pricing, testimonials, faq, cta."""
        for path in ("/products/", "/features/"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200, path)
                for marker in (
                    b"Numbers that speak for themselves",
                    b"Everything you need to launch",
                    b"Simple, transparent pricing",
                    b"Loved by teams worldwide",
                    b"Frequently asked questions",
                    b"Start Learning Today",
                ):
                    self.assertIn(marker, response.content)

    def test_projects_carries_full_document_with_repo_projects(self):
        """Projects renders the full stack plus the repo project cards (editions + shared/own features)."""
        response = self.client.get("/projects/")
        self.assertEqual(response.status_code, 200)
        for marker in (
            b"Projects in this repo",
            b"Forge POS",
            b"django-fusion",
            b"ceptor-ai",
            "Minimal \u00b7 Solo \u00b7 Full".encode(),
            b"shared",
            b"own",
            b"Numbers that speak for themselves",
            b"Everything you need to launch",
            b"Simple, transparent pricing",
            b"Loved by teams worldwide",
            b"Frequently asked questions",
            b"Start Learning Today",
        ):
            self.assertIn(marker, response.content)

    def test_projects_fragment_serves_content_region_with_cards(self):
        """HTMX request for /projects/ returns the fragment including the project cards."""
        response = self.client.get("/projects/", HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["HX-Reswap"], "innerHTML")
        self.assertIn(b'id="page-content"', response.content)
        self.assertIn(b"Forge POS", response.content)
        self.assertNotIn(b"<html", response.content)
        self.assertNotIn(b"site-header", response.content)

    def test_pricing_folded_into_features_on_about(self):
        """Pricing renders inside the features section (no standalone pricing section on /about/)."""
        response = self.client.get("/about/")
        content = response.content.decode()
        features_idx = content.index('id="features"')
        pricing_idx = content.index('id="pricing"')
        self.assertLess(features_idx, pricing_idx)
        # The features section contains the pricing grid: no closing tag between
        # the features id and the pricing id (pricing renders as a folded div).
        next_close = content.find("</section>", features_idx)
        self.assertTrue(next_close == -1 or next_close > pricing_idx)

    def test_admin_login_reachable(self):
        response = self.client.get("/admin/login/")
        self.assertEqual(response.status_code, 200)

    def test_htmx_fragment_serves_content_region_only(self):
        """HTMX requests get the fragment (content region), not the full document."""
        response = self.client.get("/about/", HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["HX-Reswap"], "innerHTML")
        self.assertIn(b'id="page-content"', response.content)
        self.assertNotIn(b"<html", response.content)
        self.assertNotIn(b"site-header", response.content)

    def test_site_root_points_at_home(self):
        site = Site.objects.get(hostname="localhost")
        self.assertIsInstance(site.root_page.specific, HomePage)

    def test_landing_models_created(self):
        self.assertTrue(HomePage.objects.exists())
        for model in (
            AboutPage,
            CompanyPage,
            ServicesPage,
            ProductsPage,
            FeaturesPage,
            ProjectsPage,
            ContactPage,
            FaqPage,
            PrivacyPage,
        ):
            self.assertTrue(model.objects.exists(), model.__name__)

    def test_page_tree(self):
        root = Page.objects.filter(depth=1).first()
        self.assertEqual({c.slug for c in root.get_children()}, {"home"})

        home = HomePage.objects.first()
        self.assertEqual(home.depth, 2)

        child_slugs = {c.slug for c in home.get_children()}
        self.assertEqual(
            child_slugs,
            {"about", "company", "services", "products", "features", "projects", "contact", "faq", "privacy"},
        )
        for child in home.get_children():
            self.assertEqual(child.depth, 3, child.slug)
