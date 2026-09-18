"""Tests for the Gmail / Outlook email-sync OAuth connect flow.

Mirrors ``apps.marketing.tests.test_oauth``: URL builders are unit-tested
without HTTP, ``connect_start`` holds state and redirects honestly when client
credentials are missing, and ``oauth_callback`` verifies state before upserting
an ``EmailAccount`` with server-side tokens.
"""

from __future__ import annotations

from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from apps.core.email_oauth import gmail_authorize_url, outlook_authorize_url
from apps.core.email_sync import _Http
from apps.core.models import EmailAccount, EmailMessage, Workspace

User = get_user_model()

OAUTH_SETTINGS = override_settings(
    GMAIL_CLIENT_ID="gmail-test",
    GMAIL_CLIENT_SECRET="gmail-secret",
    OUTLOOK_CLIENT_ID="outlook-test",
    OUTLOOK_CLIENT_SECRET="outlook-secret",
)


class EmailAuthorizeUrlTests(TestCase):
    def test_gmail_authorize_url_carries_client_redirect_scope_and_offline_access(self):
        url = gmail_authorize_url(client_id="gmail-test", redirect_uri="https://crm.structa.cloud/connect/email/gmail/callback/", state="state-1")
        self.assertIn("https://accounts.google.com/o/oauth2/v2/auth", url)
        self.assertIn("client_id=gmail-test", url)
        self.assertIn("gmail.readonly", url)
        self.assertIn("access_type=offline", url)
        self.assertIn("prompt=consent", url)
        self.assertIn("state=state-1", url)

    def test_outlook_authorize_url_carries_mail_and_offline_scopes(self):
        url = outlook_authorize_url(client_id="outlook-test", redirect_uri="https://crm.structa.cloud/connect/email/outlook/callback/", state="state-2")
        self.assertIn("https://login.microsoftonline.com/common/oauth2/v2.0/authorize", url)
        self.assertIn("client_id=outlook-test", url)
        self.assertIn("Mail.Read", url)
        self.assertIn("offline_access", url)
        self.assertIn("state=state-2", url)


class ConnectStartViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="seller", email="seller@example.com", password="Strong-pass-123")
        self.user.profile.workspace = Workspace.objects.create(name="Email workspace", slug="email-workspace")
        self.user.profile.save()
        self.client.force_login(self.user)

    @OAUTH_SETTINGS
    def test_gmail_connect_start_redirects_to_google_and_holds_state(self):
        response = self.client.get("/connect/email/gmail/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("https://accounts.google.com/o/oauth2/v2/auth", response.url)
        self.assertIn("state=", response.url)
        self.assertEqual(self.client.session["loop_email_oauth_provider"], "gmail")

    @OAUTH_SETTINGS
    def test_outlook_connect_start_redirects_to_microsoft_and_holds_state(self):
        response = self.client.get("/connect/email/outlook/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("https://login.microsoftonline.com/common/oauth2/v2.0/authorize", response.url)
        self.assertEqual(self.client.session["loop_email_oauth_provider"], "outlook")

    def test_unconfigured_client_redirects_honestly(self):
        response = self.client.get("/connect/email/gmail/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/settings/email/")
        self.assertFalse(EmailAccount.objects.exists())


class EmailInboxViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="seller", email="seller@example.com", password="Strong-pass-123")
        self.user.profile.workspace = Workspace.objects.create(name="Email workspace", slug="email-workspace")
        self.user.profile.save()
        self.client.force_login(self.user)

    @OAUTH_SETTINGS
    def test_email_inbox_renders_with_connect_actions(self):
        response = self.client.get("/settings/email/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Email inbox")
        self.assertContains(response, "Connect Gmail")
        self.assertContains(response, "Connect Outlook")

    def test_email_inbox_lists_connected_mailboxes(self):
        workspace = Workspace.objects.get(name="Email workspace")
        EmailAccount.objects.create(workspace=workspace, provider="gmail", email="me@gmail.com", oauth_token="tok")
        response = self.client.get("/settings/email/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "me@gmail.com")

    def test_email_inbox_deep_links_matched_messages_to_contact_and_deal(self):
        from apps.crm.models import Company, Contact, Deal, Pipeline

        workspace = Workspace.objects.get(name="Email workspace")
        account = EmailAccount.objects.create(
            workspace=workspace, provider="gmail", email="me@gmail.com", oauth_token="tok"
        )
        company = Company.objects.create(workspace=workspace, name="Acme")
        contact = Contact.objects.create(
            workspace=workspace, company=company, first_name="Ada", last_name="Lovelace", email="ada@acme.com"
        )
        pipeline = Pipeline.objects.create(workspace=workspace, name="Sales", is_default=True)
        deal = Deal.objects.create(
            workspace=workspace,
            company=company,
            contact=contact,
            pipeline=pipeline,
            name="Big deal",
            value="1000.00",
            expected_close_date="2026-12-31",
        )
        EmailMessage.objects.create(
            workspace=workspace,
            account=account,
            contact=contact,
            deal=deal,
            external_id="msg-1",
            subject="Contract review",
            sender_email="ada@acme.com",
            sender_name="Ada Lovelace",
            direction="inbound",
        )
        response = self.client.get("/settings/email/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Contract review")
        self.assertContains(response, f"/crm/contacts/#contact-{contact.pk}")
        self.assertContains(response, f"/crm/deals/#deal-{deal.pk}")


class CallbackViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="seller", email="seller@example.com", password="Strong-pass-123")
        self.user.profile.workspace = Workspace.objects.create(name="Email workspace", slug="email-workspace")
        self.user.profile.save()
        self.client.force_login(self.user)

    def _seed_session(self, provider: str, state: str) -> None:
        session = self.client.session
        session["loop_email_oauth_provider"] = provider
        session["loop_email_oauth_state"] = state
        session.save()

    @OAUTH_SETTINGS
    @mock.patch.object(_Http, "post_form", return_value=(200, {"access_token": "g-access", "refresh_token": "g-refresh", "expires_in": 86400}))
    @mock.patch.object(_Http, "get", return_value=(200, {"email": "me@gmail.com"}))
    def test_gmail_callback_creates_account_with_email_and_tokens(self, _get, _post_form):
        self._seed_session("gmail", "state-1")
        response = self.client.get("/connect/email/gmail/callback/?state=state-1&code=secret-code")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/settings/email/")

        account = EmailAccount.objects.get()
        self.assertEqual(account.provider, "gmail")
        self.assertEqual(account.email, "me@gmail.com")
        self.assertEqual(account.oauth_token, "g-access")
        self.assertEqual(account.oauth_refresh_token, "g-refresh")
        self.assertIsNotNone(account.token_expires_at)
        self.assertEqual(account.created_by, self.user)
        _post_form.assert_called_once()
        _get.assert_called_once()

    @OAUTH_SETTINGS
    @mock.patch.object(_Http, "post_form", return_value=(200, {"access_token": "o-access", "refresh_token": "o-refresh", "expires_in": 7200}))
    @mock.patch.object(_Http, "get", return_value=(200, {"mail": "me@outlook.com", "userPrincipalName": "me@outlook.com"}))
    def test_outlook_callback_uses_mail_identity(self, _get, _post_form):
        self._seed_session("outlook", "state-2")
        response = self.client.get("/connect/email/outlook/callback/?state=state-2&code=secret-code")
        self.assertEqual(response.status_code, 302)

        account = EmailAccount.objects.get()
        self.assertEqual(account.provider, "outlook")
        self.assertEqual(account.email, "me@outlook.com")
        self.assertEqual(account.oauth_token, "o-access")

    @OAUTH_SETTINGS
    @mock.patch.object(_Http, "post_form", return_value=(200, {"access_token": "g-access"}))
    @mock.patch.object(_Http, "get", return_value=(200, {"email": "me@gmail.com"}))
    def test_state_mismatch_rejects_without_creating_account(self, _get, _post_form):
        self._seed_session("gmail", "expected-state")
        response = self.client.get("/connect/email/gmail/callback/?state=wrong-state&code=secret-code")
        self.assertEqual(response.status_code, 302)
        self.assertFalse(EmailAccount.objects.exists())
        _post_form.assert_not_called()

    @OAUTH_SETTINGS
    @mock.patch.object(_Http, "post_form", return_value=(200, {"access_token": "g-access"}))
    @mock.patch.object(_Http, "get", return_value=(200, {"email": "me@gmail.com"}))
    def test_reconnect_updates_existing_account_instead_of_duplicating(self, _get, _post_form):
        workspace = Workspace.objects.get(name="Email workspace")
        EmailAccount.objects.create(workspace=workspace, provider="gmail", email="me@gmail.com", oauth_token="stale")
        self._seed_session("gmail", "state-1")
        self.client.get("/connect/email/gmail/callback/?state=state-1&code=secret-code")
        self.assertEqual(EmailAccount.objects.count(), 1)
        account = EmailAccount.objects.get()
        self.assertEqual(account.oauth_token, "g-access")
