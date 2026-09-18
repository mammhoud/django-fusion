"""Tests for the Wagtail landing pages — seed command + /apis/pages/ JSON road.

The public landing is data-driven: Astro fetches /apis/pages/<slug>/ and
renders. These tests pin the seed (idempotent, all five pages) and the JSON
contract the frontend consumes (hero, sections, section heads, legal body).
"""
from __future__ import annotations

import json

from django.core.management import call_command
from django.test import TestCase
from wagtail.models import Page, Site

from apps.pages.models import FaqPage, HomePage, PricingPage, PrivacyPage, TermsPage


class SeedPagesCommandTests(TestCase):
    def test_seed_creates_site_and_all_pages(self):
        call_command("seed_pages")

        self.assertEqual(HomePage.objects.count(), 1)
        home = HomePage.objects.first()
        self.assertEqual(home.slug, "home")
        self.assertTrue(home.live)
        # Children of the home page.
        child_slugs = set(home.get_children().values_list("slug", flat=True))
        self.assertEqual(child_slugs, {"pricing", "faq", "privacy", "terms"})
        for model in (PricingPage, FaqPage, PrivacyPage, TermsPage):
            self.assertEqual(model.objects.filter(live=True).count(), 1)
        site = Site.objects.get(is_default_site=True)
        self.assertEqual(site.root_page_id, home.pk)
        self.assertEqual(site.site_name, "Loop CRM")

    def test_seed_is_idempotent(self):
        call_command("seed_pages")
        call_command("seed_pages")
        self.assertEqual(HomePage.objects.count(), 1)
        self.assertEqual(PricingPage.objects.count(), 1)
        self.assertEqual(FaqPage.objects.count(), 1)
        self.assertEqual(PrivacyPage.objects.count(), 1)
        self.assertEqual(TermsPage.objects.count(), 1)

    def test_seed_populates_home_content(self):
        call_command("seed_pages")
        home = HomePage.objects.first()
        self.assertTrue(home.hero)
        self.assertTrue(home.dna)
        self.assertTrue(home.features)
        self.assertTrue(home.steps)
        self.assertTrue(home.pricing)
        self.assertTrue(home.faq)
        self.assertTrue(home.cta)


class PageApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_pages")

    def test_home_payload_contract(self):
        resp = self.client.get("/apis/pages/home/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["slug"], "home")
        self.assertEqual(data["type"], "HomePage")
        # Hero + CTA resolve to plain hrefs.
        self.assertEqual(data["hero"]["primary_cta"]["href"], "/accounts/signup/")
        self.assertEqual(data["hero"]["primary_cta"]["label"], "Start free")
        self.assertIn("cta", data)
        # Section stacks + their heads.
        self.assertEqual(len(data["dna"]), 3)
        self.assertEqual(len(data["features"]), 3)
        self.assertEqual(data["features_head"]["title"], "Three modules, one source of truth")
        self.assertEqual(data["features"][0]["href"], "/crm/")
        self.assertEqual(len(data["steps"]), 4)
        self.assertEqual(len(data["pricing"]), 3)
        self.assertTrue(data["pricing"][1]["featured"])
        self.assertEqual(data["pricing_head"]["title"], "Start free, scale when the loop is proven")
        self.assertEqual(len(data["faq"]), 5)

    def test_pricing_page_payload(self):
        resp = self.client.get("/apis/pages/pricing/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["type"], "PricingPage")
        self.assertIn("pricing", data)
        self.assertIn("faq", data)

    def test_legal_pages_carry_body(self):
        for slug in ("privacy", "terms"):
            resp = self.client.get(f"/apis/pages/{slug}/")
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertTrue(data["body"].startswith("<p>"))
            # No license grant in the legal copy.
            self.assertNotIn("AGPL", data["body"])
            self.assertNotIn("licen", data["body"].lower())

    def test_unknown_slug_404(self):
        resp = self.client.get("/apis/pages/does-not-exist/")
        self.assertEqual(resp.status_code, 404)

    def test_page_list(self):
        resp = self.client.get("/apis/pages/")
        self.assertEqual(resp.status_code, 200)
        slugs = {p["slug"] for p in resp.json()["pages"]}
        self.assertEqual(slugs, {"home", "pricing", "faq", "privacy", "terms"})

    def test_no_hardcoded_license_claims_in_payloads(self):
        """The seeded copy must never reintroduce license claims."""
        for slug in ("home", "pricing", "faq", "privacy", "terms"):
            payload = json.dumps(self.client.get(f"/apis/pages/{slug}/").json()).lower()
            self.assertNotIn("agpl", payload)
            self.assertNotIn("license", payload)
