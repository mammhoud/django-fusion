"""Smoke tests for the landing Wagtail pages (rendered through the real stack)."""
from django.test import TestCase
from wagtail.models import Page, Site

from apps.pages.models import (
    AboutPage,
    BlogPage,
    BlogPostPage,
    ContactPage,
    FaqPage,
    FeaturesPage,
    HomePage,
    PricingPage,
    PrivacyPage,
    ProductPage,
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
        # Hero titles are stored WITHOUT the accent word — the Astro frontend
        # renders ``title`` + its own ``accent`` ("documents", "Moustafa", …)
        # so the stored titles must stay free of the accent phrase.
        expected_hero = {
            "/": b"Platforms that ship as",
            "/about/": b"Mahmoud Ezzat",
            "/services/": b"Services",
            "/products/": b"Everything we build, shipped as",
            "/features/": b"Built to ship as",
            "/projects/": b"Everything we build, shipped as",
            "/blog/": b"The Blog",
            "/pricing/": b"Pricing",
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
        self.assertIn(b"Platforms that ship as", response.content)
        self.assertIn(b"Everything is open source", response.content)
        for moved in (
            b"Numbers that speak for themselves",
            b"Everything you need to launch",
            b"Trusted by developers",
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
            b"Trusted by developers",
            b"Frequently asked questions",
            b"Built open-source, shipped as HTML",
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
                    b"Trusted by developers",
                    b"Frequently asked questions",
                    b"Built open-source, shipped as HTML",
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
            b"Trusted by developers",
            b"Frequently asked questions",
            b"Built open-source, shipped as HTML",
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

    def test_fusion_render_mode_both_options(self):
        """Seeded content is served under both content-delivery options."""
        from django.conf import settings as django_settings

        # Option A — “data APIs” (default): the client renders from /apis/* JSON.
        self.assertFalse(django_settings.FUSION_RENDER_FIRST_DEFAULT)
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Platforms that ship as", response.content)
        self.assertIn(b'name="fusion-render-mode" content="data-api"', response.content)

        # The same seeded content is available via JSON.
        data = self.client.get("/apis/pages/about/").json()
        self.assertEqual([s["label"] for s in data["stats"]], ["Open-source repos", "Blog posts", "Production sites", "Years building"])
        self.assertEqual([t["author"] for t in data["testimonials"]], ["Sarah Mitchell", "David Chen", "Amira Hassan"])

        # Option B — “fusion render first” still works via the header override.
        response = self.client.get("/", HTTP_X_FUSION_RENDER_FIRST="true")
        self.assertIn(b'name="fusion-render-mode" content="fusion-render"', response.content)

    def test_render_mode_api_reports_both_options(self):
        """/apis/render-mode/ reports the configured mode + per-request override."""
        # Default (data APIs).
        response = self.client.get("/apis/render-mode/")
        self.assertEqual(response.json()["fusion_render_first"], False)
        self.assertEqual(response.json()["mode"], "data-api")

        # Header override to render-first.
        response = self.client.get("/apis/render-mode/", HTTP_X_FUSION_RENDER_FIRST="true")
        self.assertEqual(response.json()["fusion_render_first"], True)
        self.assertEqual(response.json()["mode"], "fusion-render")

        # The django-fusion setting drives the mode, and the header overrides it.
        with self.settings(FUSION_RENDER_FIRST_DEFAULT=True):
            response = self.client.get("/apis/render-mode/")
            self.assertEqual(response.json()["mode"], "fusion-render")
            response = self.client.get(
                "/apis/render-mode/", HTTP_X_FUSION_RENDER_FIRST="false"
            )
            self.assertEqual(response.json()["mode"], "data-api")
            # The page document is marked fusion-render too.
            response = self.client.get("/")
            self.assertIn(b'name="fusion-render-mode" content="fusion-render"', response.content)

    def test_contact_submit_endpoint(self):
        """POST /fragment/contact/ accepts JSON + HTMX and form-encoded bodies."""
        # JSON + HTMX (Astro ContactForm) → HTML fragment swapped into the form.
        response = self.client.post(
            "/fragment/contact/",
            data='{"name": "Test", "email": "t@example.com", "message": "A sufficiently long message."}',
            content_type="application/json",
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Thanks, Test", response.content)

        # Form-encoded (Django template form) → JSON.
        response = self.client.post(
            "/fragment/contact/",
            data={"name": "Test", "email": "t@example.com", "message": "A sufficiently long message."},
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"success": True, "message": "Thanks, Test! We'll be in touch."})

        # Invalid input → 400.
        response = self.client.post(
            "/fragment/contact/",
            data='{"name": "", "email": "bad"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

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
            ServicesPage,
            ProductsPage,
            FeaturesPage,
            ProjectsPage,
            BlogPage,
            PricingPage,
            ContactPage,
            FaqPage,
            PrivacyPage,
            ProductPage,
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
            {"about", "services", "products", "features", "projects", "blog", "pricing", "contact", "faq", "privacy"},
        )
        for child in home.get_children():
            self.assertEqual(child.depth, 3, child.slug)

    def test_company_redirects_to_about(self):
        """Company merged into About — /company/ permanently redirects and Company is not in the tree."""
        response = self.client.get("/company/")
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "/about/")
        # No Company page in the nav or the tree.
        nav = self.client.get("/apis/navigation/").json()
        self.assertNotIn("Company", [item["label"] for item in nav["nav_items"]])

    def test_product_pages_render_with_editions_and_snippets(self):
        """Each ProductPage renders hero + editions & pricing + reference snippets."""
        for slug, hero in (("forge-pos", b"Forge POS"), ("lms", b"Fusion LMS"), ("cms", b"Fusion CMS")):
            with self.subTest(slug=slug):
                response = self.client.get(f"/products/{slug}/")
                self.assertEqual(response.status_code, 200, slug)
                self.assertIn(hero, response.content)
                self.assertIn(b"editions", response.content.lower())

    def test_unknown_product_slug_404s(self):
        """An unknown product slug is a 404 — never a silent fallback to another product."""
        response = self.client.get("/products/does-not-exist/")
        self.assertEqual(response.status_code, 404)

        # Known slugs still resolve (no regression from the 404 change).
        self.assertEqual(self.client.get("/products/forge-pos/").status_code, 200)

    def test_forge_pos_renders_all_editions_with_pricing(self):
        """The POS reference page lists Minimal · Solo · Full with per-edition pricing."""
        response = self.client.get("/products/forge-pos/")
        self.assertEqual(response.status_code, 200)
        for marker in (b"Minimal", b"Solo", b"Full", b"$0", b"$49", b"$99", b"Reference", b"SQLite", b"Rust"):
            self.assertIn(marker, response.content)

    def test_products_lists_product_pages(self):
        """/products/ lists the product pages (cards) alongside the project grid."""
        response = self.client.get("/products/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"The product line", response.content)
        for href in (b"/products/forge-pos/", b"/products/lms/", b"/products/cms/"):
            self.assertIn(href, response.content)

        data = self.client.get("/apis/pages/products/").json()
        self.assertTrue(any(p["slug"] == "forge-pos" for p in data["products"]), data.get("products"))

    def test_services_carries_offering_and_process(self):
        """Services renders the offering grid (features) + the 'build as you go' process."""
        response = self.client.get("/services/")
        self.assertEqual(response.status_code, 200)
        for marker in (
            b"Sites that ship as documents",
            b"Django + Wagtail build",
            b"Build as you go",
            b"From brief to shipped, in four steps",
            b"Discover",
            b"Ship &amp; grow",  # Wagtail escapes the ampersand in template output
        ):
            self.assertIn(marker, response.content)

    def test_products_carries_project_cards(self):
        """Products renders the project cards (projects + products) alongside the full document."""
        response = self.client.get("/products/")
        self.assertEqual(response.status_code, 200)
        for marker in (
            b"Projects in this repo",
            b"Forge POS",
            b"django-fusion",
            b"ceptor-ai",
        ):
            self.assertIn(marker, response.content)

    def test_blog_renders_post_grid(self):
        """Blog renders the seeded post grid (hero + cards + cta)."""
        response = self.client.get("/blog/")
        self.assertEqual(response.status_code, 200)
        for marker in (
            b"From the blog",
            b"Why we ship landing pages as documents",
            b"HTMX fragments vs. JSON APIs",
            b"monorepo-six-products",
            b"Everything is open source",
        ):
            self.assertIn(marker, response.content)

    def test_blog_post_pages_render_with_body(self):
        """Each seeded BlogPostPage renders at /blog/<slug>/ with its body content."""
        for slug, body_marker in (
            ("why-landing-pages-as-documents", b"The document model"),
            ("htmx-fragments-vs-json-apis", b"The API contract tax"),
            ("wagtail-streamfield-marketing", b"Sections, not pages"),
            ("alpine-reactivity-landing", b"A few x-data attributes"),
            ("monorepo-six-products", b"Shared everything"),
            ("server-time-streamed-htmx", b"/fragment/ping/"),
        ):
            with self.subTest(slug=slug):
                response = self.client.get(f"/blog/{slug}/")
                self.assertEqual(response.status_code, 200, slug)
                self.assertIn(body_marker, response.content)
                self.assertIn(b"All posts", response.content)

    def test_unknown_blog_slug_404s(self):
        """An unknown blog post slug is a 404 — never a silent fallback."""
        response = self.client.get("/blog/does-not-exist/")
        self.assertEqual(response.status_code, 404)

        # Known slugs still resolve (no regression from the 404 change).
        self.assertEqual(
            self.client.get("/blog/why-landing-pages-as-documents/").status_code, 200
        )

    def test_blog_post_children_created(self):
        """BlogPostPage children exist under the Blog index with matching slugs."""
        blog = BlogPage.objects.first()
        child_slugs = {c.slug for c in blog.get_children().live()}
        self.assertEqual(
            child_slugs,
            {
                "why-landing-pages-as-documents",
                "htmx-fragments-vs-json-apis",
                "wagtail-streamfield-marketing",
                "alpine-reactivity-landing",
                "monorepo-six-products",
                "server-time-streamed-htmx",
            },
        )
        self.assertTrue(BlogPostPage.objects.exists())

    def test_pricing_renders_tiers_and_faq(self):
        """Pricing renders its own tier grid + faq (dedicated page, not folded into features)."""
        response = self.client.get("/pricing/")
        self.assertEqual(response.status_code, 200)
        for marker in (
            b"Simple, transparent pricing",
            b"Starter",
            b"Pro",
            b"Team",
            b"Frequently asked questions",
        ):
            self.assertIn(marker, response.content)

    def test_faq_and_privacy_not_in_nav(self):
        """FAQ + Privacy are footer-only — never in the header nav (HTML or API)."""
        response = self.client.get("/")
        content = response.content.decode()
        nav_region = content[content.index('aria-label="Main"'):]
        nav_region = nav_region[: nav_region.index("</nav>")]
        self.assertNotIn("/faq/", nav_region)
        self.assertNotIn("/privacy/", nav_region)
        # New pages ARE in the nav.
        self.assertIn("/blog/", nav_region)
        self.assertIn("/pricing/", nav_region)

        data = self.client.get("/apis/navigation/").json()
        nav_labels = [item["label"] for item in data["nav_items"]]
        self.assertNotIn("FAQ", nav_labels)
        self.assertNotIn("Privacy Policy", nav_labels)
        self.assertIn("Blog", nav_labels)
        self.assertIn("Pricing", nav_labels)
