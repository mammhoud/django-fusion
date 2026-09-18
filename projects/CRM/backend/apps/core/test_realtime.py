"""Realtime layer tests: workspace-scoped SSE auth + publish helpers.

The streaming response is an infinite generator, so these tests exercise the
guard rails (auth + cross-tenant rejection + group naming + best-effort
publish) directly rather than blocking on an endless ``StreamingHttpResponse``.
"""
from __future__ import annotations

import asyncio
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from apps.core.models import Workspace
from apps.core.realtime import (
    safe_apublish_workspace_event,
    safe_publish_workspace_event,
    workspace_group,
)


class RealtimeHelperTests(TestCase):
    def test_workspace_group_name_is_deterministic(self):
        self.assertEqual(workspace_group(7), "workspace_7")
        self.assertEqual(workspace_group("demo"), "workspace_demo")

    def test_safe_publish_is_a_noop_without_a_workspace(self):
        # A caller with no workspace must never publish (and never raise).
        self.assertIsNone(safe_publish_workspace_event(None, "resource.created", {}))

    def test_safe_publish_swallows_channel_layer_outages(self):
        # Realtime is best-effort: a broken channel layer must not 500 a write.
        with patch(
            "apps.core.realtime.publish_workspace_event",
            side_effect=RuntimeError("redis down"),
        ):
            self.assertIsNone(safe_publish_workspace_event(1, "resource.created", {}))

    def test_safe_apublish_is_a_noop_without_a_workspace(self):
        async def run():
            await safe_apublish_workspace_event(None, "resource.created", {})

        asyncio.run(run())

    def test_safe_apublish_swallows_channel_layer_outages(self):
        async def run():
            with patch(
                "apps.core.realtime.apublish_workspace_event",
                side_effect=RuntimeError("redis down"),
            ):
                await safe_apublish_workspace_event(1, "resource.created", {})

        asyncio.run(run())


class WorkspaceEventsSseTests(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name="Realtime", slug="realtime")
        self.user = User.objects.create_user(
            username="realtime-member", email="rt@example.com", password="Strong-pass-123"
        )
        self.user.profile.workspace = self.workspace
        self.user.profile.save()

    def test_sse_requires_authentication(self):
        # The SSE view is called directly to avoid consuming the stream; it must
        # still enforce auth before opening the generator.
        from django.test import RequestFactory

        from apps.core.realtime import workspace_events_sse

        request = RequestFactory().get(f"/sse/workspace/{self.workspace.pk}/events/")
        from django.contrib.auth.models import AnonymousUser

        request.user = AnonymousUser()
        import asyncio

        response = asyncio.run(workspace_events_sse(request, self.workspace.pk))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response["Content-Type"], "text/event-stream")

    def test_sse_rejects_cross_workspace(self):
        from django.test import RequestFactory

        from apps.core.realtime import workspace_events_sse

        other = Workspace.objects.create(name="Other", slug="other")
        request = RequestFactory().get(f"/sse/workspace/{other.pk}/events/")
        request.user = self.user
        import asyncio

        response = asyncio.run(workspace_events_sse(request, other.pk))
        self.assertEqual(response.status_code, 403)

    def test_workspace_current_endpoint_requires_auth_and_returns_the_id(self):
        anonymous = self.client.get("/api/v1/workspace/current/")
        self.assertEqual(anonymous.status_code, 302)  # login redirect

        self.client.force_login(self.user)
        response = self.client.get("/api/v1/workspace/current/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"workspace_id": self.workspace.pk})
