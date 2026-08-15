"""Tests for outbound webhooks (HMAC + retry + dead-letter) and connectors."""
from __future__ import annotations

import hashlib
import hmac
import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase

from apps.core.integrations import EmailConnector, SlackConnector
from apps.core.models import Webhook, WebhookDelivery, Workspace
from apps.core.webhooks import dispatch_webhooks, sign_payload

User = get_user_model()


class WebhookDispatchTests(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name="Hooks", slug="hooks")
        self.user = User.objects.create_user(
            username="hook-owner", email="hook@example.com", password="Strong-pass-123"
        )
        self.user.profile.workspace = self.workspace
        self.user.profile.save()

    def test_dispatch_creates_a_delivery_for_each_subscribed_webhook(self):
        Webhook.objects.create(workspace=self.workspace, url="https://in.example/a", events=["deal_won"])
        Webhook.objects.create(workspace=self.workspace, url="https://in.example/all", events=[])
        with patch("plugins.workers.tasks.broker_reachable", return_value=True):
            with patch("plugins.workers.tasks.deliver_webhook.send") as send:
                created = dispatch_webhooks(self.workspace.pk, "deal_won", {"deal_id": 1})
        self.assertEqual(created, 2)
        self.assertEqual(send.call_count, 2)
        self.assertEqual(WebhookDelivery.objects.filter(event="deal_won").count(), 2)

    def test_dispatch_filters_inactive_and_non_subscribed_webhooks(self):
        active = Webhook.objects.create(workspace=self.workspace, url="https://in.example/active", events=["deal_won"])
        Webhook.objects.create(workspace=self.workspace, url="https://in.example/other", events=["post_published"])
        Webhook.objects.create(workspace=self.workspace, url="https://in.example/off", events=["deal_won"], is_active=False)
        with patch("plugins.workers.tasks.broker_reachable", return_value=True):
            with patch("plugins.workers.tasks.deliver_webhook.send") as send:
                created = dispatch_webhooks(self.workspace.pk, "deal_won", {"deal_id": 1})
        self.assertEqual(created, 1)
        send.assert_called_once()
        self.assertEqual(list(WebhookDelivery.objects.values_list("webhook_id", flat=True)), [active.pk])

    def test_dispatch_marks_deliveries_dead_when_broker_unreachable(self):
        Webhook.objects.create(workspace=self.workspace, url="https://in.example/a", events=["deal_won"])
        with patch("plugins.workers.tasks.broker_reachable", return_value=False):
            with patch("plugins.workers.tasks.deliver_webhook.send") as send:
                created = dispatch_webhooks(self.workspace.pk, "deal_won", {"deal_id": 1})
        self.assertEqual(created, 1)
        delivery = WebhookDelivery.objects.get(event="deal_won")
        self.assertEqual(delivery.status, "dead")
        self.assertIn("broker unreachable", delivery.last_error)
        send.assert_not_called()

    def test_dispatch_ignores_unsupported_and_other_workspace_events(self):
        other = Workspace.objects.create(name="Other hooks", slug="other-hooks")
        Webhook.objects.create(workspace=other, url="https://in.example/other", events=[])
        self.assertEqual(dispatch_webhooks(self.workspace.pk, "deal_won", {}), 0)
        self.assertEqual(dispatch_webhooks(self.workspace.pk, "not_an_event", {}), 0)
        self.assertEqual(WebhookDelivery.objects.count(), 0)

    def test_webhook_resource_hides_the_secret(self):
        self.client.force_login(self.user)
        response = self.client.post(
            "/api/v1/webhooks/",
            data=json.dumps({"url": "https://in.example/hook", "secret": "s3cret", "events": ["deal_won"]}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertNotIn("secret", response.json())
        self.assertTrue(Webhook.objects.filter(workspace=self.workspace, secret="s3cret").exists())
        listing = self.client.get("/api/v1/webhooks/").json()
        self.assertNotIn("secret", listing["results"][0])


class WebhookDeliveryActorTests(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name="Delivery", slug="delivery")
        self.webhook = Webhook.objects.create(
            workspace=self.workspace, url="https://in.example/hook", secret="s3cret", events=["deal_won"]
        )

    def _delivery(self):
        return WebhookDelivery.objects.create(
            webhook=self.webhook, event="deal_won", payload={"deal_id": 1}
        )

    def test_sign_payload_is_a_deterministic_hmac(self):
        raw = b'{"a": 1}'
        expected = "sha256=" + hmac.new(b"s3cret", raw, hashlib.sha256).hexdigest()
        self.assertEqual(sign_payload("s3cret", raw), expected)

    def test_deliver_webhook_succeeds_and_signs_the_request(self):
        from plugins.workers.tasks import deliver_webhook

        delivery = self._delivery()
        with patch("apps.core.webhooks.post_json", return_value=(200, {})) as post:
            deliver_webhook.fn(delivery.pk)
        delivery.refresh_from_db()
        self.assertEqual(delivery.status, "succeeded")
        self.assertEqual(delivery.response_status, 200)
        _, kwargs = post.call_args
        self.assertTrue(kwargs["headers"]["X-Loop-Signature"].startswith("sha256="))
        self.assertEqual(kwargs["headers"]["X-Loop-Event"], "deal_won")

    def test_deliver_webhook_retries_with_backoff_on_failure(self):
        from plugins.workers.tasks import deliver_webhook

        delivery = self._delivery()
        with patch("apps.core.webhooks.post_json", return_value=(500, {})):
            with patch("plugins.workers.tasks.deliver_webhook.send_with_options") as retry:
                deliver_webhook.fn(delivery.pk)
        delivery.refresh_from_db()
        self.assertEqual(delivery.status, "failed")
        self.assertEqual(delivery.attempt_count, 1)
        retry.assert_called_once()
        self.assertEqual(retry.call_args.kwargs["delay"], 2000)

    def test_deliver_webhook_dead_letters_after_max_attempts(self):
        from plugins.workers.tasks import deliver_webhook

        delivery = self._delivery()
        delivery.attempt_count = 2  # one more attempt hits MAX_ATTEMPTS
        delivery.save(update_fields=["attempt_count"])
        with patch("apps.core.webhooks.post_json", return_value=(500, {})):
            with patch("plugins.workers.tasks.deliver_webhook.send_with_options") as retry:
                deliver_webhook.fn(delivery.pk)
        delivery.refresh_from_db()
        self.assertEqual(delivery.status, "dead")
        retry.assert_not_called()


class ConnectorTests(TestCase):
    def test_email_connector_delivers_through_the_backend(self):
        EmailConnector().send("Welcome", "Body", ["mara@example.com"])
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["mara@example.com"])

    def test_slack_connector_reports_unconfigured_without_a_webhook(self):
        connector = SlackConnector(None)
        self.assertFalse(connector.configured)
        status, body = connector.post("hello")
        self.assertEqual(status, 0)
        self.assertIn("configured", body["detail"])

    def test_slack_connector_posts_when_configured(self):
        connector = SlackConnector("https://hooks.example/slack")
        with patch("apps.core.integrations.post_json", return_value=(200, {})) as post:
            status, _ = connector.post("paid")
        self.assertEqual(status, 200)
        post.assert_called_once_with("https://hooks.example/slack", {"text": "paid"})
