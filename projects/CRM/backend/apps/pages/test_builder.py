"""Tests for the landing builder reference mount (apps.pages.BuilderPage).

Covers the seed command, the /apis/builder/ JSON road, dynamic template
field resolution, theme attributes, server-side rendering, and preview
issue reporting — the full assembly layer composed from Wagtail + the
theme engine + dynamic template fields.
"""

from __future__ import annotations

from django.core.management import call_command
from django.test import TestCase

from apps.pages.models import BuilderPage


class SeedBuilderCommandTests(TestCase):
    def test_seed_creates_builder_pages(self):
        call_command("seed_pages")
        call_command("seed_builder")
        self.assertEqual(BuilderPage.objects.count(), 2)
        slugs = set(BuilderPage.objects.values_list("slug", flat=True))
        self.assertEqual(slugs, {"saas-launch", "dark-contrast"})

    def test_seed_is_idempotent(self):
        call_command("seed_pages")
        call_command("seed_builder")
        call_command("seed_builder")
        self.assertEqual(BuilderPage.objects.count(), 2)


class BuilderApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_pages")
        call_command("seed_builder")

    def test_page_list(self):
        resp = self.client.get("/apis/builder/")
        self.assertEqual(resp.status_code, 200)
        pages = {p["slug"]: p for p in resp.json()["pages"]}
        self.assertEqual(set(pages), {"saas-launch", "dark-contrast"})
        self.assertEqual(pages["saas-launch"]["theme"], "saas")
        self.assertEqual(pages["saas-launch"]["brand"], "loop")
        self.assertFalse(pages["saas-launch"]["dark_mode"])
        self.assertTrue(pages["dark-contrast"]["dark_mode"])

    def test_page_data_resolves_dynamic_fields(self):
        resp = self.client.get("/apis/builder/saas-launch/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["theme"], "saas")
        self.assertEqual(data["brand"], "loop")
        hero = data["sections"][0]
        self.assertEqual(hero["type"], "hero")
        self.assertEqual(hero["title"], "Welcome to Structa Cloud")
        self.assertEqual(hero["accent"], "Loop CRM")
        pricing = next(s for s in data["sections"] if s["type"] == "pricing")
        self.assertEqual(pricing["tiers"][1]["price"], "$29")

    def test_page_data_truncate_filter(self):
        resp = self.client.get("/apis/builder/saas-launch/")
        stats = next(s for s in resp.json()["sections"] if s["type"] == "stats")
        self.assertEqual(stats["stats"][2]["value"], "Struc…")

    def test_page_data_theme_state(self):
        resp = self.client.get("/apis/builder/dark-contrast/")
        data = resp.json()
        self.assertEqual(data["theme"], "dark")
        self.assertTrue(data["dark_mode"])
        self.assertEqual(data["brand"], "")

    def test_unknown_slug_404(self):
        resp = self.client.get("/apis/builder/does-not-exist/")
        self.assertEqual(resp.status_code, 404)


class BuilderRendererTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_pages")
        call_command("seed_builder")

    def test_theme_attrs(self):
        page = BuilderPage.objects.get(slug="saas-launch").specific
        attrs = page.get_builder_renderer().theme_attrs()
        self.assertIn('data-theme="saas"', attrs)
        self.assertIn('data-brand="loop"', attrs)
        self.assertNotIn("class=", attrs)

    def test_dark_theme_attrs(self):
        page = BuilderPage.objects.get(slug="dark-contrast").specific
        attrs = page.get_builder_renderer().theme_attrs()
        self.assertIn('data-theme="dark"', attrs)
        self.assertIn('class="dark"', attrs)

    def test_sections_html_renders_components(self):
        page = BuilderPage.objects.get(slug="saas-launch").specific
        html = page.get_builder_renderer().sections_html()
        for component in ("fu-btn", "fu-card", "fu-pricing", "fu-accordion", "fu-counter", "fu-section-title"):
            self.assertIn(component, html)
        self.assertIn("Welcome to Structa Cloud", html)

    def test_unresolved_dynamic_field_reported(self):
        page = BuilderPage.objects.get(slug="saas-launch").specific
        page.template_context = {}
        page.save()
        renderer = page.get_builder_renderer()
        issues = renderer.preview_issues()
        unresolved = [issue for issue in issues if issue["code"] == "unresolved"]
        self.assertTrue(unresolved)
        self.assertGreaterEqual(renderer.unresolved_count, 1)
        self.assertTrue(renderer.has_unresolved())

    def test_all_resolved_when_context_present(self):
        page = BuilderPage.objects.get(slug="saas-launch").specific
        renderer = page.get_builder_renderer()
        self.assertFalse(renderer.has_unresolved())

    def test_href_sanitized(self):
        page = BuilderPage.objects.get(slug="saas-launch").specific
        # A dynamic href backed by a malicious context value must be sanitized.
        page.template_context = {"company": {"name": "X"}, "evil": "javascript:alert(1)"}
        page.save()
        renderer = page.get_builder_renderer()
        # Force a dynamic href through the resolver.
        from django_fusion.builder.rendering import _resolve_dynamic
        from django_fusion.template_fields import TemplateFieldEngine

        resolved = _resolve_dynamic(
            {"href": "{{ evil }}"},
            TemplateFieldEngine(),
            {"evil": "javascript:alert(1)"},
        )
        self.assertEqual(resolved["href"], "#")
        # The rendered payload never contains a live javascript: href.
        payload = renderer.to_dict()
        self.assertNotIn("javascript:", str(payload["sections"]))


class BuilderPageRenderingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_pages")
        call_command("seed_builder")

    def test_page_serves_html_with_theme_attrs(self):
        page = BuilderPage.objects.get(slug="saas-launch").specific
        resp = self.client.get(page.url)
        self.assertEqual(resp.status_code, 200)
        body = resp.content.decode()
        self.assertIn('data-theme="saas"', body)
        self.assertIn('data-brand="loop"', body)
        self.assertIn("fu-builder", body)
        self.assertIn("Welcome to Structa Cloud", body)

    def test_dark_page_serves_dark_class(self):
        page = BuilderPage.objects.get(slug="dark-contrast").specific
        resp = self.client.get(page.url)
        self.assertEqual(resp.status_code, 200)
        body = resp.content.decode()
        self.assertIn('data-theme="dark"', body)
        self.assertIn('class="dark"', body)
