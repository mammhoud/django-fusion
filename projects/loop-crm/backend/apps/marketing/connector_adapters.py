"""Provider adapters for Loop-CRM social publishing.

Six platforms (LinkedIn, X/Twitter, Mastodon, Bluesky, Discord, Slack)
implement the ``SocialConnector`` contract with real provider HTTP. Discord
and Slack publish via incoming webhooks — no OAuth, the webhook URL stored on
the channel is itself the credential. The remaining six catalog platforms
(Instagram, Facebook, TikTok, YouTube, Reddit, WhatsApp) use
``CatalogOnlyConnector``: they are discoverable and credential-gated, but
honestly report that their publish API is not wired yet rather than marking a
post published without provider I/O.

A real adapter runs only when the channel holds a credential; otherwise the
dispatcher returns the safe ``UnconfiguredConnector``.

HTTP uses ``urllib.request`` (stdlib) so no extra dependency is needed.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from .connectors import PublishResult, SocialConnector


class _Http:
    """Tiny JSON/form HTTP helper with sane timeouts and error capture."""

    @staticmethod
    def _request(url: str, *, method: str = "GET", headers: dict | None = None, data: bytes | None = None) -> tuple[int, dict]:
        request = urllib.request.Request(url, method=method, headers=headers or {}, data=data)
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                body = response.read().decode("utf-8", errors="replace")
                if not body:
                    return response.status, {}
                try:
                    return response.status, json.loads(body)
                except ValueError:
                    # Some providers (e.g. Slack webhooks) ack with a plain-text
                    # body rather than JSON; surface it under ``_raw``.
                    return response.status, {"_raw": body}
        except urllib.error.HTTPError as exc:
            try:
                body = json.loads(exc.read().decode("utf-8", errors="replace"))
            except (ValueError, TypeError):
                body = {"detail": exc.reason}
            return exc.code, body
        except urllib.error.URLError as exc:
            return 0, {"detail": f"Network error: {exc.reason}"}

    @classmethod
    def get(cls, url: str, token: str) -> tuple[int, dict]:
        return cls._request(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})

    @classmethod
    def post_json(cls, url: str, token: str | None, payload: dict, extra_headers: dict | None = None) -> tuple[int, dict]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            **(extra_headers or {}),
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return cls._request(url, method="POST", headers=headers, data=json.dumps(payload).encode("utf-8"))

    @classmethod
    def post_form(cls, url: str, fields: dict, token: str | None = None) -> tuple[int, dict]:
        data = urllib.parse.urlencode(fields).encode("utf-8")
        headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return cls._request(url, method="POST", headers=headers, data=data)


def _with_query(url: str, **params: str) -> str:
    """Append query parameters to a URL, preserving any existing query."""
    parts = urllib.parse.urlsplit(url)
    query = urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
    query.extend((key, value) for key, value in params.items())
    return urllib.parse.urlunsplit(
        (parts.scheme, parts.netloc, parts.path, urllib.parse.urlencode(query), parts.fragment)
    )


def _error_message(status: int, body: dict, fallback: str) -> str:
    if status == 401:
        return "Access token expired or invalid. Reconnect the channel."
    if status == 403:
        return "The provider rejected this request. Check the account permissions."
    detail = body.get("detail") or body.get("message") or body.get("error_description")
    if isinstance(detail, str) and detail:
        return f"{fallback}: {detail[:200]}"
    return fallback


class LinkedInConnector(SocialConnector):
    """LinkedIn UGC post publisher (Share API v2)."""

    platform = "linkedin"
    _publish_url = "https://api.linkedin.com/v2/ugcPosts"
    _refresh_url = "https://www.linkedin.com/oauth/v2/accessToken"

    def __init__(self, channel):
        self.channel = channel

    def _author_urn(self, post) -> str:
        """The author URN lives on the channel account record."""
        urn = self.channel.account_name.strip()
        if urn.startswith("urn:li:"):
            return urn
        raise ValueError(
            "LinkedIn needs the page/person URN (urn:li:person:... or urn:li:organization:...) "
            "as the channel account name before publishing."
        )

    def publish(self, post) -> PublishResult:
        if not self.channel.oauth_token:
            return PublishResult(False, message="Connect a LinkedIn account before publishing.")
        try:
            author = self._author_urn(post)
        except ValueError as exc:
            return PublishResult(False, message=str(exc))
        payload = {
            "author": author,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": post.content[:3000]},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }
        status, body = _Http.post_json(
            self._publish_url,
            self.channel.oauth_token,
            payload,
            extra_headers={"X-Restli-Protocol-Version": "2.0.0"},
        )
        if status not in (200, 201):
            return PublishResult(False, message=_error_message(status, body, "LinkedIn rejected the post"))
        external_id = str(body.get("id") or "").strip()
        if not external_id:
            return PublishResult(False, message="LinkedIn returned no share id for the post.")
        return PublishResult(True, external_id=external_id, message="Published to LinkedIn.")

    def fetch_analytics(self, post) -> dict[str, int]:
        # The LinkedIn analytics API requires audience-network permissions per
        # organization; return nothing rather than a fake metric.
        return {}

    def refresh(self) -> bool:
        """Exchange the stored refresh token for a new access pair."""
        if not (self.channel.oauth_refresh_token and settings.LINKEDIN_CLIENT_ID):
            return False
        status, body = _Http.post_form(
            self._refresh_url,
            {
                "grant_type": "refresh_token",
                "refresh_token": self.channel.oauth_refresh_token,
                "client_id": settings.LINKEDIN_CLIENT_ID,
                "client_secret": settings.LINKEDIN_CLIENT_SECRET,
            },
        )
        access = str(body.get("access_token") or "")
        if status != 200 or not access:
            return False
        self.channel.oauth_token = access
        if body.get("refresh_token"):
            self.channel.oauth_refresh_token = str(body["refresh_token"])
        expires_in = int(body.get("expires_in") or 0)
        if expires_in:
            self.channel.token_expires_at = timezone.now() + timedelta(seconds=expires_in)
        self.channel.save(update_fields=["oauth_token", "oauth_refresh_token", "token_expires_at", "updated_at"])
        return True


class XConnector(SocialConnector):
    """X (Twitter) v2 tweet publisher."""

    platform = "twitter"
    _publish_url = "https://api.twitter.com/2/tweets"
    _analytics_url = "https://api.twitter.com/2/tweets/{tweet_id}?tweet.fields=public_metrics"
    _refresh_url = "https://api.twitter.com/2/oauth2/token"

    def __init__(self, channel):
        self.channel = channel

    def publish(self, post) -> PublishResult:
        if not self.channel.oauth_token:
            return PublishResult(False, message="Connect an X (Twitter) account before publishing.")
        status, body = _Http.post_json(self._publish_url, self.channel.oauth_token, {"text": post.content[:280]})
        if status not in (200, 201):
            return PublishResult(False, message=_error_message(status, body, "X rejected the post"))
        data = body.get("data") or {}
        external_id = str(data.get("id") or "").strip()
        if not external_id:
            return PublishResult(False, message="X returned no tweet id for the post.")
        return PublishResult(True, external_id=external_id, message="Published to X.")

    def fetch_analytics(self, post) -> dict[str, int]:
        if not (self.channel.oauth_token and post.external_id):
            return {}
        status, body = _Http.get(self._analytics_url.format(tweet_id=post.external_id), self.channel.oauth_token)
        if status != 200:
            return {}
        metrics = (body.get("data") or {}).get("public_metrics") or {}
        return {
            "impressions": int(metrics.get("impression_count") or 0),
            "likes": int(metrics.get("like_count") or 0),
            "comments": int(metrics.get("reply_count") or 0),
            "shares": int(metrics.get("retweet_count") or 0),
        }

    def refresh(self) -> bool:
        """Exchange the stored refresh token using the OAuth 2.0 PKCE client."""
        if not (self.channel.oauth_refresh_token and settings.X_CLIENT_ID):
            return False
        status, body = _Http.post_form(
            self._refresh_url,
            {
                "grant_type": "refresh_token",
                "refresh_token": self.channel.oauth_refresh_token,
                "client_id": settings.X_CLIENT_ID,
                "client_secret": settings.X_CLIENT_SECRET,
            },
        )
        access = str(body.get("access_token") or "")
        if status != 200 or not access:
            return False
        self.channel.oauth_token = access
        if body.get("refresh_token"):
            self.channel.oauth_refresh_token = str(body["refresh_token"])
        expires_in = int(body.get("expires_in") or 0)
        if expires_in:
            self.channel.token_expires_at = timezone.now() + timedelta(seconds=expires_in)
        self.channel.save(update_fields=["oauth_token", "oauth_refresh_token", "token_expires_at", "updated_at"])
        return True


class MastodonConnector(SocialConnector):
    """Mastodon status publisher (ActivityPub ``POST /api/v1/statuses``)."""

    platform = "mastodon"

    def __init__(self, channel):
        self.channel = channel

    def _base_url(self) -> str:
        name = self.channel.account_name.strip().lstrip("@")
        instance = name.rsplit("@", 1)[-1].rstrip("/") if "@" in name else "mastodon.social"
        return instance if instance.startswith("http") else f"https://{instance}"

    def publish(self, post) -> PublishResult:
        if not self.channel.oauth_token:
            return PublishResult(False, message="Connect a Mastodon account before publishing.")
        status, body = _Http.post_form(
            f"{self._base_url()}/api/v1/statuses",
            {"status": post.content[:500]},
            token=self.channel.oauth_token,
        )
        if status not in (200, 201):
            return PublishResult(False, message=_error_message(status, body, "Mastodon rejected the post"))
        external_id = str(body.get("id") or "").strip()
        if not external_id:
            return PublishResult(False, message="Mastodon returned no status id for the post.")
        return PublishResult(True, external_id=external_id, message="Published to Mastodon.")

    def fetch_analytics(self, post) -> dict[str, int]:
        # Mastodon exposes per-status counters (not impressions) on the status
        # resource; keep this honest rather than fabricating a metric.
        return {}


class BlueskyConnector(SocialConnector):
    """Bluesky (AT Protocol) publisher using an app password session."""

    platform = "bluesky"
    _base_url = "https://bsky.social"

    def __init__(self, channel):
        self.channel = channel

    def _session(self) -> dict | None:
        status, body = _Http.post_json(
            f"{self._base_url}/xrpc/com.atproto.server.createSession",
            None,
            {"identifier": self.channel.account_name.strip(), "password": self.channel.oauth_token},
        )
        return body if status == 200 else None

    def publish(self, post) -> PublishResult:
        if not (self.channel.oauth_token and self.channel.account_name):
            return PublishResult(False, message="Connect a Bluesky account before publishing.")
        session = self._session()
        if not session or not session.get("accessJwt") or not session.get("did"):
            return PublishResult(False, message="Bluesky login failed. Check the handle and app password.")
        record = {
            "text": post.content[:300],
            "createdAt": timezone.now().isoformat(),
        }
        status, body = _Http.post_json(
            f"{self._base_url}/xrpc/com.atproto.repo.createRecord",
            session["accessJwt"],
            {"repo": session["did"], "collection": "app.bsky.feed.post", "record": record},
        )
        if status not in (200, 201):
            return PublishResult(False, message=_error_message(status, body, "Bluesky rejected the post"))
        uri = str(body.get("uri") or "").strip()
        if not uri:
            return PublishResult(False, message="Bluesky returned no post URI.")
        return PublishResult(True, external_id=uri, message="Published to Bluesky.")

    def fetch_analytics(self, post) -> dict[str, int]:
        # AT Protocol does not expose per-post public metrics via the session
        # API; return nothing rather than a fake metric.
        return {}


class CatalogOnlyConnector(SocialConnector):
    """Honest, credential-gated adapter for platforms in the catalog whose
    publish API is not yet wired into Loop-CRM.

    The connector is discoverable (it appears in the integrations/channels
    surface) and gates on the channel credential, but publishing never
    succeeds: without a token it asks the operator to connect, and with one it
    honestly reports that the platform's API road is not implemented yet.
    """

    label = ""
    credential_hint = "an access token"

    def __init__(self, channel):
        self.channel = channel

    def publish(self, post) -> PublishResult:
        if not getattr(self.channel, "oauth_token", ""):
            return PublishResult(False, message=f"Connect {self.label} before publishing.")
        return PublishResult(
            False,
            message=f"{self.label} is in the catalog, but its publish API is not wired into Loop-CRM yet.",
        )

    def fetch_analytics(self, post) -> dict[str, int]:
        return {}


class InstagramConnector(CatalogOnlyConnector):
    platform = "instagram"
    label = "Instagram"
    credential_hint = "a Meta Graph API token"


class FacebookConnector(CatalogOnlyConnector):
    platform = "facebook"
    label = "Facebook"
    credential_hint = "a Meta Graph API token"


class TikTokConnector(CatalogOnlyConnector):
    platform = "tiktok"
    label = "TikTok"
    credential_hint = "a Content Posting API token"


class YouTubeConnector(CatalogOnlyConnector):
    platform = "youtube"
    label = "YouTube"
    credential_hint = "a Google OAuth token"


class RedditConnector(CatalogOnlyConnector):
    platform = "reddit"
    label = "Reddit"
    credential_hint = "an OAuth token"


class DiscordConnector(SocialConnector):
    """Discord incoming-webhook publisher (``POST /api/webhooks/{id}/{token}``).

    Discord needs no OAuth — the incoming webhook URL is the credential and is
    stored on the channel's ``oauth_token``. ``?wait=true`` asks Discord to
    return the created message so Loop-CRM can store its id.
    """

    platform = "discord"

    def __init__(self, channel):
        self.channel = channel

    def publish(self, post) -> PublishResult:
        webhook_url = (getattr(self.channel, "oauth_token", "") or "").strip()
        if not webhook_url:
            return PublishResult(False, message="Connect Discord (add an incoming webhook URL) before publishing.")
        status, body = _Http.post_json(
            _with_query(webhook_url, wait="true"), None, {"content": post.content[:2000]}
        )
        if status not in (200, 204):
            return PublishResult(False, message=_error_message(status, body, "Discord rejected the post"))
        external_id = str(body.get("id") or "").strip()
        return PublishResult(True, external_id=external_id, message="Published to Discord.")

    def fetch_analytics(self, post) -> dict[str, int]:
        # Webhook delivery has no per-message analytics endpoint; stay honest.
        return {}


class SlackConnector(SocialConnector):
    """Slack incoming-webhook publisher (``POST hooks.slack.com/services/...``).

    The webhook URL is the credential (stored on ``oauth_token``) — no OAuth.
    Slack acks with a plain-text ``ok`` and returns no message id, so the
    post's ``external_id`` stays empty.
    """

    platform = "slack"

    def __init__(self, channel):
        self.channel = channel

    def publish(self, post) -> PublishResult:
        webhook_url = (getattr(self.channel, "oauth_token", "") or "").strip()
        if not webhook_url:
            return PublishResult(False, message="Connect Slack (add an incoming webhook URL) before publishing.")
        status, body = _Http.post_json(webhook_url, None, {"text": post.content[:40000]})
        if status != 200:
            return PublishResult(False, message=_error_message(status, body, "Slack rejected the post"))
        return PublishResult(True, message="Published to Slack.")

    def fetch_analytics(self, post) -> dict[str, int]:
        # Incoming webhooks expose no per-message analytics; stay honest.
        return {}


class WhatsAppConnector(CatalogOnlyConnector):
    platform = "whatsapp"
    label = "WhatsApp"
    credential_hint = "a Cloud API token"


ADAPTERS: dict[str, type[SocialConnector]] = {
    "linkedin": LinkedInConnector,
    "twitter": XConnector,
    "mastodon": MastodonConnector,
    "bluesky": BlueskyConnector,
    "instagram": InstagramConnector,
    "facebook": FacebookConnector,
    "tiktok": TikTokConnector,
    "youtube": YouTubeConnector,
    "reddit": RedditConnector,
    "discord": DiscordConnector,
    "slack": SlackConnector,
    "whatsapp": WhatsAppConnector,
}


#: Catalog platforms an operator connects by pasting a credential directly (no
#: redirect OAuth). The credential is stored on ``SocialChannel.oauth_token``
#: and drives the manual-connect UI on the channels page.
MANUAL_CONNECT: tuple[dict[str, str], ...] = (
    {"platform": "instagram", "label": "Instagram", "hint": "Meta Graph API access token"},
    {"platform": "facebook", "label": "Facebook", "hint": "Meta Graph API access token"},
    {"platform": "tiktok", "label": "TikTok", "hint": "TikTok Content Posting API token"},
    {"platform": "youtube", "label": "YouTube", "hint": "Google OAuth access token"},
    {"platform": "reddit", "label": "Reddit", "hint": "Reddit OAuth access token"},
    {"platform": "discord", "label": "Discord", "hint": "Incoming webhook URL"},
    {"platform": "slack", "label": "Slack", "hint": "Incoming webhook URL"},
    {"platform": "whatsapp", "label": "WhatsApp", "hint": "WhatsApp Cloud API token"},
)
