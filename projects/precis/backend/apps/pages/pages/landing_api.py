"""Astro landing contract for the consolidated LMS Fusion site.

The Astro frontend owns the document shell while this module provides the
small, stable content/fragment contract originally proven by landing-fusion.
It deliberately reads the existing LMS/Wagtail models instead of introducing
parallel landing tables or a second migration graph.
"""

from __future__ import annotations

import html
import json
import logging
import re
from datetime import datetime

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from wagtail.models import Page

logger = logging.getLogger(__name__)


def _live_page(slug: str):
    normalized = slug.strip("/") or "home"
    try:
        return Page.objects.live().filter(slug=normalized).first()
    except Exception:
        logger.exception("Unable to load Wagtail page %s", normalized)
        return None


def _plain(value):
    """Convert Wagtail values and related model objects to JSON-safe values."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if hasattr(value, "items"):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    if hasattr(value, "isoformat"):
        return value.isoformat()

    # StreamField values frequently contain RichText and Wagtail image
    # instances.  Passing those objects directly to JsonResponse raises a
    # TypeError and turns otherwise healthy page API requests into HTTP 500s.
    # Preserve useful image metadata while reducing other Wagtail values to a
    # stable string representation.
    if hasattr(value, "pk"):
        result = {"id": value.pk, "title": str(value)}
        try:
            result["url"] = value.file.url
        except (AttributeError, ValueError, OSError):
            pass
        return result
    if hasattr(value, "__str__"):
        return str(value)
    return str(value)


def _stream_items(page, field_name: str) -> list[dict]:
    value = getattr(page, field_name, None)
    if not value:
        return []
    items: list[dict] = []
    for block in value:
        data = _plain(block.value)
        if isinstance(data, dict):
            data.setdefault("type", block.block_type)
            items.append(data)
    return items


def _page_data(page) -> dict:
    """Return a frontend-shaped page payload from any live LMS page."""
    specific = page.specific
    data = {
        "id": page.pk,
        "slug": page.slug or "home",
        "title": page.title,
        "type": specific.__class__.__name__,
        "show_in_nav": bool(getattr(specific, "show_in_nav", True)),
        "seo_title": getattr(page, "seo_title", "") or page.title,
        "search_description": getattr(page, "search_description", "") or "",
    }

    hero_heading = getattr(specific, "hero_heading", "")
    hero_subheading = getattr(specific, "hero_subheading", "")
    data["hero"] = {
        "badge": "fusion lms · server-rendered content",
        "title": hero_heading or page.title,
        "subtitle": hero_subheading or getattr(specific, "intro_text", "") or "",
        "primary_cta": {"label": "Explore courses", "href": "/courses/", "style": "primary"},
        "secondary_cta": {"label": "Learn about Fusion", "href": "/about/", "style": "secondary"},
    }

    body = getattr(specific, "body", None) or getattr(specific, "intro_text", None)
    if body:
        data["body"] = str(body)

    for field_name in ("stats", "features", "testimonials", "pricing", "faq", "projects", "services", "process", "blog"):
        items = _stream_items(specific, field_name)
        if items:
            data[field_name] = items

    # Existing LMS pages use these fields rather than landing-fusion's names.
    for source, target in (("summary", "features"), ("facts", "testimonials"), ("CTA", "cta")):
        if target not in data:
            items = _stream_items(specific, source)
            if items:
                data[target] = items

    data.setdefault("cta", {
        "title": "Start learning with Fusion LMS",
        "subtitle": "A focused learning platform built with Django, Wagtail, and Astro.",
        "primary_cta": {"label": "Browse courses", "href": "/courses/", "style": "primary"},
    })
    return data


def site_settings_api(request: HttpRequest) -> JsonResponse:
    try:
        from apps.content.models.settings import SiteSettings

        settings_obj = SiteSettings.for_request(request)
    except Exception:
        settings_obj = None

    return JsonResponse({
        "site_name": getattr(settings_obj, "site_name", "Fusion LMS"),
        "site_tagline": getattr(settings_obj, "site_tagline", "Learning that ships."),
        "logo_url": None,
        "favicon_url": "/favicon.svg",
        "primary_color": "#00a1b3",
        "accent_color": "#008080",
        "meta_description": getattr(settings_obj, "footer_description", ""),
        "meta_keywords": "learning, LMS, django-fusion, Astro",
        "meta_author": "Fusion Team",
        "og_image_url": None,
        "twitter_handle": "",
        "analytics_provider": "",
        "google_tag_manager_id": "",
        "google_analytics_id": "",
        "nav_show_home": True,
        "nav_show_contact": True,
        "nav_cta_label": "Browse courses",
        "nav_cta_url": "/courses/",
        "footer_description": getattr(settings_obj, "footer_description", "A modern learning platform powered by django-fusion."),
        "footer_address": getattr(settings_obj, "footer_address", ""),
        "footer_phone": getattr(settings_obj, "footer_phone", ""),
        "footer_email": getattr(settings_obj, "footer_email", ""),
        "footer_copyright": getattr(settings_obj, "footer_copyright", "© 2026 Fusion LMS"),
        "newsletter_prompt": getattr(settings_obj, "newsletter_prompt", ""),
        "google_play_url": "",
        "apple_store_url": "",
        "privacy_policy_url": getattr(settings_obj, "privacy_policy_url", "/privacy/"),
        "terms_of_use_url": getattr(settings_obj, "terms_of_use_url", "/legal/terms/"),
        "chat_enabled": False,
        "chat_provider": "",
        "chat_widget_id": "",
        "social_links": [],
        "footer_link_groups": [],
    })


def navigation_api(request: HttpRequest) -> JsonResponse:
    items = [{"label": "Home", "href": "/", "active": request.path == "/"}]
    try:
        root = Page.get_first_root_node()
        for child in root.get_children().live().order_by("title"):
            specific = child.specific
            if not getattr(specific, "show_in_nav", True):
                continue
            items.append({
                "label": child.title,
                "href": child.url or f"/{child.slug}/",
                "active": request.path.startswith(child.url or f"/{child.slug}/"),
            })
    except Exception:
        # The API remains useful before the optional Wagtail seed command runs.
        items.extend([
            {"label": "Courses", "href": "/courses/", "active": False},
            {"label": "About", "href": "/about/", "active": False},
            {"label": "Contact", "href": "/contact/", "active": False},
        ])
    return JsonResponse({"nav_items": items})


def page_data_api(request: HttpRequest, slug: str) -> JsonResponse:
    page = _live_page(slug)
    if page is None:
        return JsonResponse({"error": "Page not found"}, status=404)
    return JsonResponse(_page_data(page))


def page_list_api(request: HttpRequest) -> JsonResponse:
    pages = []
    for page in Page.objects.live().filter(depth__gt=1).order_by("title"):
        pages.append({"id": page.pk, "slug": page.slug, "title": page.title, "type": page.specific_class.__name__})
    return JsonResponse({"pages": pages, "total": len(pages)})


def contact_api(request: HttpRequest) -> JsonResponse:
    return JsonResponse({
        "title": "Get in touch",
        "description": "Questions about courses, content, or the Fusion platform? Send a message.",
        "methods": [{
            "type": "email",
            "label": "Email",
            "value": "support@lms-fusion.com",
            "href": "mailto:support@lms-fusion.com",
        }],
        "form_title": "Send us a message",
        "form_description": "We will get back to you within one business day.",
    })


def assets_api(request: HttpRequest) -> JsonResponse:
    from django.conf import settings

    return JsonResponse({
        "version": "lms-fusion-astro",
        "static_url": settings.STATIC_URL,
        "fusion_render_first": bool(getattr(settings, "FUSION_RENDER_FIRST_DEFAULT", True)),
        "enabled": True,
        "webpack_enabled": False,
        "webpack_bundle_dir": "",
        "top": {"preconnect": ["https://fonts.googleapis.com"], "fonts": [], "css": []},
        "bottom": {"js": []},
        "fonts": [],
        "preconnect": ["https://fonts.googleapis.com"],
    })


@csrf_exempt
def contact_submit_api(request: HttpRequest) -> HttpResponse:
    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)

    payload = request.POST
    if request.content_type == "application/json":
        try:
            payload = json.loads(request.body or "{}")
        except (TypeError, ValueError):
            payload = {}

    name = html.escape(str(payload.get("name", "")).strip())
    email = html.escape(str(payload.get("email", "")).strip())
    subject = str(payload.get("subject", "")).strip()
    message = str(payload.get("message", "")).strip()
    if (
        not name
        or not subject
        or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email)
        or len(message) < 10
    ):
        return HttpResponse(
            '<p class="text-red-500 font-medium">Please provide a name, subject, valid email, and message.</p>',
            status=400,
        )

    # Reuse the existing Wagtail contact-submission model rather than
    # introducing a second landing-only table or migration graph.
    from apps.content.models.contact import ContactSubmission

    ContactSubmission.objects.create(
        form_id="landing-contact",
        page_id=0,
        page_title="Astro landing contact",
        page_url=request.build_absolute_uri(),
        submitted_data={"name": name, "email": email, "subject": subject, "message": message},
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        referrer=request.META.get("HTTP_REFERER", ""),
    )
    return HttpResponse(f'<p class="text-fu-live font-medium">✓ Thanks, {name}! We will reply at {email}.</p>')


@csrf_exempt
def newsletter_subscribe_api(request: HttpRequest) -> JsonResponse:
    email = request.POST.get("email", "").strip()
    valid = bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email))
    return JsonResponse({"success": valid, "message": "Subscribed!" if valid else "Please enter a valid email address."}, status=200 if valid else 400)


def htmx_ping_api(request: HttpRequest) -> HttpResponse:
    return HttpResponse(
        f'<div class="text-center"><p class="font-mono text-2xl font-bold text-fu-link">{datetime.now():%Y-%m-%d %H:%M:%S}</p>'
        '<p class="mt-1 font-mono text-[0.65rem] uppercase tracking-[0.16em] text-fu-muted">server time · text/html fragment</p></div>'
    )


def render_mode_api(request: HttpRequest) -> JsonResponse:
    from django.conf import settings

    render_first = bool(getattr(settings, "FUSION_RENDER_FIRST_DEFAULT", True))
    header = request.headers.get("X-Fusion-Render-First")
    if header in {"true", "false"}:
        render_first = header == "true"
    return JsonResponse({
        "fusion_render_first": render_first,
        "mode": "fusion-render" if render_first else "data-api",
        "content": {"html": "/", "data": "/apis/pages/home/"},
    })
