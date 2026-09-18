"""Provider adapters for Loop-CRM social publishing.

Every catalog platform now implements the ``SocialConnector`` contract with
real provider HTTP — no ``CatalogOnlyConnector`` stand-ins remain. A real
adapter runs only when the channel holds a credential; otherwise the
dispatcher returns the safe ``UnconfiguredConnector`` so nothing is ever
marked published without provider I/O.

Publish roads per family:

* **Text-capable (feed/message post):** Facebook (Page feed), Reddit (self
  post), WhatsApp (Cloud API message). These publish ``post.content`` as text
  and accept an optional attached media file where the platform supports a
  public-file URL (Facebook photo/video, WhatsApp image).
* **Media-capable (byte/URL pull):** Instagram (container + publish), TikTok
  (direct-post init/upload/status), YouTube (``videos.insert`` upload). These
  require an attached ``Post.media`` file and fail honestly when a post has no
  media — none of the three has a text-only publish API.
* **Webhook publishers:** Discord and Slack publish via incoming webhooks —
  no OAuth, the webhook URL stored on the channel is the credential.

Channel contract (shared by the connect hints on the channels screen):

* ``account_name`` carries the platform-specific target identity:
  Facebook Page ID, Instagram professional account ID, TikTok ``open_id``,
  Reddit subreddit (``r/...`` or bare), WhatsApp recipient E.164 number.
* ``oauth_token`` carries the credential the platform's API accepts
  (Bearer access token, or permanent token for WhatsApp).
* ``oauth_refresh_token`` is optional and only used by adapters whose client
  credentials are configured in settings (LinkedIn/X).

HTTP uses ``urllib.request`` (stdlib) so no extra dependency is needed.
Media files are read through Django's storage layer, so the adapters work
with any storage backend the product is deployed on.
"""
from __future__ import annotations

import json
import mimetypes
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from .connectors import PublishResult, SocialConnector


class _Http:
    """Tiny JSON/form/binary HTTP helper with sane timeouts and error capture."""

    @staticmethod
    def _request(url: str, *, method: str = "GET", headers: dict | None = None, data: bytes | None = None) -> tuple[int, dict]:
        request = urllib.request.Request(url, method=method, headers=headers or {}, data=data)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
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
    def post_form(cls, url: str, fields: dict, token: str | None = None, extra_headers: dict | None = None) -> tuple[int, dict]:
        data = urllib.parse.urlencode(fields).encode("utf-8")
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            **(extra_headers or {}),
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return cls._request(url, method="POST", headers=headers, data=data)

    @classmethod
    def put_bytes(cls, url: str, data: bytes, *, content_type: str, extra_headers: dict | None = None) -> tuple[int, dict]:
        headers = {
            "Content-Type": content_type,
            **(extra_headers or {}),
        }
        return cls._request(url, method="PUT", headers=headers, data=data)

    @classmethod
    def post_bytes(cls, url: str, data: bytes, token: str | None, *, content_type: str, extra_headers: dict | None = None) -> tuple[int, dict]:
        headers = {
            "Content-Type": content_type,
            **(extra_headers or {}),
        }
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
    detail = (
        body.get("detail")
        or body.get("message")
        or body.get("error_description")
        or (body.get("error") or {}).get("message")
        or (body.get("json") or {}).get("error")
    )
    if isinstance(detail, str) and detail:
        return f"{fallback}: {detail[:200]}"
    if isinstance(body.get("error"), dict) and isinstance(body["error"].get("code"), (int, str)):
        return f"{fallback}: {body['error']['code']}"
    return fallback


# ── Media helpers ────────────────────────────────────────────────────────────

_IMAGE_EXTS = frozenset({"jpg", "jpeg", "png", "gif", "webp", "heic", "heif", "bmp", "tif", "tiff"})
_VIDEO_EXTS = frozenset({"mp4", "mov", "m4v", "webm", "avi", "mkv", "mpeg", "mpg", "wmv", "flv"})


def _media_kind(media) -> str | None:
    """Return ``image`` or ``video`` for a Media row, or None when unknown."""
    name = (getattr(media, "file", None) and getattr(media.file, "name", "")) or ""
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if ext in _IMAGE_EXTS:
        return "image"
    if ext in _VIDEO_EXTS:
        return "video"
    return None


def _media_bytes(media) -> bytes:
    """Read a Media row's file bytes through the Django storage layer."""
    if media is None or not getattr(media, "file", None):
        raise ValueError("The post has no media file attached.")
    media.file.open("rb")
    try:
        return media.file.read()
    finally:
        media.file.close()


def _media_mime(media) -> str:
    name = (getattr(media, "file", None) and getattr(media.file, "name", "")) or "file"
    return mimetypes.guess_type(name)[0] or "application/octet-stream"


def _public_media_url(media) -> str | None:
    """Absolute public URL for a Media row, when one can be derived.

    Media is served by the backend at ``MEDIA_URL`` (the Astro dev proxy and
    the Traefik /media route both forward there), so the public URL is
    ``PUBLIC_SITE_URL + file.url``. Returns None when no public site base is
    configured (the operator must expose media publicly for pull-based
    providers such as Facebook/Instagram/TikTok/WhatsApp).
    """
    base = str(getattr(settings, "PUBLIC_SITE_URL", "") or "").rstrip("/")
    media_url = str(getattr(settings, "MEDIA_URL", "media/") or "").lstrip("/")
    name = (getattr(media, "file", None) and getattr(media.file, "name", "")) or ""
    if not (base and name):
        return None
    return f"{base}/{media_url}{name}"


def _public_media_url_result(media, platform: str) -> PublishResult | None:
    """Fail early (returning a result) when media lacks a public URL."""
    if media is None:
        return PublishResult(False, message=f"{platform} needs an attached image or video to publish.")
    url = _public_media_url(media)
    if not url:
        return PublishResult(
            False,
            message=(
                f"{platform} pulls media from a public URL, but no PUBLIC_SITE_URL is configured "
                "and the attached file is not publicly reachable. Serve /media on a public host first."
            ),
        )
    return None


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


# ── Meta Graph family (Facebook + Instagram) ────────────────────────────────

_GRAPH_VERSION = "v25.0"


def _graph_url(path: str) -> str:
    return f"https://graph.facebook.com/{_GRAPH_VERSION}{path}"


class FacebookConnector(SocialConnector):
    """Facebook Page publisher (Graph API).

    Text posts go to the Page feed (``/{{page}}/feed``). With an attached
    image or video the adapter publishes a photo/video post referencing the
    public media URL (Meta cURLs it), so media must be publicly reachable.
    ``account_name`` must hold the numeric Page ID; ``oauth_token`` the Page
    access token.
    """

    platform = "facebook"

    def __init__(self, channel):
        self.channel = channel

    def _page_id(self) -> str | None:
        value = (getattr(self.channel, "account_name", "") or "").strip()
        return value or None

    def publish(self, post) -> PublishResult:
        token = (getattr(self.channel, "oauth_token", "") or "").strip()
        if not token:
            return PublishResult(False, message="Connect a Facebook Page before publishing.")
        page_id = self._page_id()
        if not page_id:
            return PublishResult(
                False,
                message="Facebook publishing needs the Page ID as the channel account name.",
            )

        media = getattr(post, "media", None)
        kind = _media_kind(media)
        # Meta Graph reads the token from the ``access_token`` query parameter;
        # the JSON body carries the post payload only.
        if kind is None:
            status, body = _Http.post_json(
                _with_query(_graph_url(f"/{page_id}/feed"), access_token=token),
                None,
                {"message": post.content[:63206]},
            )
            if status not in (200, 201):
                return PublishResult(False, message=_error_message(status, body, "Facebook rejected the post"))
            external_id = str(body.get("id") or "").strip()
            if not external_id:
                return PublishResult(False, message="Facebook returned no post id.")
            return PublishResult(True, external_id=external_id, message="Published to Facebook.")
        if kind == "video":
            blocked = _public_media_url_result(media, "Facebook")
            if blocked:
                return blocked
            status, body = _Http.post_json(
                _with_query(_graph_url(f"/{page_id}/videos"), access_token=token),
                None,
                {"file_url": _public_media_url(media), "description": post.content[:5000]},
            )
            if status not in (200, 201):
                return PublishResult(False, message=_error_message(status, body, "Facebook rejected the video"))
            external_id = str(body.get("id") or "").strip()
            if not external_id:
                return PublishResult(False, message="Facebook returned no video id.")
            return PublishResult(True, external_id=external_id, message="Published video to Facebook.")
        blocked = _public_media_url_result(media, "Facebook")
        if blocked:
            return blocked
        status, body = _Http.post_json(
            _with_query(_graph_url(f"/{page_id}/photos"), access_token=token),
            None,
            {"url": _public_media_url(media), "caption": post.content[:2200]},
        )
        if status not in (200, 201):
            return PublishResult(False, message=_error_message(status, body, "Facebook rejected the photo"))
        external_id = str(body.get("id") or body.get("post_id") or "").strip()
        if not external_id:
            return PublishResult(False, message="Facebook returned no photo id.")
        return PublishResult(True, external_id=external_id, message="Published photo to Facebook.")

    def fetch_analytics(self, post) -> dict[str, int]:
        # Page insights need pages_read_engagement + the page insights edge;
        # keep this honest rather than fabricating a metric.
        return {}


class InstagramConnector(SocialConnector):
    """Instagram professional-account publisher (Graph API container flow).

    Instagram has no text-only publish API: every post is an image or video.
    Publishing is two-step — create a container (``/{{ig}}/media``) then
    publish it (``/{{ig}}/media_publish``). ``account_name`` holds the
    Instagram professional account ID; ``oauth_token`` a token carrying the
    ``instagram_content_publish`` permission.
    """

    platform = "instagram"

    def __init__(self, channel):
        self.channel = channel

    def _ig_id(self) -> str | None:
        value = (getattr(self.channel, "account_name", "") or "").strip()
        return value or None

    def publish(self, post) -> PublishResult:
        token = (getattr(self.channel, "oauth_token", "") or "").strip()
        if not token:
            return PublishResult(False, message="Connect an Instagram professional account before publishing.")
        ig_id = self._ig_id()
        if not ig_id:
            return PublishResult(
                False,
                message="Instagram publishing needs the professional account ID as the channel account name.",
            )
        media = getattr(post, "media", None)
        kind = _media_kind(media)
        if kind is None:
            return PublishResult(
                False,
                message="Instagram publishing needs an attached image or video — the platform has no text-post API.",
            )
        blocked = _public_media_url_result(media, "Instagram")
        if blocked:
            return blocked
        public_url = _public_media_url(media)
        caption = post.content[:2200]
        container_payload = (
            {"image_url": public_url, "caption": caption}
            if kind == "image"
            else {"video_url": public_url, "media_type": "VIDEO", "caption": caption}
        )
        status, body = _Http.post_json(
            _with_query(_graph_url(f"/{ig_id}/media"), access_token=token),
            None,
            container_payload,
        )
        if status not in (200, 201):
            return PublishResult(False, message=_error_message(status, body, "Instagram rejected the media container"))
        creation_id = str(body.get("id") or "").strip()
        if not creation_id:
            return PublishResult(False, message="Instagram returned no container id.")
        status, body = _Http.post_json(
            _with_query(_graph_url(f"/{ig_id}/media_publish"), access_token=token),
            None,
            {"creation_id": creation_id},
        )
        if status not in (200, 201):
            return PublishResult(False, message=_error_message(status, body, "Instagram rejected the media publish"))
        external_id = str(body.get("id") or "").strip()
        if not external_id:
            return PublishResult(False, message="Instagram returned no published media id.")
        return PublishResult(True, external_id=external_id, message="Published to Instagram.")

    def fetch_analytics(self, post) -> dict[str, int]:
        # Per-media insights require the insights edge + page permissions;
        # stay honest rather than returning a fake metric.
        return {}


# ── TikTok Content Posting API ───────────────────────────────────────────────

_TIKTOK_API = "https://open.tiktokapis.com/v2"
_TIKTOK_TERMINAL = {"FINISH", "FAIL", "PUBLISH_COMPLETE"}


class TikTokConnector(SocialConnector):
    """TikTok publisher (Content Posting API v2, direct post).

    Requires a video file (TikTok's public API has no text-post road) and the
    creator's ``open_id`` as the channel account name, plus a user access
    token carrying the ``video.publish`` scope. Publishing initializes a
    direct-post session (``/v2/post/publish/video/init/``), uploads the file
    to the returned ``upload_url`` (single-chunk PUT), then polls
    ``/v2/post/publish/status/fetch/`` until TikTok reports a terminal state.
    """

    platform = "tiktok"

    def __init__(self, channel):
        self.channel = channel

    def _open_id(self) -> str | None:
        value = (getattr(self.channel, "account_name", "") or "").strip()
        return value or None

    def publish(self, post) -> PublishResult:
        token = (getattr(self.channel, "oauth_token", "") or "").strip()
        if not token:
            return PublishResult(False, message="Connect a TikTok account before publishing.")
        open_id = self._open_id()
        if not open_id:
            return PublishResult(
                False,
                message="TikTok publishing needs the creator open_id as the channel account name.",
            )
        media = getattr(post, "media", None)
        if _media_kind(media) != "video":
            return PublishResult(
                False,
                message="TikTok publishing needs an attached video file — the platform has no text-post API.",
            )
        try:
            video_bytes = _media_bytes(media)
        except (ValueError, OSError) as exc:
            return PublishResult(False, message=f"TikTok could not read the attached video: {exc}")
        size = len(video_bytes)
        if not size:
            return PublishResult(False, message="The attached video file is empty.")

        privacy = getattr(settings, "TIKTOK_PRIVACY_LEVEL", "PUBLIC_TO_EVERYONE") or "PUBLIC_TO_EVERYONE"
        status, body = _Http.post_json(
            _with_query(f"{_TIKTOK_API}/post/publish/video/init/", open_id=open_id),
            token,
            {
                "post_info": {"title": post.content[:2200], "privacy_level": privacy},
                "source_info": {
                    "source": "FILE_UPLOAD",
                    "video_size": size,
                    "chunk_size": size,
                    "total_chunk_count": 1,
                },
            },
            extra_headers={"Content-Type": "application/json; charset=UTF-8"},
        )
        if status not in (200, 201):
            return PublishResult(False, message=_error_message(status, body, "TikTok rejected the publish request"))
        data = body.get("data") or {}
        error = body.get("error") or {}
        if error.get("code") not in (None, "", "ok"):
            return PublishResult(
                False,
                message=f"TikTok rejected the publish request: {error.get('code')} {error.get('message', '')}".strip(),
            )
        publish_id = str(data.get("publish_id") or "").strip()
        upload_url = str(data.get("upload_url") or "").strip()
        if not publish_id or not upload_url:
            return PublishResult(False, message="TikTok returned no publish_id or upload_url.")
        status, body = _Http.put_bytes(
            upload_url,
            video_bytes,
            content_type="video/mp4",
            extra_headers={
                "Content-Length": str(size),
                "Content-Range": f"bytes 0-{size - 1}/{size}",
            },
        )
        if status not in (200, 201, 204):
            return PublishResult(False, message=_error_message(status, body, "TikTok rejected the video upload"))

        # TikTok publishes asynchronously; poll the status endpoint until the
        # post reaches a terminal state (bounded so the actor can retry).
        deadline = time.monotonic() + 12
        while time.monotonic() < deadline:
            status, body = _Http.post_json(
                f"{_TIKTOK_API}/post/publish/status/fetch/",
                token,
                {"publish_id": publish_id},
            )
            if status == 200:
                data = body.get("data") or {}
                state = str(data.get("status") or "")
                fail_reason = data.get("fail_reason")
                if state in {"FINISH", "PUBLISH_COMPLETE"}:
                    item_id = str(data.get("item_id") or publish_id).strip()
                    return PublishResult(True, external_id=item_id, message="Published to TikTok.")
                if state == "FAIL" or fail_reason:
                    detail = fail_reason if isinstance(fail_reason, str) else "TikTok processing failed"
                    return PublishResult(False, message=f"TikTok failed to publish: {detail[:200]}")
            time.sleep(1)
        return PublishResult(
            False,
            message=(
                "TikTok accepted the video but had not finished processing within the timeout "
                "(publish_id %s). Retry publishing to re-check the status."
            )
            % publish_id,
        )

    def fetch_analytics(self, post) -> dict[str, int]:
        # TikTok analytics need the separate analytics API + scope; stay honest.
        return {}


# ── YouTube Data API ─────────────────────────────────────────────────────────

_YOUTUBE_UPLOAD = "https://www.googleapis.com/upload/youtube/v3/videos"


def _multipart_related(*parts: tuple[str, str, bytes]) -> bytes:
    """Build a multipart/related body from ``(name, content_type, data)`` parts."""
    boundary = f"----loopcrm{int(time.time() * 1000)}"
    chunks: list[bytes] = []
    for name, content_type, data in parts:
        chunks.append(
            f"--{boundary}\r\nContent-Type: {content_type}\r\nContent-Transfer-Encoding: binary\r\n\r\n".encode()
        )
        chunks.append(data if isinstance(data, bytes) else str(data).encode("utf-8"))
        chunks.append(b"\r\n")
    chunks.append(f"--{boundary}--\r\n".encode())
    return b"".join(chunks)


class YouTubeConnector(SocialConnector):
    """YouTube publisher (Data API ``videos.insert`` upload).

    Requires an attached video file and an OAuth access token with the
    ``youtube.upload`` scope. The video is uploaded with ``uploadType=multipart``
    (metadata + media in one request) and defaults to a private upload —
    YouTube restricts new unverified projects to private viewing until their
    API project passes an audit, and a private default is the safe choice for a
    publishing tool. The post content becomes the video description; the title
    is its first non-empty line (or a truncated content).
    """

    platform = "youtube"

    def __init__(self, channel):
        self.channel = channel

    def publish(self, post) -> PublishResult:
        token = (getattr(self.channel, "oauth_token", "") or "").strip()
        if not token:
            return PublishResult(False, message="Connect a YouTube channel before publishing.")
        media = getattr(post, "media", None)
        if _media_kind(media) != "video":
            return PublishResult(
                False,
                message="YouTube publishing needs an attached video file — the platform has no text-post API.",
            )
        try:
            video_bytes = _media_bytes(media)
        except (ValueError, OSError) as exc:
            return PublishResult(False, message=f"YouTube could not read the attached video: {exc}")
        if not video_bytes:
            return PublishResult(False, message="The attached video file is empty.")

        lines = [line.strip() for line in post.content.splitlines() if line.strip()]
        title = (lines[0] if lines else "Loop CRM post")[:100]
        description = post.content[:5000]
        privacy = str(getattr(settings, "YOUTUBE_PRIVACY_STATUS", "private") or "private").lower()
        metadata = json.dumps(
            {
                "snippet": {"title": title, "description": description},
                "status": {"privacyStatus": privacy},
            }
        ).encode("utf-8")
        mime = _media_mime(media)
        body = _multipart_related(("metadata", "application/json; charset=UTF-8", metadata), ("media", mime, video_bytes))
        url = _with_query(
            _YOUTUBE_UPLOAD,
            uploadType="multipart",
            part="snippet,status",
        )
        boundary = body.split(b"\r\n", 1)[0][2:].decode("utf-8")
        status, response = _Http.post_bytes(
            url,
            body,
            token,
            content_type=f"multipart/related; boundary={boundary}",
        )
        if status not in (200, 201):
            return PublishResult(False, message=_error_message(status, response, "YouTube rejected the upload"))
        external_id = str(response.get("id") or "").strip()
        if not external_id:
            return PublishResult(False, message="YouTube returned no video id.")
        return PublishResult(True, external_id=external_id, message=f"Uploaded video to YouTube ({privacy}).")

    def fetch_analytics(self, post) -> dict[str, int]:
        # videos.list?part=statistics requires youtube.readonly scope; stay
        # honest rather than fabricating view counts.
        return {}


# ── Reddit API ───────────────────────────────────────────────────────────────

_REDDIT_OAUTH = "https://oauth.reddit.com"
_REDDIT_USER_AGENT = "loop-crm:social-publisher:v1 (by /u/loop-crm)"


class RedditConnector(SocialConnector):
    """Reddit publisher (OAuth2 ``/api/submit``).

    ``account_name`` holds the target subreddit (``r/name`` or ``name``);
    ``oauth_token`` a Reddit access token with the ``submit`` scope. The post
    content is split on the first newline: the first line becomes the post
    title (Reddit requires one) and the remainder becomes the self-text body.
    A single-line post under 300 characters becomes a title-only self post.
    """

    platform = "reddit"

    def __init__(self, channel):
        self.channel = channel

    def _subreddit(self) -> str | None:
        value = (getattr(self.channel, "account_name", "") or "").strip().lstrip("r/")
        return value or None

    @staticmethod
    def _split_title_body(content: str) -> tuple[str, str]:
        lines = content.strip().splitlines()
        title = lines[0].strip() if lines else ""
        body = "\n".join(lines[1:]).strip()
        if not body and len(title) <= 300:
            return title, ""
        return title[:300], content.strip()

    def publish(self, post) -> PublishResult:
        token = (getattr(self.channel, "oauth_token", "") or "").strip()
        if not token:
            return PublishResult(False, message="Connect a Reddit account before publishing.")
        subreddit = self._subreddit()
        if not subreddit:
            return PublishResult(
                False,
                message="Reddit publishing needs the target subreddit as the channel account name.",
            )
        title, body = self._split_title_body(post.content)
        if not title:
            return PublishResult(False, message="A Reddit post needs a title (first line of the post).")
        fields = {
            "api_type": "json",
            "kind": "self",
            "sr": subreddit,
            "title": title,
            "resubmit": "true",
        }
        if body:
            fields["text"] = body
        status, response = _Http.post_form(
            f"{_REDDIT_OAUTH}/api/submit",
            fields,
            token=token,
            extra_headers={"User-Agent": _REDDIT_USER_AGENT},
        )
        if status != 200:
            return PublishResult(False, message=_error_message(status, response, "Reddit rejected the post"))
        reddit_json = response.get("json") or {}
        errors = reddit_json.get("errors") or []
        if errors:
            detail = "; ".join(
                f"{item[0]}: {item[1]}" for item in errors if isinstance(item, (list, tuple)) and len(item) >= 2
            )
            return PublishResult(False, message=f"Reddit rejected the post: {detail[:200]}")
        # Successful self submissions may not include an id in the sync body;
        # treat an empty-error response as accepted.
        data = reddit_json.get("data") or {}
        external_id = str(data.get("id") or "").strip() if isinstance(data, dict) else ""
        return PublishResult(True, external_id=external_id, message="Submitted to Reddit.")

    def fetch_analytics(self, post) -> dict[str, int]:
        return {}


# ── WhatsApp Cloud API ───────────────────────────────────────────────────────

_WHATSAPP_GRAPH = "https://graph.facebook.com"


class WhatsAppConnector(SocialConnector):
    """WhatsApp Cloud API message publisher.

    ``account_name`` holds the recipient phone number in E.164 (e.g.
    ``+15551234567``); ``oauth_token`` the WhatsApp Business permanent access
    token. The sending ``phone-number-id`` comes from the
    ``WHATSAPP_PHONE_NUMBER_ID`` setting (the workspace's single connected
    WhatsApp Business number). The post content becomes a text message, or an
    image message when the post carries a public image URL.
    """

    platform = "whatsapp"

    def __init__(self, channel):
        self.channel = channel

    def _recipient(self) -> str | None:
        value = (getattr(self.channel, "account_name", "") or "").strip()
        return value or None

    def publish(self, post) -> PublishResult:
        token = (getattr(self.channel, "oauth_token", "") or "").strip()
        if not token:
            return PublishResult(False, message="Connect a WhatsApp Business account before publishing.")
        recipient = self._recipient()
        if not recipient or not recipient.startswith("+"):
            return PublishResult(
                False,
                message="WhatsApp publishing needs the recipient E.164 number (e.g. +15551234567) as the channel account name.",
            )
        phone_number_id = str(getattr(settings, "WHATSAPP_PHONE_NUMBER_ID", "") or "").strip()
        if not phone_number_id:
            return PublishResult(
                False,
                message="WhatsApp publishing needs WHATSAPP_PHONE_NUMBER_ID configured (the sending business number).",
            )
        base = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
        }
        media = getattr(post, "media", None)
        kind = _media_kind(media)
        if kind == "image":
            blocked = _public_media_url_result(media, "WhatsApp")
            if blocked:
                return blocked
            payload = {**base, "type": "image", "image": {"link": _public_media_url(media), "caption": post.content[:1024]}}
        else:
            payload = {**base, "type": "text", "text": {"body": post.content[:4096]}}
        status, body = _Http.post_json(
            f"{_WHATSAPP_GRAPH}/{_GRAPH_VERSION}/{phone_number_id}/messages",
            token,
            payload,
        )
        if status not in (200, 201):
            return PublishResult(False, message=_error_message(status, body, "WhatsApp rejected the message"))
        messages = body.get("messages") or []
        external_id = str(messages[0].get("id") or "") if messages and isinstance(messages[0], dict) else ""
        return PublishResult(True, external_id=external_id, message="Sent WhatsApp message.")

    def fetch_analytics(self, post) -> dict[str, int]:
        # Message delivery/read status arrives via webhooks; stay honest.
        return {}


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
#: and drives the manual-connect UI on the channels page. Each ``account_name``
#: carries the platform-specific target identity documented in the adapter
#: classes above.
MANUAL_CONNECT: tuple[dict[str, str], ...] = (
    {
        "platform": "instagram",
        "label": "Instagram",
        "hint": "Professional account ID as the account name + Graph API token (image/video posts)",
    },
    {
        "platform": "facebook",
        "label": "Facebook",
        "hint": "Page ID as the account name + Page access token",
    },
    {
        "platform": "tiktok",
        "label": "TikTok",
        "hint": "Creator open_id as the account name + Content Posting API token (video posts)",
    },
    {
        "platform": "youtube",
        "label": "YouTube",
        "hint": "Channel name as the account name + Google OAuth token (youtube.upload, video posts)",
    },
    {
        "platform": "reddit",
        "label": "Reddit",
        "hint": "Subreddit (r/name) as the account name + OAuth access token",
    },
    {
        "platform": "discord",
        "label": "Discord",
        "hint": "Incoming webhook URL as the credential",
    },
    {
        "platform": "slack",
        "label": "Slack",
        "hint": "Incoming webhook URL as the credential",
    },
    {
        "platform": "whatsapp",
        "label": "WhatsApp",
        "hint": "Recipient E.164 number as the account name + permanent Cloud API token",
    },
)
