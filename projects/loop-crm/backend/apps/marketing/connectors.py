"""Social connector contracts for Loop-CRM.

The catalog covers the source platform families without pretending credentials
or API calls are configured. Real OAuth adapters implement ``SocialConnector``
and are dispatched by platform from the Dramatiq worker.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

PLATFORM_CATALOG: tuple[dict[str, Any], ...] = (
    {"id": "linkedin", "label": "LinkedIn", "capabilities": ["publish", "analytics"]},
    {"id": "twitter", "label": "Twitter / X", "capabilities": ["publish", "analytics"]},
    {"id": "instagram", "label": "Instagram", "capabilities": ["publish", "media", "analytics"]},
    {"id": "facebook", "label": "Facebook", "capabilities": ["publish", "media", "analytics"]},
    {"id": "tiktok", "label": "TikTok", "capabilities": ["publish", "media", "analytics"]},
    {"id": "youtube", "label": "YouTube", "capabilities": ["publish", "media", "analytics"]},
    {"id": "reddit", "label": "Reddit", "capabilities": ["publish", "analytics"]},
    {"id": "discord", "label": "Discord", "capabilities": ["publish"]},
    {"id": "slack", "label": "Slack", "capabilities": ["publish"]},
    {"id": "bluesky", "label": "Bluesky", "capabilities": ["publish", "analytics"]},
    {"id": "mastodon", "label": "Mastodon", "capabilities": ["publish", "analytics"]},
    {"id": "whatsapp", "label": "WhatsApp", "capabilities": ["publish", "analytics"]},
)


@dataclass(frozen=True)
class PublishResult:
    """Connector result; ``external_id`` is returned by a real provider adapter."""

    success: bool
    external_id: str = ""
    message: str = "Connector credentials are not configured."


class SocialConnector:
    """Minimal adapter contract shared by every social provider."""

    platform = ""

    def publish(self, post: Any) -> PublishResult:
        raise NotImplementedError

    def fetch_analytics(self, post: Any) -> dict[str, int]:
        raise NotImplementedError


class UnconfiguredConnector(SocialConnector):
    """Safe default that never marks a post published without provider I/O."""

    def __init__(self, platform: str):
        self.platform = platform

    def publish(self, post: Any) -> PublishResult:
        return PublishResult(False, message=f"Connect {self.platform} before publishing.")

    def fetch_analytics(self, post: Any) -> dict[str, int]:
        return {}


def connector_for(platform: str) -> SocialConnector:
    """Resolve a connector without leaking OAuth tokens or making network calls."""
    return UnconfiguredConnector(platform)


def platform_catalog() -> list[dict[str, Any]]:
    return [dict(platform, capabilities=list(platform["capabilities"])) for platform in PLATFORM_CATALOG]
