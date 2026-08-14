"""Focused tests for the Product snippet catalog API (/api/products/).

The catalog-of-record is the editor-managed ``Product`` snippet carrying the
same language + unified-currency contract as courses. These tests verify the
language filter, unified currency default, and that language variants point
at their canonical detail page through ``detail_slug``.
"""
from django.test import Client, TestCase

from apps.content.models.products import Product


class ProductsApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.en = Product.objects.create(
            title="django-fusion",
            slug="django-fusion",
            category="library",
            language="en",
            price="0.00",
            is_published=True,
        )
        self.ar = Product.objects.create(
            title="جانغو-فيوجن",
            slug="django-fusion-ar",
            detail_slug="django-fusion",
            category="library",
            language="ar",
            price="0.00",
            is_published=True,
        )
        self.hidden = Product.objects.create(
            title="Draft",
            slug="draft-product",
            category="application",
            language="en",
            price="9.99",
            is_published=False,
        )

    def test_list_returns_published_products_with_currency(self):
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["pagination"]["total"], 2)
        slugs = {item["slug"] for item in data["data"]}
        self.assertEqual(slugs, {"django-fusion", "django-fusion-ar"})
        for item in data["data"]:
            self.assertEqual(item["currency"], "USD")

    def test_language_filter(self):
        response = self.client.get("/api/products/?language=ar")
        data = response.json()
        self.assertEqual([item["slug"] for item in data["data"]], ["django-fusion-ar"])

    def test_language_variant_links_to_canonical_page(self):
        response = self.client.get("/api/products/?language=ar")
        item = response.json()["data"][0]
        self.assertEqual(item["detail_slug"], "django-fusion")
        self.assertEqual(item["href"], "/products/django-fusion/")

    def test_category_filter(self):
        response = self.client.get("/api/products/?category=library")
        data = response.json()
        self.assertEqual(data["pagination"]["total"], 2)

    def test_unpublished_products_are_excluded(self):
        response = self.client.get("/api/products/")
        slugs = [item["slug"] for item in response.json()["data"]]
        self.assertNotIn("draft-product", slugs)
