"""Email sync (Gmail/Outlook) connector + service + API tests.

Mirrors ``test_webhooks.py``: connectors degrade honestly without credentials,
the sync service is idempotent and tenant-scoped, and the API never projects
OAuth tokens.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from apps.core.email_sync import (
    GmailConnector,
    OutlookConnector,
    UnconfiguredEmailConnector,
    connector_for,
    sync_account,
)
from apps.core.models import EmailAccount, EmailMessage, Workspace
from apps.crm.models import Company, Contact, Deal, Pipeline, PipelineStage

User = get_user_model()


def _iso(dt: datetime) -> str:
    return dt.isoformat()


class ConnectorResolutionTests(TestCase):
    def test_connector_for_resolves_real_adapters(self):
        self.assertIsInstance(connector_for("gmail"), GmailConnector)
        self.assertIsInstance(connector_for("outlook"), OutlookConnector)

    def test_connector_for_unknown_provider_is_honest(self):
        self.assertIsInstance(connector_for("aol"), UnconfiguredEmailConnector)

    def test_unconfigured_connector_never_fetches(self):
        workspace = Workspace.objects.create(name="Mail", slug="mail")
        account = EmailAccount.objects.create(workspace=workspace, provider="gmail", email="x@example.com")
        with self.assertRaises(ValueError):
            UnconfiguredEmailConnector("aol").fetch_messages(account)


class GmailConnectorTests(TestCase):
    def _account(self):
        workspace = Workspace.objects.create(name="Gmail", slug="gmail")
        return EmailAccount.objects.create(
            workspace=workspace, provider="gmail", email="me@gmail.com", oauth_token="tok"
        )

    def _fetch(self):
        return GmailConnector().fetch_messages(self._account())

    def test_fetch_normalizes_gmail_messages(self):
        with patch("apps.core.email_sync._Http.get", return_value=(200, {
            "messages": [
                {
                    "id": "msg-1",
                    "threadId": "thread-1",
                    "snippet": "Hi there",
                    "payload": {"headers": [
                        {"name": "From", "value": "Ada Lovelace <ada@example.com>"},
                        {"name": "Subject", "value": "Contract review"},
                        {"name": "Date", "value": "Mon, 10 Aug 2026 09:00:00 +0000"},
                    ]},
                }
            ]
        })) as get:
            messages = self._fetch()
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["external_id"], "msg-1")
        self.assertEqual(messages[0]["thread_id"], "thread-1")
        self.assertEqual(messages[0]["subject"], "Contract review")
        self.assertEqual(messages[0]["sender_email"], "ada@example.com")
        self.assertEqual(messages[0]["sender_name"], "Ada Lovelace")
        self.assertIsNotNone(messages[0]["received_at"])
        get.assert_called_once()

    def test_fetch_requires_a_token(self):
        workspace = Workspace.objects.create(name="Gmail 2", slug="gmail-2")
        account = EmailAccount.objects.create(workspace=workspace, provider="gmail", email="me@gmail.com")
        with self.assertRaises(ValueError):
            GmailConnector().fetch_messages(account)

    def test_fetch_honors_cursor_watermark(self):
        account = self._account()
        account.sync_cursor = {"last_received_at": 1700000000}
        account.save(update_fields=["sync_cursor"])
        with patch("apps.core.email_sync._Http.get", return_value=(200, {"messages": []})) as get:
            GmailConnector().fetch_messages(account)
        url = get.call_args.args[0]
        self.assertIn("q=after%3A1700000000", url)

    @override_settings(GMAIL_CLIENT_ID="cid", GMAIL_CLIENT_SECRET="csec")
    def test_refresh_updates_token_pair(self):
        account = self._account()
        account.oauth_refresh_token = "refresh"
        account.save(update_fields=["oauth_refresh_token"])
        with patch("apps.core.email_sync._Http.post_form", return_value=(200, {"access_token": "new", "expires_in": 3600})) as post:
            ok = GmailConnector().refresh(account)
        self.assertTrue(ok)
        account.refresh_from_db()
        self.assertEqual(account.oauth_token, "new")
        self.assertIsNotNone(account.token_expires_at)
        post.assert_called_once()


class OutlookConnectorTests(TestCase):
    def _account(self):
        workspace = Workspace.objects.create(name="Outlook", slug="outlook")
        return EmailAccount.objects.create(
            workspace=workspace, provider="outlook", email="me@outlook.com", oauth_token="tok"
        )

    def test_fetch_normalizes_outlook_messages(self):
        with patch("apps.core.email_sync._Http.get", return_value=(200, {
            "value": [
                {
                    "id": "om-1",
                    "conversationId": "conv-1",
                    "subject": "Invoice",
                    "bodyPreview": "Please find attached",
                    "from": {"emailAddress": {"address": "bo@example.com", "name": "Bo Jones"}},
                    "receivedDateTime": "2026-08-10T09:00:00Z",
                }
            ]
        })) as get:
            messages = OutlookConnector().fetch_messages(self._account())
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["external_id"], "om-1")
        self.assertEqual(messages[0]["sender_email"], "bo@example.com")
        self.assertEqual(messages[0]["snippet"], "Please find attached")
        get.assert_called_once()


class SyncServiceTests(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name="Sync", slug="sync")
        self.other = Workspace.objects.create(name="Other sync", slug="other-sync")
        self.account = EmailAccount.objects.create(
            workspace=self.workspace, provider="gmail", email="me@example.com", oauth_token="tok"
        )
        self.company = Company.objects.create(workspace=self.workspace, name="Northline")
        self.contact = Contact.objects.create(
            workspace=self.workspace, company=self.company, first_name="Ada", last_name="Lovelace", email="ada@example.com"
        )
        self.pipeline = Pipeline.objects.create(workspace=self.workspace, name="P")
        self.stage = PipelineStage.objects.create(pipeline=self.pipeline, name="Lead", stage_type="lead")
        self.deal = Deal.objects.create(
            workspace=self.workspace,
            company=self.company,
            contact=self.contact,
            name="Big deal",
            value="1000.00",
            pipeline=self.pipeline,
            stage=self.stage,
            expected_close_date="2026-11-01",
        )

    def _messages(self, *rows):
        return [
            {
                "external_id": ext,
                "thread_id": "t",
                "subject": subject,
                "snippet": "…",
                "sender_email": sender,
                "sender_name": "",
                "received_at": received,
            }
            for ext, subject, sender, received in rows
        ]

    def test_sync_creates_idempotent_tenant_scoped_messages(self):
        with patch("apps.core.email_sync.connector_for") as connector_for:
            connector_for.return_value.fetch_messages.return_value = self._messages(
                ("m1", "Hello", "ada@example.com", datetime(2026, 8, 10, tzinfo=timezone.utc)),
            )
            result = sync_account(self.account)
            result2 = sync_account(self.account)
        self.assertEqual(result.status, "synced")
        self.assertEqual(result.synced, 1)
        self.assertEqual(result.matched, 1)
        self.assertEqual(result2.synced, 0)  # idempotent
        self.assertEqual(result2.skipped, 1)
        self.assertEqual(EmailMessage.objects.filter(workspace=self.workspace).count(), 1)

    def test_sync_matches_contact_and_open_deal(self):
        with patch("apps.core.email_sync.connector_for") as connector_for:
            connector_for.return_value.fetch_messages.return_value = self._messages(
                ("m1", "Hello", "ada@example.com", datetime(2026, 8, 10, tzinfo=timezone.utc)),
            )
            sync_account(self.account)
        message = EmailMessage.objects.get(external_id="m1")
        self.assertEqual(message.contact, self.contact)
        self.assertEqual(message.deal, self.deal)
        self.assertEqual(message.workspace, self.workspace)

    def test_sync_advances_cursor(self):
        received = datetime(2026, 8, 10, tzinfo=timezone.utc)
        with patch("apps.core.email_sync.connector_for") as connector_for:
            connector_for.return_value.fetch_messages.return_value = self._messages(
                ("m1", "Hello", "ada@example.com", received),
            )
            sync_account(self.account)
        self.account.refresh_from_db()
        self.assertAlmostEqual(self.account.sync_cursor["last_received_at"], received.timestamp(), places=3)
        self.assertIsNotNone(self.account.last_synced_at)

    def test_sync_reports_unconfigured_without_token(self):
        self.account.oauth_token = ""
        self.account.save(update_fields=["oauth_token"])
        result = sync_account(self.account)
        self.assertEqual(result.status, "unconfigured")
        self.assertIn("Connect", result.detail)

    def test_sync_reports_unconfigured_for_paused_account(self):
        self.account.is_active = False
        self.account.save(update_fields=["is_active"])
        result = sync_account(self.account)
        self.assertEqual(result.status, "unconfigured")
        self.assertIn("paused", result.detail)

    def test_sync_does_not_leak_other_workspace_messages(self):
        # A foreign-workspace message must never be created by this account's sync.
        with patch("apps.core.email_sync.connector_for") as connector_for:
            connector_for.return_value.fetch_messages.return_value = self._messages(
                ("m1", "Hello", "ada@example.com", datetime(2026, 8, 10, tzinfo=timezone.utc)),
            )
            sync_account(self.account)
        self.assertEqual(EmailMessage.objects.filter(workspace=self.other).count(), 0)


class EmailApiTests(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name="API", slug="api")
        self.user = User.objects.create_user(
            username="mail-user", email="mail@example.com", password="Strong-pass-123"
        )
        self.user.profile.workspace = self.workspace
        self.user.profile.save()
        self.client.force_login(self.user)

    def test_accounts_api_hides_oauth_tokens(self):
        with patch("apps.core.email_sync.sync_account") as sync:
            sync.return_value = None
            response = self.client.post(
                "/api/v1/email/accounts/",
                data=json.dumps({"provider": "gmail", "email": "me@gmail.com", "oauth_token": "s3cret"}),
                content_type="application/json",
            )
        self.assertEqual(response.status_code, 201)
        self.assertNotIn("s3cret", response.content.decode())
        listing = self.client.get("/api/v1/email/accounts/").json()
        self.assertNotIn("oauth_token", listing["results"][0])
        self.assertEqual(listing["providers"][0]["id"], "gmail")

    def test_accounts_api_rejects_unknown_provider(self):
        response = self.client.post(
            "/api/v1/email/accounts/",
            data=json.dumps({"provider": "aol", "email": "me@aol.com"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_sync_endpoint_is_tenant_scoped(self):
        other = Workspace.objects.create(name="Other API", slug="other-api")
        account = EmailAccount.objects.create(workspace=other, provider="gmail", email="x@example.com", oauth_token="tok")
        response = self.client.post(f"/api/v1/email/accounts/{account.pk}/sync/")
        self.assertEqual(response.status_code, 404)

    def test_messages_api_returns_workspace_scoped_rows(self):
        account = EmailAccount.objects.create(workspace=self.workspace, provider="gmail", email="me@gmail.com")
        EmailMessage.objects.create(
            workspace=self.workspace, account=account, external_id="m1", subject="Hi", sender_email="a@b.c"
        )
        other = Workspace.objects.create(name="Other msgs", slug="other-msgs")
        other_account = EmailAccount.objects.create(workspace=other, provider="gmail", email="other@gmail.com")
        EmailMessage.objects.create(
            workspace=other, account=other_account, external_id="m2", subject="Secret", sender_email="x@y.z"
        )
        response = self.client.get("/api/v1/email/messages/")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["results"][0]["subject"], "Hi")
