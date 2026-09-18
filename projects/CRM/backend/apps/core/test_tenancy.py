"""Tenant-isolation tests: a member can see and mutate only their own workspace.

The ``Workspace`` model is the multi-tenant boundary for every domain record.
These tests prove the read/mutation layer enforces that boundary across the
render-first pages, the ``/api/v1/`` resource road, and the HTMX mutation
endpoints.
"""
from __future__ import annotations

import json

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from apps.core.models import WorkflowDefinition, Workspace
from apps.crm.models import Activity, Company, Contact, Deal, Pipeline, PipelineStage
from apps.marketing.models import Campaign, Media, Post, SocialChannel


class TenantIsolationTests(TestCase):
    def setUp(self):
        self.workspace_a = Workspace.objects.create(name="Tenant A", slug="tenant-a")
        self.workspace_b = Workspace.objects.create(name="Tenant B", slug="tenant-b")

        self.user_a = User.objects.create_user(
            username="member-a", email="a@example.com", password="Strong-pass-123"
        )
        self.user_a.profile.workspace = self.workspace_a
        self.user_a.profile.save()

        self.user_b = User.objects.create_user(
            username="member-b", email="b@example.com", password="Strong-pass-123"
        )
        self.user_b.profile.workspace = self.workspace_b
        self.user_b.profile.save()

        # Tenant A's own record (positive control).
        self.company_a = Company.objects.create(workspace=self.workspace_a, name="Alpha A")

        # Tenant B's records — must stay invisible/untouchable for member A.
        self.company_b = Company.objects.create(workspace=self.workspace_b, name="Acme B")
        self.contact_b = Contact.objects.create(
            workspace=self.workspace_b,
            company=self.company_b,
            first_name="Bo",
            last_name="Jones",
            email="bo@acme.example",
        )
        self.pipeline_b = Pipeline.objects.create(workspace=self.workspace_b, name="B pipeline")
        self.stage_b = PipelineStage.objects.create(
            pipeline=self.pipeline_b, name="Lead", stage_type="lead"
        )
        self.stage_qualified_b = PipelineStage.objects.create(
            pipeline=self.pipeline_b, name="Qualified", stage_type="qualified", order=1
        )
        self.deal_b = Deal.objects.create(
            workspace=self.workspace_b,
            company=self.company_b,
            contact=self.contact_b,
            name="B deal",
            value="1000.00",
            pipeline=self.pipeline_b,
            stage=self.stage_b,
            expected_close_date="2026-10-16",
        )
        self.channel_b = SocialChannel.objects.create(
            workspace=self.workspace_b, platform="linkedin", account_name="B channel"
        )
        self.post_b = Post.objects.create(
            workspace=self.workspace_b,
            channel=self.channel_b,
            content="B post",
            scheduled_at=timezone.now(),
        )
        self.workflow_b = WorkflowDefinition.objects.create(
            workspace=self.workspace_b,
            slug="b-flow",
            name="B flow",
            trigger="contact.created",
            actions=[],
            status="active",
        )

    def test_member_reads_only_their_own_workspace_resources(self):
        self.client.force_login(self.user_a)
        response = self.client.get("/api/v1/companies/")
        self.assertEqual(response.status_code, 200)
        names = [row["name"] for row in response.json()["results"]]
        self.assertEqual(names, ["Alpha A"])

    def test_company_page_hides_other_workspace_records(self):
        self.client.force_login(self.user_a)
        response = self.client.get("/crm/companies/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alpha A")
        self.assertNotContains(response, "Acme B")

    def test_member_cannot_move_other_workspace_deal(self):
        self.client.force_login(self.user_a)
        response = self.client.post(
            f"/api/v1/deals/{self.deal_b.pk}/stage/",
            data=json.dumps({"stage_id": self.stage_qualified_b.pk}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)
        self.deal_b.refresh_from_db()
        self.assertEqual(self.deal_b.stage_id, self.stage_b.pk)

    def test_member_cannot_toggle_other_workspace_workflow(self):
        self.client.force_login(self.user_a)
        response = self.client.post(
            f"/fragments/workflows/{self.workflow_b.pk}/toggle/",
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 404)
        self.workflow_b.refresh_from_db()
        self.assertEqual(self.workflow_b.status, "active")

    def test_member_cannot_transition_other_workspace_post(self):
        self.client.force_login(self.user_a)
        response = self.client.post(
            f"/fragments/posts/{self.post_b.pk}/transition/",
            {"action": "submit"},
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 404)
        self.post_b.refresh_from_db()
        self.assertEqual(self.post_b.status, "draft")

    def test_member_can_create_and_update_own_workspace_company_via_resource_api(self):
        self.client.force_login(self.user_a)
        response = self.client.post(
            "/api/v1/companies/",
            data=json.dumps({"name": "New A account", "industry": "SaaS"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["name"], "New A account")
        company = Company.objects.get(name="New A account")
        self.assertEqual(company.workspace_id, self.workspace_a.pk)

        response = self.client.patch(
            f"/api/v1/companies/{company.pk}/",
            data=json.dumps({"industry": "Fintech"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        company.refresh_from_db()
        self.assertEqual(company.industry, "Fintech")

        response = self.client.get(f"/api/v1/companies/{company.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "New A account")

    def test_member_cannot_update_or_delete_other_workspace_company(self):
        self.client.force_login(self.user_a)
        response = self.client.patch(
            f"/api/v1/companies/{self.company_b.pk}/",
            data=json.dumps({"name": "Hijacked"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)
        self.company_b.refresh_from_db()
        self.assertEqual(self.company_b.name, "Acme B")

        response = self.client.delete(f"/api/v1/companies/{self.company_b.pk}/")
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Company.objects.filter(pk=self.company_b.pk).exists())

    def test_resource_api_requires_workspace_for_write(self):
        self.user_a.profile.workspace = None
        self.user_a.profile.save()
        self.client.force_login(self.user_a)
        response = self.client.post(
            "/api/v1/companies/",
            data=json.dumps({"name": "No workspace"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Company.objects.filter(name="No workspace").exists())

    def test_channels_page_lists_only_own_channels_and_disconnect_is_scoped(self):
        channel_a = SocialChannel.objects.create(
            workspace=self.workspace_a, platform="mastodon", account_name="alice@mastodon.social", oauth_token="tok-a"
        )
        self.client.force_login(self.user_a)
        response = self.client.get("/marketing/channels/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "alice@mastodon.social")
        self.assertNotContains(response, "B channel")
        self.assertContains(response, 'hx-post="/fragments/marketing/channels/')

        # Member A cannot disconnect tenant B's channel.
        response = self.client.post(
            f"/fragments/marketing/channels/{self.channel_b.pk}/disconnect/",
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 404)
        self.channel_b.refresh_from_db()
        self.assertTrue(self.channel_b.is_active)

        # Member A can disconnect their own channel.
        response = self.client.post(
            f"/fragments/marketing/channels/{channel_a.pk}/disconnect/",
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(response.status_code, 200)
        channel_a.refresh_from_db()
        self.assertFalse(channel_a.is_active)
        self.assertEqual(channel_a.oauth_token, "")

    def test_activities_and_media_screens_and_api_are_workspace_scoped(self):
        pipeline_a = Pipeline.objects.create(workspace=self.workspace_a, name="A pipeline")
        stage_a = PipelineStage.objects.create(pipeline=pipeline_a, name="Lead", stage_type="lead")
        deal_a = Deal.objects.create(
            workspace=self.workspace_a,
            company=self.company_a,
            name="A deal",
            value="500.00",
            pipeline=pipeline_a,
            stage=stage_a,
            expected_close_date="2026-10-16",
        )
        Activity.objects.create(
            workspace=self.workspace_a, deal=deal_a, activity_type="call", subject="Call Alpha"
        )
        Activity.objects.create(
            workspace=self.workspace_b, deal=self.deal_b, activity_type="call", subject="Call Beta"
        )
        Media.objects.create(workspace=self.workspace_a, file="a/asset.png", alt_text="Alpha asset")
        Media.objects.create(workspace=self.workspace_b, file="b/asset.png", alt_text="Beta asset")

        self.client.force_login(self.user_a)

        activities_page = self.client.get("/crm/activities/")
        self.assertEqual(activities_page.status_code, 200)
        self.assertContains(activities_page, "Call Alpha")
        self.assertNotContains(activities_page, "Call Beta")

        media_page = self.client.get("/marketing/media/")
        self.assertEqual(media_page.status_code, 200)
        self.assertContains(media_page, "a/asset.png")
        self.assertNotContains(media_page, "b/asset.png")

        activities_api = self.client.get("/api/v1/activities/")
        self.assertEqual(activities_api.status_code, 200)
        subjects = [row["subject"] for row in activities_api.json()["results"]]
        self.assertEqual(subjects, ["Call Alpha"])

    def test_content_calendar_form_dropdowns_are_workspace_scoped(self):
        channel_a = SocialChannel.objects.create(
            workspace=self.workspace_a, platform="linkedin", account_name="A channel"
        )
        Campaign.objects.create(workspace=self.workspace_a, name="A campaign")
        Campaign.objects.create(workspace=self.workspace_b, name="B campaign")

        self.client.force_login(self.user_a)
        response = self.client.get("/marketing/calendar/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Compose a post")
        # The composer dropdowns only offer the member's own workspace records.
        # (SocialChannel.__str__ renders "<platform> — <account>", so the option
        # text carries the platform prefix.)
        self.assertContains(response, "LinkedIn — A channel")
        self.assertNotContains(response, "LinkedIn — B channel")
        self.assertContains(response, ">A campaign</option>")
        self.assertNotContains(response, ">B campaign</option>")
        self.assertContains(response, ">Tenant A</option>")
        self.assertNotContains(response, ">Tenant B</option>")
