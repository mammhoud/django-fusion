"""Tests for the expanded workflow action catalog and domain triggers.

Each action is exercised on its completed, skipped/deferred, and (where it
matters) cross-tenant paths. Triggers are verified through the post_save
signals with the Dramatiq send patched, mirroring how the existing deal-won
workflow tests avoid a real broker.
"""
from __future__ import annotations

from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.utils import timezone
from plugins.workers.tasks import trigger_workflow

from apps.core.models import WorkflowDefinition, WorkflowRun, Workspace
from apps.core.workflow_actions import execute_action
from apps.crm.models import Activity, Company, Contact, Deal, Pipeline, PipelineStage
from apps.finance.models import Invoice, Payment, RevenueEvent
from apps.pos.models import PosSale

User = get_user_model()


class WorkflowActionTests(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name="Actions", slug="actions")
        self.owner = User.objects.create_user(
            username="wf-owner", email="owner@example.com", password="Strong-pass-123"
        )
        self.company = Company.objects.create(workspace=self.workspace, name="Northline Studio")
        self.contact = Contact.objects.create(
            workspace=self.workspace,
            company=self.company,
            first_name="Mara",
            last_name="Ellison",
            email="mara@northline.example",
        )
        self.pipeline = Pipeline.objects.create(workspace=self.workspace, name="New business")
        self.won_stage = PipelineStage.objects.create(
            pipeline=self.pipeline, name="Closed won", stage_type="closed_won", probability=100
        )
        self.deal = Deal.objects.create(
            workspace=self.workspace,
            company=self.company,
            contact=self.contact,
            name="Annual planning",
            value=Decimal("10000.00"),
            pipeline=self.pipeline,
            stage=self.won_stage,
            expected_close_date=timezone.localdate() + timedelta(days=30),
        )
        self._slug_counter = 0

    def _run(self, actions, payload, workspace=None, created_by=None):
        self._slug_counter += 1
        definition = WorkflowDefinition.objects.create(
            workspace=None,
            slug=f"test-actions-{self._slug_counter}",
            name="Test actions",
            module="test",
            trigger="test",
            actions=actions,
            status="active",
            created_by=created_by,
        )
        return WorkflowRun.objects.create(
            definition=definition,
            workspace=workspace or self.workspace,
            trigger_payload=payload,
        )

    def _invoice(self, *, status="issued", due_days=-5, amount="100.00"):
        return Invoice.objects.create(
            workspace=self.workspace,
            number=f"INV-{self._slug_counter}-{status}",
            company=self.company,
            status=status,
            due_on=timezone.localdate() + timedelta(days=due_days),
            subtotal=Decimal(amount),
            tax=Decimal("0.00"),
        )

    # ── mark_invoice_overdue ────────────────────────────────────────────────

    def test_mark_invoice_overdue_completes_for_a_past_due_issued_invoice(self):
        invoice = self._invoice(status="issued", due_days=-3)
        run = self._run(["mark_invoice_overdue"], {"invoice_id": invoice.pk})
        result = execute_action("mark_invoice_overdue", run)
        self.assertEqual(result["status"], "completed")
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, "overdue")

    def test_mark_invoice_overdue_skips_paid_and_future_invoices(self):
        paid = self._invoice(status="paid", due_days=-3)
        future = self._invoice(status="issued", due_days=10)
        self.assertEqual(execute_action("mark_invoice_overdue", self._run([], {"invoice_id": paid.pk}))["status"], "skipped")
        self.assertEqual(execute_action("mark_invoice_overdue", self._run([], {"invoice_id": future.pk}))["status"], "skipped")

    def test_mark_invoice_overdue_is_tenant_scoped(self):
        other = Workspace.objects.create(name="Other", slug="other-actions")
        other_invoice = Invoice.objects.create(
            workspace=other,
            number="OTHER-1",
            company=Company.objects.create(workspace=other, name="Other Co"),
            status="issued",
            due_on=timezone.localdate() - timedelta(days=3),
            subtotal=Decimal("50.00"),
        )
        result = execute_action("mark_invoice_overdue", self._run([], {"invoice_id": other_invoice.pk}))
        self.assertEqual(result["status"], "skipped")
        other_invoice.refresh_from_db()
        self.assertEqual(other_invoice.status, "issued")

    # ── record_payment ──────────────────────────────────────────────────────

    def test_record_payment_creates_a_payment_and_marks_the_invoice_paid(self):
        invoice = self._invoice(amount="100.00")
        run = self._run(["record_payment"], {"invoice_id": invoice.pk, "amount": "100.00", "reference": "BANK-1"})
        result = execute_action("record_payment", run)
        self.assertEqual(result["status"], "completed")
        self.assertTrue(result["created"])
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, "paid")
        self.assertEqual(Payment.objects.get(invoice=invoice).amount, Decimal("100.00"))

    def test_record_payment_is_idempotent_by_reference(self):
        invoice = self._invoice(amount="100.00")
        payload = {"invoice_id": invoice.pk, "amount": "60.00", "reference": "BANK-2"}
        first = execute_action("record_payment", self._run([], payload))
        second = execute_action("record_payment", self._run([], payload))
        self.assertTrue(first["created"])
        self.assertFalse(second["created"])
        self.assertEqual(Payment.objects.filter(invoice=invoice, reference="BANK-2").count(), 1)

    def test_record_payment_skips_without_an_amount(self):
        invoice = self._invoice()
        result = execute_action("record_payment", self._run([], {"invoice_id": invoice.pk}))
        self.assertEqual(result["status"], "skipped")

    # ── reconcile_pos_sale ──────────────────────────────────────────────────

    def test_reconcile_pos_sale_bridges_a_completed_sale_into_revenue(self):
        pos_sale = PosSale.objects.create(
            workspace=self.workspace,
            external_id="sale-1",
            subtotal=Decimal("40.00"),
            total=Decimal("40.00"),
            status="completed",
        )
        run = self._run(["reconcile_pos_sale"], {"pos_sale_id": pos_sale.pk})
        result = execute_action("reconcile_pos_sale", run)
        self.assertEqual(result["status"], "completed")
        self.assertTrue(
            RevenueEvent.objects.filter(
                workspace=self.workspace, kind="pos_sale", external_ref="pos:sale-1"
            ).exists()
        )

    def test_reconcile_pos_sale_skips_without_a_sale(self):
        result = execute_action("reconcile_pos_sale", self._run([], {"pos_sale_id": 999999}))
        self.assertEqual(result["status"], "skipped")

    # ── create_follow_up_task ───────────────────────────────────────────────

    def test_create_follow_up_task_schedules_a_task_for_the_deal(self):
        run = self._run(["create_follow_up_task"], {"deal_id": self.deal.pk, "due_in_days": "5"})
        result = execute_action("create_follow_up_task", run)
        self.assertEqual(result["status"], "completed")
        activity = Activity.objects.get(deal=self.deal, activity_type="task")
        self.assertIsNotNone(activity.scheduled_at)
        self.assertEqual(activity.status, "pending")

    def test_create_follow_up_task_skips_without_a_deal(self):
        result = execute_action("create_follow_up_task", self._run([], {}))
        self.assertEqual(result["status"], "skipped")

    # ── send_email / send_slack / call_webhook ──────────────────────────────

    def test_send_email_delivers_to_the_recipient(self):
        result = execute_action("send_email", self._run([], {"to": "mara@northline.example", "subject": "Welcome"}))
        self.assertEqual(result["status"], "completed")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["mara@northline.example"])

    def test_send_email_skips_without_a_recipient(self):
        self.assertEqual(execute_action("send_email", self._run([], {}))["status"], "skipped")

    def test_send_slack_defers_without_a_webhook_url(self):
        self.assertEqual(execute_action("send_slack", self._run([], {}))["status"], "deferred")

    def test_send_slack_posts_when_configured(self):
        with patch("apps.core.integrations.post_json", return_value=(200, {})) as post:
            result = execute_action(
                "send_slack",
                self._run([], {"slack_webhook_url": "https://hooks.example/slack", "text": "Paid"}),
            )
        self.assertEqual(result["status"], "completed")
        post.assert_called_once()

    def test_call_webhook_signs_the_payload_and_posts(self):
        with patch("apps.core.workflow_actions.post_json", return_value=(200, {})) as post:
            result = execute_action(
                "call_webhook",
                self._run(
                    [],
                    {"webhook_url": "https://hooks.example/in", "webhook_secret": "s3cret", "webhook_payload": {"a": 1}},
                ),
            )
        self.assertEqual(result["status"], "completed")
        _, kwargs = post.call_args
        self.assertIn("X-Loop-Signature", kwargs["headers"])

    def test_call_webhook_skips_without_a_url(self):
        self.assertEqual(execute_action("call_webhook", self._run([], {}))["status"], "skipped")

    # ── refresh_analytics ───────────────────────────────────────────────────

    def test_refresh_analytics_skips_without_a_post(self):
        self.assertEqual(execute_action("refresh_analytics", self._run([], {}))["status"], "skipped")


    # ── publish-on-mutation (realtime dashboard refreshes) ───────────────

    def test_update_campaign_roi_publishes_a_revenue_event(self):
        run = self._run(["update_campaign_roi"], {"deal_id": self.deal.pk})
        with patch("apps.core.workflow_actions.safe_publish_workspace_event") as publish:
            result = execute_action("update_campaign_roi", run)
        self.assertEqual(result["status"], "completed")
        publish.assert_called_once_with(
            self.workspace.pk,
            "resource.created",
            {"resource": "revenue", "pk": result["revenue_event_id"]},
        )

    def test_record_touchpoint_publishes_a_touchpoints_event(self):
        from apps.marketing.models import Campaign, Post, SocialChannel

        campaign = Campaign.objects.create(workspace=self.workspace, name="Launch")
        channel = SocialChannel.objects.create(workspace=self.workspace, platform="linkedin", account_name="page")
        post = Post.objects.create(
            workspace=self.workspace, channel=channel, campaign=campaign, content="Hi", scheduled_at=timezone.now()
        )
        run = self._run(["record_touchpoint"], {"deal_id": self.deal.pk, "post_id": post.pk})
        with patch("apps.core.workflow_actions.safe_publish_workspace_event") as publish:
            result = execute_action("record_touchpoint", run)
        self.assertEqual(result["status"], "completed")
        publish.assert_called_once_with(
            self.workspace.pk,
            "resource.created",
            {"resource": "touchpoints", "pk": result["touchpoint_id"]},
        )

    def test_record_payment_publishes_payment_and_invoice_events(self):
        invoice = self._invoice(amount="100.00")
        run = self._run(["record_payment"], {"invoice_id": invoice.pk, "amount": "100.00", "reference": "BANK-PUB"})
        with patch("apps.core.workflow_actions.safe_publish_workspace_event") as publish:
            result = execute_action("record_payment", run)
        calls = [call[0] for call in publish.call_args_list]
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0][1], "resource.created")
        self.assertEqual(calls[0][2], {"resource": "payments", "pk": result["payment_id"]})
        self.assertEqual(calls[1][1], "resource.updated")
        self.assertEqual(calls[1][2], {"resource": "invoices", "pk": invoice.pk})

    def test_mark_invoice_overdue_publishes_an_invoices_event(self):
        invoice = self._invoice(status="issued", due_days=-3)
        run = self._run(["mark_invoice_overdue"], {"invoice_id": invoice.pk})
        with patch("apps.core.workflow_actions.safe_publish_workspace_event") as publish:
            execute_action("mark_invoice_overdue", run)
        publish.assert_called_once_with(
            self.workspace.pk, "resource.updated", {"resource": "invoices", "pk": invoice.pk}
        )

    def test_reconcile_pos_sale_publishes_a_revenue_event(self):
        pos_sale = PosSale.objects.create(
            workspace=self.workspace, external_id="sale-pub", subtotal=Decimal("40.00"), total=Decimal("40.00"), status="completed"
        )
        run = self._run(["reconcile_pos_sale"], {"pos_sale_id": pos_sale.pk})
        with patch("apps.core.workflow_actions.safe_publish_workspace_event") as publish:
            execute_action("reconcile_pos_sale", run)
        publish.assert_called_once_with(
            self.workspace.pk, "resource.updated", {"resource": "revenue", "pos_sale_id": pos_sale.pk}
        )

    def test_skipped_actions_do_not_publish(self):
        run = self._run(["record_payment"], {"invoice_id": 999999})
        with patch("apps.core.workflow_actions.safe_publish_workspace_event") as publish:
            result = execute_action("record_payment", run)
        self.assertEqual(result["status"], "skipped")
        publish.assert_not_called()


class WorkflowTriggerSignalTests(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name="Triggers", slug="triggers")
        self.company = Company.objects.create(workspace=self.workspace, name="Northline Studio")

    def test_contact_created_triggers_contact_nurture(self):
        with patch("plugins.workers.tasks.execute_workflow.send") as send:
            Contact.objects.create(
                workspace=self.workspace,
                company=self.company,
                first_name="Ada",
                last_name="Lovelace",
                email="ada@example.com",
            )
        self.assertTrue(
            WorkflowRun.objects.filter(
                workspace=self.workspace, definition__slug="contact-nurture", trigger_payload__email="ada@example.com"
            ).exists()
        )

    def test_payment_created_triggers_payment_received(self):
        invoice = Invoice.objects.create(
            workspace=self.workspace,
            number="INV-TRIG-1",
            company=self.company,
            status="issued",
            due_on=timezone.localdate() + timedelta(days=10),
            subtotal=Decimal("100.00"),
        )
        with patch("plugins.workers.tasks.execute_workflow.send") as send:
            Payment.objects.create(
                workspace=self.workspace,
                invoice=invoice,
                amount=Decimal("100.00"),
                method="bank_transfer",
            )
        self.assertTrue(
            WorkflowRun.objects.filter(
                workspace=self.workspace, definition__slug="payment-received"
            ).exists()
        )

    def test_overdue_invoice_triggers_dunning_but_paid_invoices_do_not(self):
        def dunning_runs():
            return WorkflowRun.objects.filter(
                workspace=self.workspace, definition__slug="invoice-dunning"
            )

        # A settled (paid) invoice never triggers dunning, even when past due.
        with patch("plugins.workers.tasks.execute_workflow.send") as send:
            Invoice.objects.create(
                workspace=self.workspace,
                number="INV-TRIG-3",
                company=self.company,
                status="paid",
                due_on=timezone.localdate() - timedelta(days=3),
                subtotal=Decimal("100.00"),
            )
        self.assertEqual(dunning_runs().count(), 0)

        # A past-due issued invoice triggers dunning exactly once.
        with patch("plugins.workers.tasks.execute_workflow.send") as send:
            Invoice.objects.create(
                workspace=self.workspace,
                number="INV-TRIG-2",
                company=self.company,
                status="issued",
                due_on=timezone.localdate() - timedelta(days=3),
                subtotal=Decimal("100.00"),
            )
        self.assertEqual(dunning_runs().count(), 1)

        # Marking it overdue (what the workflow action does) must not re-trigger.
        invoice = Invoice.objects.get(number="INV-TRIG-2")
        with patch("plugins.workers.tasks.execute_workflow.send") as send:
            invoice.status = "overdue"
            invoice.save(update_fields=["status", "updated_at"])
        self.assertEqual(dunning_runs().count(), 1)


class WorkflowBrokerGateTests(TestCase):
    """The broker-reachability gate that keeps signal triggers cheap.

    A down broker must mark the run failed immediately (no slow ``send``
    round-trip); an up broker must enqueue normally. The probe result is cached
    so the test suite (and a transient outage) does not re-probe per trigger.
    """

    def setUp(self):
        self.workspace = Workspace.objects.create(name="Gate", slug="gate")

    def test_down_broker_marks_run_failed_without_enqueuing(self):
        with patch("plugins.workers.tasks.broker_reachable", return_value=False), patch(
            "plugins.workers.tasks.execute_workflow.send"
        ) as send:
            trigger_workflow(
                "contact-nurture",
                self.workspace.pk,
                {"contact_id": 1, "email": "gate@example.com"},
            )
        send.assert_not_called()
        run = WorkflowRun.objects.get(workspace=self.workspace)
        self.assertEqual(run.status, "failed")
        self.assertIn("broker unreachable", run.error)

    def test_up_broker_enqueues_normally(self):
        with patch("plugins.workers.tasks.broker_reachable", return_value=True), patch(
            "plugins.workers.tasks.execute_workflow.send"
        ) as send:
            trigger_workflow(
                "contact-nurture",
                self.workspace.pk,
                {"contact_id": 1, "email": "gate@example.com"},
            )
        send.assert_called_once()
        run = WorkflowRun.objects.get(workspace=self.workspace)
        self.assertEqual(run.status, "queued")

    def test_broker_probe_result_is_cached(self):
        from plugins.workers import tasks as tasks_module

        with patch.object(tasks_module, "_broker_reachable_cache", None):
            with patch.object(
                tasks_module.socket, "create_connection", side_effect=OSError("down")
            ) as probe:
                self.assertFalse(tasks_module.broker_reachable())
                self.assertFalse(tasks_module.broker_reachable())
        self.assertEqual(probe.call_count, 1)
