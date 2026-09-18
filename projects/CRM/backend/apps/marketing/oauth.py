"""OAuth 2.0 connect flows for every redirect-OAuth social publisher.

``connect_start`` redirects the user to the provider's authorization screen
(state, and PKCE for X, are held in the session); ``oauth_callback`` verifies
state, exchanges the code for tokens, fetches the account identity, and upserts
a ``SocialChannel`` in the user's workspace. From there the existing
``SocialConnector`` adapters (``apps.marketing.connector_adapters``) publish
with the stored token, refreshing it when it expires.

Flows: LinkedIn, X (PKCE), Meta Graph for Facebook Pages / Instagram
professional accounts / WhatsApp Business (one app, per-platform scopes),
TikTok (Content Posting API), YouTube (Google OAuth), and Reddit (script
app, permanent token). HTTP uses the same stdlib helper as the adapters, so
no extra dependency is added. Nothing is sent to a provider unless the client
credentials from ``settings`` are configured; otherwise the user gets an
honest redirect notice.
"""
from __future__ import annotations

import base64
import hashlib
import secrets
from datetime import timedelta
from urllib.parse import urlencode

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone

from .connector_adapters import _GRAPH_VERSION, _Http, _with_query
from .models import SocialChannel

PROVIDERS = {
    "linkedin",
    "twitter",
    "facebook",
    "instagram",
    "whatsapp",
    "tiktok",
    "youtube",
    "reddit",
}

_SESSION_STATE = "loop_oauth_state"
_SESSION_PLATFORM = "loop_oauth_platform"
_SESSION_VERIFIER = "loop_pkce_verifier"

# ── Pure URL builders (unit-testable without HTTP) ───────────────────────────

def linkedin_authorize_url(*, client_id: str, redirect_uri: str, state: str) -> str:
    params = urlencode(
        {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": "w_member_social r_liteprofile r_emailaddress offline_access",
            "state": state,
        }
    )
    return f"https://www.linkedin.com/oauth/v2/authorization?{params}"


def x_authorize_url(*, client_id: str, redirect_uri: str, state: str, code_challenge: str) -> str:
    params = urlencode(
        {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": "tweet.read tweet.write users.read offline.access",
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
    )
    return f"https://twitter.com/i/oauth2/authorize?{params}"


def _pkce_pair() -> tuple[str, str]:
    """Return (verifier, S256 challenge) for the X OAuth 2.0 PKCE flow."""
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("utf-8")).digest()).rstrip(b"=").decode("ascii")
    return verifier, challenge


# ── Token exchange + identity fetch (real provider I/O via stdlib HTTP) ──────

def exchange_linkedin_code(*, code: str, redirect_uri: str) -> dict:
    status, body = _Http.post_form(
        "https://www.linkedin.com/oauth/v2/accessToken",
        {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": settings.LINKEDIN_CLIENT_ID,
            "client_secret": settings.LINKEDIN_CLIENT_SECRET,
        },
    )
    if status != 200:
        raise ValueError(body.get("error_description") or body.get("error") or "LinkedIn token exchange failed.")
    return body


def fetch_linkedin_identity(access_token: str) -> dict:
    status, body = _Http.get("https://api.linkedin.com/v2/userinfo", access_token)
    if status != 200:
        raise ValueError("LinkedIn identity fetch failed.")
    return body


def exchange_x_code(*, code: str, redirect_uri: str, code_verifier: str) -> dict:
    status, body = _Http.post_form(
        "https://api.twitter.com/2/oauth2/token",
        {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": settings.X_CLIENT_ID,
            "client_secret": settings.X_CLIENT_SECRET,
            "code_verifier": code_verifier,
        },
    )
    if status != 200:
        raise ValueError(body.get("error_description") or body.get("error") or "X token exchange failed.")
    return body


def fetch_x_identity(access_token: str) -> dict:
    status, body = _Http.get("https://api.twitter.com/2/users/me", access_token)
    if status != 200:
        raise ValueError("X identity fetch failed.")
    return body.get("data") or {}


# ── Meta Graph (Facebook / Instagram / WhatsApp) ──────────────────────────────

META_SCOPES = {
    "facebook": "pages_show_list pages_manage_posts pages_read_engagement",
    "instagram": "instagram_basic instagram_content_publish pages_show_list",
    "whatsapp": "business_management whatsapp_business_messaging",
}


#: Reddit requires a descriptive User-Agent on every OAuth API call.
REDDIT_USER_AGENT = "loop-crm:social-publisher:v1 (by /u/loop-crm)"


def meta_authorize_url(*, client_id: str, redirect_uri: str, state: str, scope: str) -> str:
    params = urlencode(
        {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
            "state": state,
        }
    )
    return f"https://www.facebook.com/{_GRAPH_VERSION}/dialog/oauth?{params}"


def exchange_meta_code(*, code: str, redirect_uri: str) -> dict:
    """Exchange the short-lived code, then upgrade to a long-lived token."""
    status, body = _Http.post_form(
        f"https://graph.facebook.com/{_GRAPH_VERSION}/oauth/access_token",
        {
            "client_id": settings.META_CLIENT_ID,
            "client_secret": settings.META_CLIENT_SECRET,
            "redirect_uri": redirect_uri,
            "code": code,
        },
    )
    if status != 200:
        raise ValueError(_meta_error(body, "Meta token exchange failed."))
    status, body = _Http.post_form(
        f"https://graph.facebook.com/{_GRAPH_VERSION}/oauth/access_token",
        {
            "grant_type": "fb_exchange_token",
            "client_id": settings.META_CLIENT_ID,
            "client_secret": settings.META_CLIENT_SECRET,
            "fb_exchange_token": body["access_token"],
        },
    )
    if status != 200:
        raise ValueError(_meta_error(body, "Meta long-lived token exchange failed."))
    return body


def _meta_error(body: dict, fallback: str) -> str:
    error = body.get("error")
    if isinstance(error, dict) and error.get("message"):
        return f"{fallback} {error['message']}"
    return str(body.get("error_description") or body.get("error") or fallback)


def _meta_get(path: str, token: str) -> tuple[int, dict]:
    """Graph API GET — the access token travels as a query parameter."""
    url = _with_query(f"https://graph.facebook.com/{_GRAPH_VERSION}{path}", access_token=token)
    return _Http._request(url)


def fetch_meta_identity(platform: str, access_token: str) -> str:
    """Resolve the account name a publisher targets, per Meta platform."""
    if platform == "whatsapp":
        status, body = _meta_get("/me/businesses", access_token)
        if status != 200:
            raise ValueError("WhatsApp identity fetch failed.")
        business = (body.get("data") or [{}])[0]
        if not business.get("id"):
            raise ValueError("No Meta Business is attached to this WhatsApp token.")
        status, body = _meta_get(f"/{business['id']}/client_whatsapp_business_accounts", access_token)
        if status != 200:
            raise ValueError("WhatsApp Business Account fetch failed.")
        waba = (body.get("data") or [{}])[0]
        if not waba.get("id"):
            raise ValueError("No WhatsApp Business Account is linked to this Meta Business.")
        status, body = _meta_get(f"/{waba['id']}/phone_numbers", access_token)
        if status != 200:
            raise ValueError("WhatsApp phone number fetch failed.")
        number = (body.get("data") or [{}])[0]
        return str(number.get("display_phone_number") or number.get("id") or "")
    status, body = _meta_get("/me/accounts?fields=id,name,instagram_business_account{id,username}", access_token)
    if status != 200:
        raise ValueError("Facebook Page identity fetch failed.")
    pages = body.get("data") or []
    if platform == "facebook":
        page = pages[0] if pages else {}
        return str(page.get("name") or page.get("id") or "")
    # Instagram: the token must see a Page that owns an IG business account.
    for page in pages:
        ig = page.get("instagram_business_account") or {}
        if ig.get("username") or ig.get("id"):
            return str(ig.get("username") or ig.get("id"))
    raise ValueError("No Instagram business account is linked to any Page this token can see.")


# ── TikTok Content Posting API ────────────────────────────────────────────────

def tiktok_authorize_url(*, client_key: str, redirect_uri: str, state: str) -> str:
    params = urlencode(
        {
            "client_key": client_key,
            "response_type": "code",
            "scope": "user.info.basic video.publish",
            "redirect_uri": redirect_uri,
            "state": state,
        }
    )
    return f"https://www.tiktok.com/v2/auth/authorize/?{params}"


def exchange_tiktok_code(*, code: str, redirect_uri: str) -> dict:
    status, body = _Http.post_form(
        "https://open.tiktokapis.com/v2/oauth/token/",
        {
            "client_key": settings.TIKTOK_CLIENT_KEY,
            "client_secret": settings.TIKTOK_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        },
    )
    if status != 200:
        raise ValueError(body.get("error_description") or body.get("error") or "TikTok token exchange failed.")
    return body


# ── YouTube (Google OAuth) ────────────────────────────────────────────────────

def youtube_authorize_url(*, client_id: str, redirect_uri: str, state: str) -> str:
    params = urlencode(
        {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly",
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }
    )
    return f"https://accounts.google.com/o/oauth2/v2/auth?{params}"


def exchange_youtube_code(*, code: str, redirect_uri: str) -> dict:
    status, body = _Http.post_form(
        "https://oauth2.googleapis.com/token",
        {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        },
    )
    if status != 200:
        raise ValueError(body.get("error_description") or body.get("error") or "YouTube token exchange failed.")
    return body


def fetch_youtube_identity(access_token: str) -> str:
    status, body = _Http.get(
        "https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true",
        access_token,
    )
    if status != 200:
        raise ValueError("YouTube identity fetch failed.")
    items = body.get("items") or []
    if not items:
        raise ValueError("No YouTube channel is attached to this Google account.")
    return str((items[0].get("snippet") or {}).get("title") or "")


# ── Reddit ────────────────────────────────────────────────────────────────────

def reddit_authorize_url(*, client_id: str, redirect_uri: str, state: str) -> str:
    params = urlencode(
        {
            "client_id": client_id,
            "response_type": "code",
            "state": state,
            "redirect_uri": redirect_uri,
            "duration": "permanent",
            "scope": "identity submit",
        }
    )
    return f"https://www.reddit.com/api/v1/authorize?{params}"


def _reddit_basic_auth() -> str:
    raw = f"{settings.REDDIT_CLIENT_ID}:{settings.REDDIT_CLIENT_SECRET}"
    return base64.b64encode(raw.encode("utf-8")).decode("ascii")


def exchange_reddit_code(*, code: str, redirect_uri: str) -> dict:
    status, body = _Http.post_form(
        "https://www.reddit.com/api/v1/access_token",
        {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        },
        extra_headers={
            "Authorization": f"Basic {_reddit_basic_auth()}",
            "User-Agent": REDDIT_USER_AGENT,
        },
    )
    if status != 200:
        raise ValueError(body.get("error_description") or body.get("error") or "Reddit token exchange failed.")
    return body


def fetch_reddit_identity(access_token: str) -> str:
    status, body = _Http._request(
        "https://oauth.reddit.com/api/v1/me",
        headers={
            "Authorization": f"Bearer {access_token}",
            "User-Agent": REDDIT_USER_AGENT,
            "Accept": "application/json",
        },
    )
    if status != 200:
        raise ValueError("Reddit identity fetch failed.")
    return str(body.get("name") or "")


# ── Views ────────────────────────────────────────────────────────────────────

def _client_configured(platform: str) -> bool:
    if platform == "linkedin":
        return bool(settings.LINKEDIN_CLIENT_ID and settings.LINKEDIN_CLIENT_SECRET)
    if platform == "twitter":
        return bool(settings.X_CLIENT_ID and settings.X_CLIENT_SECRET)
    if platform in {"facebook", "instagram", "whatsapp"}:
        return bool(settings.META_CLIENT_ID and settings.META_CLIENT_SECRET)
    if platform == "tiktok":
        return bool(settings.TIKTOK_CLIENT_KEY and settings.TIKTOK_CLIENT_SECRET)
    if platform == "youtube":
        return bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)
    if platform == "reddit":
        return bool(settings.REDDIT_CLIENT_ID and settings.REDDIT_CLIENT_SECRET)
    return False


def _redirect_uri(request, platform: str) -> str:
    callback_path = reverse("oauth_callback", args=[platform])
    base = getattr(settings, "SOCIAL_REDIRECT_BASE", "")
    if base:
        return f"{base.rstrip('/')}{callback_path}"
    return request.build_absolute_uri(callback_path)


def _workspace_id(request):
    try:
        return request.user.profile.workspace_id
    except Exception:  # noqa: BLE001 - a profile is optional for auth
        return None


@login_required
def connect_start(request, platform: str) -> HttpResponseRedirect:
    """Redirect the user to the provider's authorization screen."""
    calendar = reverse("marketing_calendar")
    if platform not in PROVIDERS:
        messages.error(request, f"Unknown connector: {platform}.")
        return redirect(calendar)
    if not _client_configured(platform):
        messages.error(
            request,
            f"Connect {platform} client credentials are not configured. "
            "Add them to the backend .env (LINKEDIN_CLIENT_ID / X_CLIENT_ID / META_CLIENT_ID / "
            "TIKTOK_CLIENT_KEY / GOOGLE_CLIENT_ID / REDDIT_CLIENT_ID) and retry.",
        )
        return redirect(calendar)

    state = secrets.token_urlsafe(24)
    redirect_uri = _redirect_uri(request, platform)
    if platform == "linkedin":
        url = linkedin_authorize_url(
            client_id=settings.LINKEDIN_CLIENT_ID,
            redirect_uri=redirect_uri,
            state=state,
        )
    elif platform == "twitter":
        verifier, challenge = _pkce_pair()
        request.session[_SESSION_VERIFIER] = verifier
        url = x_authorize_url(
            client_id=settings.X_CLIENT_ID,
            redirect_uri=redirect_uri,
            state=state,
            code_challenge=challenge,
        )
    elif platform in {"facebook", "instagram", "whatsapp"}:
        url = meta_authorize_url(
            client_id=settings.META_CLIENT_ID,
            redirect_uri=redirect_uri,
            state=state,
            scope=META_SCOPES[platform],
        )
    elif platform == "tiktok":
        url = tiktok_authorize_url(
            client_key=settings.TIKTOK_CLIENT_KEY,
            redirect_uri=redirect_uri,
            state=state,
        )
    elif platform == "youtube":
        url = youtube_authorize_url(
            client_id=settings.GOOGLE_CLIENT_ID,
            redirect_uri=redirect_uri,
            state=state,
        )
    else:  # reddit
        url = reddit_authorize_url(
            client_id=settings.REDDIT_CLIENT_ID,
            redirect_uri=redirect_uri,
            state=state,
        )

    request.session[_SESSION_STATE] = state
    request.session[_SESSION_PLATFORM] = platform
    return redirect(url)


@login_required
def oauth_callback(request, platform: str) -> HttpResponseRedirect:
    """Handle the provider redirect: verify state, exchange, store channel."""
    calendar = reverse("marketing_calendar")
    if platform not in PROVIDERS:
        messages.error(request, f"Unknown connector: {platform}.")
        return redirect(calendar)

    expected_platform = request.session.pop(_SESSION_PLATFORM, None)
    expected_state = request.session.pop(_SESSION_STATE, None)
    if expected_platform != platform or not expected_state:
        messages.error(request, "The connector flow expired. Start it again from the calendar.")
        return redirect(calendar)
    if request.GET.get("state") != expected_state:
        messages.error(request, "The connector flow did not verify. Start it again.")
        return redirect(calendar)
    if request.GET.get("error"):
        messages.warning(request, f"Provider authorization cancelled: {request.GET['error']}.")
        return redirect(calendar)

    workspace_id = _workspace_id(request)
    if workspace_id is None:
        messages.error(request, "You need a workspace before connecting a channel.")
        return redirect(calendar)

    code = request.GET.get("code", "")
    if not code:
        messages.error(request, "The provider returned no authorization code.")
        return redirect(calendar)

    redirect_uri = _redirect_uri(request, platform)
    try:
        if platform == "linkedin":
            tokens = exchange_linkedin_code(code=code, redirect_uri=redirect_uri)
            identity = fetch_linkedin_identity(tokens["access_token"])
            account_name = f"urn:li:person:{identity.get('sub') or ''}"
        elif platform == "twitter":
            tokens = exchange_x_code(
                code=code,
                redirect_uri=redirect_uri,
                code_verifier=request.session.pop(_SESSION_VERIFIER, ""),
            )
            identity = fetch_x_identity(tokens["access_token"])
            account_name = identity.get("username") or identity.get("name") or ""
        elif platform in {"facebook", "instagram", "whatsapp"}:
            tokens = exchange_meta_code(code=code, redirect_uri=redirect_uri)
            account_name = fetch_meta_identity(platform, tokens["access_token"])
        elif platform == "tiktok":
            tokens = exchange_tiktok_code(code=code, redirect_uri=redirect_uri)
            account_name = str(tokens.get("open_id") or "")
        elif platform == "youtube":
            tokens = exchange_youtube_code(code=code, redirect_uri=redirect_uri)
            account_name = fetch_youtube_identity(tokens["access_token"])
        else:  # reddit
            tokens = exchange_reddit_code(code=code, redirect_uri=redirect_uri)
            account_name = fetch_reddit_identity(tokens["access_token"])
    except (KeyError, ValueError) as exc:
        messages.error(request, f"Could not finish the {platform} connection: {exc}")
        return redirect(calendar)
    if not account_name:
        messages.error(request, f"{platform} returned no account identity.")
        return redirect(calendar)

    expires_in = int(tokens.get("expires_in") or 0)
    _, created = SocialChannel.objects.update_or_create(
        workspace_id=workspace_id,
        platform=platform,
        account_name=account_name,
        defaults={
            "oauth_token": tokens["access_token"],
            "oauth_refresh_token": str(tokens.get("refresh_token") or ""),
            "token_expires_at": timezone.now() + timedelta(seconds=expires_in) if expires_in else None,
            "is_active": True,
        },
    )
    verb = "Connected" if created else "Reconnected"
    display = SocialChannel.objects.get(
        workspace_id=workspace_id, platform=platform, account_name=account_name
    ).get_platform_display()
    message = f"{verb} {display} · {account_name}."
    if platform == "reddit":
        message += " Set this channel's account name to the subreddit (r/…) you moderate before publishing."
    messages.success(request, message)
    return redirect(calendar)
