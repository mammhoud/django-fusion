"""Broker-reachability gating for the marketing actor enqueue paths.

The publish and OAuth-refresh fragment views enqueue Dramatiq actors from the
request path; both are gated behind ``broker_reachable`` so a down broker fails
fast (and honestly) instead of paying the per-request ``.send()`` round-trip.
"""

from __future__ import annotations

from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from apps.core.models import Workspace
from apps.marketing.models import Post, SocialChannel


class MarketingBrokerGateTests(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name="Gate", slug="gate")
        self.user = User.objects.create_user(
            username="marketer", email="m@example.com", password="Strong-pass-123"
        )
        self.user.profile.workspace = self.workspace
        self.user.profile.save()
        self.channel = SocialChannel.objects.create(
            workspace=self.workspace, platform="linkedin", account_name="acme", oauth_token="tok"
        )
        self.client.force_login(self.user)

    def _post(self):
        # "publish" transitions scheduled → publishing (the lifecycle gate the
        # fragment view enforces before it touches the queue).
        return Post.objects.create(
            workspace=self.workspace,
            channel=self.channel,
            content="Hello",
            scheduled_at=timezone.now(),
            status="scheduled",
        )

    def test_channel_refresh_skips_enqueue_when_broker_down(self):
        with patch("plugins.workers.tasks.broker_reachable", return_value=False):
            with patch("plugins.workers.tasks.refresh_oauth_token.send") as send:
                response = self.client.post(
                    f"/fragments/marketing/channels/{self.channel.pk}/refresh/",
                    HTTP_HX_REQUEST="true",
                )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Refresh queued")
        send.assert_not_called()

    def test_channel_refresh_enqueues_when_broker_up(self):
        with patch("plugins.workers.tasks.broker_reachable", return_value=True):
            with patch("plugins.workers.tasks.refresh_oauth_token.send") as send:
                response = self.client.post(
                    f"/fragments/marketing/channels/{self.channel.pk}/refresh/",
                    HTTP_HX_REQUEST="true",
                )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Refresh queued")
        send.assert_called_once_with(self.channel.pk)

    def test_publish_marks_post_failed_when_broker_down(self):
        post = self._post()
        with patch("plugins.workers.tasks.broker_reachable", return_value=False):
            with patch("plugins.workers.tasks.publish_post.send") as send:
                response = self.client.post(
                    f"/fragments/posts/{post.pk}/transition/",
                    {"action": "publish"},
                    HTTP_HX_REQUEST="true",
                )
        self.assertEqual(response.status_code, 200)
        post.refresh_from_db()
        self.assertEqual(post.status, "failed")
        self.assertContains(response, "broker unreachable")
        send.assert_not_called()

    def test_publish_enqueues_when_broker_up(self):
        post = self._post()
        with patch("plugins.workers.tasks.broker_reachable", return_value=True):
            with patch("plugins.workers.tasks.publish_post.send") as send:
                response = self.client.post(
                    f"/fragments/posts/{post.pk}/transition/",
                    {"action": "publish"},
                    HTTP_HX_REQUEST="true",
                )
        self.assertEqual(response.status_code, 200)
        send.assert_called_once_with(post.pk)
