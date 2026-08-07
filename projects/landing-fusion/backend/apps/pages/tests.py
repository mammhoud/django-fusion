"""Smoke tests for the landing Wagtail pages (rendered through the real stack)."""
from django.test import TestCase
from wagtail.models import Page, Site

from apps.pages.models import (
    AboutPage,
    BlogPage,
    BlogPostPage,
    BrandPage,
    ContactPage,
    FaqPage,
    FeaturesPage,
    FounderPage,
    HomePage,
    PricingPage,
    PrivacyPage,
    ProductPage,
    ProductsPage,
    ServicesPage,
    StartupPage,
    TeamPage,
)
from apps.pages.management.commands.seed_pages import Command as SeedCommand


class LandingPagesTestCase(TestCase):
    """Seed the tree and assert every landing page renders with its hero."""

    @classmethod
    def setUpTestData(cls):
        SeedCommand().handle()

    def test_all_pages_render(self):
        # Hero titles are stored WITHOUT the accent word — both render roads
        # (Astro Hero.astro and content/blocks/hero.html) render ``title`` +
        # ``accent`` separately, so the stored titles must stay free of the
        # accent phrase.
        expected_hero = {
            "/": b"Digital products, shipped as",
            "/about/": b"A clearer path to market",
            "/services/": b"From idea to market",
            "/products/": b"Most of what we build, shipped as",
            "/features/": b"Built to ship as",
            "/blog/": b"Ideas from real launches",
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
        self.assertIn(b"Digital products, shipped as", response.content)
        self.assertIn(b"A useful first release beats a noisy roadmap", response.content)
        for moved in (
            b"Built for steady growth",
            b"The details that make a service usable",
            b"Designed around the people using it",
            b"Simple, transparent pricing",
            b"Frequently asked questions",
        ):
            self.assertNotIn(moved, response.content)

    def test_about_carries_full_document(self):
        """About renders the whole stack: mission, stats, founder features, pricing, testimonials, cta.

        Pricing moved onto About (from the home page) and the feature grid was
        reframed around the founder + company; the generic FAQ stays on /faq/.
        """
        response = self.client.get("/about/")
        self.assertEqual(response.status_code, 200)
        for marker in (
            b"Built for steady growth",
            b"Built by one engineer, for real teams",
            b"Designed around the people using it",
            b"Simple, transparent pricing",
            b"Built in the open, shipped as HTML",
            b"Meet the team",
        ):
            self.assertIn(marker, response.content)
        self.assertNotIn(b"Frequently asked questions", response.content)

    def test_team_subpage_renders(self):
        """About → Team (/about/team/) renders the member cards + social links."""
        response = self.client.get("/about/team/")
        self.assertEqual(response.status_code, 200)
        for marker in (
            b"The people behind structa.cloud",
            b"Mahmoud Ezzat Moustafa",
            b"Founder",
            b"Who builds what",
            b"linkedin.com/in/mammhoud",
            b"facebook.com/mammhoud",
        ):
            self.assertIn(marker, response.content)
        # The team API carries the members with their links.
        data = self.client.get("/apis/pages/team/").json()
        members = data.get("team", [])
        self.assertTrue(members)
        self.assertEqual(members[0]["name"], "Mahmoud Ezzat Moustafa")

    def test_founder_subpage_renders(self):
        """About → Founder (/about/founder/) renders the engineer story + stack + skills."""
        response = self.client.get("/about/founder/")
        self.assertEqual(response.status_code, 200)
        for marker in (
            b"Mahmoud Ezzat Moustafa",
            b"The engineer",
            b"Full-stack developer",
            b"Built on",
            b"django-fusion",
            b"Tauri 2",
            b"Ships as documents",
            b"Built in the open",
        ):
            self.assertIn(marker, response.content)
        # The founder API carries the tech stack + skills grid.
        data = self.client.get("/apis/pages/founder/").json()
        self.assertEqual(data["type"], "FounderPage")
        self.assertIn("Python", data.get("tech", []))
        self.assertTrue(data.get("features"))

    def test_startup_subpage_renders(self):
        """About → Startup (/about/startup/) renders the timeline + stats."""
        response = self.client.get("/about/startup/")
        self.assertEqual(response.status_code, 200)
        for marker in (
            b"The Startup",
            b"The story",
            b"Freelance foundations",
            b"The reusable library",
            b"Open source and AI",
            b"Products and scale",
            b"The story in numbers",
            b"Five products, one repo",
        ):
            self.assertIn(marker, response.content)
        # The startup API carries the timeline steps + stats.
        data = self.client.get("/apis/pages/startup/").json()
        self.assertEqual(data["type"], "StartupPage")
        self.assertTrue(data.get("process"))
        self.assertTrue(data.get("stats"))

    def test_products_and_features_carry_full_document(self):
        """Products + Features render the full stack like About: stats, features, testimonials, cta."""
        for path in ("/products/", "/features/"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200, path)
                for marker in (
                    b"Built for steady growth",
                    b"Built by one engineer, for real teams",
                    b"Designed around the people using it",
                    b"Built in the open, shipped as HTML",
                ):
                    self.assertIn(marker, response.content)
                # Generic FAQ moved to the dedicated /faq/ page.
                self.assertNotIn(b"Frequently asked questions", response.content)

    def test_projects_redirects_permanently_to_products(self):
        """Projects merged into Products — /projects/ is a permanent redirect and is not in the nav."""
        response = self.client.get("/projects/")
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "/products/")
        # The merged catalog carries the product cards (projects grid folded in).
        data = self.client.get("/apis/pages/products/").json()
        slugs = [p["slug"] for p in data.get("products", [])]
        self.assertIn("formint-pos", slugs)
        self.assertNotIn("django-bolt", slugs)
        self.assertNotIn("ceptor-ai", slugs)  # hidden products are excluded
        # No Projects item in the nav (API or HTML).
        nav = self.client.get("/apis/navigation/").json()
        self.assertNotIn("Projects", [item["label"] for item in nav["nav_items"]])
        home_content = self.client.get("/").content.decode()
        self.assertNotIn('href="/projects/"', home_content)

    def test_products_fragment_serves_content_region_with_cards(self):
        """HTMX request for /products/ returns the fragment including the product cards + project grid."""
        response = self.client.get("/products/", HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["HX-Reswap"], "innerHTML")
        self.assertIn(b'id="page-content"', response.content)
        self.assertIn(b"Formints", response.content)
        self.assertNotIn(b"<html", response.content)
        self.assertNotIn(b"site-header", response.content)

    def test_direct_page_fragment_api_is_content_only(self):
        """The Astro LiveFragment endpoint returns Django content, never a document shell."""
        response = self.client.get("/fragment/pages/products/", HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'id="page-content"', response.content)
        self.assertIn(b"Formints", response.content)
        self.assertNotIn(b"<!doctype", response.content.lower())
        self.assertNotIn(b"<html", response.content.lower())
        self.assertNotIn(b"site-header", response.content)

        missing = self.client.get("/fragment/pages/does-not-exist/", HTTP_HX_REQUEST="true")
        self.assertEqual(missing.status_code, 404)

    def test_page_list_api_skips_orphaned_pages(self):
        """The page list API must survive a page whose specific class is unresolvable.

        Orphaned/stale content types (removed models or old seeds) used to crash
        the whole /apis/pages/ endpoint — the frontend then silently built zero
        dynamic pages. Guarded pages are skipped, not fatal.
        """
        from django.contrib.contenttypes.models import ContentType
        from wagtail.models import Page

        data = self.client.get("/apis/pages/").json()
        self.assertGreater(data["total"], 0)
        slugs = {p["slug"] for p in data["pages"]}
        self.assertIn("products", slugs)
        self.assertIn("formint-pos", slugs)

        # Simulate an orphan: detach the "privacy" page's content type so its
        # specific class can no longer resolve (models removed in a migration
        # leave exactly this state behind), then confirm the API still lists
        # every other page instead of returning an empty list.
        privacy = Page.objects.get(slug="privacy")
        stale_ct, _ = ContentType.objects.get_or_create(
            app_label="pages", model="removedmodel"
        )
        original_ct = privacy.content_type
        privacy.content_type = stale_ct
        privacy.save()
        try:
            data = self.client.get("/apis/pages/").json()
        finally:
            privacy.content_type = original_ct
            privacy.save()
        self.assertGreater(data["total"], 0)
        self.assertNotIn("privacy", {p["slug"] for p in data["pages"]})
        self.assertIn("formint-pos", {p["slug"] for p in data["pages"]})

    def test_edition_preview_uses_shared_slug_normalization(self):
        """Backend preview links resolve the same normalized edition slugs as Astro."""
        for edition in ("community", "standard", "pro", "cloud"):
            with self.subTest(edition=edition):
                response = self.client.get(f"/products/formint-pos/preview/{edition}/")
                self.assertEqual(response.status_code, 200)
                self.assertIn(edition.title().encode(), response.content)

        self.assertEqual(
            self.client.get("/products/formint-pos/preview/not-an-edition/").status_code,
            404,
        )

    def test_pricing_on_about_and_dedicated_page(self):
        """The transparent-pricing section moved onto About AND lives on /pricing/."""
        response = self.client.get("/about/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'id="pricing"', response.content)
        self.assertIn(b"Simple, transparent pricing", response.content)
        # The dedicated pricing page still has the section (not removed).
        pricing_response = self.client.get("/pricing/")
        self.assertIn(b'id="pricing"', pricing_response.content)

    def test_admin_login_reachable(self):
        response = self.client.get("/admin/login/")
        self.assertEqual(response.status_code, 200)

    def test_allauth_headless_api_reachable(self):
        """The allauth headless API is wired: config + session report the flows."""
        response = self.client.get("/api/auth/browser/v1/config")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], 200)
        self.assertIn("email", payload["data"]["account"]["login_methods"])

        # Anonymous session → 401 with login/signup flows (the modal shows).
        response = self.client.get("/api/auth/browser/v1/auth/session")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["meta"]["is_authenticated"], False)

    def test_allauth_login_flow(self):
        """A real login round-trip: create a user, POST credentials, get a session."""
        from allauth.account.models import EmailAddress

        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.create_user("demo@structa.cloud", "demo@structa.cloud", "pass-1234")
        # Mandatory email verification — the login only passes for a verified address.
        EmailAddress.objects.create(
            user=user, email="demo@structa.cloud", verified=True, primary=True
        )
        response = self.client.post(
            "/api/auth/browser/v1/auth/login",
            data='{"email": "demo@structa.cloud", "password": "pass-1234"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200, response.content[:300])
        payload = response.json()
        self.assertEqual(payload["status"], 200)
        self.assertTrue(payload["data"]["user"]["email"], "demo@structa.cloud")

        # Session now authenticated.
        session = self.client.get("/api/auth/browser/v1/auth/session")
        self.assertEqual(session.status_code, 200)
        self.assertTrue(session.json()["meta"]["is_authenticated"])

        # Logout (DELETE on the session endpoint) clears the session — the
        # response is the anonymous 401 (post-logout user is anonymous).
        logout = self.client.delete("/api/auth/browser/v1/auth/session")
        self.assertEqual(logout.status_code, 401)
        session = self.client.get("/api/auth/browser/v1/auth/session")
        self.assertEqual(session.status_code, 401)

    def test_login_modal_in_page_markup(self):
        """The backend header carries a Log In button wired to the login modal."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Log In", response.content)
        self.assertIn(b"fusion:open-login", response.content)
        self.assertIn(b"api/auth/browser/v1/auth/login", response.content)
        self.assertIn(b"GitHub", response.content)
        self.assertIn(b"Google", response.content)

    def test_login_and_language_controls_in_page_markup(self):
        """The backend road exposes working auth and language controls."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Log In", response.content)
        self.assertIn(b"fusion:open-login", response.content)
        self.assertIn(b"api/auth/browser/v1/auth/login", response.content)
        self.assertIn(b"Change language", response.content)
        self.assertIn(b"data-fusion-i18n=\"nav_login\"", response.content)
        self.assertIn(b"Svenska", response.content)
        self.assertIn(b"/accounts/password/reset/", response.content)
        self.assertIn(b"/learning/dashboard/", response.content)
        # Social buttons (GitHub + Google) are rendered.
        self.assertIn(b"GitHub", response.content)
        self.assertIn(b"Google", response.content)

    def test_english_arabic_content_api_and_fallback(self):
        """Arabic model overlays merge over canonical Wagtail content."""
        from apps.content.models.translations import PageTranslation

        arabic = self.client.get("/apis/pages/about/?lang=ar")
        self.assertEqual(arabic.status_code, 200)
        payload = arabic.json()
        self.assertEqual(payload["language"], "ar")
        self.assertEqual(payload["available_languages"], ["en", "ar"])
        self.assertEqual(payload["title"], "من نحن")
        self.assertEqual(payload["hero"]["title"], "شريكك في المنتج الرقمي")
        # Stats are not translated in the seed and therefore remain available.
        self.assertTrue(payload["stats"])
        self.assertEqual(payload["translation_source"], "model")
        self.assertEqual(payload["translation_language"], "ar")

        english = self.client.get("/apis/pages/about/?lang=en")
        self.assertEqual(english.status_code, 200)
        self.assertEqual(english.json()["language"], "en")
        self.assertEqual(english.json()["title"], AboutPage.objects.first().title)
        self.assertEqual(english.json()["translation_source"], "model")
        self.assertEqual(english.json()["translation_language"], "en")

        languages = self.client.get("/apis/content/languages/").json()
        self.assertEqual(
            [item["code"] for item in languages["languages"]],
            ["en", "ar", "sv", "fr", "de", "es", "pt"],
        )
        self.assertEqual(languages["coverage"]["ar"], PageTranslation.objects.filter(language="ar").count())

    def test_site_languages_are_seeded_and_served(self):
        """The SiteLanguage catalog is seeded idempotently and drives the API."""
        from apps.content.models.languages import SiteLanguage

        # All seven offered languages exist as seeded snippet rows.
        self.assertEqual(SiteLanguage.objects.count(), 7)
        active = list(SiteLanguage.active().values_list("code", flat=True))
        self.assertEqual(active, ["en", "ar", "sv", "fr", "de", "es", "pt"])

        # Swedish is active and carries its native name + flag for the switcher.
        sv = SiteLanguage.objects.get(code="sv")
        self.assertTrue(sv.is_active)
        self.assertEqual(sv.native_name, "Svenska")
        self.assertEqual(sv.flag, "🇸🇪")

        # The API serves the seeded catalog with UI chrome metadata.
        data = self.client.get("/apis/content/languages/").json()
        self.assertEqual(data["ui_languages"], ["en", "ar", "sv", "fr", "de", "es", "pt"])
        by_code = {item["code"]: item for item in data["languages"]}
        self.assertEqual(by_code["ar"]["dir"], "rtl")
        self.assertEqual(by_code["ar"]["native"], "العربية")
        self.assertEqual(by_code["sv"]["flag"], "🇸🇪")

        # Seeding is idempotent — a second run creates no duplicates.
        SeedCommand().handle()
        self.assertEqual(SiteLanguage.objects.count(), 7)

        # Re-running with --force refreshes metadata without adding rows.
        command = SeedCommand()
        command.force = True
        command.handle()
        self.assertEqual(SiteLanguage.objects.count(), 7)
        self.assertEqual(SiteLanguage.objects.get(code="de").flag, "🇩🇪")

    def test_arabic_navigation_uses_page_translation_titles(self):
        """The navigation API translates labels without changing URLs."""
        response = self.client.get("/apis/navigation/?lang=ar")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["language"], "ar")
        labels = {item["href"]: item["label"] for item in response.json()["nav_items"]}
        self.assertEqual(labels.get("/about/"), "من نحن")
        self.assertEqual(labels.get("/products/"), "المنتجات")

    def test_navigation_children_feed_dropdowns(self):
        """Nav items with subpages carry a children list for the hover dropdown."""
        nav = self.client.get("/apis/navigation/").json()
        by_href = {item["href"]: item for item in nav["nav_items"]}

        # About → curated children (team/founder/startup routes).
        about = by_href["/about/"]
        self.assertEqual(
            [c["href"] for c in about["children"]],
            ["/about/team/", "/about/founder/", "/about/startup/"],
        )
        self.assertEqual(about["children"][0]["label"], "Team")

        # Products → live product pages, hidden ones excluded.
        products = by_href["/products/"]
        product_hrefs = [c["href"] for c in products["children"]]
        self.assertIn("/products/formint-pos/", product_hrefs)
        self.assertNotIn("/products/ceptor-ai/", product_hrefs)  # hidden product

        # Services → delivery phases.
        services = by_href["/services/"]
        self.assertTrue(any(c["href"].startswith("/services/phases/") for c in services["children"]))

        # Blog → posts.
        blog = by_href["/blog/"]
        self.assertTrue(blog["children"])

        # Leaf pages (home, pricing, contact) have no dropdown.
        for href in ("/", "/pricing/", "/contact/"):
            self.assertEqual(by_href[href]["children"], [])

    def test_header_renders_dropdown_markup(self):
        """The backend header renders the hover-dropdown affordance for pages with subpages."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"nav-dropdown", response.content)
        self.assertIn(b"@mouseenter=\"openSoon()\"", response.content)
        # About's children appear in the rendered dropdown panel.
        self.assertIn(b"/about/team/", response.content)
        self.assertIn(b"/about/founder/", response.content)
        self.assertIn(b"/about/startup/", response.content)

    def test_translation_model_is_unique_per_page_and_language(self):
        """Wagtail editors cannot accidentally create duplicate locale records."""
        from django.db import IntegrityError
        from apps.content.models.translations import PageTranslation

        page = AboutPage.objects.first()
        existing = PageTranslation.objects.get(page=page, language="en")
        self.assertIsNotNone(existing)
        with self.assertRaises(IntegrityError):
            PageTranslation.objects.create(page=page, language="en")

    def test_fusion_render_mode_both_options(self):
        """Seeded content is served under both content-delivery options."""
        from django.conf import settings as django_settings

        # Option A — “data APIs” (default): the client renders from /apis/* JSON.
        self.assertFalse(django_settings.FUSION_RENDER_FIRST_DEFAULT)
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Digital products, shipped as", response.content)
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

    def test_seeded_buttons_navigate_to_real_pages(self):
        """Every seeded button/link href points at a real page — no dead /#cta
        anchors and no slash-less internal links (APPEND_SLASH is off, so
        "/contact" without a trailing slash would 404)."""
        # The site settings API serves the header CTA pointing at the page.
        settings = self.client.get("/apis/site/settings/").json()
        self.assertEqual(settings["nav_cta_url"], "/contact/")
        self.assertEqual(settings["nav_cta_label"], "Get Started")

        # No dead anchors anywhere on the rendered homepage.
        home = self.client.get("/").content.decode()
        self.assertNotIn("/#cta", home)
        self.assertNotIn('href="/contact"', home)
        self.assertNotIn('href="/about"', home)
        self.assertNotIn('href="/products"', home)
        self.assertNotIn('href="#"', home)
        # Real internal pages are linked with trailing slashes.
        self.assertIn('href="/contact/"', home)
        self.assertIn('href="/about/"', home)

        # The header/footer partials never fall back to /#cta either.
        for path in ("/about/", "/products/"):
            with self.subTest(path=path):
                content = self.client.get(path).content.decode()
                self.assertNotIn("/#cta", content)
                self.assertIn('href="/contact/"', content)

    def test_button_page_chooser_resolves_url_and_title(self):
        """A ButtonBlock whose editor picked a Wagtail page resolves to the
        live page URL — and the page title fills the button label — on both
        the data road (/apis/*) and the render road (Django fragments)."""
        home = HomePage.objects.first()
        target = ContactPage.objects.first()
        self.assertIsNotNone(target)

        home.hero = [
            {
                "type": "hero",
                "value": {
                    "badge": "",
                    "title": home.title,
                    "subtitle": "",
                    # Page chooser only — label + href left empty on purpose.
                    "primary_cta": {"label": "", "href": "", "page": target.pk, "style": "primary"},
                    # Manual external URL — must stay untouched.
                    "secondary_cta": {"label": "View on GitHub", "href": "https://github.com/mammhoud", "style": "secondary"},
                    "trusted_by": "",
                },
            }
        ]
        home.save_revision().publish()

        # Data road: the API resolves the chosen page to its URL + title label.
        data = self.client.get("/apis/pages/home/").json()
        primary = data["hero"]["primary_cta"]
        self.assertEqual(primary["href"], target.url)
        self.assertEqual(primary["label"], target.title)
        self.assertEqual(primary["page"]["url"], target.url)
        self.assertEqual(primary["page"]["title"], target.title)
        # Manual hrefs are preserved verbatim.
        self.assertEqual(data["hero"]["secondary_cta"]["href"], "https://github.com/mammhoud")
        self.assertEqual(data["hero"]["secondary_cta"]["label"], "View on GitHub")

        # Render road: the backend fragment renders the resolved link + title
        # (the anchor is multiline, so a whitespace-tolerant regex is used).
        import re

        fragment = self.client.get("/fragment/pages/home/").content.decode()
        self.assertIn(f'href="{target.url}"', fragment)
        self.assertRegex(
            fragment,
            rf'btn-primary">\s*{re.escape(target.title)}\s*</a>',
        )

    def test_edition_cta_page_resolves_on_pricing_road(self):
        """A cta_page chooser on a product edition resolves to the live URL on
        every edition road: get_editions (pricing API), get_edition (preview),
        and the /apis/pricing/ output — not just the page-data API."""
        import json

        from apps.pages.models import ProductPage

        product = ProductPage.objects.get(slug="formint-pos")
        target = ContactPage.objects.first()
        field = ProductPage._meta.get_field("editions")
        # Round-trip through the field's own JSON (use_json_field wraps every
        # item as {"type": "item", "value": {...}}) instead of mutating
        # StructValue/ListValue in place — those aren't JSON-serializable when
        # save_revision() re-serializes the stream. Patch Community's CTA to
        # point at an internal page, then re-assign the plain JSON form.
        raw = json.loads(field.value_to_string(product))
        block_item = next(i for i in raw if i["type"] == "editions")
        wrapped = next(
            t for t in block_item["value"]["editions"]
            if str(t.get("value", {}).get("name", "")).lower() == "community"
        )
        wrapped["value"].update({"cta_page": target.pk, "cta_label": "", "cta_href": ""})
        product.editions = raw
        product.save_revision().publish()

        # get_editions → the pricing tabs / product cards.
        editions = ProductPage.objects.get(slug="formint-pos").get_editions()
        community = next(e for e in editions if e["name"].lower() == "community")
        self.assertEqual(community["cta_href"], target.url)
        self.assertEqual(community["cta_label"], target.title)

        # get_edition → the per-edition preview road.
        edition = ProductPage.objects.get(slug="formint-pos").get_edition("community")
        self.assertEqual(edition["cta_href"], target.url)
        self.assertEqual(edition["cta_label"], target.title)

        # /apis/pricing/ carries the resolved CTA to the Astro pricing tabs.
        data = self.client.get("/apis/pricing/").json()
        forge = next(p for p in data["products"] if p["slug"] == "formint-pos")
        community_pricing = next(
            e for e in forge["editions"] if e["name"].lower() == "community"
        )
        self.assertEqual(community_pricing["cta_href"], target.url)

        # The rendered preview page (get_edition → product_preview.html) links
        # to the resolved page too — covers the template that consumes the dict.
        import re

        preview = self.client.get("/products/formint-pos/preview/community/").content.decode()
        self.assertRegex(
            preview,
            rf'href="{re.escape(target.url)}"[^>]*>\s*{re.escape(target.title)}\s*</a>',
        )

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
            BlogPage,
            PricingPage,
            ContactPage,
            FaqPage,
            PrivacyPage,
            ProductPage,
            TeamPage,
            FounderPage,
            StartupPage,
            BrandPage,
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
            {"about", "services", "products", "features", "blog", "brand", "pricing", "contact", "faq", "privacy"},
        )

        # Brand page carries the display-mode option (page / modal / both) and
        # is a real Wagtail model — the modal road reads it from the API.
        brand = BrandPage.objects.first()
        self.assertIsNotNone(brand)
        self.assertEqual(brand.display_mode, "both")
        brand_page = self.client.get("/brand/")
        self.assertEqual(brand_page.status_code, 200)
        for child in home.get_children():
            self.assertEqual(child.depth, 3, child.slug)

        # About subpages live one level deeper (/about/team/, /about/founder/,
        # /about/startup/).
        about = AboutPage.objects.first()
        team_slugs = {c.slug for c in about.get_children().live()}
        self.assertEqual(
            team_slugs, {"team", "founder", "startup"},
        )

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
        for slug, hero in (("formint-pos", b"Formints"), ("lms", b"Precis LMS"), ("cms", b"Loop")):
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
        self.assertEqual(self.client.get("/products/formint-pos/").status_code, 200)

    def test_formint_pos_renders_all_editions_with_pricing(self):
        """The POS reference page lists Community · Standard · Pro · Cloud with per-edition pricing."""
        response = self.client.get("/products/formint-pos/")
        self.assertEqual(response.status_code, 200)
        for marker in (b"Community", b"Standard", b"Pro", b"Cloud", b"$0", b"$119", b"$79", b"Custom", b"Models &amp; snippets you can reuse", b"SQLite", b"Rust"):
            self.assertIn(marker, response.content)
        # The Pro edition carries the seeded annual 50% launch offer: badge
        # chip + struck-through original price next to the discounted price.
        self.assertIn(b"/per year", response.content)
        self.assertNotIn(b"$79</span>\n                    <span class=\"font-mono text-xs uppercase tracking-wider text-fu-muted\">/per month", response.content)
        self.assertIn(b"badge-offer", response.content)
        self.assertIn(b"50% off", response.content)
        self.assertIn(b"$158", response.content)
        # The tiered card system renders: outline Community, featured Pro (most
        # shipped), managed Cloud (corner ribbon).
        self.assertIn(b"edition__card--outline", response.content)
        self.assertIn(b"edition__card--featured", response.content)
        self.assertIn(b"most shipped", response.content)
        self.assertIn(b"managed-ribbon", response.content)

    def test_formint_pos_renders_feature_comparison_table(self):
        """The POS reference page ships the full edition-vs-edition comparison table (~33 rows)."""
        response = self.client.get("/products/formint-pos/")
        self.assertEqual(response.status_code, 200)
        for marker in (
            b"Compare editions",
            b"Community vs Standard vs Pro vs Cloud",
            b"React 19 + TypeScript frontend",
            b"High-end interface design",
            b"Food &amp; beverage (F&amp;B) menu support",
            b"Inventory adjustments + stock control",
            b"Kitchen display system",
            b"High-throughput Rust API (60k+ RPS)",
            b"Hosted deployment + managed backups",
        ):
            self.assertIn(marker, response.content)
        # The table body carries per-edition cells with the 4 columns aligned.
        self.assertIn(b"cloud master", response.content)
        # Kitchen display moved from Community → Standard (Community column No).
        kitchen_row = next(
            row for row in self.client.get("/apis/pages/formint-pos/").json().get("comparison", [])[0]["rows"]
            if row["feature"] == "Kitchen display system"
        )
        self.assertEqual(kitchen_row["cells"], ["No", "Yes", "Yes", "Yes"])

        # The API exports the comparison block with columns + rows intact.
        data = self.client.get("/apis/pages/formint-pos/").json()
        pro = next(
            edition for edition in data.get("editions", [])
            if edition.get("name") == "Pro"
        )
        self.assertEqual(pro["period"], "/per year")
        comparison = data.get("comparison", [])
        self.assertTrue(comparison, "products API should carry the comparison block")
        block = comparison[0]
        self.assertEqual(block["columns"], ["Community", "Standard", "Pro", "Cloud"])
        self.assertGreaterEqual(len(block["rows"]), 32)

        # New capability rows are present with the right per-edition cells.
        by_feature = {row["feature"]: row["cells"] for row in block["rows"]}
        self.assertEqual(by_feature["Offline-first mode"], ["Yes", "Yes", "Yes", "Yes"])
        self.assertEqual(by_feature["Loyalty & rewards program"], ["No", "Yes", "Yes", "Yes"])
        self.assertEqual(by_feature["Multi-currency & tax profiles"], ["No", "Yes", "Yes", "Yes"])
        self.assertEqual(by_feature["Custom roles & permissions"], ["No", "Yes", "Yes", "Yes"])
        self.assertEqual(by_feature["Data export (CSV/JSON)"], ["No", "Yes", "Yes", "Yes"])
        self.assertEqual(by_feature["Automatic cloud backups"], ["No", "No", "No", "Yes"])

    def test_formint_pos_renders_roadmap_and_new_snippets(self):
        """The POS reference page ships the product roadmap section + new reference snippets."""
        response = self.client.get("/products/formint-pos/")
        self.assertEqual(response.status_code, 200)
        for marker in (
            b"Product roadmap",
            b"Loyalty &amp; rewards engine",
            b"Multi-currency &amp; tax profiles",
            b"Automatic cloud backups",
            b"Diesel migration (up.sql)",
            b"Tauri command (invoice PDF)",
        ):
            self.assertIn(marker, response.content)
        # The API carries the roadmap items under the flattened features list.
        data = self.client.get("/apis/pages/formint-pos/").json()
        features = data.get("features", [])
        self.assertTrue(any(f.get("title") == "Loyalty & rewards engine" for f in features))
        snippets = data.get("snippets", [])
        self.assertTrue(any(s.get("title") == "Diesel migration (up.sql)" for s in snippets))
        self.assertTrue(any(s.get("title") == "Tauri command (invoice PDF)" for s in snippets))

    def test_products_lists_product_pages(self):
        """/products/ lists the product pages (cards) alongside the project grid."""
        response = self.client.get("/products/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Projects in this repo", response.content)
        for href in (b"/products/formint-pos/", b"/products/lms/", b"/products/cms/"):
            self.assertIn(href, response.content)

        data = self.client.get("/apis/pages/products/").json()
        self.assertTrue(any(p["slug"] == "formint-pos" for p in data["products"]), data.get("products"))

    def test_services_carries_offering_and_process(self):
        """Services renders the three service lines + the 'build as you go' process."""
        response = self.client.get("/services/")
        self.assertEqual(response.status_code, 200)
        for marker in (
            b"Build for the market you serve",
            b"Market-ready websites",
            b"Digital product delivery",
            b"Improve what already works",
            b"A measured path to launch",
            b"Discover",
            b"Ship &amp; grow",  # Wagtail escapes the ampersand in template output
        ):
            self.assertIn(marker, response.content)

    def test_products_carries_merged_catalog(self):
        """Products renders the merged catalog: renamed products as cards, no
        removed (django-bolt) or hidden (ceptor-ai) products."""
        response = self.client.get("/products/")
        self.assertEqual(response.status_code, 200)
        for marker in (
            b"Projects in this repo",
            b"Formints",
            b"Precis LMS",
            b"Loop",
            b"Syntara",
            b"vResume",
            b"Browse the monorepo on GitHub",
        ):
            self.assertIn(marker, response.content)
        for marker in (b"django-bolt", b"/products/ceptor-ai/", b"The product line"):
            self.assertNotIn(marker, response.content)

    def test_brand_page_renders_identity_boards(self):
        """The /brand/ page renders one identity board per live product with
        the brandkit story (essence, metaphor, construction, voice) and each
        product's own constructed mark (data-brand chip)."""
        response = self.client.get("/brand/")
        self.assertEqual(response.status_code, 200)
        for marker in (
            b"One family, five marks",
            b"The till, made trustworthy.",
            b"Learning, precisely.",
            b"Content, composed.",
            b"Chat, routed around your brand.",
            b"Your career, on the record.",
        ):
            self.assertIn(marker, response.content)
        # Every brand mark renders with its own data-brand chip.
        for data_brand in (b"data-brand=\"formints\"", b"data-brand=\"precis\"", b"data-brand=\"loop\"", b"data-brand=\"syntara\"", b"data-brand=\"vresume\""):
            self.assertIn(data_brand, response.content)

    def test_product_logo_styles_assigned(self):
        """Each seeded product carries its own constructed logo style — the
        family system, not shared generic marks."""
        expected = {
            "formint-pos": "crest",
            "lms": "ribbon",
            "cms": "isometric",
            "cypercloud": "orbit",
            "vresume": "ascent",
        }
        for slug, style in expected.items():
            with self.subTest(slug=slug):
                page = ProductPage.objects.filter(slug=slug).first()
                self.assertIsNotNone(page, slug)
                self.assertEqual(page.logo_style, style)

    def test_brand_in_footer_not_nav(self):
        """Brand moved to footer-only — reachable from the footer, never the header nav."""
        nav = self.client.get("/apis/navigation/").json()
        nav_labels = [item["label"] for item in nav["nav_items"]]
        self.assertNotIn("Brand", nav_labels)

        # The footer still links to /brand/ on every page.
        for path in ("/", "/about/", "/products/"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertIn(b'href="/brand/"', response.content)
                self.assertIn(b'id="newsletter-feedback"', response.content)

    def test_allauth_server_pages_render(self):
        """Full allauth pages render at /accounts/* with the branded layout."""
        from django.contrib.auth import get_user_model

        # Entrance pages are public.
        pages = (
            "/accounts/login/",
            "/accounts/signup/",
            "/accounts/password/reset/",
        )
        for path in pages:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200, path)
                self.assertIn(b"Structa Cloud", response.content)
                self.assertIn(b"auth-card", response.content)

        # Manage pages require an authenticated session (302 → login).
        User = get_user_model()
        user = User.objects.create_user("manage@structa.cloud", "manage@structa.cloud", "pass-1234")
        self.client.force_login(user)
        for path in (
            "/accounts/password/change/",
            "/accounts/email/",
            "/accounts/logout/",
        ):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200, path)
                self.assertIn(b"auth-card", response.content)

        # Default (non-overridden) allauth templates — e.g. reauthenticate — keep
        # the branded card shell too, via the auth_inner/content dual bridge.
        response = self.client.get("/accounts/reauthenticate/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"auth-card", response.content)
        self.assertIn(b"back to structa.cloud", response.content)

    def test_allauth_email_confirmation_flow(self):
        """Signup renders the confirmation page + branded email templates render."""
        from types import SimpleNamespace

        from allauth.account.models import EmailAddress

        from django.contrib.auth import get_user_model
        from django.core import mail
        from django.template.loader import render_to_string

        User = get_user_model()
        user = User.objects.create_user("confirm@structa.cloud", "confirm@structa.cloud", "pass-1234")
        site = SimpleNamespace(name="Structa Cloud", domain="structa.cloud")

        email_ctx = {
            "activate_url": "http://testserver/confirm/abc",
            "user": user,
            "current_site": site,
            "key": "abc",
        }

        # The email templates (branded HTML + subject) render for confirmation.
        subject = render_to_string("account/email/email_confirmation_subject.txt")
        self.assertIn("Structa Cloud", subject)
        body = render_to_string("account/email/email_confirmation_message.html", email_ctx)
        self.assertIn("Confirm email address", body)
        self.assertIn("http://testserver/confirm/abc", body)

        # Password reset email template renders the branded CTA.
        reset = render_to_string(
            "account/email/password_reset_key_message.html",
            {"password_reset_url": "http://testserver/reset/xyz", "user": user, "current_site": site},
        )
        self.assertIn("Reset password", reset)
        self.assertIn("http://testserver/reset/xyz", reset)

        # A real password reset request sends a branded email (console backend → outbox).
        # Mandatory verification: the reset flow needs a confirmed address on record.
        reset_user = User.objects.create_user("reset@structa.cloud", "reset@structa.cloud", "pass-1234")
        EmailAddress.objects.create(
            user=reset_user, email="reset@structa.cloud", verified=True, primary=True
        )
        response = self.client.post(
            "/accounts/password/reset/",
            {"email": "reset@structa.cloud"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(mail.outbox)
        self.assertIn("Structa Cloud", mail.outbox[0].subject)

    def test_newsletter_subscribe_persists(self):
        """POST /api/newsletter/subscribe/ persists a NewsletterSubscriber row."""
        from apps.content.models.newsletter import NewsletterSubscriber

        # HTMX request → HTML fragment.
        response = self.client.post(
            "/api/newsletter/subscribe/",
            data={"email": "news@structa.cloud", "source": "footer"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Subscribed", response.content)
        self.assertTrue(NewsletterSubscriber.objects.filter(email="news@structa.cloud").exists())

        # JSON request → JSON success; duplicate email upserts (no new row).
        response = self.client.post(
            "/api/newsletter/subscribe/",
            data='{"email": "news@structa.cloud", "source": "contact"}',
            content_type="application/json",
        )
        self.assertJSONEqual(response.content, {"success": True, "message": "Subscribed! We'll send updates to news@structa.cloud."})
        self.assertEqual(NewsletterSubscriber.objects.filter(email="news@structa.cloud").count(), 1)
        sub = NewsletterSubscriber.objects.get(email="news@structa.cloud")
        self.assertTrue(sub.is_active)

        # Invalid email → 400, nothing persisted.
        response = self.client.post(
            "/api/newsletter/subscribe/",
            data={"email": "not-an-email"},
        )
        self.assertEqual(response.status_code, 400)

        # Status endpoint reports the active count.
        status = self.client.get("/api/newsletter/status/")
        self.assertEqual(status.json()["subscriber_count"], 1)

    def test_brand_api_and_modal_triggers(self):
        """/apis/brand/ serves the boards (page + modal share one source) and
        product pages carry the [data-open-brand] modal triggers + the modal
        markup (fusion:open-brand listener, marks map)."""
        data = self.client.get("/apis/brand/").json()
        boards = data.get("boards", [])
        slugs = [b["slug"] for b in boards]
        self.assertEqual(slugs, ["formint-pos", "lms", "cms", "cypercloud", "vresume"])
        board = boards[0]
        self.assertEqual(board["name"], "Formints")
        self.assertEqual(board["mark"], "crest")
        self.assertTrue(board["swatches"])
        self.assertIn("essence", board)
        self.assertIn("metaphor", board)
        # display_mode is exposed on the page API (BrandPage is a real model).
        page_data = self.client.get("/apis/pages/brand/").json()
        self.assertEqual(page_data.get("display_mode"), "both")

        # Product pages render the modal trigger + the shared brand modal.
        response = self.client.get("/products/formint-pos/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'data-open-brand="formint-pos"', response.content)
        self.assertIn(b"fusion:open-brand", response.content)
        self.assertIn(b"/apis/brand/", response.content)

        # The products listing carries a trigger per card.
        listing = self.client.get("/products/")
        self.assertEqual(listing.status_code, 200)
        for slug in ("formint-pos", "lms", "cms", "cypercloud", "vresume"):
            self.assertIn(f'data-open-brand="{slug}"'.encode(), listing.content)
        # Hidden products get no trigger.
        self.assertNotIn(b'data-open-brand="ceptor-ai"', listing.content)

    def test_blog_renders_post_grid(self):
        """Blog renders the seeded post grid (hero + cards + cta)."""
        response = self.client.get("/blog/")
        self.assertEqual(response.status_code, 200)
        for marker in (
            b"Ideas for the next release",
            b"A fast first visit is a product decision",
            b"Designing bilingual journeys without duplication",
            b"monorepo-six-products",
            b"A useful first release beats a noisy roadmap",
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

    def test_pricing_renders_product_tabs_and_faq(self):
        """Pricing renders the tabbed per-product editions and links out to the FAQ."""
        response = self.client.get("/pricing/")
        self.assertEqual(response.status_code, 200)
        for marker in (
            b"Pick a product, see its editions",
            b"Formints",
            b"Precis LMS",
            b"Loop",
            b"Syntara",
            b"vResume",
            b"Read the FAQ",
        ):
            self.assertIn(marker, response.content)
        # The generic FAQ moved to /faq/ — pricing just links to it.
        self.assertNotIn(b"Frequently asked questions", response.content)
        # No legacy generic tiers; hidden products get no tab and no link.
        self.assertNotIn(b"Starter", response.content)
        self.assertNotIn(b"/products/ceptor-ai/", response.content)
        # The API drives the tabs.
        data = self.client.get("/apis/pricing/").json()
        slugs = [p["slug"] for p in data["products"]]
        self.assertEqual(
            slugs, ["formint-pos", "lms", "cms", "cypercloud", "vresume"], slugs
        )

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


class NewsletterEmailAndSyncTestCase(TestCase):
    """Welcome email, provider sync, and the Wagtail broadcast action.

    Uses the real console→locmem mail backend (``mail.outbox``), so a fresh
    subscription through the API is asserted end-to-end. No page seeding is
    needed — subscribers are created directly.
    """

    def _subscribe(self, email, source="footer", **extra):
        return self.client.post(
            "/api/newsletter/subscribe/",
            {"email": email, "source": source},
            **extra,
        )

    def test_welcome_email_sent_on_fresh_subscribe(self):
        """A fresh signup gets the branded welcome email + a welcome_sent_at stamp."""
        from django.core import mail

        from apps.content.models.newsletter import NewsletterSubscriber

        response = self._subscribe("welcome@structa.cloud")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, ["welcome@structa.cloud"])
        self.assertIn("Welcome to Structa Cloud", message.subject)
        # HTML part is the branded shell; plain part rides along.
        html = message.alternatives[0][0]
        self.assertIn("You're on the list", html)
        self.assertIn("Formints", html)
        self.assertIn("Browse the products", html)

        subscriber = NewsletterSubscriber.objects.get(email="welcome@structa.cloud")
        self.assertIsNotNone(subscriber.welcome_sent_at)
        # No provider configured in tests → no sync stamp.
        self.assertIsNone(subscriber.provider_synced_at)

    def test_no_welcome_email_on_resubscribe(self):
        """Re-subscribing (upsert) does not re-send the welcome email."""
        from django.core import mail

        self._subscribe("again@structa.cloud")
        self._subscribe("again@structa.cloud", source="contact")
        self.assertEqual(len(mail.outbox), 1)

    def test_broadcast_sends_to_active_subscribers_only(self):
        """The broadcast service emails active subscribers, not paused ones."""
        from django.core import mail

        from apps.content.models.newsletter import NewsletterSubscriber
        from apps.content.services.newsletter import send_newsletter_broadcast

        for index, active in enumerate([True, True, False]):
            NewsletterSubscriber.objects.create(email=f"b{index}@structa.cloud", is_active=active)

        sent = send_newsletter_broadcast("Product update", "Here is the news.")
        self.assertEqual(sent, 2)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual({m.to[0] for m in mail.outbox}, {"b0@structa.cloud", "b1@structa.cloud"})
        html = mail.outbox[0].alternatives[0][0]
        self.assertIn("Here is the news.", html)

        # include_inactive widens to the whole list (including paused).
        sent = send_newsletter_broadcast("All", "Everyone.", include_inactive=True)
        self.assertEqual(sent, 3)

    def test_broadcast_admin_view_requires_staff(self):
        """The broadcast page redirects anonymous users to the Wagtail admin login."""
        from django.contrib.auth import get_user_model

        response = self.client.get("/admin/newsletter/broadcast/")
        self.assertEqual(response.status_code, 302)

        staff = get_user_model().objects.create_user(
            "staff@structa.cloud", "staff@structa.cloud", "pass-1234", is_staff=True,
        )
        self.client.force_login(staff)
        response = self.client.get("/admin/newsletter/broadcast/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Email subscribers")
        self.assertContains(response, "active subscriber")

    def test_broadcast_admin_view_sends(self):
        """A staff POST through the Wagtail action emails every active subscriber."""
        from django.contrib.auth import get_user_model
        from django.core import mail

        from apps.content.models.newsletter import NewsletterSubscriber

        NewsletterSubscriber.objects.create(email="target@structa.cloud")
        staff = get_user_model().objects.create_user(
            "staff2@structa.cloud", "staff2@structa.cloud", "pass-1234", is_staff=True,
        )
        self.client.force_login(staff)

        response = self.client.post(
            "/admin/newsletter/broadcast/",
            {"subject": "Product update", "message": "Here is the news."},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["target@structa.cloud"])
        self.assertIn("Here is the news.", mail.outbox[0].alternatives[0][0])

    def test_snippet_admin_lists_subscribers_with_broadcast_button(self):
        """The snippet index renders the subscriber list + the broadcast header button."""
        from django.contrib.auth import get_user_model
        from django.urls import reverse

        from apps.content.models.newsletter import NewsletterSubscriber

        from django.contrib.auth.models import Permission

        NewsletterSubscriber.objects.create(email="listed@structa.cloud")
        staff = get_user_model().objects.create_user(
            "staff3@structa.cloud", "staff3@structa.cloud", "pass-1234", is_staff=True,
        )
        # Programmatic staff users need admin access + the model's change
        # permission to reach the snippet list.
        staff.user_permissions.add(Permission.objects.get(codename="access_admin"))
        change_perm = Permission.objects.get(
            content_type__app_label="content", codename="change_newslettersubscriber",
        )
        staff.user_permissions.add(change_perm)
        self.client.force_login(staff)

        url = reverse("wagtailsnippets_content_newslettersubscriber:list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "listed@structa.cloud")
        self.assertContains(response, "Email subscribers")
        self.assertContains(response, "/admin/newsletter/broadcast/")

    def test_mailchimp_sync_on_subscribe(self):
        """With a provider configured, subscribing pushes the row to Mailchimp."""
        from unittest.mock import patch

        from apps.content.models.newsletter import NewsletterSubscriber

        with patch("urllib.request.urlopen") as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = b"{}"
            with self.settings(
                NEWSLETTER_PROVIDER="mailchimp",
                NEWSLETTER_MAILCHIMP_API_KEY="test-api-key",
                NEWSLETTER_MAILCHIMP_LIST_ID="list-1",
            ):
                response = self._subscribe("mc@structa.cloud")

        self.assertEqual(response.status_code, 200)
        mock_open.assert_called_once()
        request = mock_open.call_args.args[0]
        self.assertIn("api.mailchimp.com/3.0/lists/list-1/members/", request.full_url)
        # Mailchimp authenticates with HTTP Basic where the username IS the key.
        import base64
        auth = request.headers["Authorization"]
        self.assertTrue(auth.startswith("Basic "))
        self.assertIn("test-api-key", base64.b64decode(auth.split(" ", 1)[1]).decode())

        subscriber = NewsletterSubscriber.objects.get(email="mc@structa.cloud")
        self.assertIsNotNone(subscriber.provider_synced_at)

    def test_provider_sync_skipped_when_unconfigured(self):
        """Without a provider, subscribing is a no-op for sync (no network)."""
        from apps.content.models.newsletter import NewsletterSubscriber

        self._subscribe("nosync@structa.cloud")
        subscriber = NewsletterSubscriber.objects.get(email="nosync@structa.cloud")
        self.assertIsNone(subscriber.provider_synced_at)

    def test_sync_management_command_reports_when_unconfigured(self):
        """The bulk export command explains when no provider is configured."""
        from io import StringIO

        from django.core.management import call_command

        out = StringIO()
        call_command("sync_newsletter_provider", stdout=out, stderr=out)
        self.assertIn("No NEWSLETTER_PROVIDER configured", out.getvalue())


class MfaAuthTestCase(TestCase):
    """Branded two-factor + passkey journey on top of mandatory email verification.

    Covers the whole MFA auth path: unverified logins are blocked, TOTP can be
    activated from the branded page, subsequent logins hit the branded 2FA
    challenge, and every manage page (index, totp, webauthn, recovery codes,
    reauthenticate) renders inside the auth-card shell with the fido2 wiring
    intact.
    """

    def _create_user(self, email, verified=True):
        """Create a user with an optional verified primary email address."""
        from allauth.account.models import EmailAddress

        from django.contrib.auth import get_user_model

        user = get_user_model().objects.create_user(email, email, "pass-1234")
        if verified:
            EmailAddress.objects.create(
                user=user, email=email, verified=True, primary=True
            )
        return user

    def _totp_code(self, secret):
        """RFC-6238 TOTP code for the current time step (allauth's own primitives)."""
        import time

        from allauth.mfa import app_settings as mfa_settings
        from allauth.mfa.totp.internal.auth import format_hotp_value, hotp_value

        counter = int(time.time()) // mfa_settings.TOTP_PERIOD
        return format_hotp_value(hotp_value(secret, counter))

    def test_unverified_login_blocked(self):
        """Mandatory verification: an unverified email cannot log in via the API."""
        self._create_user("unverified@structa.cloud", verified=False)

        response = self.client.post(
            "/api/auth/browser/v1/auth/login",
            data='{"email": "unverified@structa.cloud", "password": "pass-1234"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401, response.content[:300])
        flows = response.json()["data"]["flows"]
        self.assertIn(
            {"id": "verify_email", "is_pending": True},
            flows,
        )
        # The session stays anonymous.
        session = self.client.get("/api/auth/browser/v1/auth/session")
        self.assertEqual(session.status_code, 401)

        # The server-rendered “verification sent” page is branded too.
        response = self.client.get("/accounts/confirm-email/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "auth-card")

    def test_totp_activate_and_2fa_challenge_full_flow(self):
        """Activate TOTP from the branded page, then complete a 2FA login."""
        from allauth.mfa.models import Authenticator

        user = self._create_user("totp@structa.cloud")
        # A real login marks the session as recently authenticated, which the
        # TOTP activation view requires (force_login would bounce to reauth).
        self.client.post(
            "/accounts/login/",
            {"login": "totp@structa.cloud", "password": "pass-1234"},
        )

        # The branded activation page carries the QR + secret.
        response = self.client.get("/accounts/2fa/totp/activate/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "auth-card")
        self.assertContains(response, "Authenticator secret")
        secret = response.context["form"].secret

        response = self.client.post(
            "/accounts/2fa/totp/activate/", {"code": self._totp_code(secret)}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Authenticator.objects.filter(user=user, type="totp").exists())
        self.client.logout()

        # The next login is routed through the branded 2FA challenge.
        response = self.client.post(
            "/accounts/login/",
            {"login": "totp@structa.cloud", "password": "pass-1234"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/accounts/2fa/authenticate/")

        response = self.client.get("/accounts/2fa/authenticate/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Two-factor authentication")
        self.assertContains(response, "auth-card")

        response = self.client.post(
            "/accounts/2fa/authenticate/", {"code": self._totp_code(secret)}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/")

        session = self.client.get("/api/auth/browser/v1/auth/session")
        self.assertEqual(session.status_code, 200)
        self.assertTrue(session.json()["meta"]["is_authenticated"])

    def test_branded_mfa_manage_pages_render(self):
        """Every 2FA/passkey manage page renders in the branded auth card."""
        user = self._create_user("mfa@structa.cloud")
        # A real login marks the session as recently authenticated, which the
        # WebAuthn add view requires (force_login would redirect to reauth).
        self.client.post(
            "/accounts/login/",
            {"login": "mfa@structa.cloud", "password": "pass-1234"},
        )
        for path in (
            "/accounts/2fa/",
            "/accounts/2fa/totp/activate/",
            "/accounts/2fa/webauthn/add/",
            "/accounts/2fa/recovery-codes/generate/",
        ):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200, path)
                self.assertContains(response, "auth-card")

        # The passkey add page keeps the fido2 JS wiring + onload config.
        response = self.client.get("/accounts/2fa/webauthn/add/")
        self.assertContains(response, "mfa_webauthn_add")
        self.assertContains(response, "webauthn.js")
        self.assertContains(response, "js_data")

        # The security hub links to the 2FA management page.
        response = self.client.get("/accounts/password/change/")
        self.assertContains(response, "/accounts/2fa/")

    def test_reauthenticate_redirects_to_branded_confirm_access(self):
        """Sessions without a recent auth record must reauthenticate before
        adding keys — and the reauthenticate page renders branded."""
        from allauth.account.internal.flows.login import AUTHENTICATION_METHODS_SESSION_KEY

        user = self._create_user("reauth@structa.cloud")
        self.client.post(
            "/accounts/login/",
            {"login": "reauth@structa.cloud", "password": "pass-1234"},
        )

        # Activate TOTP in this session, then drop the auth record so the
        # next sensitive action demands reauthentication.
        response = self.client.get("/accounts/2fa/totp/activate/")
        secret = response.context["form"].secret
        self.client.post(
            "/accounts/2fa/totp/activate/", {"code": self._totp_code(secret)}
        )
        session = self.client.session
        session.pop(AUTHENTICATION_METHODS_SESSION_KEY, None)
        session.save()

        # Adding a key now demands reauthentication.
        response = self.client.get("/accounts/2fa/webauthn/add/")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response["Location"].startswith("/accounts/reauthenticate/"))

        response = self.client.get("/accounts/reauthenticate/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Confirm access")
        self.assertContains(response, "auth-card")

    def test_webauthn_list_renders_with_keys(self):
        """The security-key list shows a created key with the passkey badge."""
        from allauth.mfa.models import Authenticator

        user = self._create_user("keys@structa.cloud")
        Authenticator.objects.create(
            user=user,
            type="webauthn",
            data={
                "credential": {
                    "id": "abc123",
                    "public_key": "def456",
                    "sign_count": 0,
                },
                "name": "MacBook Touch ID",
            },
        )
        self.client.force_login(user)

        response = self.client.get("/accounts/2fa/webauthn/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Security keys")
        self.assertContains(response, "MacBook Touch ID")
        self.assertContains(response, "auth-card")
