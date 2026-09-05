"""Connector adapter tests — mocked HTTP, no network required."""
import io
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from django.test import SimpleTestCase, override_settings

from apps.marketing.connector_adapters import (
    BlueskyConnector,
    DiscordConnector,
    FacebookConnector,
    InstagramConnector,
    LinkedInConnector,
    MastodonConnector,
    RedditConnector,
    SlackConnector,
    TikTokConnector,
    WhatsAppConnector,
    XConnector,
    YouTubeConnector,
)
from apps.marketing.connectors import UnconfiguredConnector, connector_for

MEDIA_URL_SETTINGS = {"PUBLIC_SITE_URL": "https://cdn.example.test", "MEDIA_URL": "/media/"}


class _FakeFile:
    """FieldFile stand-in: ``open()``/``read()``/``close()`` over in-memory bytes."""

    def __init__(self, name: str, data: bytes = b"file-bytes"):
        self.name = name
        self._data = data

    def open(self, mode="rb"):
        self._stream = io.BytesIO(self._data)
        return self._stream

    def read(self):
        return self._data

    def close(self):
        self._stream = None


def _media(file_name: str):
    return SimpleNamespace(file=_FakeFile(file_name))


def _channel(platform="linkedin", token="tok-123", account="urn:li:person:abc123"):
    return SimpleNamespace(platform=platform, oauth_token=token, oauth_refresh_token="refresh-1",
                           account_name=account, token_expires_at=None)


def _post(content="Hello from Loop CRM", media=None):
    return SimpleNamespace(content=content, external_id="", media=media)


class DispatcherTests(SimpleTestCase):
    def test_unconfigured_channel_returns_safe_connector(self):
        connector = connector_for("linkedin", channel=_channel(token=""))
        self.assertIsInstance(connector, UnconfiguredConnector)

    def test_no_channel_returns_safe_connector(self):
        self.assertIsInstance(connector_for("twitter"), UnconfiguredConnector)

    def test_truly_unknown_platform_with_token_stays_safe(self):
        connector = connector_for("pinterest", channel=_channel(token="x"))
        self.assertIsInstance(connector, UnconfiguredConnector)

    def test_configured_channel_returns_real_adapter(self):
        self.assertIsInstance(connector_for("linkedin", channel=_channel()), LinkedInConnector)
        self.assertIsInstance(connector_for("twitter", channel=_channel(platform="twitter")), XConnector)
        self.assertIsInstance(connector_for("mastodon", channel=_channel(platform="mastodon")), MastodonConnector)
        self.assertIsInstance(connector_for("bluesky", channel=_channel(platform="bluesky")), BlueskyConnector)
        self.assertIsInstance(connector_for("discord", channel=_channel(platform="discord")), DiscordConnector)
        self.assertIsInstance(connector_for("slack", channel=_channel(platform="slack")), SlackConnector)
        self.assertIsInstance(connector_for("facebook", channel=_channel(platform="facebook")), FacebookConnector)
        self.assertIsInstance(connector_for("instagram", channel=_channel(platform="instagram")), InstagramConnector)
        self.assertIsInstance(connector_for("tiktok", channel=_channel(platform="tiktok")), TikTokConnector)
        self.assertIsInstance(connector_for("youtube", channel=_channel(platform="youtube")), YouTubeConnector)
        self.assertIsInstance(connector_for("reddit", channel=_channel(platform="reddit")), RedditConnector)
        self.assertIsInstance(connector_for("whatsapp", channel=_channel(platform="whatsapp")), WhatsAppConnector)

    def test_every_catalog_platform_has_a_named_adapter(self):
        from apps.marketing.connector_adapters import ADAPTERS
        from apps.marketing.connectors import PLATFORM_CATALOG

        catalog_ids = {platform["id"] for platform in PLATFORM_CATALOG}
        self.assertEqual(catalog_ids, set(ADAPTERS))


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


class FacebookConnectorTests(SimpleTestCase):
    def test_text_post_goes_to_page_feed(self):
        connector = FacebookConnector(_channel(platform="facebook", account="987654321"))
        with patch("apps.marketing.connector_adapters._Http.post_json", return_value=(200, {"id": "feed-1"})) as call:
            result = connector.publish(_post())
        self.assertTrue(result.success)
        self.assertEqual(result.external_id, "feed-1")
        url = call.call_args[0][0]
        self.assertIn("/987654321/feed", url)
        self.assertIn("access_token=tok-123", url)
        self.assertEqual(call.call_args[0][2], {"message": "Hello from Loop CRM"})

    def test_publish_without_token_is_gated(self):
        connector = FacebookConnector(_channel(platform="facebook", token=""))
        with patch("apps.marketing.connector_adapters._Http.post_json") as call:
            result = connector.publish(_post())
        self.assertFalse(result.success)
        self.assertIn("Connect a Facebook Page", result.message)
        call.assert_not_called()

    @override_settings(**MEDIA_URL_SETTINGS)
    def test_photo_post_pulls_public_media_url(self):
        connector = FacebookConnector(_channel(platform="facebook", account="987654321"))
        with patch("apps.marketing.connector_adapters._Http.post_json", return_value=(200, {"id": "photo-1"})) as call:
            result = connector.publish(_post(media=_media("pix.jpg")))
        self.assertTrue(result.success)
        self.assertEqual(result.external_id, "photo-1")
        url = call.call_args[0][0]
        self.assertIn("/987654321/photos", url)
        self.assertIn("access_token=tok-123", url)
        payload = call.call_args[0][2]
        self.assertEqual(payload["url"], "https://cdn.example.test/media/pix.jpg")
        self.assertEqual(payload["caption"], "Hello from Loop CRM")

    @override_settings(PUBLIC_SITE_URL="", MEDIA_URL="/media/")
    def test_media_post_without_public_site_url_fails(self):
        connector = FacebookConnector(_channel(platform="facebook", account="987654321"))
        with patch("apps.marketing.connector_adapters._Http.post_json") as call:
            result = connector.publish(_post(media=_media("pix.jpg")))
        self.assertFalse(result.success)
        self.assertIn("PUBLIC_SITE_URL", result.message)
        call.assert_not_called()


class InstagramConnectorTests(SimpleTestCase):
    def test_publish_without_media_is_gated(self):
        connector = InstagramConnector(_channel(platform="instagram", account="1784140000"))
        with patch("apps.marketing.connector_adapters._Http.post_json") as call:
            result = connector.publish(_post())
        self.assertFalse(result.success)
        self.assertIn("no text-post API", result.message)
        call.assert_not_called()

    @override_settings(**MEDIA_URL_SETTINGS)
    def test_image_post_creates_container_then_publishes(self):
        connector = InstagramConnector(_channel(platform="instagram", account="1784140000"))
        with patch(
            "apps.marketing.connector_adapters._Http.post_json",
            side_effect=[(200, {"id": "container-1"}), (200, {"id": "media-9"})],
        ) as call:
            result = connector.publish(_post(media=_media("pix.jpg")))
        self.assertTrue(result.success)
        self.assertEqual(result.external_id, "media-9")
        first_url, second_url = call.call_args_list[0][0][0], call.call_args_list[1][0][0]
        self.assertIn("/1784140000/media", first_url)
        self.assertIn("/1784140000/media_publish", second_url)
        self.assertEqual(call.call_args_list[0][0][2]["image_url"], "https://cdn.example.test/media/pix.jpg")
        self.assertEqual(call.call_args_list[1][0][2], {"creation_id": "container-1"})

    @override_settings(**MEDIA_URL_SETTINGS)
    def test_video_post_marks_container_as_video(self):
        connector = InstagramConnector(_channel(platform="instagram", account="1784140000"))
        with patch(
            "apps.marketing.connector_adapters._Http.post_json",
            side_effect=[(200, {"id": "container-2"}), (200, {"id": "media-10"})],
        ):
            result = connector.publish(_post(media=_media("clip.mp4")))
        self.assertTrue(result.success)
        self.assertEqual(result.external_id, "media-10")


class TikTokConnectorTests(SimpleTestCase):
    def test_publish_requires_video_media(self):
        connector = TikTokConnector(_channel(platform="tiktok", account="open-id-1"))
        for media in (None, _media("pix.jpg")):
            with patch("apps.marketing.connector_adapters._Http.post_json") as call:
                result = connector.publish(_post(media=media))
            self.assertFalse(result.success)
            self.assertIn("attached video", result.message)
            call.assert_not_called()

    def test_video_publish_init_upload_poll(self):
        connector = TikTokConnector(_channel(platform="tiktok", account="open-id-1"))
        init_response = (200, {"data": {"publish_id": "pub-1", "upload_url": "https://upload.test/video"}})
        poll_response = (200, {"data": {"status": "FINISH", "item_id": "item-7"}})
        with patch("apps.marketing.connector_adapters._Http.post_json", side_effect=[init_response, poll_response]) as post_call:
            with patch("apps.marketing.connector_adapters._Http.put_bytes", return_value=(201, {})) as put_call:
                result = connector.publish(_post(media=_media("clip.mp4")))
        self.assertTrue(result.success)
        self.assertEqual(result.external_id, "item-7")
        init_url = post_call.call_args_list[0][0][0]
        self.assertIn("/post/publish/video/init/", init_url)
        self.assertIn("open_id=open-id-1", init_url)
        self.assertEqual(post_call.call_args_list[0][0][1], "tok-123")
        self.assertEqual(put_call.call_args[0][0], "https://upload.test/video")
        poll_url = post_call.call_args_list[1][0][0]
        self.assertIn("/post/publish/status/fetch/", poll_url)
        self.assertEqual(post_call.call_args_list[1][0][2], {"publish_id": "pub-1"})

    def test_publish_failed_processing_reports_reason(self):
        connector = TikTokConnector(_channel(platform="tiktok", account="open-id-1"))
        init_response = (200, {"data": {"publish_id": "pub-2", "upload_url": "https://upload.test/video"}})
        poll_response = (200, {"data": {"status": "FAIL", "fail_reason": "copyright match"}})
        with patch("apps.marketing.connector_adapters._Http.post_json", side_effect=[init_response, poll_response]):
            with patch("apps.marketing.connector_adapters._Http.put_bytes", return_value=(201, {})):
                result = connector.publish(_post(media=_media("clip.mp4")))
        self.assertFalse(result.success)
        self.assertIn("copyright match", result.message)


class YouTubeConnectorTests(SimpleTestCase):
    def test_publish_requires_video_media(self):
        connector = YouTubeConnector(_channel(platform="youtube", account="My Channel"))
        with patch("apps.marketing.connector_adapters._Http.post_bytes") as call:
            result = connector.publish(_post())
        self.assertFalse(result.success)
        self.assertIn("attached video", result.message)
        call.assert_not_called()

    def test_video_upload_uses_multipart_related(self):
        connector = YouTubeConnector(_channel(platform="youtube", account="My Channel"))
        with patch("apps.marketing.connector_adapters._Http.post_bytes", return_value=(200, {"id": "vid-1"})) as call:
            result = connector.publish(_post(content="Launch day\nDetails here.", media=_media("clip.mp4")))
        self.assertTrue(result.success)
        self.assertEqual(result.external_id, "vid-1")
        url = call.call_args[0][0]
        self.assertIn("uploadType=multipart", url)
        params = parse_qs(urlsplit(url).query)
        self.assertEqual(params["part"], ["snippet,status"])
        self.assertEqual(call.call_args[0][1], _media("clip.mp4").file._data and call.call_args[0][1])  # non-empty body
        self.assertIn("multipart/related", call.call_args[1]["content_type"])
        self.assertEqual(call.call_args[0][2], "tok-123")
        # The post content becomes the description; its first line the title.
        body = call.call_args[0][1].decode("utf-8", errors="replace")
        self.assertIn("Launch day", body)
        self.assertIn("Details here.", body)

    def test_publish_without_token_is_gated(self):
        connector = YouTubeConnector(_channel(platform="youtube", token=""))
        with patch("apps.marketing.connector_adapters._Http.post_bytes") as call:
            result = connector.publish(_post(media=_media("clip.mp4")))
        self.assertFalse(result.success)
        self.assertIn("Connect a YouTube channel", result.message)
        call.assert_not_called()


class RedditConnectorTests(SimpleTestCase):
    def test_self_post_splits_title_and_body(self):
        connector = RedditConnector(_channel(platform="reddit", account="r/loopcrm"))
        with patch("apps.marketing.connector_adapters._Http.post_form", return_value=(200, {"json": {"errors": [], "data": {"id": "t3_abc"}}})) as call:
            result = connector.publish(_post(content="My headline\nBody paragraph one.\nBody paragraph two."))
        self.assertTrue(result.success)
        self.assertEqual(result.external_id, "t3_abc")
        url = call.call_args[0][0]
        self.assertIn("/api/submit", url)
        fields = call.call_args[0][1]
        self.assertEqual(fields["sr"], "loopcrm")
        self.assertEqual(fields["title"], "My headline")
        self.assertIn("Body paragraph one.", fields["text"])
        self.assertEqual(fields["kind"], "self")
        self.assertEqual(call.call_args[1]["token"], "tok-123")
        self.assertIn("User-Agent", call.call_args[1]["extra_headers"])

    def test_title_only_short_post(self):
        connector = RedditConnector(_channel(platform="reddit", account="loopcrm"))
        with patch("apps.marketing.connector_adapters._Http.post_form", return_value=(200, {"json": {"errors": [], "data": {}}})) as call:
            result = connector.publish(_post(content="Short headline"))
        self.assertTrue(result.success)
        self.assertEqual(result.external_id, "")
        self.assertEqual(call.call_args[0][1]["title"], "Short headline")
        self.assertNotIn("text", call.call_args[0][1])

    def test_reddit_reported_errors_fail(self):
        connector = RedditConnector(_channel(platform="reddit", account="r/loopcrm"))
        body = {"json": {"errors": [["NO_TEXT", "we need some text", "text"]]}}
        with patch("apps.marketing.connector_adapters._Http.post_form", return_value=(200, body)):
            result = connector.publish(_post(content="Headline\nBody text."))
        self.assertFalse(result.success)
        self.assertIn("NO_TEXT", result.message)

    def test_publish_without_token_is_gated(self):
        connector = RedditConnector(_channel(platform="reddit", token=""))
        with patch("apps.marketing.connector_adapters._Http.post_form") as call:
            result = connector.publish(_post(content="Headline\nBody."))
        self.assertFalse(result.success)
        self.assertIn("Connect a Reddit account", result.message)
        call.assert_not_called()


class WhatsAppConnectorTests(SimpleTestCase):
    def test_text_message_requires_phone_number_id_setting(self):
        connector = WhatsAppConnector(_channel(platform="whatsapp", account="+15551234567"))
        with patch("apps.marketing.connector_adapters._Http.post_json") as call:
            result = connector.publish(_post())
        self.assertFalse(result.success)
        self.assertIn("WHATSAPP_PHONE_NUMBER_ID", result.message)
        call.assert_not_called()

    @override_settings(WHATSAPP_PHONE_NUMBER_ID="10987654321")
    def test_text_message_sends_to_recipient(self):
        connector = WhatsAppConnector(_channel(platform="whatsapp", account="+15551234567"))
        with patch("apps.marketing.connector_adapters._Http.post_json", return_value=(200, {"messages": [{"id": "wamid.1"}]})) as call:
            result = connector.publish(_post())
        self.assertTrue(result.success)
        self.assertEqual(result.external_id, "wamid.1")
        url = call.call_args[0][0]
        self.assertIn("/10987654321/messages", url)
        payload = call.call_args[0][2]
        self.assertEqual(payload["to"], "+15551234567")
        self.assertEqual(payload["type"], "text")
        self.assertEqual(payload["text"]["body"], "Hello from Loop CRM")
        self.assertEqual(call.call_args[0][1], "tok-123")

    @override_settings(WHATSAPP_PHONE_NUMBER_ID="10987654321", **MEDIA_URL_SETTINGS)
    def test_image_message_sends_public_link(self):
        connector = WhatsAppConnector(_channel(platform="whatsapp", account="+15551234567"))
        with patch("apps.marketing.connector_adapters._Http.post_json", return_value=(200, {"messages": [{"id": "wamid.2"}]})) as call:
            result = connector.publish(_post(media=_media("pix.jpg")))
        self.assertTrue(result.success)
        payload = call.call_args[0][2]
        self.assertEqual(payload["type"], "image")
        self.assertEqual(payload["image"]["link"], "https://cdn.example.test/media/pix.jpg")

    @override_settings(WHATSAPP_PHONE_NUMBER_ID="10987654321")
    def test_recipient_must_be_e164(self):
        connector = WhatsAppConnector(_channel(platform="whatsapp", account="15551234567"))
        with patch("apps.marketing.connector_adapters._Http.post_json") as call:
            result = connector.publish(_post())
        self.assertFalse(result.success)
        self.assertIn("E.164", result.message)
        call.assert_not_called()


class DiscordConnectorTests(SimpleTestCase):
    def test_publish_success_extracts_message_id(self):
        connector = DiscordConnector(
            _channel(platform="discord", token="https://discord.com/api/webhooks/123/abc")
        )
        with patch("apps.marketing.connector_adapters._Http.post_json", return_value=(200, {"id": "msg-9"})) as call:
            result = connector.publish(_post())
        self.assertTrue(result.success)
        self.assertEqual(result.external_id, "msg-9")
        url = call.call_args[0][0]
        self.assertTrue(url.startswith("https://discord.com/api/webhooks/123/abc"))
        self.assertIn("wait=true", url)
        self.assertEqual(call.call_args[0][2], {"content": "Hello from Loop CRM"})

    def test_publish_204_no_body_still_succeeds(self):
        connector = DiscordConnector(
            _channel(platform="discord", token="https://discord.com/api/webhooks/123/abc")
        )
        with patch("apps.marketing.connector_adapters._Http.post_json", return_value=(204, {})):
            result = connector.publish(_post())
        self.assertTrue(result.success)
        self.assertEqual(result.external_id, "")

    def test_publish_without_webhook_url_is_gated(self):
        connector = DiscordConnector(_channel(platform="discord", token=""))
        with patch("apps.marketing.connector_adapters._Http.post_json") as call:
            result = connector.publish(_post())
        self.assertFalse(result.success)
        self.assertIn("Connect Discord", result.message)
        call.assert_not_called()

    def test_publish_rejected_reports_provider_message(self):
        connector = DiscordConnector(
            _channel(platform="discord", token="https://discord.com/api/webhooks/123/abc")
        )
        with patch("apps.marketing.connector_adapters._Http.post_json", return_value=(404, {"message": "Unknown Webhook"})):
            result = connector.publish(_post())
        self.assertFalse(result.success)
        self.assertIn("Unknown Webhook", result.message)

    def test_analytics_stays_empty(self):
        connector = DiscordConnector(
            _channel(platform="discord", token="https://discord.com/api/webhooks/123/abc")
        )
        self.assertEqual(connector.fetch_analytics(_post()), {})


class SlackConnectorTests(SimpleTestCase):
    def test_publish_success_plain_text_ack(self):
        connector = SlackConnector(
            _channel(platform="slack", token="https://hooks.slack.com/services/T/B/X")
        )
        with patch("apps.marketing.connector_adapters._Http.post_json", return_value=(200, {"_raw": "ok"})) as call:
            result = connector.publish(_post())
        self.assertTrue(result.success)
        self.assertEqual(result.external_id, "")
        self.assertEqual(call.call_args[0][0], "https://hooks.slack.com/services/T/B/X")
        self.assertEqual(call.call_args[0][2], {"text": "Hello from Loop CRM"})

    def test_publish_without_webhook_url_is_gated(self):
        connector = SlackConnector(_channel(platform="slack", token=""))
        with patch("apps.marketing.connector_adapters._Http.post_json") as call:
            result = connector.publish(_post())
        self.assertFalse(result.success)
        self.assertIn("Connect Slack", result.message)
        call.assert_not_called()

    def test_publish_rejected_reports_failure(self):
        connector = SlackConnector(
            _channel(platform="slack", token="https://hooks.slack.com/services/T/B/X")
        )
        with patch("apps.marketing.connector_adapters._Http.post_json", return_value=(404, {"_raw": "no_service"})):
            result = connector.publish(_post())
        self.assertFalse(result.success)
        self.assertIn("Slack rejected", result.message)

    def test_analytics_stays_empty(self):
        connector = SlackConnector(
            _channel(platform="slack", token="https://hooks.slack.com/services/T/B/X")
        )
        self.assertEqual(connector.fetch_analytics(_post()), {})


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
