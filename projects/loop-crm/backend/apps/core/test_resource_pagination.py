"""Pagination + search filtering on the resource API road.

Proves the collection GET honors ``limit``/``offset``/``search`` while keeping
``count`` as the *total* (not the page length) and never leaking another
workspace's rows through the search filter.
"""

from __future__ import annotations

from django.contrib.auth.models import User
from django.test import TestCase

from apps.core.models import Workspace
from apps.crm.models import Company


class ResourcePaginationTests(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name="Tenant A", slug="tenant-a")
        self.user = User.objects.create_user(
            username="member", email="member@example.com", password="Strong-pass-123"
        )
        self.user.profile.workspace = self.workspace
        self.user.profile.save()
        for index in range(5):
            Company.objects.create(workspace=self.workspace, name=f"Account {index}")
        self.client.force_login(self.user)

    def _get(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()

    def test_pagination_slices_and_reports_total_count(self):
        payload = self._get("/api/v1/companies/?limit=2")
        self.assertEqual([row["name"] for row in payload["results"]], ["Account 0", "Account 1"])
        self.assertEqual(payload["count"], 5)
        self.assertEqual(payload["next"], 2)
        self.assertIsNone(payload["previous"])

        payload = self._get("/api/v1/companies/?limit=2&offset=2")
        self.assertEqual([row["name"] for row in payload["results"]], ["Account 2", "Account 3"])
        self.assertEqual(payload["previous"], 0)

        payload = self._get("/api/v1/companies/?limit=2&offset=4")
        self.assertEqual([row["name"] for row in payload["results"]], ["Account 4"])
        self.assertEqual(payload["count"], 5)
        self.assertIsNone(payload["next"])

    def test_search_filters_and_stays_tenant_scoped(self):
        other = Workspace.objects.create(name="Tenant B", slug="tenant-b")
        Company.objects.create(workspace=other, name="Acme secret")

        payload = self._get("/api/v1/companies/?search=account")
        self.assertEqual(payload["count"], 5)
        self.assertTrue(all("Account" in row["name"] for row in payload["results"]))

        payload = self._get("/api/v1/companies/?search=Acme")
        self.assertEqual(payload["count"], 0)
        self.assertEqual(payload["results"], [])

    def test_limit_clamps_and_invalid_value_falls_back(self):
        payload = self._get("/api/v1/companies/?limit=0")
        self.assertEqual(len(payload["results"]), 1)  # clamped to the minimum of 1

        payload = self._get("/api/v1/companies/?limit=abc")
        self.assertEqual(len(payload["results"]), 5)  # invalid → default 100
        self.assertEqual(payload["count"], 5)
