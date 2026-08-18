from datetime import timedelta
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, override_settings
from django.test.client import RequestFactory
from django.utils import timezone
from django_fusion.comp.tags.menu import app_menu

from apps.core.bolt_api import bolt
from apps.core.fusion import loop_crm_application
from apps.core.models import TaskExecution, WorkflowDefinition, WorkflowRun, Workspace
from apps.core.navigation import breadcrumbs_for, navigation_context
from apps.core.workflows import persisted_workflow_catalog
from apps.crm.custom_fields import custom_object_catalog, validate_custom_attributes
from apps.crm.models import Company, Contact, CustomFieldDefinition, Deal, Pipeline, PipelineStage
from apps.finance.models import Invoice, Payment, RevenueEvent
from apps.marketing.connectors import platform_catalog
from apps.marketing.models import Campaign, Post, SocialChannel


class NavigationContractTests(TestCase):
    def _login(self, username: str = "member") -> User:
        user = User.objects.create_user(
            username=username, email=f"{username}@example.com", password="Strong-pass-123"
        )
        self.client.force_login(user)
        return user

    def test_module_and_subpage_active_states(self):
        tree = navigation_context("/crm/deals/")
        crm = next(item for item in tree if item["id"] == "crm")
        deals = next(item for item in crm["children"] if item["id"] == "deals")
        self.assertTrue(crm["active"])
        self.assertTrue(deals["active"])
        self.assertFalse(next(item for item in tree if item["id"] == "marketing")["active"])

    def test_breadcrumbs_include_current_page(self):
        trail = breadcrumbs_for("/marketing/calendar/", "Content calendar")
        self.assertEqual(
            trail,
            [
                {"label": "Home", "href": "/"},
                {"label": "Marketing", "href": "/marketing/"},
                {"label": "Content calendar", "href": "/marketing/calendar/"},
            ],
        )

    def test_fusion_menu_path_entries_resolve_to_real_urls(self):
        request = RequestFactory().get("/crm/")
        context = app_menu(
            {"request": request}, loop_crm_application, AnonymousUser()
        )
        dashboard = next(item for item in context["items"] if item.get("name") == "dashboard")
        self.assertEqual(dashboard["url"], "/")

    def test_fusion_application_routes_render(self):
        self._login()
        response = self.client.get("/crm/deals/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Deals")
        self.assertContains(response, 'aria-label="Breadcrumb"')
        self.assertContains(response, "/crm/companies/")

    def test_bolt_runtime_is_optional_and_fallback_token_contract_exists(self):
        # The checkout contains a documentation stub, not the runtime. The
        # product must still import cleanly and retain its Django fallback.
        self.assertTrue(bolt is None or hasattr(bolt, "get"))
        response = self.client.get("/api/v1/auth/token/")
        self.assertEqual(response.status_code, 405)

        response = self.client.post(
            "/api/v1/auth/token/",
            data="not-json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        response = self.client.post(
            "/api/v1/auth/refresh/",
            data='{"refresh_token":"invalid"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    def test_navigation_fragment_returns_complete_tree_for_new_path(self):
        response = self.client.get(
            "/fragments/navigation/?path=/marketing/calendar/",
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'aria-current="page"')
        self.assertContains(response, "/crm/companies/")
        self.assertContains(response, 'href="/marketing/calendar/" aria-current="page"')
        self.assertNotContains(response, "hx-trigger=\"load\"")

    def test_navigation_fragment_marks_crm_child_active(self):
        response = self.client.get("/fragments/navigation/?path=/crm/companies/", HTTP_HX_REQUEST="true")
        self.assertContains(response, 'href="/crm/companies/" aria-current="page"')
        self.assertNotContains(response, 'href="/crm/contacts/" aria-current="page"')

    def test_workflow_create_toggle_and_queue_are_real_interactions(self):
        self._login()
        workflow = WorkflowDefinition.objects.get(slug="lead-capture")
        response = self.client.get("/settings/workflows/")
        self.assertContains(response, "database-backed")
        self.assertContains(response, "Define a workflow")

        response = self.client.post(
            "/fragments/workflows/create/",
            {
                "name": "Notify RevOps",
                "slug": "notify-revops",
                "description": "Keep the revenue team informed.",
                "module": "workspace",
                "trigger": "deal.stage_changed:closed_won",
                "actions": '["notify_revops"]',
                "status": "active",
            },
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        created = WorkflowDefinition.objects.get(slug="notify-revops")
        self.assertContains(response, "Notify RevOps")
        self.assertEqual(created.actions, ["notify_revops"])

        response = self.client.post(
            f"/fragments/workflows/{workflow.pk}/toggle/",
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        workflow.refresh_from_db()
        self.assertEqual(workflow.status, "paused")

        workflow.status = "active"
        workflow.save(update_fields=["status"])
        with patch("plugins.workers.tasks.execute_workflow.send") as send:
            response = self.client.post(
                f"/fragments/workflows/{workflow.pk}/run/",
                HTTP_HX_REQUEST="true",
            )
        self.assertEqual(response.status_code, 200)
        send.assert_called_once()
        self.assertEqual(WorkflowRun.objects.filter(definition=workflow).count(), 1)

    def test_content_calendar_composes_and_transitions_posts(self):
        self._login()
        workspace = Workspace.objects.create(name="Test workspace", slug="test-workspace")
        channel = SocialChannel.objects.create(
            workspace=workspace,
            platform="linkedin",
            account_name="Structa test",
        )
        response = self.client.get("/marketing/calendar/")
        self.assertContains(response, "Compose a post")

        response = self.client.post(
            "/fragments/posts/create/",
            {
                "workspace": workspace.pk,
                "channel": channel.pk,
                "content": "A real content review checkpoint.",
                "scheduled_at": (timezone.now() + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M"),
            },
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        post = Post.objects.get(workspace=workspace)
        self.assertEqual(post.status, "draft")

        response = self.client.post(
            f"/fragments/posts/{post.pk}/transition/",
            {"action": "submit"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        post.refresh_from_db()
        self.assertEqual(post.status, "pending_approval")

    def test_crm_company_contact_and_deal_forms_are_real_htmx_interactions(self):
        self._login()
        workspace = Workspace.objects.create(name="CRM workspace", slug="crm-workspace")
        response = self.client.get("/crm/companies/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add a company")
        self.assertContains(response, 'hx-post="/fragments/crm/companies/create/"')

        response = self.client.post(
            "/fragments/crm/companies/create/",
            {
                "workspace": workspace.pk,
                "name": "Northline Studio",
                "industry": "Architecture",
                "email": "hello@northline.example",
                "city": "Chicago",
                "annual_revenue": "480000.00",
                "employee_count": "18",
            },
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Northline Studio")
        self.assertContains(response, 'hx-swap-oob="outerHTML"')
        company = Company.objects.get(name="Northline Studio")

        response = self.client.post(
            "/fragments/crm/contacts/create/",
            {
                "workspace": workspace.pk,
                "company": company.pk,
                "first_name": "Mara",
                "last_name": "Ellison",
                "email": "mara@northline.example",
                "title": "Operations lead",
            },
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mara Ellison")
        contact = Contact.objects.get(email="mara@northline.example")

        pipeline = Pipeline.objects.create(workspace=workspace, name="New business", is_default=True)
        stage = PipelineStage.objects.create(pipeline=pipeline, name="Qualified", stage_type="qualified", probability=40)
        campaign = Campaign.objects.create(workspace=workspace, name="Spring planning")
        response = self.client.post(
            "/fragments/crm/deals/create/",
            {
                "workspace": workspace.pk,
                "company": company.pk,
                "contact": contact.pk,
                "name": "Northline annual planning",
                "value": "92500.00",
                "pipeline": pipeline.pk,
                "stage": stage.pk,
                "expected_close_date": "2026-10-16",
                "campaign": campaign.pk,
            },
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Northline annual planning")
        self.assertEqual(Deal.objects.get(name="Northline annual planning").stage_id, stage.pk)

    def test_crm_contact_and_deal_forms_reject_cross_workspace_relationships(self):
        self._login()
        first = Workspace.objects.create(name="First workspace", slug="first-workspace")
        second = Workspace.objects.create(name="Second workspace", slug="second-workspace")
        company = Company.objects.create(workspace=second, name="Second account")
        response = self.client.post(
            "/fragments/crm/contacts/create/",
            {
                "workspace": first.pk,
                "company": company.pk,
                "first_name": "Cross",
                "last_name": "Tenant",
                "email": "cross@example.com",
            },
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 422)
        self.assertFalse(Contact.objects.filter(email="cross@example.com").exists())

    def test_allauth_pages_and_profile_permissions_are_available(self):
        login = self.client.get("/accounts/login/")
        signup = self.client.get("/accounts/signup/")
        self.assertEqual(login.status_code, 200)
        self.assertEqual(signup.status_code, 200)
        self.assertContains(login, "Sign in")
        self.assertContains(signup, "Create account")

    def test_domain_subpages_render_real_list_screens(self):
        self._login()
        # The pipelines screen is the schema-aware-table contract check: seed
        # one pipeline so the table (not the empty state) renders its typed
        # column headers.
        workspace = Workspace.objects.create(name="List screens", slug="list-screens")
        Pipeline.objects.create(workspace=workspace, name="New business", is_default=True)
        for path in [
            "/crm/pipelines/",
            "/crm/activities/",
            "/marketing/campaigns/",
            "/marketing/media/",
            "/attribution/touchpoints/",
            "/attribution/reports/",
            "/settings/integrations/",
            "/settings/custom-fields/",
            "/settings/audit/",
        ]:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)
            self.assertContains(response, "workspace-scoped")
            if path == "/crm/pipelines/":
                self.assertContains(response, 'data-column-type="text"')

    def test_allauth_password_email_and_social_pages_render(self):
        reset = self.client.get("/accounts/password/reset/")
        self.assertEqual(reset.status_code, 200)
        self.assertContains(reset, "Reset password")

        user = User.objects.create_user(username="account-member", email="account-member@example.com", password="Strong-pass-123")
        user.profile.workspace = Workspace.objects.create(name="Account workspace", slug="account-workspace")
        user.profile.save()
        self.client.force_login(user)
        from django.urls import reverse

        for path, marker in [
            ("/accounts/password/change/", "Change password"),
            ("/accounts/email/", "Email addresses"),
            (reverse("socialaccount_connections"), "Connected accounts"),
        ]:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)
            self.assertContains(response, marker)

        user = User.objects.create_user(username="member", email="member@example.com", password="Strong-pass-123")
        user.profile.role = "revops_manager"
        user.profile.workspace = Workspace.objects.create(name="Member workspace", slug="member-workspace")
        user.profile.save()
        self.client.force_login(user)
        profile = self.client.get("/account/profile/")
        members = self.client.get("/settings/members/")
        self.assertEqual(profile.status_code, 200)
        self.assertEqual(members.status_code, 200)
        self.assertContains(profile, "revops_manager")
        self.assertContains(members, "Manage deals")
        self.assertNotContains(members, "refresh_token")

    def test_custom_field_definitions_validate_typed_values_without_polymorphic_models(self):
        workspace = Workspace.objects.create(name="Fields workspace", slug="fields-workspace")
        definition = CustomFieldDefinition.objects.create(
            workspace=workspace,
            object_type="company",
            key="segment",
            label="Segment",
            field_type="select",
            options=["startup", "enterprise"],
            required=True,
        )
        self.assertEqual(
            validate_custom_attributes(workspace, "company", {"segment": "enterprise"}),
            {"segment": "enterprise"},
        )
        with self.assertRaises(Exception):
            validate_custom_attributes(workspace, "company", {"segment": "unknown"})
        catalog = custom_object_catalog(workspace)
        company = next(item for item in catalog if item["object"] == "company")
        self.assertIn(definition.key, {field["key"] for field in company["fields"]})

    def test_user_bound_token_endpoint_rejects_anonymous_arbitrary_subjects(self):
        response = self.client.post(
            "/api/v1/auth/token/",
            data='{"subject":"some-other-user"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

    @override_settings(FUSION_BOLT_JWT_SECRET="loop-crm-user-token-test-secret")
    def test_bearer_token_resolves_live_user_role_and_workspace(self):
        try:
            import jwt
        except ImportError:
            self.skipTest("PyJWT is not installed in the workspace environment")
        if not hasattr(jwt, "encode") or not hasattr(jwt, "decode"):
            self.skipTest("The installed jwt module is not PyJWT")
        from django_fusion.plugins.apis.auth import user_token_payload

        workspace = Workspace.objects.create(name="Token workspace", slug="token-workspace")
        user = User.objects.create_user(username="token-user", email="token@example.com", password="Strong-pass-123")
        user.profile.workspace = workspace
        user.profile.role = "sales_manager"
        user.profile.save()
        token = user_token_payload(user)["token"]
        response = self.client.get("/api/v1/auth/me/", HTTP_AUTHORIZATION=f"Bearer {token}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user"]["role"], "sales_manager")
        self.assertEqual(response.json()["user"]["workspace_id"], workspace.pk)

    def test_finance_invoice_payment_and_revenue_surfaces_are_real(self):
        self._login()
        workspace = Workspace.objects.create(name="Finance workspace", slug="finance-workspace")
        company = Company.objects.create(workspace=workspace, name="Northline Studio")
        response = self.client.get("/finance/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Issue an invoice")
        response = self.client.post(
            "/fragments/finance/invoices/create/",
            {
                "workspace": workspace.pk,
                "number": "INV-2026-0042",
                "company": company.pk,
                "currency": "USD",
                "status": "issued",
                "issued_on": "2026-08-13",
                "due_on": "2026-09-12",
                "subtotal": "92500.00",
                "tax": "18500.00",
                "notes": "Net 30",
            },
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        invoice = Invoice.objects.get(number="INV-2026-0042")
        self.assertEqual(invoice.total, Decimal("111000.00"))
        response = self.client.post(
            "/fragments/finance/payments/create/",
            {
                "workspace": workspace.pk,
                "invoice": invoice.pk,
                "amount": "111000.00",
                "paid_on": "2026-08-13",
                "method": "bank_transfer",
                "reference": "BANK-REF-1042",
            },
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, "paid")
        self.assertEqual(Payment.objects.get(invoice=invoice).amount, Decimal("111000.00"))
        self.assertEqual(self.client.get("/api/v1/invoices/").json()["count"], 1)

    def test_deal_won_workflow_creates_revenue_and_invoice_from_pipeline_data(self):
        workspace = Workspace.objects.create(name="Revenue workspace", slug="revenue-workspace")
        company = Company.objects.create(workspace=workspace, name="Northline Studio")
        pipeline = Pipeline.objects.create(workspace=workspace, name="New business")
        won_stage = PipelineStage.objects.create(pipeline=pipeline, name="Closed won", stage_type="closed_won", probability=100)
        campaign = Campaign.objects.create(workspace=workspace, name="Spring planning")
        deal = Deal.objects.create(
            workspace=workspace,
            company=company,
            name="Northline annual planning",
            value=Decimal("92500.00"),
            pipeline=pipeline,
            stage=won_stage,
            expected_close_date="2026-10-16",
            campaign=campaign,
        )
        definition = WorkflowDefinition.objects.get(slug="deal-won", workspace=None)
        run = WorkflowRun.objects.create(
            definition=definition,
            workspace=workspace,
            trigger_payload={"deal_id": deal.pk, "source": "test"},
        )
        from plugins.workers.tasks import execute_workflow

        execute_workflow.fn(run.pk)
        run.refresh_from_db()
        self.assertEqual(run.status, "succeeded")
        self.assertTrue(RevenueEvent.objects.filter(deal=deal, kind="deal_won", amount=deal.value).exists())
        self.assertTrue(Invoice.objects.filter(deal=deal, status="issued", total=deal.value).exists())

    def test_deal_transition_to_closed_won_queues_the_workflow(self):
        workspace = Workspace.objects.create(name="Pipeline workspace", slug="pipeline-workspace")
        company = Company.objects.create(workspace=workspace, name="Northline Studio")
        pipeline = Pipeline.objects.create(workspace=workspace, name="New business")
        lead_stage = PipelineStage.objects.create(pipeline=pipeline, name="Lead", stage_type="lead")
        won_stage = PipelineStage.objects.create(pipeline=pipeline, name="Closed won", stage_type="closed_won", probability=100)
        deal = Deal.objects.create(
            workspace=workspace,
            company=company,
            name="Pipeline conversion",
            value=Decimal("12000.00"),
            pipeline=pipeline,
            stage=lead_stage,
            expected_close_date="2026-10-16",
        )
        with patch("plugins.workers.tasks.execute_workflow.send") as send, patch(
            "plugins.workers.tasks.broker_reachable", return_value=True
        ):
            deal.transition_to_stage(won_stage)
        self.assertEqual(deal.actual_close_date, timezone.localdate())
        send.assert_called_once()
        self.assertEqual(WorkflowRun.objects.filter(workspace=workspace, trigger_payload__deal_id=deal.pk).count(), 1)

class TaskCenterTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="ops", email="ops@example.com", password="Strong-pass-123"
        )

    def test_tasks_page_requires_login(self):
        response = self.client.get("/tasks/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_tasks_page_renders_website_record(self):
        TaskExecution.objects.create(
            job_id="job-1",
            task_name="plugins.workers.tasks.execute_workflow",
            queue_name="default",
            site_name="loop-crm",
            status="finished",
        )
        self.client.force_login(self.user)
        response = self.client.get("/tasks/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "execute_workflow")
        self.assertContains(response, "finished")

    def test_backend_dual_write_persists_website_record(self):
        from django_fusion.tasks.backends.dramatiq import DramatiqBackend

        registration = SimpleNamespace(name="test.task", queue="default")
        DramatiqBackend._create_website_log(registration, "loop-crm", "job-2", "queued")
        record = TaskExecution.objects.get(job_id="job-2")
        self.assertEqual(record.status, "queued")
        self.assertEqual(record.site_name, "loop-crm")

        DramatiqBackend._touch_website_log(
            "job-2", status="finished", result={"ok": True}
        )
        record.refresh_from_db()
        self.assertEqual(record.status, "finished")
        self.assertEqual(record.result, {"ok": True})

    def test_sync_website_record_is_safe_without_shared_table(self):
        from django_fusion.tasks.views import sync_website_record

        # loop-crm has no shared BackgroundTaskLog table; the mirror helper
        # must degrade to zero rather than raise.
        self.assertEqual(sync_website_record("loop-crm"), 0)

    def test_api_contracts_expose_integration_and_workflow_catalogs(self):
        self.client.force_login(self.user)
        integrations = self.client.get("/api/v1/integrations/")
        workflows = self.client.get("/api/v1/workflows/")
        self.assertEqual(integrations.status_code, 200)
        self.assertEqual(workflows.status_code, 200)
        self.assertEqual(integrations.json()["count"], len(platform_catalog()))
        self.assertEqual(workflows.json()["count"], len(persisted_workflow_catalog()))
        custom_fields = self.client.get("/api/v1/custom-fields/")
        self.assertEqual(custom_fields.json()["count"], len(custom_object_catalog()))
