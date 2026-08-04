"""
Site settings & navigation API.

Serves Wagtail SiteSettings, social links, and navigation trees to the
frontend for rendering header/footer/global chrome.

Endpoints:
    GET /apis/site/settings/  — full site identity + footer
    GET /apis/site/nav/        — navigation tree
"""

from django_fusion.routes.rendering.renderers import fusion_json_response


def site_settings(request):
    """GET /apis/site/settings/ — Wagtail SiteSettings + social links."""
    try:
        from apps.content.models.settings import SiteSettings

        instance = SiteSettings.for_request(request)
        socials = _get_social_links()
        footer_groups = _get_footer_groups(instance)

        return fusion_json_response(
            data={
                "site_name": instance.site_name,
                "site_tagline": instance.site_tagline,
                "logo_url": (
                    instance.logo.get_rendition("height-60").url
                    if instance.logo else None
                ),
                "footer": {
                    "description": instance.footer_description or "",
                    "address": instance.footer_address or "",
                    "phone": instance.footer_phone or "",
                    "email": instance.footer_email or "",
                    "copyright": instance.footer_copyright or "",
                    "google_play_url": instance.google_play_url or "",
                    "apple_store_url": instance.apple_store_url or "",
                    "privacy_policy_url": instance.privacy_policy_url or "/privacy",
                    "terms_of_use_url": instance.terms_of_use_url or "/terms",
                    "link_groups": footer_groups,
                },
                "social_links": socials,
            },
            status=200,
        )
    except Exception:
        return fusion_json_response(
            data={"site_name": "Fusion CMS"},
            status=200,
        )


def site_nav(request):
    """GET /apis/site/nav/ — navigation tree for header menus."""
    try:
        from wagtail.models import Page

        nav_items = []
        for page in Page.objects.live().filter(depth__gt=1, show_in_nav=True).order_by("path"):
            nav_items.append({
                "id": page.pk,
                "title": page.title,
                "slug": page.slug,
                "url": page.url if hasattr(page, "url") else f"/{page.slug}/",
                "children": [
                    {"id": c.pk, "title": c.title, "slug": c.slug, "url": f"/{c.slug}/"}
                    for c in page.get_children().live().filter(show_in_nav=True)
                ],
            })

        return fusion_json_response(data={"items": nav_items}, status=200)
    except Exception:
        return fusion_json_response(data={"items": []}, status=200)


# ── Internal Helpers ──────────────────────────────────────────────────

def _get_social_links():
    """Return active social links as a list of dicts."""
    try:
        from apps.content.models.settings import SocialLink

        return [
            {
                "platform": s.platform,
                "label": s.label or s.get_platform_display(),
                "url": s.url,
                "icon_svg": s.icon_svg or "",
                "icon_class": s.icon_class or f"fab fa-{s.platform}",
            }
            for s in SocialLink.objects.filter(is_active=True)
        ]
    except Exception:
        return []


def _get_footer_groups(instance):
    """Serialize footer link groups."""
    try:
        groups = []
        for group in instance.footer_link_groups.all().order_by("sort_order"):
            links = [
                {"label": link.label, "url": link.url}
                for link in group.links.all().order_by("sort_order")
            ]
            groups.append({"title": group.title, "links": links})
        return groups
    except Exception:
        return []
