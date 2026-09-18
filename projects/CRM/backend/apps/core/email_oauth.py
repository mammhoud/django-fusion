"""OAuth 2.0 connect flows for Gmail and Outlook email sync.

``connect_start`` redirects the user to the provider's authorization screen
(state is held in the session); ``oauth_callback`` verifies state, exchanges
the code for tokens, fetches the mailbox identity, and upserts an
``EmailAccount`` in the user's workspace. From there the existing
``apps.core.email_sync`` adapters (``GmailConnector`` / ``OutlookConnector``)
sync inbound messages with the stored tokens, refreshing them when they expire.

This mirrors the social channel flows in ``apps.marketing.oauth`` (state
verification, honest unconfigured behavior, stdlib-only HTTP). Nothing is sent
to a provider unless the client credentials from ``settings`` are configured;
otherwise the user gets an honest redirect notice.
"""

from __future__ import annotations

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

from .email_sync import _Http
from .models import EmailAccount

EMAIL_PROVIDERS = {"gmail", "outlook"}

_SESSION_STATE = "loop_email_oauth_state"
_SESSION_PROVIDER = "loop_email_oauth_provider"

# ── Pure URL builders (unit-testable without HTTP) ───────────────────────────

def gmail_authorize_url(*, client_id: str, redirect_uri: str, state: str) -> str:
    """Google authorization URL for read-only Gmail access with offline refresh."""
    params = urlencode(
        {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "https://www.googleapis.com/auth/gmail.readonly",
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
        }
    )
    return f"https://accounts.google.com/o/oauth2/v2/auth?{params}"


def outlook_authorize_url(*, client_id: str, redirect_uri: str, state: str) -> str:
    """Microsoft identity authorization URL for Graph Mail.Read + offline access."""
    params = urlencode(
        {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "https://graph.microsoft.com/Mail.Read https://graph.microsoft.com/User.Read offline_access",
            "state": state,
        }
    )
    return f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?{params}"


# ── Token exchange + identity fetch (real provider I/O via stdlib HTTP) ──────

def exchange_gmail_code(*, code: str, redirect_uri: str) -> dict:
    status, body = _Http.post_form(
        "https://oauth2.googleapis.com/token",
        {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": settings.GMAIL_CLIENT_ID,
            "client_secret": settings.GMAIL_CLIENT_SECRET,
        },
    )
    if status != 200:
        raise ValueError(body.get("error_description") or body.get("error") or "Gmail token exchange failed.")
    return body


def fetch_gmail_identity(access_token: str) -> dict:
    status, body = _Http.get("https://www.googleapis.com/oauth2/v3/userinfo", access_token)
    if status != 200:
        raise ValueError("Gmail identity fetch failed.")
    return body


def exchange_outlook_code(*, code: str, redirect_uri: str) -> dict:
    status, body = _Http.post_form(
        "https://login.microsoftonline.com/common/oauth2/v2.0/token",
        {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": settings.OUTLOOK_CLIENT_ID,
            "client_secret": settings.OUTLOOK_CLIENT_SECRET,
        },
    )
    if status != 200:
        raise ValueError(body.get("error_description") or body.get("error") or "Outlook token exchange failed.")
    return body


def fetch_outlook_identity(access_token: str) -> dict:
    status, body = _Http.get("https://graph.microsoft.com/v1.0/me", access_token)
    if status != 200:
        raise ValueError("Outlook identity fetch failed.")
    return body


# ── Views ────────────────────────────────────────────────────────────────────

def _client_configured(provider: str) -> bool:
    if provider == "gmail":
        return bool(settings.GMAIL_CLIENT_ID and settings.GMAIL_CLIENT_SECRET)
    return bool(settings.OUTLOOK_CLIENT_ID and settings.OUTLOOK_CLIENT_SECRET)


def _redirect_uri(request, provider: str) -> str:
    callback_path = reverse("email_oauth_callback", args=[provider])
    base = getattr(settings, "EMAIL_REDIRECT_BASE", "") or getattr(settings, "SOCIAL_REDIRECT_BASE", "")
    if base:
        return f"{base.rstrip('/')}{callback_path}"
    return request.build_absolute_uri(callback_path)


def _workspace_id(request):
    try:
        return request.user.profile.workspace_id
    except Exception:  # noqa: BLE001 - a profile is optional for auth
        return None


def _email_inbox() -> str:
    return reverse("settings_email")


@login_required
def connect_start(request, provider: str) -> HttpResponseRedirect:
    """Redirect the user to the provider's authorization screen."""
    inbox = _email_inbox()
    if provider not in EMAIL_PROVIDERS:
        messages.error(request, f"Unknown email provider: {provider}.")
        return redirect(inbox)
    if not _client_configured(provider):
        messages.error(
            request,
            f"Connect {provider} client credentials are not configured "
            "(GMAIL_CLIENT_ID / OUTLOOK_CLIENT_ID). Add them to the backend .env and retry.",
        )
        return redirect(inbox)

    state = secrets.token_urlsafe(24)
    redirect_uri = _redirect_uri(request, provider)
    if provider == "gmail":
        url = gmail_authorize_url(client_id=settings.GMAIL_CLIENT_ID, redirect_uri=redirect_uri, state=state)
    else:
        url = outlook_authorize_url(client_id=settings.OUTLOOK_CLIENT_ID, redirect_uri=redirect_uri, state=state)

    request.session[_SESSION_STATE] = state
    request.session[_SESSION_PROVIDER] = provider
    return redirect(url)


@login_required
def oauth_callback(request, provider: str) -> HttpResponseRedirect:
    """Handle the provider redirect: verify state, exchange, store the account."""
    inbox = _email_inbox()
    if provider not in EMAIL_PROVIDERS:
        messages.error(request, f"Unknown email provider: {provider}.")
        return redirect(inbox)

    expected_provider = request.session.pop(_SESSION_PROVIDER, None)
    expected_state = request.session.pop(_SESSION_STATE, None)
    if expected_provider != provider or not expected_state:
        messages.error(request, "The email connect flow expired. Start it again from the inbox.")
        return redirect(inbox)
    if request.GET.get("state") != expected_state:
        messages.error(request, "The email connect flow did not verify. Start it again.")
        return redirect(inbox)
    if request.GET.get("error"):
        messages.warning(request, f"Provider authorization cancelled: {request.GET['error']}.")
        return redirect(inbox)

    workspace_id = _workspace_id(request)
    if workspace_id is None:
        messages.error(request, "You need a workspace before connecting a mailbox.")
        return redirect(inbox)

    code = request.GET.get("code", "")
    if not code:
        messages.error(request, "The provider returned no authorization code.")
        return redirect(inbox)

    redirect_uri = _redirect_uri(request, provider)
    try:
        if provider == "gmail":
            tokens = exchange_gmail_code(code=code, redirect_uri=redirect_uri)
            identity = fetch_gmail_identity(tokens["access_token"])
            email = str(identity.get("email") or "").strip().lower()
        else:
            tokens = exchange_outlook_code(code=code, redirect_uri=redirect_uri)
            identity = fetch_outlook_identity(tokens["access_token"])
            email = str(identity.get("mail") or identity.get("userPrincipalName") or "").strip().lower()
    except (KeyError, ValueError) as exc:
        messages.error(request, f"Could not finish the {provider} connection: {exc}")
        return redirect(inbox)
    if not email:
        messages.error(request, f"{provider} returned no mailbox identity.")
        return redirect(inbox)

    expires_in = int(tokens.get("expires_in") or 0)
    account, created = EmailAccount.objects.update_or_create(
        workspace_id=workspace_id,
        provider=provider,
        email=email,
        defaults={
            "oauth_token": tokens["access_token"],
            "oauth_refresh_token": str(tokens.get("refresh_token") or ""),
            "token_expires_at": timezone.now() + timedelta(seconds=expires_in) if expires_in else None,
            "is_active": True,
            "created_by": request.user if getattr(request.user, "is_authenticated", False) else None,
        },
    )
    verb = "Connected" if created else "Reconnected"
    messages.success(request, f"{verb} {account.get_provider_display()} · {email}.")
    return redirect(inbox)
