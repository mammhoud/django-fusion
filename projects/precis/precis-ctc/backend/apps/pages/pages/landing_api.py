"""Astro landing contract for the consolidated LMS Fusion site.

The Astro frontend owns the document shell while this module provides the
small, stable content/fragment contract originally proven by precis-landing.
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
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from wagtail.blocks.list_block import ListValue
from wagtail.blocks.struct_block import StructValue
from wagtail.blocks.stream_block import StreamValue
from wagtail.models import Page
from wagtail.rich_text import RichText

logger = logging.getLogger(__name__)


def _requested_language(request: HttpRequest) -> str:
    """Return a supported language code from the query or Django locale."""
    requested = (request.GET.get("lang") or getattr(request, "LANGUAGE_CODE", "en")).lower()
    return requested if requested in {"en", "sv", "fr", "de", "es", "ar", "pt-br"} else "en"


def get_effective_render_first(request: HttpRequest | None = None) -> bool:
    """Return the effective ``fusion_render_first`` preference.

    Thin wrapper over django-fusion's canonical ``resolve_render_first``
    chain (``X-Fusion-Render-First`` header → explicit session preference →
    the ``FUSION_RENDER_FIRST`` setting).

    ``True``  → “fusion render first” — Django renders finished HTML.
    ``False`` → “data APIs” — the client renders from /apis/* JSON.
    """
    from django_fusion.routes.rendering.render_mode import resolve_render_first

    return resolve_render_first(request)


def _live_page(slug: str, language: str = "en"):
    normalized = slug.strip("/") or "home"
    try:
        pages = Page.objects.live().filter(slug=normalized)
        if language:
            localized = pages.filter(locale__language_code=language).first()
            if localized is not None:
                return localized
        return pages.filter(locale__language_code="en").first() or pages.first()
    except Exception:
        logger.exception("Unable to load Wagtail page %s", normalized)
        return None


def _plain(value):
    """Convert Wagtail values and related model objects to JSON-safe values.

    Handles the Wagtail container/value types that appear inside StreamField
    blocks — ``StructValue``, ``ListValue``, ``StreamValue`` and ``RichText`` —
    so that seeded blocks (gallery ``media_items``, counters, contact-form
    ``fields``, ``methods``, ``team_members``) serialize as clean JSON instead
    of the default ``<ListValue: [...]>`` string representation.
    """
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")

    # RichText → its rendered HTML.
    if isinstance(value, RichText):
        return str(value)

    # Wagtail StreamValue → list of {type, ...value} entries.
    if isinstance(value, StreamValue):
        items = []
        for block in value:
            data = _plain(block.value)
            if isinstance(data, dict):
                data.setdefault("type", block.block_type)
                items.append(data)
            else:
                items.append({"type": block.block_type, "value": data})
        return items

    # Wagtail StructValue and plain dicts → recurse over items.
    if isinstance(value, (StructValue, dict)) or (
        not isinstance(value, (str, bytes, list, tuple, ListValue))
        and hasattr(value, "items")
    ):
        return {str(key): _plain(item) for key, item in value.items()}

    # Wagtail ListValue and plain lists/tuples → recurse over items.
    if isinstance(value, (ListValue, list, tuple)):
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
        "badge": "ctc research · medical research learning",
        "title": hero_heading or page.title,
        "subtitle": hero_subheading or getattr(specific, "intro_text", "") or "",
        "primary_cta": {"label": "Explore courses", "href": "/courses/", "style": "primary"},
        "secondary_cta": {"label": "Learn about CTC Research", "href": "/about/", "style": "secondary"},
    }

    body = getattr(specific, "body", None) or getattr(specific, "intro_text", None)
    if body:
        data["body"] = str(body)

    for field_name in ("stats", "features", "testimonials", "pricing", "faq", "projects", "services", "process", "blog"):
        items = _stream_items(specific, field_name)
        if items:
            data[field_name] = items

    # Existing LMS pages use these fields rather than precis-landing's names.
    for source, target in (("summary", "features"), ("facts", "testimonials"), ("CTA", "cta")):
        if target not in data:
            items = _stream_items(specific, source)
            if items:
                data[target] = items

    # Expose the concrete seeded blocks the Astro shell renders directly —
    # team members, gallery media, counters, the about experience/video
    # fields, and the home "methods" list — so the frontend never needs a
    # hardcoded fallback. Values are localized via _live_page().
    _extract_seeded_blocks(specific, data)

    data.setdefault("cta", {
        "title": "Start learning with CTC Research",
        "subtitle": "A medical research center built with Django, Wagtail, and Astro.",
        "primary_cta": {"label": "Browse courses", "href": "/courses/", "style": "primary"},
    })
    return data


def _extract_seeded_blocks(specific, data: dict) -> None:
    """Populate structured seed blocks the frontend renders directly.

    Keeps the Astro data contract explicit for team members, gallery media,
    counters, the about experience/video fields, and the home "methods" list.
    """
    # Team members (TeamPage.body → team_section blocks).
    body = getattr(specific, "body", None)
    if body is not None:
        for block in body:
            if block.block_type == "team_section":
                members = block.value.get("team_members") or []
                if members:
                    data["team_members"] = _plain(members)
                    data.setdefault("team_title", _plain(block.value.get("title") or ""))
                    data.setdefault("team_subtitle", _plain(block.value.get("subtitle") or ""))
                break

    # About page: gallery, counters, experience + video (facts → about).
    facts = getattr(specific, "facts", None)
    if facts is not None:
        for block in facts:
            if block.block_type == "about":
                about = block.value
                gallery = about.get("gallery")
                if gallery is not None:
                    media_items = gallery.get("media_items") or []
                    if media_items:
                        data["gallery"] = _plain(media_items)
                counters = about.get("counters")
                if counters:
                    data["counters"] = _plain(counters)
                if about.get("experience_description"):
                    data["experience_description"] = _plain(about["experience_description"])
                if about.get("video_link"):
                    data["video_link"] = _plain(about["video_link"])
                break

    # Home page: why-choose "methods" list (CTA → why_choose_section).
    cta = getattr(specific, "CTA", None)
    if cta is not None:
        for block in cta:
            if block.block_type == "why_choose_section":
                methods = block.value.get("methods") or []
                if methods:
                    data["methods"] = _plain(methods)
                break

    # Events page: active/visible Event rows so the Astro /events/ route
    # renders the seeded calendar instead of a 404/fallback.
    if specific.__class__.__name__ == "EventPage":
        try:
            from apps.pages.accounts.models import Event

            data["events"] = [
                {
                    "title": event.title,
                    "description": event.description,
                    "event_type": event.event_type,
                    "event_type_label": event.get_event_type_display(),
                    "location": event.location,
                    "start_date": event.start_date.isoformat() if event.start_date else None,
                    "end_date": event.end_date.isoformat() if event.end_date else None,
                }
                for event in Event.objects.filter(is_active=True, is_visible=True).order_by("start_date", "title")
            ]
        except Exception:
            logger.exception("Event listing unavailable")


def site_settings_api(request: HttpRequest) -> JsonResponse:
    """GET /apis/site/settings/ — branding, social links, footer content.

    Returns Wagtail-managed site identity data (SiteSettings + seeded
    SocialLink/FooterLinkGroup snippets) consumed by the Astro chrome.
    """
    try:
        from apps.content.models.settings import SiteSettings

        settings_obj = SiteSettings.for_request(request)
    except Exception:
        settings_obj = None

    # Social links — real seeded snippet rows when available.
    social_links = []
    try:
        from apps.content.models.settings import SocialLink

        social_links = [
            {
                "platform": link.platform,
                "label": link.label or link.get_platform_display(),
                "url": link.url,
                "icon_class": link.icon_class or f"fab fa-{link.platform}",
            }
            for link in SocialLink.objects.filter(is_active=True).order_by("sort_order")
        ]
    except Exception:
        pass

    # Footer link groups — inline children of SiteSettings.
    footer_groups = []
    if settings_obj:
        try:
            for group in settings_obj.footer_link_groups.all().order_by("sort_order"):
                footer_groups.append({
                    "title": group.title,
                    "links": [
                        {"label": link.label, "url": link.url}
                        for link in group.links.all().order_by("sort_order")
                    ],
                })
        except Exception:
            pass

    logo_url = None
    if settings_obj and settings_obj.logo:
        try:
            logo_url = settings_obj.logo.get_rendition("height-60").url
        except Exception:
            pass

    favicon_url = None
    if settings_obj and settings_obj.favicon:
        try:
            favicon_url = settings_obj.favicon.get_rendition("width-32").url
        except Exception:
            pass
    if not favicon_url:
        favicon_url = "/favicon.svg"

    # Best-effort model helpers: if the deployed schema predates the
    # parity migration, degrade to {} instead of 500ing the endpoint
    # (matches the defensive style of the rest of this view).
    seo = {}
    analytics = {}
    if settings_obj:
        try:
            seo = settings_obj.get_seo_context()
        except Exception:
            pass
        try:
            analytics = settings_obj.get_analytics_context()
        except Exception:
            pass

    return JsonResponse({
        "site_name": getattr(settings_obj, "site_name", "CTC Research"),
        "site_tagline": getattr(settings_obj, "site_tagline", "Evidence you can build on."),
        "logo_url": logo_url,
        "favicon_url": favicon_url,
        "primary_color": getattr(settings_obj, "primary_color", "") or "#00a1b3",
        "accent_color": getattr(settings_obj, "accent_color", "") or "#008080",
        "meta_description": seo.get("meta_description", "") or getattr(settings_obj, "footer_description", ""),
        "meta_keywords": seo.get("meta_keywords", ""),
        "meta_author": seo.get("meta_author", ""),
        "og_image_url": seo.get("og_image_url"),
        "twitter_handle": seo.get("twitter_handle", ""),
        "analytics_provider": analytics.get("provider", ""),
        "google_tag_manager_id": analytics.get("gtm_id", ""),
        "google_analytics_id": analytics.get("ga4_id", ""),
        "nav_show_home": getattr(settings_obj, "nav_show_home", True),
        "nav_show_contact": getattr(settings_obj, "nav_show_contact", True),
        "nav_cta_label": getattr(settings_obj, "nav_cta_label", "") or "Browse courses",
        "nav_cta_url": getattr(settings_obj, "nav_cta_url", "/courses/"),
        "footer_description": getattr(settings_obj, "footer_description", "Medical research education and evidence services for clinical and research teams."),
        "footer_address": getattr(settings_obj, "footer_address", ""),
        "footer_phone": getattr(settings_obj, "footer_phone", ""),
        "footer_email": getattr(settings_obj, "footer_email", ""),
        "footer_copyright": getattr(settings_obj, "footer_copyright", "© 2026 CTC Research"),
        "footer_banner_enabled": getattr(settings_obj, "footer_banner_enabled", False),
        "footer_banner_text": getattr(settings_obj, "footer_banner_text", ""),
        "footer_banner_style": getattr(settings_obj, "footer_banner_style", ""),
        "footer_text_secondary": getattr(settings_obj, "footer_text_secondary", ""),
        "newsletter_prompt": getattr(settings_obj, "newsletter_prompt", ""),
        "google_play_url": getattr(settings_obj, "google_play_url", ""),
        "apple_store_url": getattr(settings_obj, "apple_store_url", ""),
        "privacy_policy_url": getattr(settings_obj, "privacy_policy_url", "/privacy/"),
        "terms_of_use_url": getattr(settings_obj, "terms_of_use_url", "/legal/terms/"),
        "chat_enabled": getattr(settings_obj, "chat_enabled", False),
        "chat_provider": getattr(settings_obj, "chat_provider", ""),
        "chat_widget_id": getattr(settings_obj, "chat_widget_id", ""),
        "social_links": social_links,
        "footer_link_groups": footer_groups,
    })


def _language_catalog() -> list[dict]:
    """Return the seeded Precis language catalog, with a safe bootstrap fallback."""
    fallback = [
        {"code": "en", "name": "English", "native": "English", "dir": "ltr", "flag": "🇬🇧"},
        {"code": "sv", "name": "Swedish", "native": "Svenska", "dir": "ltr", "flag": "🇸🇪"},
        {"code": "fr", "name": "French", "native": "Français", "dir": "ltr", "flag": "🇫🇷"},
        {"code": "de", "name": "German", "native": "Deutsch", "dir": "ltr", "flag": "🇩🇪"},
        {"code": "es", "name": "Spanish", "native": "Español", "dir": "ltr", "flag": "🇪🇸"},
        {"code": "ar", "name": "Arabic", "native": "العربية", "dir": "rtl", "flag": "🇸🇦"},
        {"code": "pt-br", "name": "Portuguese (Brazil)", "native": "Português (Brasil)", "dir": "ltr", "flag": "🇧🇷"},
    ]
    try:
        from apps.content.models.languages import SiteLanguage
        rows = [language.as_dict() for language in SiteLanguage.active()]
        return rows or fallback
    except Exception:
        logger.exception("Precis language catalog unavailable")
        return fallback


def content_languages_api(request: HttpRequest) -> JsonResponse:
    """GET /apis/content/languages/ — seeded language choices for the frontend."""
    languages = _language_catalog()
    return JsonResponse({
        "languages": languages,
        "coverage": {language["code"]: 0 for language in languages},
        "ui_languages": [language["code"] for language in languages],
    })


# Frontend route table — the Astro app is the renderer, so navigation only
# ever links to routes it actually builds. Wagtail page slugs are mapped onto
# the closest frontend route. The map also drops locale-prefixed `child.url`
# values the static app cannot serve.
_FRONTEND_ROUTES = {
    "home": "/",
    "all-courses": "/courses/",
    "about": "/about/",
    "contact": "/contact/",
    "services": "/services/",
    "team": "/team/",
    "events": "/events/",
}


def navigation_api(request: HttpRequest) -> JsonResponse:
    language = _requested_language(request)
    items = [{"label": "Home", "href": "/", "active": request.path == "/"}]
    try:
        from wagtail.models import Locale

        # The seeded tree is ``root -> home -> {about, contact, team,
        # all-courses, events, services}``. Iterate the *home* page's
        # children — not ``root.get_children()``, which only yields the
        # single ``home`` page and therefore never surfaced the real nav
        # links.
        home = _live_page("home", language)
        if home is None:
            home = Page.objects.live().filter(slug="home").first()
        children = home.get_children().live() if home else Page.objects.none()
        locale = Locale.objects.filter(language_code=language).first()
        if locale is not None:
            children = children.filter(locale=locale)
        for child in children.order_by("title"):
            route = _FRONTEND_ROUTES.get(child.slug)
            if route is None:
                continue
            specific = child.specific
            if not (getattr(specific, "show_in_nav", True) or getattr(specific, "show_in_menus", True)):
                continue
            items.append({
                "label": child.title,
                "href": route,
                "active": request.path == route.rstrip("/") or request.path.startswith(route),
            })
    except Exception:
        # The API remains useful before the optional Wagtail seed command runs.
        items.extend([
            {"label": "Courses", "href": "/courses/", "active": False},
            {"label": "About", "href": "/about/", "active": False},
            {"label": "Contact", "href": "/contact/", "active": False},
        ])
    return JsonResponse({
        "nav_items": items,
        "language": language,
        "available_languages": [item["code"] for item in _language_catalog()],
    })


def page_data_api(request: HttpRequest, slug: str) -> JsonResponse:
    language = _requested_language(request)
    page = _live_page(slug, language)
    if page is None:
        return JsonResponse({"error": "Page not found"}, status=404)
    data = _page_data(page)
    data["language"] = language
    data["available_languages"] = [item["code"] for item in _language_catalog()]
    return JsonResponse(data)


def page_list_api(request: HttpRequest) -> JsonResponse:
    pages = []
    for page in Page.objects.live().filter(depth__gt=1).order_by("title"):
        pages.append({"id": page.pk, "slug": page.slug, "title": page.title, "type": page.specific_class.__name__})
    return JsonResponse({"pages": pages, "total": len(pages)})


def contact_api(request: HttpRequest) -> JsonResponse:
    """GET /apis/contact/ — seeded ContactPage form fields + contact methods.

    Reads the localized ContactPage so the Astro contact form renders the
    editor-managed fields (translated per locale) instead of hardcoded
    fallbacks. Falls back to a minimal email method only when the page tree
    has not been seeded yet.
    """
    language = _requested_language(request)
    page = _live_page("contact", language)

    title = "Get in touch"
    description = "Questions about courses, content, or the platform? Send a message."
    form_title = "Send us a message"
    form_description = "We will get back to you within one business day."
    fields: list[dict] = []
    methods: list[dict] = []

    if page is not None:
        specific = page.specific
        title = page.title or title

        # Seeded form fields (contact_form → contact_form → fields).
        for block in getattr(specific, "contact_form", []) or []:
            if block.block_type == "contact_form":
                fields = _plain(block.value.get("fields") or [])
                break

        if getattr(specific, "form_title", ""):
            form_title = strip_tags(_plain(getattr(specific, "form_title")))
        if getattr(specific, "form_intro", ""):
            form_description = strip_tags(_plain(getattr(specific, "form_intro")))

        # Contact info description (contact_info → contact_info → description).
        for block in getattr(specific, "contact_info", []) or []:
            if block.block_type == "contact_info":
                description = block.value.get("description") or description
                break

        # Contact details → methods (address / phone / email).
        for block in getattr(specific, "contact_details", []) or []:
            value = block.value
            lines = value.get("lines") or []
            label = value.get("title") or block.block_type.title()
            if block.block_type == "email":
                for line in lines:
                    methods.append({"type": "email", "label": label, "value": str(line), "href": f"mailto:{line}"})
            elif block.block_type == "phone":
                for line in lines:
                    methods.append({"type": "phone", "label": label, "value": str(line), "href": f"tel:{line}"})
            else:
                methods.append({"type": block.block_type, "label": label, "value": " / ".join(map(str, lines)), "href": ""})

    if not methods:
        methods = [{
            "type": "email",
            "label": "Email",
            "value": "support@ctc-research.com",
            "href": "mailto:support@ctc-research.com",
        }]

    return JsonResponse({
        "title": title,
        "description": description,
        "methods": methods,
        "form_title": form_title,
        "form_description": form_description,
        "fields": fields,
    })


def assets_api(request: HttpRequest) -> JsonResponse:
    """GET /apis/assets/ — unified asset manifest for frontend bundler integration.

    Single source of truth for both render roads: configured FUSION_ASSETS
    (CSS/fonts/preconnect) are merged with generated webpack bundle links
    (from bundles.json) by django-fusion's ``load_merged_asset_manifest()``.
    ``fusion_render_first`` reports the effective render mode so the
    frontend can switch between server-rendered components and /apis/* data.
    """
    from django.conf import settings
    from django_fusion.config.manifest import load_merged_asset_manifest

    merged = load_merged_asset_manifest()
    top = merged.get("top") or {}
    bottom = merged.get("bottom") or {}
    webpack = merged.get("webpack") or {}

    return JsonResponse({
        "version": str(merged.get("version", 1)),
        "static_url": settings.STATIC_URL,
        "fusion_render_first": get_effective_render_first(request),
        "enabled": True,
        "webpack_enabled": bool(webpack.get("enabled", False)),
        "webpack_bundle_dir": str(webpack.get("bundle_dir", "") or ""),
        "top": {
            "preconnect": top.get("preconnect") or ["https://fonts.googleapis.com"],
            "fonts": top.get("fonts") or [],
            "css": top.get("css") or [],
            "inline_css": top.get("inline_css") or [],
        },
        "bottom": {
            "js": bottom.get("js") or [],
            "inline_js": bottom.get("inline_js") or [],
        },
        "fonts": top.get("fonts") or [],
        "preconnect": top.get("preconnect") or ["https://fonts.googleapis.com"],
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
    # The seeded ContactPage form uses name/email/message only; subject is
    # optional so the editor-managed field set remains the source of truth.
    subject = str(payload.get("subject", "")).strip() or "Contact form submission"
    message = str(payload.get("message", "")).strip()
    if (
        not name
        or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email)
        or len(message) < 10
    ):
        return HttpResponse(
            '<p class="text-red-500 font-medium">Please provide a name, valid email, and message.</p>',
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


@ensure_csrf_cookie
def auth_status_api(request: HttpRequest) -> JsonResponse:
    """GET /apis/auth/status/ — auth state plus learner entitlements.

    Mirrors precis-landing's endpoint so the shared Astro header can render
    the same session-aware dropdown (user avatar, profile, learning summary)
    on both sites. The account stays owned by allauth; learning contributes
    a compact summary of the user's active/completed enrollments.
    """
    user = request.user if request.user.is_authenticated else None
    learning = {"active": 0, "completed": 0, "next": None}
    if user:
        try:
            from apps.learning.models.enrollment import Enrollment

            rows = Enrollment.objects.filter(student=user)
            # Status field is the lifecycle contract (active/completed/dropped)
            # — consistent with precis-landing's auth-status semantics.
            active = rows.filter(status="active")
            next_enrollment = (
                active.select_related("course").order_by("-last_accessed_at", "-created_at").first()
            )
            learning = {
                "active": active.count(),
                "completed": rows.filter(status="completed").count(),
                "next": (
                    {
                        "title": next_enrollment.course.title,
                        # Precis detail route: /learning/course/<slug>/
                        "href": f"/learning/course/{next_enrollment.course.slug}/",
                        "progress": next_enrollment.progress,
                    }
                    if next_enrollment
                    else None
                ),
            }
        except Exception:
            logger.exception("auth_status learning summary failed")
    return JsonResponse(
        {
            "authenticated": user is not None,
            "user": (
                {
                    "email": user.email,
                    "display": user.email.split("@")[0] if user else None,
                }
                if user
                else None
            ),
            "learning": learning,
        }
    )


def htmx_ping_api(request: HttpRequest) -> HttpResponse:
    return HttpResponse(
        f'<div class="text-center"><p class="font-mono text-2xl font-bold text-fu-link">{datetime.now():%Y-%m-%d %H:%M:%S}</p>'
        '<p class="mt-1 font-mono text-[0.65rem] uppercase tracking-[0.16em] text-fu-muted">server time · text/html fragment</p></div>'
    )


def render_mode_api(request: HttpRequest) -> JsonResponse:
    """GET /apis/render-mode/ — report the active fusion render mode.

    Mirrors precis-landing's render-mode contract so operators (and the
    frontend) can verify and switch between the two content-delivery roads:

    .. code-block:: json

        {
          "fusion_render_first": true,
          "mode": "fusion-render",
          "content": {"html": "/", "data": "/apis/pages/home/"}
        }

    The ``X-Fusion-Render-First: true|false`` request header overrides the
    configured default for a single request.
    """
    render_first = get_effective_render_first(request)
    return JsonResponse({
        "fusion_render_first": render_first,
        "mode": "fusion-render" if render_first else "data-api",
        "content": {"html": "/", "data": "/apis/pages/home/"},
    })
