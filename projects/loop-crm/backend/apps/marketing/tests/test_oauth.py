"""Tests for the redirect-OAuth connect flows (LinkedIn, X, Meta
Facebook/Instagram/WhatsApp, TikTok, YouTube, Reddit) and the pre-publish
token refresh in the publish actor."""
from __future__ import annotations

from datetime import timedelta
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone
from plugins.workers.tasks import _ensure_fresh_channel

from apps.core.models import Workspace
from apps.marketing.connector_adapters import _Http
from apps.marketing.models import SocialChannel
from apps.marketing.oauth import (
    META_SCOPES,
    _pkce_pair,
    linkedin_authorize_url,
    meta_authorize_url,
    reddit_authorize_url,
    tiktok_authorize_url,
    x_authorize_url,
    youtube_authorize_url,
)

User = get_user_model()

OAUTH_SETTINGS = override_settings(
    LINKEDIN_CLIENT_ID="li-test",
    LINKEDIN_CLIENT_SECRET="li-secret",
    X_CLIENT_ID="x-test",
    X_CLIENT_SECRET="x-secret",
    GOOGLE_CLIENT_ID="google-test",
    GOOGLE_CLIENT_SECRET="google-secret",
    META_CLIENT_ID="meta-test",
    META_CLIENT_SECRET="meta-secret",
    TIKTOK_CLIENT_KEY="tiktok-key",
    TIKTOK_CLIENT_SECRET="tiktok-secret",
    REDDIT_CLIENT_ID="reddit-test",
    REDDIT_CLIENT_SECRET="reddit-secret",
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

    def test_meta_authorize_url_uses_dialog_with_per_platform_scopes(self):
        url = meta_authorize_url(
            client_id="meta-test",
            redirect_uri="https://crm.structa.cloud/connect/facebook/callback/",
            state="abc123",
            scope=META_SCOPES["facebook"],
        )
        self.assertIn("https://www.facebook.com/", url)
        self.assertIn("/dialog/oauth", url)
        self.assertIn("client_id=meta-test", url)
        self.assertIn("state=abc123", url)
        self.assertIn("pages_manage_posts", url)
        self.assertIn("instagram_basic", meta_authorize_url(client_id="m", redirect_uri="r", state="s", scope=META_SCOPES["instagram"]))
        self.assertIn("whatsapp_business_messaging", meta_authorize_url(client_id="m", redirect_uri="r", state="s", scope=META_SCOPES["whatsapp"]))

    def test_tiktok_authorize_url_carries_client_key_scopes_and_state(self):
        url = tiktok_authorize_url(client_key="tiktok-key", redirect_uri="https://crm.structa.cloud/connect/tiktok/callback/", state="abc123")
        self.assertIn("https://www.tiktok.com/v2/auth/authorize/", url)
        self.assertIn("client_key=tiktok-key", url)
        self.assertIn("video.publish", url)
        self.assertIn("state=abc123", url)

    def test_youtube_authorize_url_uses_offline_consent(self):
        url = youtube_authorize_url(client_id="google-test", redirect_uri="https://crm.structa.cloud/connect/youtube/callback/", state="abc123")
        self.assertIn("https://accounts.google.com/o/oauth2/v2/auth", url)
        self.assertIn("access_type=offline", url)
        self.assertIn("prompt=consent", url)
        self.assertIn("youtube.upload", url)
        self.assertIn("youtube.readonly", url)
        self.assertIn("state=abc123", url)

    def test_reddit_authorize_url_requests_permanent_submit_token(self):
        url = reddit_authorize_url(client_id="reddit-test", redirect_uri="https://crm.structa.cloud/connect/reddit/callback/", state="abc123")
        self.assertIn("https://www.reddit.com/api/v1/authorize", url)
        self.assertIn("client_id=reddit-test", url)
        self.assertIn("duration=permanent", url)
        self.assertIn("scope=identity+submit", url)
        self.assertIn("state=abc123", url)


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

    @OAUTH_SETTINGS
    def test_meta_connect_start_redirects_to_graph_dialog(self):
        for platform, scope_fragment in (
            ("facebook", "pages_manage_posts"),
            ("instagram", "instagram_content_publish"),
            ("whatsapp", "whatsapp_business_messaging"),
        ):
            response = self.client.get(f"/connect/{platform}/")
            self.assertEqual(response.status_code, 302)
            self.assertIn("https://www.facebook.com/", response.url)
            self.assertIn("/dialog/oauth", response.url)
            self.assertIn(scope_fragment, response.url)

    @OAUTH_SETTINGS
    def test_tiktok_connect_start_redirects_to_tiktok_authorize(self):
        response = self.client.get("/connect/tiktok/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("https://www.tiktok.com/v2/auth/authorize/", response.url)
        self.assertIn("client_key=tiktok-key", response.url)

    @OAUTH_SETTINGS
    def test_youtube_connect_start_redirects_to_google_consent(self):
        response = self.client.get("/connect/youtube/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("https://accounts.google.com/o/oauth2/v2/auth", response.url)
        self.assertIn("client_id=google-test", response.url)

    @OAUTH_SETTINGS
    def test_reddit_connect_start_redirects_to_reddit_authorize(self):
        response = self.client.get("/connect/reddit/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("https://www.reddit.com/api/v1/authorize", response.url)
        self.assertIn("duration=permanent", response.url)

    def test_meta_unconfigured_redirects_honestly(self):
        response = self.client.get("/connect/facebook/")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/marketing/calendar/")
        self.assertFalse(SocialChannel.objects.exists())

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

    @OAUTH_SETTINGS
    @mock.patch.object(
        _Http,
        "post_form",
        side_effect=[
            (200, {"access_token": "short-token"}),
            (200, {"access_token": "long-token", "expires_in": 5_184_000}),
        ],
    )
    @mock.patch.object(
        _Http,
        "_request",
        return_value=(200, {"data": [{"id": "page-7", "name": "Northline Studio"}]}),
    )
    def test_facebook_callback_exchanges_long_lived_token_and_stores_page(self, _request, _post_form):
        self._seed_session("facebook", "state-fb")
        response = self.client.get("/connect/facebook/callback/?state=state-fb&code=secret-code")
        self.assertEqual(response.status_code, 302)
        channel = SocialChannel.objects.get()
        self.assertEqual(channel.platform, "facebook")
        self.assertEqual(channel.account_name, "Northline Studio")
        self.assertEqual(channel.oauth_token, "long-token")
        self.assertEqual(_post_form.call_count, 2, "short code exchange + long-lived upgrade")

    @OAUTH_SETTINGS
    @mock.patch.object(
        _Http,
        "post_form",
        side_effect=[
            (200, {"access_token": "short-token"}),
            (200, {"access_token": "ig-token", "expires_in": 5_184_000}),
        ],
    )
    @mock.patch.object(
        _Http,
        "_request",
        return_value=(
            200,
            {
                "data": [
                    {"id": "page-1", "name": "Northline", "instagram_business_account": {"id": "1784140000", "username": "northline"}}
                ]
            },
        ),
    )
    def test_instagram_callback_resolves_linked_ig_business_account(self, _request, _post_form):
        self._seed_session("instagram", "state-ig")
        response = self.client.get("/connect/instagram/callback/?state=state-ig&code=secret-code")
        self.assertEqual(response.status_code, 302)
        channel = SocialChannel.objects.get()
        self.assertEqual(channel.platform, "instagram")
        self.assertEqual(channel.account_name, "northline")
        self.assertEqual(channel.oauth_token, "ig-token")

    @OAUTH_SETTINGS
    @mock.patch.object(
        _Http,
        "post_form",
        side_effect=[
            (200, {"access_token": "short-token"}),
            (200, {"access_token": "wa-token", "expires_in": 5_184_000}),
        ],
    )
    @mock.patch.object(
        _Http,
        "_request",
        side_effect=[
            (200, {"data": [{"id": "business-1", "name": "Northline Ltd"}]}),
            (200, {"data": [{"id": "waba-9", "name": "Northline WhatsApp"}]}),
            (200, {"data": [{"id": "12345", "display_phone_number": "+15551234567"}]}),
        ],
    )
    def test_whatsapp_callback_resolves_business_to_phone_number(self, _request, _post_form):
        self._seed_session("whatsapp", "state-wa")
        response = self.client.get("/connect/whatsapp/callback/?state=state-wa&code=secret-code")
        self.assertEqual(response.status_code, 302)
        channel = SocialChannel.objects.get()
        self.assertEqual(channel.platform, "whatsapp")
        self.assertEqual(channel.account_name, "+15551234567")
        self.assertEqual(channel.oauth_token, "wa-token")
        self.assertEqual(_request.call_count, 3, "business → WABA → phone number hops")

    @OAUTH_SETTINGS
    @mock.patch.object(
        _Http,
        "post_form",
        return_value=(
            200,
            {"access_token": "tk-token", "open_id": "open-id-1", "expires_in": 86_400, "refresh_token": "tk-refresh"},
        ),
    )
    def test_tiktok_callback_uses_open_id_as_account_name(self, _post_form):
        self._seed_session("tiktok", "state-tk")
        response = self.client.get("/connect/tiktok/callback/?state=state-tk&code=secret-code")
        self.assertEqual(response.status_code, 302)
        channel = SocialChannel.objects.get()
        self.assertEqual(channel.platform, "tiktok")
        self.assertEqual(channel.account_name, "open-id-1")
        self.assertEqual(channel.oauth_token, "tk-token")
        self.assertEqual(channel.oauth_refresh_token, "tk-refresh")
        _post_form.assert_called_once()

    @OAUTH_SETTINGS
    @mock.patch.object(
        _Http,
        "post_form",
        return_value=(
            200,
            {"access_token": "yt-token", "refresh_token": "yt-refresh", "expires_in": 3599},
        ),
    )
    @mock.patch.object(
        _Http,
        "get",
        return_value=(200, {"items": [{"id": "channel-1", "snippet": {"title": "Northline Studio"}}]}),
    )
    def test_youtube_callback_stores_channel_title(self, _get, _post_form):
        self._seed_session("youtube", "state-yt")
        response = self.client.get("/connect/youtube/callback/?state=state-yt&code=secret-code")
        self.assertEqual(response.status_code, 302)
        channel = SocialChannel.objects.get()
        self.assertEqual(channel.platform, "youtube")
        self.assertEqual(channel.account_name, "Northline Studio")
        self.assertEqual(channel.oauth_token, "yt-token")
        self.assertEqual(channel.oauth_refresh_token, "yt-refresh")

    @OAUTH_SETTINGS
    @mock.patch.object(
        _Http,
        "post_form",
        return_value=(
            200,
            {"access_token": "rd-token", "refresh_token": "rd-refresh", "expires_in": 86_400},
        ),
    )
    @mock.patch.object(_Http, "_request", return_value=(200, {"name": "loopcrm-user"}))
    def test_reddit_callback_sends_basic_auth_and_stores_username(self, _request, _post_form):
        self._seed_session("reddit", "state-rd")
        response = self.client.get("/connect/reddit/callback/?state=state-rd&code=secret-code")
        self.assertEqual(response.status_code, 302)
        channel = SocialChannel.objects.get()
        self.assertEqual(channel.platform, "reddit")
        self.assertEqual(channel.account_name, "loopcrm-user")
        self.assertEqual(channel.oauth_token, "rd-token")
        exchange_headers = _post_form.call_args.kwargs["extra_headers"]
        self.assertIn("Basic ", exchange_headers["Authorization"])
        self.assertIn("User-Agent", exchange_headers)
        identity_headers = _request.call_args.kwargs["headers"]
        self.assertEqual(identity_headers["Authorization"], "Bearer rd-token")
        self.assertIn("User-Agent", identity_headers)


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
