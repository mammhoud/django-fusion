"""Focused coverage for the Phase 6 people/search contracts."""

from django.contrib.auth.models import User
from django.test import TestCase

from apps.core.models import Workspace
from apps.crm.models import Company


class PeopleAndSearchApiTests(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name="People workspace", slug="people-workspace")
        self.user = User.objects.create_user(
            username="people-owner", email="people@example.com", password="Strong-pass-123"
        )
        self.user.profile.workspace = self.workspace
        self.user.profile.role = "sales_manager"
        self.user.profile.save()
        self.client.force_login(self.user)
        Company.objects.create(workspace=self.workspace, name="Northline Studio", owner=self.user)

    def test_employee_directory_and_report_are_workspace_scoped(self):
        response = self.client.get("/apis/core/employees/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["role"], "sales_manager")

        response = self.client.get(f"/apis/core/employees/{self.user.pk}/report/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["metrics"]["deals"], 0)

    def test_search_returns_only_current_workspace_records(self):
        other = Workspace.objects.create(name="Other", slug="other-people")
        Company.objects.create(workspace=other, name="Northline Secret", owner=self.user)
        response = self.client.get("/apis/core/search/?q=Northline")
        self.assertEqual(response.status_code, 200)
        titles = [result["title"] for result in response.json()["results"]]
        self.assertEqual(titles, ["Northline Studio"])

    def test_badges_are_live_and_authenticated(self):
        response = self.client.get("/apis/core/badges/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.json()), {"approvals", "invoices", "tasks"})
