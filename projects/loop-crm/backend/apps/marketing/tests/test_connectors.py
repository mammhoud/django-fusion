"""Connector adapter tests — mocked HTTP, no network required."""
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from apps.marketing.connector_adapters import LinkedInConnector, XConnector
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
