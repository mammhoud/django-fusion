"""Connector adapter tests — mocked HTTP, no network required."""
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from apps.marketing.connector_adapters import (
    BlueskyConnector,
    LinkedInConnector,
    MastodonConnector,
    XConnector,
)
from apps.marketing.connectors import UnconfiguredConnector, connector_for


def _channel(platform="linkedin", token="tok-123", account="urn:li:person:abc123"):
    return SimpleNamespace(platform=platform, oauth_token=token, oauth_refresh_token="refresh-1",
                           account_name=account, token_expires_at=None)


def _post(content="Hello from Loop CRM"):
    return SimpleNamespace(content=content, external_id="")


class DispatcherTests(SimpleTestCase):
    def test_unconfigured_channel_returns_safe_connector(self):
        connector = connector_for("linkedin", channel=_channel(token=""))
        self.assertIsInstance(connector, UnconfiguredConnector)

    def test_no_channel_returns_safe_connector(self):
        self.assertIsInstance(connector_for("twitter"), UnconfiguredConnector)

    def test_unknown_platform_with_token_stays_safe(self):
        connector = connector_for("slack", channel=_channel(token="x"))
        self.assertIsInstance(connector, UnconfiguredConnector)

    def test_configured_channel_returns_real_adapter(self):
        self.assertIsInstance(connector_for("linkedin", channel=_channel()), LinkedInConnector)
        self.assertIsInstance(connector_for("twitter", channel=_channel(platform="twitter")), XConnector)
        self.assertIsInstance(connector_for("mastodon", channel=_channel(platform="mastodon")), MastodonConnector)
        self.assertIsInstance(connector_for("bluesky", channel=_channel(platform="bluesky")), BlueskyConnector)


class LinkedInConnectorTests(SimpleTestCase):
    def test_publish_success_extracts_share_id(self):
        connector = LinkedInConnector(_channel())
        with patch("apps.marketing.connector_adapters._Http.post_json", return_value=(201, {"id": "urn:li:share:999"})) as call:
            result = connector.publish(_post())
        self.assertTrue(result.success)
        self.assertEqual(result.external_id, "urn:li:share:999")
        payload = call.call_args[0][2]
        self.assertEqual(payload["author"], "urn:li:person:abc123")
        self.assertEqual(payload["specificContent"]["com.linkedin.ugc.ShareContent"]["shareCommentary"]["text"], "Hello from Loop CRM")

    def test_publish_without_urn_fails_honestly(self):
        connector = LinkedInConnector(_channel(account="Northwind profile"))
        with patch("apps.marketing.connector_adapters._Http.post_json") as call:
            result = connector.publish(_post())
        self.assertFalse(result.success)
        self.assertIn("urn:li:", result.message)
        call.assert_not_called()

    def test_publish_rejected_returns_error_message(self):
        connector = LinkedInConnector(_channel())
        with patch("apps.marketing.connector_adapters._Http.post_json", return_value=(401, {"message": "expired"})):
            result = connector.publish(_post())
        self.assertFalse(result.success)
        self.assertIn("token", result.message.lower())

    def test_refresh_requires_client_id(self):
        connector = LinkedInConnector(_channel())
        with patch("django.conf.settings.LINKEDIN_CLIENT_ID", ""):
            self.assertFalse(connector.refresh())


class MastodonConnectorTests(SimpleTestCase):
    def test_publish_success_extracts_status_id(self):
        connector = MastodonConnector(_channel(platform="mastodon", account="alice@mastodon.social"))
        with patch("apps.marketing.connector_adapters._Http.post_form", return_value=(200, {"id": "109000"})) as call:
            result = connector.publish(_post())
        self.assertTrue(result.success)
        self.assertEqual(result.external_id, "109000")
        self.assertEqual(call.call_args[0][0], "https://mastodon.social/api/v1/statuses")
        self.assertEqual(call.call_args[0][1]["status"], "Hello from Loop CRM")
        self.assertEqual(call.call_args[1]["token"], "tok-123")

    def test_publish_without_token_fails_honestly(self):
        connector = MastodonConnector(_channel(platform="mastodon", token=""))
        with patch("apps.marketing.connector_adapters._Http.post_form") as call:
            result = connector.publish(_post())
        self.assertFalse(result.success)
        call.assert_not_called()


class BlueskyConnectorTests(SimpleTestCase):
    def test_publish_success_extracts_post_uri(self):
        connector = BlueskyConnector(_channel(platform="bluesky", account="alice.bsky.social", token="app-pass"))
        with patch(
            "apps.marketing.connector_adapters._Http.post_json",
            side_effect=[
                (200, {"accessJwt": "jwt-1", "did": "did:plc:alice"}),
                (200, {"uri": "at://did:plc:alice/app.bsky.feed.post/x"}),
            ],
        ) as call:
            result = connector.publish(_post())
        self.assertTrue(result.success)
        self.assertEqual(result.external_id, "at://did:plc:alice/app.bsky.feed.post/x")
        # Second call is the createRecord with the session JWT and record body.
        self.assertEqual(call.call_args[0][1], "jwt-1")
        self.assertEqual(call.call_args[0][2]["repo"], "did:plc:alice")
        self.assertEqual(call.call_args[0][2]["collection"], "app.bsky.feed.post")
        self.assertEqual(call.call_args[0][2]["record"]["text"], "Hello from Loop CRM")

    def test_publish_without_app_password_fails(self):
        connector = BlueskyConnector(_channel(platform="bluesky", token=""))
        with patch("apps.marketing.connector_adapters._Http.post_json") as call:
            result = connector.publish(_post())
        self.assertFalse(result.success)
        call.assert_not_called()

    def test_publish_with_failed_session_fails(self):
        connector = BlueskyConnector(_channel(platform="bluesky", account="alice.bsky.social", token="bad"))
        with patch("apps.marketing.connector_adapters._Http.post_json", return_value=(401, {"error": "InvalidIdentifierOrPassword"})):
            result = connector.publish(_post())
        self.assertFalse(result.success)
        self.assertIn("login", result.message.lower())


class XConnectorTests(SimpleTestCase):
    def test_publish_success_extracts_tweet_id(self):
        connector = XConnector(_channel(platform="twitter"))
        with patch("apps.marketing.connector_adapters._Http.post_json", return_value=(201, {"data": {"id": "tweet-42", "text": "ok"}})) as call:
            result = connector.publish(_post())
        self.assertTrue(result.success)
        self.assertEqual(result.external_id, "tweet-42")
        self.assertEqual(call.call_args[0][2], {"text": "Hello from Loop CRM"})

    def test_publish_without_token_fails(self):
        connector = XConnector(_channel(token=""))
        with patch("apps.marketing.connector_adapters._Http.post_json") as call:
            result = connector.publish(_post())
        self.assertFalse(result.success)
        call.assert_not_called()

    def test_analytics_maps_public_metrics(self):
        connector = XConnector(_channel(platform="twitter"))
        post = _post()
        post.external_id = "tweet-42"
        body = {"data": {"public_metrics": {"impression_count": 1200, "like_count": 8, "reply_count": 2, "retweet_count": 3}}}
        with patch("apps.marketing.connector_adapters._Http.get", return_value=(200, body)):
            metrics = connector.fetch_analytics(post)
        self.assertEqual(metrics, {"impressions": 1200, "likes": 8, "comments": 2, "shares": 3})

    def test_analytics_without_external_id_returns_empty(self):
        connector = XConnector(_channel(platform="twitter"))
        with patch("apps.marketing.connector_adapters._Http.get") as call:
            self.assertEqual(connector.fetch_analytics(_post()), {})
        call.assert_not_called()
