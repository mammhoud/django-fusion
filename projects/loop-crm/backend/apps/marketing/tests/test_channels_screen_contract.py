"""Channels-screen contract: catalog platform count + per-platform capabilities.

Pins the render-first ``/marketing/channels/`` page to the connector catalog so
the platform count and each platform's capability labels stay in sync with
``apps.marketing.connectors.PLATFORM_CATALOG`` (the single source of truth).
"""
from __future__ import annotations

from django.contrib.auth.models import User
from django.test import TestCase

from apps.core.models import Workspace
from apps.marketing.connectors import platform_catalog


class ChannelsScreenContractTests(TestCase):
    def setUp(self):
        self.workspace = Workspace.objects.create(name="Channels", slug="channels")
        self.user = User.objects.create_user(
            username="channel-member", email="ch@example.com", password="Strong-pass-123"
        )
        self.user.profile.workspace = self.workspace
        self.user.profile.save()

    def test_catalog_count_matches_the_connector_catalog(self):
        self.client.force_login(self.user)
        response = self.client.get("/marketing/channels/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f"{len(platform_catalog())} platforms")

    def test_every_platform_renders_its_label_and_capability_set(self):
        self.client.force_login(self.user)
        response = self.client.get("/marketing/channels/")
        for platform in platform_catalog():
            self.assertContains(response, f'data-platform="{platform["id"]}"')
            self.assertContains(
                response,
                f'data-capabilities="{",".join(platform["capabilities"])}"',
            )
            self.assertContains(response, platform["label"])

    def test_capability_labels_match_the_catalog_exactly(self):
        self.client.force_login(self.user)
        response = self.client.get("/marketing/channels/")
        # Pinned spot-checks: "media" is advertised only where supported, and
        # the webhook platforms advertise publish alone.
        self.assertContains(response, "publish · analytics")
        self.assertContains(response, "publish · media · analytics")
        self.assertContains(response, 'data-platform="discord" data-capabilities="publish"')
        self.assertContains(response, 'data-platform="slack" data-capabilities="publish"')
