"""Inbound email sync for Loop-CRM (Gmail + Outlook).

Follows the same honest-connector contract as the social adapters: a provider
adapter fetches messages over real HTTP (stdlib only) only when the account
holds a credential, and an unconfigured account reports ``unconfigured`` rather
than fabricating a sync. ``sync_account`` is the single entry point: it pulls
new messages since the account cursor, matches the sender to a workspace
contact, creates an :class:`~apps.core.models.EmailMessage` (idempotent on the
provider message id), and links it to the contact's most recent open deal.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from django.conf import settings

from .models import EmailAccount

EMAIL_PROVIDER_CATALOG: tuple[dict[str, Any], ...] = (
    {"id": "gmail", "label": "Gmail", "capabilities": ["inbound sync"]},
    {"id": "outlook", "label": "Outlook", "capabilities": ["inbound sync"]},
)


def provider_catalog() -> list[dict[str, Any]]:
    return [dict(item, capabilities=list(item["capabilities"])) for item in EMAIL_PROVIDER_CATALOG]


class _Http:
    """Tiny stdlib JSON HTTP helper (mirrors the social adapter helper)."""

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
    def post_form(cls, url: str, fields: dict, token: str | None = None) -> tuple[int, dict]:
        data = urllib.parse.urlencode(fields).encode("utf-8")
        headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return cls._request(url, method="POST", headers=headers, data=data)


@dataclass
class SyncResult:
    """Outcome of one ``sync_account`` pass."""

    status: str  # "synced" | "unconfigured" | "error"
    synced: int = 0
    skipped: int = 0
    matched: int = 0
    detail: str = ""
    messages: list[dict[str, Any]] = field(default_factory=list)


class EmailSyncConnector:
    """Minimal adapter contract shared by Gmail and Outlook."""

    provider = ""

    def fetch_messages(self, account: EmailAccount) -> list[dict[str, Any]]:
        """Return normalized messages newer than ``account.sync_cursor``.

        Each message is ``{external_id, thread_id, subject, snippet,
        sender_email, sender_name, received_at}``.
        """
        raise NotImplementedError

    def refresh(self, account: EmailAccount) -> bool:
        """Exchange a refresh token for a new access pair. Default: unsupported."""
        return False


class UnconfiguredEmailConnector(EmailSyncConnector):
    """Safe default that never claims a sync happened without credentials."""

    def __init__(self, provider: str):
        self.provider = provider

    def fetch_messages(self, account: EmailAccount) -> list[dict[str, Any]]:
        raise ValueError(f"Connect {self.provider} before syncing email.")


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    # RFC 2822 fallback (provider email headers).
    from email.utils import parsedate_to_datetime

    try:
        return parsedate_to_datetime(text)
    except (TypeError, ValueError):
        return None


def _parse_email_header(value: str) -> tuple[str, str]:
    """Split a ``Name <email>`` header into ``(email, name)`` (tolerant)."""
    from email.utils import getaddresses

    parsed = getaddresses([value])
    if not parsed:
        return "", ""
    name, email = parsed[0]
    return email.lower().strip(), name.strip()


class GmailConnector(EmailSyncConnector):
    """Gmail REST sync via ``users.messages.list`` (Gmail API v1)."""

    provider = "gmail"
    _list_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
    _token_url = "https://oauth2.googleapis.com/token"

    def fetch_messages(self, account: EmailAccount) -> list[dict[str, Any]]:
        if not account.oauth_token:
            raise ValueError("Connect Gmail before syncing email.")
        query = {"maxResults": "100"}
        cursor = account.sync_cursor or {}
        if cursor.get("last_received_at"):
            query["q"] = f'after:{int(cursor["last_received_at"])}'
        status, body = _Http.get(f"{self._list_url}?{urllib.parse.urlencode(query)}", account.oauth_token)
        if status != 200:
            detail = str(body.get("error", {}).get("message") or body.get("detail") or f"HTTP {status}")
            raise ValueError(f"Gmail sync failed: {detail}")
        messages: list[dict[str, Any]] = []
        for item in body.get("messages") or []:
            msg_id = str(item.get("id") or "").strip()
            thread_id = str(item.get("threadId") or "").strip()
            payload = item.get("payload") or {}
            headers = {h.get("name", "").lower(): h.get("value", "") for h in payload.get("headers") or []}
            sender_email, sender_name = _parse_email_header(headers.get("from", ""))
            received_at = _parse_iso(headers.get("date"))
            messages.append(
                {
                    "external_id": msg_id,
                    "thread_id": thread_id,
                    "subject": str(headers.get("subject") or ""),
                    "snippet": str(item.get("snippet") or ""),
                    "sender_email": sender_email,
                    "sender_name": sender_name,
                    "received_at": received_at,
                }
            )
        return messages

    def refresh(self, account: EmailAccount) -> bool:
        if not (account.oauth_refresh_token and getattr(settings, "GMAIL_CLIENT_ID", "")):
            return False
        status, body = _Http.post_form(
            self._token_url,
            {
                "grant_type": "refresh_token",
                "refresh_token": account.oauth_refresh_token,
                "client_id": settings.GMAIL_CLIENT_ID,
                "client_secret": settings.GMAIL_CLIENT_SECRET,
            },
        )
        access = str(body.get("access_token") or "")
        if status != 200 or not access:
            return False
        account.oauth_token = access
        expires_in = int(body.get("expires_in") or 0)
        if expires_in:
            account.token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        account.save(update_fields=["oauth_token", "token_expires_at", "updated_at"])
        return True


class OutlookConnector(EmailSyncConnector):
    """Outlook sync via Microsoft Graph ``GET /me/messages``."""

    provider = "outlook"
    _list_url = "https://graph.microsoft.com/v1/me/messages"
    _token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"

    def fetch_messages(self, account: EmailAccount) -> list[dict[str, Any]]:
        if not account.oauth_token:
            raise ValueError("Connect Outlook before syncing email.")
        params: dict[str, str] = {
            "$top": "100",
            "$select": "id,conversationId,subject,bodyPreview,from,receivedDateTime",
            "$orderby": "receivedDateTime asc",
        }
        cursor = account.sync_cursor or {}
        if cursor.get("last_received_at"):
            params["$filter"] = f"receivedDateTime gt {cursor['last_received_at']}"
        status, body = _Http.get(f"{self._list_url}?{urllib.parse.urlencode(params)}", account.oauth_token)
        if status != 200:
            detail = str(body.get("error", {}).get("message") or body.get("detail") or f"HTTP {status}")
            raise ValueError(f"Outlook sync failed: {detail}")
        messages: list[dict[str, Any]] = []
        for item in body.get("value") or []:
            sender = item.get("from") or {}
            address = sender.get("emailAddress") or {}
            messages.append(
                {
                    "external_id": str(item.get("id") or ""),
                    "thread_id": str(item.get("conversationId") or ""),
                    "subject": str(item.get("subject") or ""),
                    "snippet": str(item.get("bodyPreview") or ""),
                    "sender_email": str(address.get("address") or "").lower().strip(),
                    "sender_name": str(address.get("name") or ""),
                    "received_at": _parse_iso(item.get("receivedDateTime")),
                }
            )
        return messages

    def refresh(self, account: EmailAccount) -> bool:
        if not (account.oauth_refresh_token and getattr(settings, "OUTLOOK_CLIENT_ID", "")):
            return False
        status, body = _Http.post_form(
            self._token_url,
            {
                "grant_type": "refresh_token",
                "refresh_token": account.oauth_refresh_token,
                "client_id": settings.OUTLOOK_CLIENT_ID,
                "client_secret": settings.OUTLOOK_CLIENT_SECRET,
                "scope": "https://graph.microsoft.com/Mail.Read offline_access",
            },
        )
        access = str(body.get("access_token") or "")
        if status != 200 or not access:
            return False
        account.oauth_token = access
        expires_in = int(body.get("expires_in") or 0)
        if expires_in:
            account.token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        account.save(update_fields=["oauth_token", "token_expires_at", "updated_at"])
        return True


ADAPTERS: dict[str, type[EmailSyncConnector]] = {
    "gmail": GmailConnector,
    "outlook": OutlookConnector,
}


def connector_for(provider: str, account: EmailAccount | None = None) -> EmailSyncConnector:
    """Resolve the adapter for a provider; unconfigured falls back honestly."""
    adapter = ADAPTERS.get(provider)
    if adapter is None:
        return UnconfiguredEmailConnector(provider)
    return adapter()


def _refresh_if_expired(account: EmailAccount) -> None:
    if account.token_expires_at is None or account.token_expires_at > datetime.now(timezone.utc):
        return
    connector_for(account.provider, account).refresh(account)


def _match_contact(workspace_id: int, sender_email: str):
    from apps.crm.models import Contact

    if not sender_email:
        return None
    contact = (
        Contact.objects.filter(workspace_id=workspace_id, email__iexact=sender_email)
        .select_related("company")
        .first()
    )
    if contact is not None:
        return contact
    # Fall back to substring-insensitive match on the local part for contacts
    # whose stored email differs in casing/domain formatting.
    return (
        Contact.objects.filter(workspace_id=workspace_id, email__icontains=sender_email.split("@")[0])
        .select_related("company")
        .first()
    )


def _open_deal_for(contact) -> Any:
    """Most recent non-closed deal for a contact (or None)."""
    from apps.crm.models import Deal

    if contact is None:
        return None
    return (
        Deal.objects.filter(workspace_id=contact.workspace_id, contact=contact)
        .exclude(stage__stage_type__in=["closed_won", "closed_lost"])
        .order_by("-created_at")
        .first()
    )


def sync_account(account: EmailAccount) -> SyncResult:
    """Sync new messages for one account and return an honest summary."""
    from django.db import IntegrityError

    from .models import EmailMessage

    if not account.is_active:
        return SyncResult(status="unconfigured", detail="The account is paused.")
    try:
        _refresh_if_expired(account)
        account.refresh_from_db()
        messages = connector_for(account.provider, account).fetch_messages(account)
    except ValueError as exc:
        return SyncResult(status="unconfigured", detail=str(exc))

    synced = skipped = matched = 0
    latest: datetime | None = None
    normalized: list[dict[str, Any]] = []
    for message in messages:
        external_id = str(message.get("external_id") or "").strip()
        if not external_id:
            skipped += 1
            continue
        received = message.get("received_at")
        try:
            _, created = EmailMessage.objects.get_or_create(
                account=account,
                external_id=external_id,
                defaults={
                    "workspace_id": account.workspace_id,
                    "thread_id": str(message.get("thread_id") or ""),
                    "subject": str(message.get("subject") or ""),
                    "snippet": str(message.get("snippet") or ""),
                    "sender_email": str(message.get("sender_email") or ""),
                    "sender_name": str(message.get("sender_name") or ""),
                    "direction": "inbound",
                    "received_at": received,
                },
            )
        except IntegrityError:
            skipped += 1
            continue
        if not created:
            skipped += 1
            continue
        contact = _match_contact(account.workspace_id, str(message.get("sender_email") or ""))
        if contact is not None:
            message_record = EmailMessage.objects.get(account=account, external_id=external_id)
            message_record.contact = contact
            message_record.deal = _open_deal_for(contact)
            message_record.save(update_fields=["contact", "deal"])
            matched += 1
        synced += 1
        normalized.append(
            {
                "external_id": external_id,
                "subject": message.get("subject") or "",
                "sender_email": message.get("sender_email") or "",
                "matched": contact is not None,
            }
        )
        if isinstance(received, datetime):
            latest = received if latest is None else max(latest, received)

    if latest is not None:
        account.sync_cursor = {"last_received_at": latest.timestamp()}
        account.last_synced_at = datetime.now(timezone.utc)
        account.save(update_fields=["sync_cursor", "last_synced_at", "updated_at"])
    return SyncResult(status="synced", synced=synced, skipped=skipped, matched=matched, messages=normalized)


__all__ = [
    "ADAPTERS",
    "EmailSyncConnector",
    "GmailConnector",
    "OutlookConnector",
    "SyncResult",
    "UnconfiguredEmailConnector",
    "connector_for",
    "provider_catalog",
    "sync_account",
]
