"""OAuth 2.0 connect flows for LinkedIn and X (Twitter).

``connect_start`` redirects the user to the provider's authorization screen
(state, and PKCE for X, are held in the session); ``oauth_callback`` verifies
state, exchanges the code for tokens, fetches the account identity, and upserts
a ``SocialChannel`` in the user's workspace. From there the existing
``SocialConnector`` adapters (``apps.marketing.connector_adapters``) publish
with the stored token, refreshing it when it expires.

HTTP uses the same stdlib helper as the adapters, so no extra dependency is
added. Nothing is sent to a provider unless the client credentials from
``settings`` are configured; otherwise the user gets an honest redirect notice.
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

from .connector_adapters import _Http
from .models import SocialChannel

PROVIDERS = {"linkedin", "twitter"}

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


# ── Views ────────────────────────────────────────────────────────────────────

def _client_configured(platform: str) -> bool:
    if platform == "linkedin":
        return bool(settings.LINKEDIN_CLIENT_ID and settings.LINKEDIN_CLIENT_SECRET)
    return bool(settings.X_CLIENT_ID and settings.X_CLIENT_SECRET)


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
            f"Connect {platform} client credentials are not configured "
            "(LINKEDIN_CLIENT_ID / X_CLIENT_ID). Add them to the backend .env and retry.",
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
    else:
        verifier, challenge = _pkce_pair()
        request.session[_SESSION_VERIFIER] = verifier
        url = x_authorize_url(
            client_id=settings.X_CLIENT_ID,
            redirect_uri=redirect_uri,
            state=state,
            code_challenge=challenge,
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
        else:
            tokens = exchange_x_code(
                code=code,
                redirect_uri=redirect_uri,
                code_verifier=request.session.pop(_SESSION_VERIFIER, ""),
            )
            identity = fetch_x_identity(tokens["access_token"])
            account_name = identity.get("username") or identity.get("name") or ""
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
    messages.success(request, f"{verb} {SocialChannel.objects.get(workspace_id=workspace_id, platform=platform, account_name=account_name).get_platform_display()} · {account_name}.")
    return redirect(calendar)
