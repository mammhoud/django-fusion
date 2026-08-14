"""Tests for the LinkedIn / X (Twitter) OAuth connect flow and the
pre-publish token refresh in the publish actor."""
from __future__ import annotations

from datetime import timedelta
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone

from apps.core.models import Workspace
from apps.marketing.connector_adapters import _Http
from apps.marketing.models import SocialChannel
from apps.marketing.oauth import _pkce_pair, linkedin_authorize_url, x_authorize_url
from plugins.workers.tasks import _ensure_fresh_channel

User = get_user_model()

OAUTH_SETTINGS = override_settings(
    LINKEDIN_CLIENT_ID="li-test",
    LINKEDIN_CLIENT_SECRET="li-secret",
    X_CLIENT_ID="x-test",
    X_CLIENT_SECRET="x-secret",
)


class OAuthUrlBuilderTests(TestCase):
    def test_linkedin_authorize_url_carries_client_redirect_scope_and_state(self):
        url = linkedin_authorize_url(client_id="li-test", redirect_uri="https://crm.structa.cloud/connect/linkedin/callback/", state="abc123")
        self.assertIn("https://www.linkedin.com/oauth/v2/authorization", url)
        self.assertIn("client_id=li-test", url)
        self.assertIn("redirect_uri=https%3A%2F%2Fcrm.structa.cloud%2Fconnect%2Flinkedin%2Fcallback%2F", url)
        self.assertIn("state=abc123", url)
        self.assertIn("w_member_social", url)

    def test_x_authorize_url_uses_pkce_challenge(self):
        verifier, challenge = _pkce_pair()
        url = x_authorize_url(client_id="x-test", redirect_uri="https://crm.structa.cloud/connect/twitter/callback/", state="abc123", code_challenge=challenge)
        self.assertIn("https://twitter.com/i/oauth2/authorize", url)
        self.assertIn("code_challenge=", url)
        self.assertIn("code_challenge_method=S256", url)
        self.assertIn("tweet.write", url)
        self.assertIn("offline.access", url)
        self.assertNotIn(verifier, url, "The PKCE verifier must never leave the server.")

    def test_pkce_pair_verifier_challenge_roundtrip(self):
        verifier, challenge = _pkce_pair()
        self.assertGreaterEqual(len(verifier), 43)
        self.assertTrue(challenge)


class ConnectStartViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="marketer", email="marketer@example.com", password="Strong-pass-123")
        self.user.profile.workspace = Workspace.objects.create(name="OAuth workspace", slug="oauth-workspace")
        self.user.profile.save()
        self.client.force_login(self.user)

    @OAUTH_SETTINGS
    def test_linkedin_connect_start_redirects_to_provider_and_holds_state(self):
        response = self.client.get("/connect/linkedin/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("https://www.linkedin.com/oauth/v2/authorization", response.url)
        self.assertIn("state=", response.url)
        self.assertEqual(self.client.session["loop_oauth_platform"], "linkedin")

    @OAUTH_SETTINGS
    def test_x_connect_start_stores_pkce_verifier_in_session(self):
        response = self.client.get("/connect/twitter/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("https://twitter.com/i/oauth2/authorize", response.url)
        self.assertIn("code_challenge=", response.url)
        self.assertIn("loop_pkce_verifier", self.client.session)

    def test_unconfigured_client_redirects_honestly(self):
        response = self.client.get("/connect/linkedin/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/marketing/calendar/")
        self.assertFalse(SocialChannel.objects.exists())


class CallbackViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="marketer", email="marketer@example.com", password="Strong-pass-123")
        self.user.profile.workspace = Workspace.objects.create(name="OAuth workspace", slug="oauth-workspace")
        self.user.profile.save()
        self.client.force_login(self.user)

    def _seed_session(self, platform: str, state: str, verifier: str | None = None) -> None:
        session = self.client.session
        session["loop_oauth_platform"] = platform
        session["loop_oauth_state"] = state
        if verifier:
            session["loop_pkce_verifier"] = verifier
        session.save()

    @OAUTH_SETTINGS
    @mock.patch.object(_Http, "post_form", return_value=(200, {"access_token": "li-access", "refresh_token": "li-refresh", "expires_in": 86400}))
    @mock.patch.object(_Http, "get", return_value=(200, {"sub": "person-123", "name": "Ada Lovelace"}))
    def test_linkedin_callback_creates_channel_with_urn_and_tokens(self, _get, _post_form):
        self._seed_session("linkedin", "state-1")
        response = self.client.get("/connect/linkedin/callback/?state=state-1&code=secret-code")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/marketing/calendar/")

        channel = SocialChannel.objects.get()
        self.assertEqual(channel.platform, "linkedin")
        self.assertEqual(channel.account_name, "urn:li:person:person-123")
        self.assertEqual(channel.oauth_token, "li-access")
        self.assertEqual(channel.oauth_refresh_token, "li-refresh")
        self.assertIsNotNone(channel.token_expires_at)
        _post_form.assert_called_once()
        _get.assert_called_once()

    @OAUTH_SETTINGS
    @mock.patch.object(_Http, "post_form", return_value=(200, {"access_token": "x-access", "refresh_token": "x-refresh", "expires_in": 7200}))
    @mock.patch.object(_Http, "get", return_value=(200, {"data": {"id": "42", "username": "structa", "name": "Structa"}}))
    def test_x_callback_uses_pkce_verifier_and_stores_username(self, _get, _post_form):
        self._seed_session("twitter", "state-2", verifier="pkce-verifier-value")
        response = self.client.get("/connect/twitter/callback/?state=state-2&code=secret-code")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/marketing/calendar/")

        channel = SocialChannel.objects.get()
        self.assertEqual(channel.platform, "twitter")
        self.assertEqual(channel.account_name, "structa")
        self.assertEqual(channel.oauth_token, "x-access")
        # The verifier is consumed from the session.
        self.assertNotIn("loop_pkce_verifier", self.client.session)

    @OAUTH_SETTINGS
    @mock.patch.object(_Http, "post_form", return_value=(200, {"access_token": "li-access"}))
    @mock.patch.object(_Http, "get", return_value=(200, {"sub": "person-123"}))
    def test_state_mismatch_rejects_without_creating_channel(self, _get, _post_form):
        self._seed_session("linkedin", "expected-state")
        response = self.client.get("/connect/linkedin/callback/?state=wrong-state&code=secret-code")
        self.assertEqual(response.status_code, 302)
        self.assertFalse(SocialChannel.objects.exists())
        _post_form.assert_not_called()


class TokenRefreshTests(TestCase):
    @OAUTH_SETTINGS
    @mock.patch.object(_Http, "post_form", return_value=(200, {"access_token": "fresh-access", "refresh_token": "fresh-refresh", "expires_in": 86400}))
    def test_ensure_fresh_channel_refreshes_expired_token_through_adapter(self, _post_form):
        workspace = Workspace.objects.create(name="Refresh workspace", slug="refresh-workspace")
        channel = SocialChannel.objects.create(
            workspace=workspace,
            platform="linkedin",
            account_name="urn:li:person:p1",
            oauth_token="stale-access",
            oauth_refresh_token="stale-refresh",
            token_expires_at=timezone.now() - timedelta(minutes=1),
        )
        self.assertTrue(_ensure_fresh_channel(channel))
        channel.refresh_from_db()
        self.assertEqual(channel.oauth_token, "fresh-access")
        self.assertEqual(channel.oauth_refresh_token, "fresh-refresh")

    def test_ensure_fresh_channel_leaves_untokenized_channel_alone(self):
        workspace = Workspace.objects.create(name="Refresh workspace", slug="refresh-workspace")
        channel = SocialChannel.objects.create(workspace=workspace, platform="twitter", account_name="structa")
        self.assertFalse(_ensure_fresh_channel(channel))
        self.assertEqual(channel.oauth_token, "")

    def test_ensure_fresh_channel_keeps_unexpired_token(self):
        workspace = Workspace.objects.create(name="Refresh workspace", slug="refresh-workspace")
        channel = SocialChannel.objects.create(
            workspace=workspace,
            platform="twitter",
            account_name="structa",
            oauth_token="valid-access",
            token_expires_at=timezone.now() + timedelta(hours=1),
        )
        self.assertTrue(_ensure_fresh_channel(channel))
        self.assertEqual(channel.oauth_token, "valid-access")
