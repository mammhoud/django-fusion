"""Real provider adapters for Loop-CRM social publishing.

LinkedIn and X (Twitter) implement the ``SocialConnector`` contract from
``apps.marketing.connectors``. They run only when the channel holds an OAuth
token; without credentials the dispatcher returns the safe
``UnconfiguredConnector`` so a post is never marked published without
provider I/O.

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
                return response.status, json.loads(body) if body else {}
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
    def post_json(cls, url: str, token: str, payload: dict, extra_headers: dict | None = None) -> tuple[int, dict]:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            **(extra_headers or {}),
        }
        return cls._request(url, method="POST", headers=headers, data=json.dumps(payload).encode("utf-8"))

    @classmethod
    def post_form(cls, url: str, fields: dict) -> tuple[int, dict]:
        data = urllib.parse.urlencode(fields).encode("utf-8")
        headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
        return cls._request(url, method="POST", headers=headers, data=data)


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


ADAPTERS: dict[str, type[SocialConnector]] = {
    "linkedin": LinkedInConnector,
    "twitter": XConnector,
}
