"""Manual (non-OAuth) channel connect-flow tests.

The catalog platforms store a credential (access token or webhook URL) without
a redirect OAuth flow. These tests pin the form surface, the credential
storage path, and the tenant boundary.
"""
from __future__ import annotations

from django.contrib.auth.models import User
from django.test import TestCase

from apps.core.models import Workspace
from apps.marketing.models import SocialChannel


class ChannelConnectTests(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name="Connect", slug="connect")
        self.other = Workspace.objects.create(name="Connect Other", slug="connect-other")
        self.user = User.objects.create_user(
            username="connector", email="c@example.com", password="Strong-pass-123"
        )
        self.user.profile.workspace = self.workspace
        self.user.profile.save()

    def _post(self, **overrides):
        data = {
            "platform": "slack",
            "account_name": "#general",
            "credential": "https://hooks.slack.com/services/T/B/X",
            "refresh_token": "",
        }
        data.update(overrides)
        return self.client.post(
            "/fragments/marketing/channels/connect/", data, HTTP_HX_REQUEST="true"
        )

    def test_get_renders_form_with_all_catalog_platforms(self):
        self.client.force_login(self.user)
        response = self.client.get("/fragments/marketing/channels/connect/")
        self.assertEqual(response.status_code, 200)
        for platform in ("instagram", "facebook", "tiktok", "youtube", "reddit", "discord", "slack", "whatsapp"):
            self.assertContains(response, platform)

    def test_post_creates_channel_with_stored_credential(self):
        self.client.force_login(self.user)
        response = self._post()
        self.assertEqual(response.status_code, 200)
        channel = SocialChannel.objects.get(
            workspace=self.workspace, platform="slack", account_name="#general"
        )
        self.assertEqual(channel.oauth_token, "https://hooks.slack.com/services/T/B/X")
        self.assertTrue(channel.is_active)
        self.assertContains(response, "#general")

    def test_reconnect_updates_credential_in_place(self):
        self.client.force_login(self.user)
        self._post()
        response = self._post(credential="https://hooks.slack.com/services/T/B/REFRESHED")
        self.assertEqual(response.status_code, 200)
        channels = SocialChannel.objects.filter(
            workspace=self.workspace, platform="slack", account_name="#general"
        )
        self.assertEqual(channels.count(), 1)
        self.assertEqual(channels.get().oauth_token, "https://hooks.slack.com/services/T/B/REFRESHED")

    def test_missing_credential_returns_422_and_stores_nothing(self):
        self.client.force_login(self.user)
        response = self._post(credential="")
        self.assertEqual(response.status_code, 422)
        self.assertFalse(SocialChannel.objects.filter(workspace=self.workspace, platform="slack").exists())

    def test_unauthenticated_request_redirects_to_login(self):
        response = self._post()
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_member_without_workspace_is_forbidden(self):
        other = User.objects.create_user(
            username="nows", email="n@example.com", password="Strong-pass-123"
        )
        self.client.force_login(other)
        response = self._post()
        self.assertEqual(response.status_code, 403)
        self.assertFalse(SocialChannel.objects.filter(platform="slack").exists())

    def test_created_channel_is_scoped_to_the_callers_workspace(self):
        self.client.force_login(self.user)
        self._post()
        self.assertTrue(
            SocialChannel.objects.filter(
                workspace=self.workspace, platform="slack", account_name="#general"
            ).exists()
        )
        self.assertFalse(
            SocialChannel.objects.filter(
                workspace=self.other, platform="slack", account_name="#general"
            ).exists()
        )

    def test_channels_page_renders_the_connect_form(self):
        self.client.force_login(self.user)
        response = self.client.get("/marketing/channels/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="channel-connect-form"')
        self.assertContains(response, "Store a provider credential")
