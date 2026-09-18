"""Generic per-resource CSV/JSON export tests.

Proves ``/api/v1/export/`` downloads any registered resource table in CSV or
JSON, stays workspace-scoped, honors ``search``, and rejects unknown resources
or formats.
"""

from __future__ import annotations

from django.contrib.auth.models import User
from django.test import TestCase

from apps.core.models import Workspace
from apps.crm.models import Company, Contact


class ResourceExportTests(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name="Tenant A", slug="tenant-a")
        self.other = Workspace.objects.create(name="Tenant B", slug="tenant-b")
        self.user = User.objects.create_user(
            username="exporter", email="exporter@example.com", password="Strong-pass-123"
        )
        self.user.profile.workspace = self.workspace
        self.user.profile.save()
        self.client.force_login(self.user)

        Company.objects.create(workspace=self.workspace, name="Northline Studio")
        Company.objects.create(workspace=self.workspace, name="Bluebell Labs")
        # Cross-tenant row that must never be exported.
        Company.objects.create(workspace=self.other, name="Other Co")
        Contact.objects.create(
            workspace=self.workspace,
            company=Company.objects.get(workspace=self.workspace, name="Northline Studio"),
            first_name="Ada",
            last_name="Lovelace",
            email="ada@example.com",
        )

    def test_csv_export_returns_header_and_workspace_scoped_rows(self):
        response = self.client.get("/api/v1/export/?resource=companies&format=csv")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/csv")
        content = response.content.decode()
        self.assertIn("name", content)  # header row
        self.assertIn("Northline Studio", content)
        self.assertIn("Bluebell Labs", content)
        self.assertNotIn("Other Co", content)

    def test_json_export_returns_results_and_count(self):
        response = self.client.get("/api/v1/export/?resource=companies&format=json")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["count"], 2)
        self.assertEqual({row["name"] for row in payload["results"]}, {"Northline Studio", "Bluebell Labs"})

    def test_export_honors_search(self):
        response = self.client.get("/api/v1/export/?resource=companies&format=json&search=bluebell")
        payload = response.json()
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["results"][0]["name"], "Bluebell Labs")

    def test_export_uses_read_projection_for_related_fields(self):
        # contacts read projection exposes company_id (a related FK name).
        response = self.client.get("/api/v1/export/?resource=contacts&format=json")
        payload = response.json()
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["results"][0]["email"], "ada@example.com")
        self.assertIn("company_id", payload["results"][0])

    def test_export_rejects_unknown_resource_and_bad_format(self):
        self.assertEqual(self.client.get("/api/v1/export/?resource=nope").status_code, 404)
        self.assertEqual(self.client.get("/api/v1/export/?resource=companies&format=xml").status_code, 400)
