"""Extensibility + workflow-editor coverage (merge-plan §12 items 1, 3, 4, 5).

Covers the runtime custom-object schema, member-scoped saved views (including
the ``?view=`` apply path), tenant-scoped CSV import, the approval/report
queues, and the no-code workflow step editor endpoint.
"""
from __future__ import annotations

import csv
import io
import json

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone

from apps.core.models import SavedView, WorkflowDefinition, Workspace
from apps.crm.models import Company, Contact, CustomObjectDefinition, CustomObjectRecord
from apps.marketing.models import Campaign, Post, SocialChannel


def _member(workspace: Workspace, username: str, email: str) -> User:
    user = User.objects.create_user(username=username, email=email, password="Strong-pass-123")
    user.profile.workspace = workspace
    user.profile.save()
    return user


class CustomObjectTests(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name="Objects", slug="objects")
        self.user = _member(self.workspace, "obj-user", "obj@example.com")
        self.client.force_login(self.user)

    def _create_definition(self, key="project", fields=None):
        return self.client.post(
            "/api/v1/custom-objects/",
            data=json.dumps(
                {
                    "name": "Project",
                    "key": key,
                    "fields": fields
                    or [
                        {"key": "title", "label": "Title", "type": "text", "required": True},
                        {"key": "budget", "label": "Budget", "type": "number"},
                        {"key": "status", "label": "Status", "type": "select", "options": ["open", "closed"]},
                    ],
                }
            ),
            content_type="application/json",
        )

    def test_create_definition_and_record(self):
        response = self._create_definition()
        self.assertEqual(response.status_code, 201)
        key = response.json()["key"]
        record = self.client.post(
            f"/api/v1/custom-objects/{key}/records/",
            data=json.dumps({"data": {"title": "Apollo", "budget": 2500, "status": "open"}}),
            content_type="application/json",
        )
        self.assertEqual(record.status_code, 201)
        self.assertEqual(record.json()["data"]["budget"], "2500")
        self.assertEqual(record.json()["data"]["title"], "Apollo")

    def test_record_validation(self):
        self._create_definition()
        missing_required = self.client.post(
            "/api/v1/custom-objects/project/records/",
            data=json.dumps({"data": {"budget": 1}}),
            content_type="application/json",
        )
        self.assertEqual(missing_required.status_code, 400)
        bad_option = self.client.post(
            "/api/v1/custom-objects/project/records/",
            data=json.dumps({"data": {"title": "X", "status": "nope"}}),
            content_type="application/json",
        )
        self.assertEqual(bad_option.status_code, 400)
        unknown_field = self.client.post(
            "/api/v1/custom-objects/project/records/",
            data=json.dumps({"data": {"title": "X", "hacker": "value"}}),
            content_type="application/json",
        )
        self.assertEqual(unknown_field.status_code, 400)

    def test_records_are_workspace_scoped(self):
        other_ws = Workspace.objects.create(name="Other", slug="other")
        self._create_definition()
        self.client.post(
            "/api/v1/custom-objects/project/records/",
            data=json.dumps({"data": {"title": "Mine"}}),
            content_type="application/json",
        )
        definition = CustomObjectDefinition.objects.get(key="project", workspace=self.workspace)
        CustomObjectRecord.objects.create(
            workspace=other_ws, definition=definition, data={"title": "Theirs"}
        )
        listing = self.client.get("/api/v1/custom-objects/project/records/")
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(listing.json()["count"], 1)
        titles = [row["data"]["title"] for row in listing.json()["results"]]
        self.assertEqual(titles, ["Mine"])

    def test_screen_renders(self):
        self._create_definition()
        response = self.client.get("/settings/custom-objects/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Project")


class SavedViewTests(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name="Views", slug="views")
        self.user = _member(self.workspace, "view-user", "view@example.com")
        self.client.force_login(self.user)
        self.alpha = Company.objects.create(workspace=self.workspace, name="Alpha")
        Company.objects.create(workspace=self.workspace, name="Beta")

    def test_create_and_list_saved_view(self):
        response = self.client.post(
            "/api/v1/saved-views/",
            data=json.dumps(
                {"resource": "companies", "name": "My pipeline", "view_type": "kanban", "config": {"sort": "name"}}
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        listing = self.client.get("/api/v1/saved-views/")
        self.assertEqual(listing.json()["count"], 1)

    def test_saved_view_is_member_scoped(self):
        other = _member(Workspace.objects.create(name="B", slug="b"), "b-user", "b@example.com")
        self.client.post(
            "/api/v1/saved-views/",
            data=json.dumps({"resource": "companies", "name": "A view", "config": {}}),
            content_type="application/json",
        )
        SavedView.objects.create(
            workspace=self.workspace, user=other, resource="companies", name="B view", config={}
        )
        listing = self.client.get("/api/v1/saved-views/")
        names = [row["name"] for row in listing.json()["results"]]
        self.assertEqual(names, ["A view"])

    def test_view_config_applied_to_resource_list(self):
        view = SavedView.objects.create(
            workspace=self.workspace,
            user=self.user,
            resource="companies",
            name="Alpha only",
            config={"sort": "name", "filters": {"name": "Alpha"}},
        )
        response = self.client.get(f"/api/v1/companies/?view={view.pk}")
        self.assertEqual(response.status_code, 200)
        names = [row["name"] for row in response.json()["results"]]
        self.assertEqual(names, ["Alpha"])
        self.assertEqual(response.json()["count"], 1)

    def test_foreign_view_id_is_ignored(self):
        other = _member(Workspace.objects.create(name="C", slug="c"), "c-user", "c@example.com")
        foreign = SavedView.objects.create(
            workspace=other.profile.workspace, user=other, resource="companies", name="Foreign", config={}
        )
        response = self.client.get(f"/api/v1/companies/?view={foreign.pk}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 2)


class CsvImportTests(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name="Import", slug="import")
        self.user = _member(self.workspace, "import-user", "import@example.com")
        self.client.force_login(self.user)
        Company.objects.create(workspace=self.workspace, name="Acme")

    def _upload(self, object_type: str, text: str):
        return self.client.post(
            "/settings/import/",
            data={"object_type": object_type, "csv_file": SimpleUploadedFile("rows.csv", text.encode("utf-8"), content_type="text/csv")},
        )

    def test_import_companies(self):
        response = self._upload("companies", "name,industry\nGlobex,Software\nInitech,Defense\n")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "2 records created")
        self.assertTrue(Company.objects.filter(workspace=self.workspace, name="Globex").exists())

    def test_import_contacts_resolves_company_in_workspace(self):
        response = self._upload(
            "contacts", "first_name,last_name,email,company\nJane,Doe,jane@acme.com,Acme\n"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Contact.objects.filter(workspace=self.workspace, email="jane@acme.com").exists())

    def test_import_errors_are_reported(self):
        response = self._upload("contacts", "first_name,last_name,email,company\nJohn,Doe,john@nowhere.com,MissingCo\n")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "not found in this workspace")
        self.assertEqual(Contact.objects.filter(workspace=self.workspace).count(), 0)

    def test_import_screen_renders(self):
        response = self.client.get("/settings/import/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Import a CSV")


class ApprovalAndReportQueueTests(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name="Queues", slug="queues")
        self.user = _member(self.workspace, "queue-user", "queue@example.com")
        self.client.force_login(self.user)
        self.channel = SocialChannel.objects.create(workspace=self.workspace, platform="linkedin", account_name="acme")
        self.pending = Post.objects.create(
            workspace=self.workspace,
            channel=self.channel,
            content="Waiting for review",
            scheduled_at=timezone.now(),
            status="pending_approval",
        )

    def test_approvals_screen_lists_pending_only(self):
        Post.objects.create(
            workspace=self.workspace, channel=self.channel, content="Already approved",
            scheduled_at=timezone.now(), status="approved",
        )
        response = self.client.get("/marketing/approvals/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Waiting for review")
        self.assertNotContains(response, "Already approved")

    def test_approve_transition(self):
        self.client.post(
            f"/fragments/posts/{self.pending.pk}/transition/", {"action": "approve"}, HTTP_HX_REQUEST="true"
        )
        self.pending.refresh_from_db()
        self.assertEqual(self.pending.status, "approved")

    def test_reports_screen_renders(self):
        from apps.finance.models import RevenueEvent

        campaign = Campaign.objects.create(workspace=self.workspace, name="Launch")
        RevenueEvent.objects.create(workspace=self.workspace, campaign=campaign, kind="deal_won", amount="100.00")
        response = self.client.get("/attribution/reports/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Launch")
        self.assertContains(response, "By campaign")


class WorkflowStepEditorTests(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name="Editor", slug="editor")
        self.user = _member(self.workspace, "editor-user", "editor@example.com")
        self.client.force_login(self.user)
        self.workflow = WorkflowDefinition.objects.create(
            workspace=self.workspace,
            slug="my-flow",
            name="My flow",
            trigger="contact.created",
            actions=["assign_owner"],
            status="draft",
        )

    def _update(self, actions):
        return self.client.post(
            f"/fragments/workflows/{self.workflow.pk}/steps/",
            data=json.dumps({"trigger": "deal.stage_changed:closed_won", "actions": actions}),
            content_type="application/json",
        )

    def test_update_saves_trigger_and_ordered_actions(self):
        response = self._update(["create_invoice", "notify_revops"])
        self.assertEqual(response.status_code, 200)
        self.workflow.refresh_from_db()
        self.assertEqual(self.workflow.trigger, "deal.stage_changed:closed_won")
        self.assertEqual(self.workflow.actions, ["create_invoice", "notify_revops"])

    def test_update_rejects_unknown_action(self):
        response = self._update(["run_arbitrary_code"])
        self.assertEqual(response.status_code, 400)
        self.workflow.refresh_from_db()
        self.assertEqual(self.workflow.actions, ["assign_owner"])

    def test_editor_screen_renders(self):
        response = self.client.get("/settings/workflows/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Visual editor")
        self.assertContains(response, "workflow-editor")
        self.assertContains(response, "Node &amp; edge graph")
        self.assertContains(response, "workflow-dag")
        self.assertContains(response, "dag-canvas")


class WorkflowGraphEditorTests(TestCase):
    """The visual DAG canvas persists a validated acyclic node/edge graph."""

    def setUp(self):
        self.workspace = Workspace.objects.create(name="Graph", slug="graph")
        self.user = _member(self.workspace, "graph-user", "graph@example.com")
        self.client.force_login(self.user)
        self.workflow = WorkflowDefinition.objects.create(
            workspace=self.workspace,
            slug="branch-flow",
            name="Branch flow",
            trigger="contact.created",
            actions=["assign_owner"],
            status="draft",
        )

    def _branch_payload(self):
        # trigger → assign_owner → (notify_sales, send_email) — a real fork.
        return {
            "trigger": "contact.created",
            "nodes": [
                {"id": "trigger", "action": None, "x": 32, "y": 48},
                {"id": "step-1", "action": "assign_owner", "x": 232, "y": 48},
                {"id": "step-2", "action": "notify_sales", "x": 432, "y": 20},
                {"id": "step-3", "action": "send_email", "x": 432, "y": 96},
            ],
            "edges": [
                {"from": "trigger", "to": "step-1"},
                {"from": "step-1", "to": "step-2"},
                {"from": "step-1", "to": "step-3"},
            ],
        }

    def _update(self, payload):
        return self.client.post(
            f"/fragments/workflows/{self.workflow.pk}/graph/",
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_save_persists_graph_and_topological_actions(self):
        response = self._update(self._branch_payload())
        self.assertEqual(response.status_code, 200)
        self.workflow.refresh_from_db()
        self.assertEqual(self.workflow.graph["trigger"], "contact.created")
        self.assertEqual(len(self.workflow.graph["nodes"]), 4)
        self.assertEqual(len(self.workflow.graph["edges"]), 3)
        # Topological order: assign_owner precedes its two children; the two
        # children follow in stable edge order.
        self.assertEqual(self.workflow.actions[0], "assign_owner")
        self.assertEqual(set(self.workflow.actions[1:]), {"notify_sales", "send_email"})

    def test_rejects_cycle(self):
        payload = self._branch_payload()
        payload["edges"].append({"from": "step-3", "to": "step-1"})
        response = self._update(payload)
        self.assertEqual(response.status_code, 400)
        self.workflow.refresh_from_db()
        self.assertEqual(self.workflow.actions, ["assign_owner"])

    def test_rejects_orphan_node(self):
        payload = self._branch_payload()
        payload["nodes"].append({"id": "step-4", "action": "notify_revops", "x": 632, "y": 96})
        response = self._update(payload)
        self.assertEqual(response.status_code, 400)
        self.workflow.refresh_from_db()
        self.assertEqual(self.workflow.actions, ["assign_owner"])

    def test_rejects_unknown_action(self):
        payload = self._branch_payload()
        payload["nodes"][1]["action"] = "run_arbitrary_code"
        response = self._update(payload)
        self.assertEqual(response.status_code, 400)

    def test_rejects_missing_or_duplicate_trigger(self):
        payload = self._branch_payload()
        payload["nodes"] = [n for n in payload["nodes"] if n["id"] != "trigger"]
        self.assertEqual(self._update(payload).status_code, 400)
        payload = self._branch_payload()
        payload["nodes"].append({"id": "trigger-2", "action": None, "x": 0, "y": 0})
        self.assertEqual(self._update(payload).status_code, 400)

    def test_step_editor_keeps_linear_graph_in_sync(self):
        response = self.client.post(
            f"/fragments/workflows/{self.workflow.pk}/steps/",
            data=json.dumps({"trigger": "contact.created", "actions": ["assign_owner", "send_email"]}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.workflow.refresh_from_db()
        self.assertEqual(self.workflow.actions, ["assign_owner", "send_email"])
        self.assertEqual(len(self.workflow.graph["nodes"]), 3)
        self.assertEqual(
            [e["from"] for e in self.workflow.graph["edges"]],
            ["trigger", "step-1"],
        )


def _csv_to_string(rows: list[dict]) -> str:
    """Small helper (kept for future row generators)."""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()
