"""HTTP end-to-end checks for the Loop-CRM render and HTMX roads."""
from __future__ import annotations

from urllib.request import Request, urlopen

from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase

User = get_user_model()


class LoopCRMHTTPFlowTests(LiveServerTestCase):
    """Exercise the same URLs a browser and HTMX client use."""

    def setUp(self):
        # Dashboard pages and data APIs now require authentication. Establish a
        # session through the in-process client and replay its sessionid over
        # the real HTTP transport below.
        self.user = User.objects.create_user(
            username="e2e", email="e2e@example.com", password="Strong-pass-123"
        )
        self.client.force_login(self.user)
        self.session_cookie = self.client.session.session_key

    def fetch(self, path: str, *, htmx: bool = False) -> str:
        headers = {"HX-Request": "true"} if htmx else {}
        if getattr(self, "session_cookie", None):
            headers["Cookie"] = f"sessionid={self.session_cookie}"
        request = Request(
            f"{self.live_server_url}{path}",
            headers=headers,
        )
        with urlopen(request, timeout=5) as response:  # noqa: S310 - local test server
            self.assertEqual(response.status, 200)
            return response.read().decode("utf-8")

    def test_navigation_preloads_complete_data_and_marks_only_current_path(self):
        document = self.fetch(
            "/fragments/navigation/?path=/crm/deals/",
            htmx=True,
        )
        self.assertIn("/crm/companies/", document)
        self.assertIn('href="/crm/deals/" aria-current="page"', document)
        self.assertNotIn('hx-trigger="load"', document)

    def test_workflow_and_content_pages_are_real_database_screens(self):
        workflow_page = self.fetch("/settings/workflows/")
        content_page = self.fetch("/marketing/calendar/")
        self.assertIn("database-backed", workflow_page)
        self.assertIn("Define a workflow", workflow_page)
        self.assertIn("Compose a post", content_page)
        self.assertIn("stateful content", content_page)

    def test_crm_pages_expose_real_htmx_form_contracts(self):
        companies = self.fetch("/crm/companies/")
        contacts = self.fetch("/crm/contacts/")
        deals = self.fetch("/crm/deals/")
        self.assertIn('hx-post="/fragments/crm/companies/create/"', companies)
        self.assertIn('hx-post="/fragments/crm/contacts/create/"', contacts)
        self.assertIn('hx-post="/fragments/crm/deals/create/"', deals)
        self.assertIn("No companies yet", companies)
        self.assertIn("No contacts yet", contacts)
        self.assertIn("No deals yet", deals)
