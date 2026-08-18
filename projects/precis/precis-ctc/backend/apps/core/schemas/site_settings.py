"""
Site settings API schemas — Social links, footer content, site identity (Pydantic).

Endpoint:
    GET /apis/site/settings → SiteSettingsResponse

Replaces hardcoded data in:
    - components/common/Social.tsx
    - layouts/footers/FooterCommon.tsx
    - layouts/footers/FooterOne.tsx
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel


class SocialLinkResponse(BaseModel):
    """Single social media link."""

    id: int
    platform: str
    label: str = ""
    url: str
    icon_svg: str = ""
    icon_class: str = ""


class FooterLinkItem(BaseModel):
    """A single footer link."""

    label: str
    url: str


class FooterLinkGroupResponse(BaseModel):
    """A group of footer links with a title."""

    title: str
    links: list[FooterLinkItem] = []


class SiteIdentityResponse(BaseModel):
    """Site identity info (name, tagline, logo)."""

    site_name: str = "CTC Research"
    site_tagline: str = ""
    logo_url: Optional[str] = None


class FooterDataResponse(BaseModel):
    """Footer content — description, contact, links, copyright."""

    description: str = ""
    address: str = ""
    phone: str = ""
    email: str = ""
    copyright: str = ""
    google_play_url: str = ""
    apple_store_url: str = ""
    privacy_policy_url: str = ""
    terms_of_use_url: str = ""
    link_groups: list[FooterLinkGroupResponse] = []


class SiteSettingsResponse(BaseModel):
    """Full site settings response for GET /apis/site/settings.

    Contains all Wagtail-managed content needed by next-LMS:
    social links, footer data, site identity.
    """

    identity: SiteIdentityResponse
    social_links: list[SocialLinkResponse] = []
    footer: FooterDataResponse
