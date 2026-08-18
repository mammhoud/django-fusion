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
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from wagtail.models import Page

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


def _button_to_dict(btn) -> dict | None:
    """Serialize a ButtonBlock StructValue (label/href/page/style) to a dict.

    A chosen page resolves to its live URL; the label falls back to the page
    title (the button's visible header) when the editor left it empty.
    """
    if not btn:
        return None
    label = btn.get("label") or ""
    href = btn.get("href") or ""
    style = btn.get("style") or "primary"
    page = btn.get("page")
    page_dict = None
    if page is not None:
        try:
            page_dict = {"id": page.pk, "title": page.title, "url": page.url}
        except Exception:
            page_dict = None
        if page_dict and page_dict.get("url"):
            href = href or page_dict["url"]
            label = label or page_dict["title"]
    return {"label": label, "href": href, "style": style, "page": page_dict}


def _page_data(page) -> dict:
    """Return a frontend-shaped page payload from any live LMS page.

    Covers both the native LMS page fields and the ported landing-slice page
    models (hero/cta StreamFields, delivery phases/prompts, product editions,
    brand palettes) so the shared Astro frontend renders the same document.
    """
    specific = page.specific
    class_name = specific.__class__.__name__
    data = {
        "id": page.pk,
        "slug": page.slug or "home",
        "title": page.title,
        "type": class_name,
        "show_in_nav": bool(getattr(specific, "show_in_nav", True)),
        "seo_title": getattr(page, "seo_title", "") or page.title,
        "search_description": getattr(page, "search_description", "") or "",
    }

    # Ported landing-slice listing fields (ProductPage card, brand/display modes).
    if hasattr(specific, "logo_style"):
        data["logo_style"] = specific.logo_style
        data["status"] = specific.status
        data["hidden"] = bool(specific.hidden)
    if getattr(specific, "version", ""):
        data["version"] = specific.version
    if getattr(specific, "tagline", ""):
        data["tagline"] = specific.tagline
    if hasattr(specific, "get_category_display"):
        data["category"] = specific.get_category_display().lower()
    if getattr(specific, "display_mode", None):
        data["display_mode"] = specific.display_mode

    # Hero — the ported LandingPage hero StreamField wins; native LMS pages
    # fall back to hero_heading/hero_subheading/intro_text.
    data["hero"] = {
        "badge": "fusion lms · server-rendered content",
        "title": getattr(specific, "hero_heading", "") or page.title,
        "subtitle": getattr(specific, "hero_subheading", "") or getattr(specific, "intro_text", "") or "",
        "primary_cta": {"label": "Explore courses", "href": "/courses/", "style": "primary"},
        "secondary_cta": {"label": "Learn about Fusion", "href": "/about/", "style": "secondary"},
    }
    hero = getattr(specific, "hero", None)
    if hero:
        for block in hero:
            if block.block_type == "hero":
                value = block.value
                data["hero"] = {
                    "badge": value.get("badge", ""),
                    "title": value.get("title", page.title),
                    "accent": value.get("accent", ""),
                    "subtitle": value.get("subtitle", ""),
                    "primary_cta": _button_to_dict(value.get("primary_cta")),
                    "secondary_cta": _button_to_dict(value.get("secondary_cta")),
                    "trusted_by": value.get("trusted_by", ""),
                }
                break

    body = getattr(specific, "body", None) or getattr(specific, "intro_text", None)
    if body:
        data["body"] = str(body)

    # CTA — the ported LandingPage cta StreamField wins over the LMS default.
    cta = getattr(specific, "cta", None)
    if cta:
        for block in cta:
            if block.block_type == "cta":
                value = block.value
                data["cta"] = {
                    "title": value.get("title", ""),
                    "subtitle": value.get("subtitle", ""),
                    "primary_cta": _button_to_dict(value.get("primary_cta")),
                    "secondary_cta": _button_to_dict(value.get("secondary_cta")),
                }
                break

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

    # Delivery phases / prompts — the ported services methodology.
    if class_name == "PhasePage":
        data["phase_number"] = specific.phase_number
        data["phase_label"] = specific.get_phase_label_display()
        data["outcomes"] = [line.strip() for line in specific.outcomes.splitlines() if line.strip()]
        data["prompts"] = [
            {"slug": child.slug, "title": child.title, "href": "/about/services/"}
            for child in specific.get_children().live().specific()
        ]
    elif class_name == "PromptPage":
        data["prompt"] = specific.prompt
        data["context"] = str(specific.context) if specific.context else ""
        data["output"] = str(specific.output) if specific.output else ""
        data["tool"] = specific.tool
        parent = specific.get_parent().specific
        data["phase"] = {"title": parent.title, "slug": parent.slug, "href": "/about/services/"}

    # Product detail — editions become the public gallery + preview routes.
    if class_name == "ProductPage":
        data.pop("snippets", None)
        data["editions"] = specific.get_editions()
        data["preview_gallery"] = specific.get_preview_gallery()

    # Product listing — one card per live, non-hidden ProductPage child.
    if class_name == "ProductsPage":
        cards = specific.get_product_cards()
        if cards:
            data["products"] = cards

    # Brand page — editor-authored palette overrides per product slug.
    if class_name == "BrandPage":
        overrides = specific.get_palette_overrides()
        if overrides:
            data["palette_overrides"] = overrides

    # Services — nested delivery phases.
    if class_name == "ServicesPage":
        data["phases"] = [
            {
                "id": child.pk,
                "slug": child.slug,
                "title": child.title,
                "phase_number": child.phase_number,
                "phase_label": child.get_phase_label_display(),
                "href": "/about/services/",
            }
            for child in specific.get_children().live().specific()
            if child.__class__.__name__ == "PhasePage"
        ]

    data.setdefault("cta", {
        "title": "Start learning with Fusion LMS",
        "subtitle": "A focused learning platform built with Django, Wagtail, and Astro.",
        "primary_cta": {"label": "Browse courses", "href": "/courses/", "style": "primary"},
    })
    return data


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
        "site_name": getattr(settings_obj, "site_name", "Fusion LMS"),
        "site_tagline": getattr(settings_obj, "site_tagline", "Learning that ships."),
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
        "footer_description": getattr(settings_obj, "footer_description", "A modern learning platform powered by django-fusion."),
        "footer_address": getattr(settings_obj, "footer_address", ""),
        "footer_phone": getattr(settings_obj, "footer_phone", ""),
        "footer_email": getattr(settings_obj, "footer_email", ""),
        "footer_copyright": getattr(settings_obj, "footer_copyright", "© 2026 Fusion LMS"),
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
# the closest frontend route; pages without a frontend equivalent (team,
# events) are intentionally omitted instead of emitting 404 links. The map
# also drops locale-prefixed `child.url` values the static app cannot serve.
_FRONTEND_ROUTES = {
    "home": "/",
    "all-courses": "/courses/",
    "about": "/about/",
    "contact": "/contact/",
    "services": "/services/",
}


def navigation_api(request: HttpRequest) -> JsonResponse:
    language = _requested_language(request)
    items = [{"label": "Home", "href": "/", "active": request.path == "/"}]
    try:
        from wagtail.models import Locale

        root = Page.get_first_root_node()
        children = root.get_children().live()
        locale = Locale.objects.filter(language_code=language).first()
        if locale is not None:
            children = children.filter(locale=locale)
        for child in children.order_by("title"):
            route = _FRONTEND_ROUTES.get(child.slug)
            if route is None:
                continue
            specific = child.specific
            if not getattr(specific, "show_in_nav", True):
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


def brand_api(request: HttpRequest) -> JsonResponse:
    """GET /apis/brand/ — brand kit boards, one per live product.

    Single source for the /brand/ page and the product-tooltip brand modal:
    each board carries the product card (title, href, logo, tagline) plus the
    brandkit story (essence, metaphor, construction, voice, palette swatches
    pre-resolved to CSS).
    """
    try:
        from apps.content.models.landing import BrandPage
        from apps.pages.pages.brand_spec import get_brand_boards

        boards = get_brand_boards(brand_page=BrandPage.objects.first())
    except Exception:
        logger.exception("brand_api error")
        boards = []
    return JsonResponse({"boards": boards})


def pricing_api(request: HttpRequest) -> JsonResponse:
    """GET /apis/pricing/ — every live, non-hidden product with its editions.

    Drives the tabbed /pricing/ page: each product carries its slug, title,
    tagline, logo style, status and the edition list (name / price / period /
    tier / featured). Hidden products are excluded.
    """
    try:
        from apps.content.models.landing import PricingPage

        page = PricingPage.objects.first()
        products = page.get_product_pricing() if page else []
        return JsonResponse({"products": products})
    except Exception:
        logger.exception("pricing_api error")
        return JsonResponse({"products": []})


def products_api(request: HttpRequest) -> JsonResponse:
    """GET /apis/products/ — the Product snippet catalog with language filter.

    Editor-managed catalog-of-record (apps/content/models/products.py): each
    item carries title, slug, category, language, price and the unified
    currency from FUSION_DEFAULT_CURRENCY. Supports ``?language=``,
    ``?category=`` and ``?q=`` filters so the frontend can filter the grid by
    language without a second content source.
    """
    try:
        from apps.content.models.landing import ProductPage
        from apps.content.models.products import Product
    except Exception:
        logger.exception("products_api import failed")
        return JsonResponse({"products": []})

    qs = Product.objects.filter(is_published=True)
    # Hidden ProductPage documents stay catalog-only (direct link still
    # works), so their snippets never appear in the public catalog either.
    try:
        hidden_slugs = set(
            ProductPage.objects.filter(hidden=True).values_list("slug", flat=True)
        )
        if hidden_slugs:
            qs = qs.exclude(detail_slug__in=hidden_slugs).exclude(
                detail_slug="", slug__in=hidden_slugs
            )
    except Exception:
        logger.exception("products_api hidden-product filter failed")
    language = (request.GET.get("language") or "").lower()
    if language:
        qs = qs.filter(language=language)
    category = (request.GET.get("category") or "").lower()
    if category:
        qs = qs.filter(category=category)
    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(title__icontains=q)
    return JsonResponse({
        "products": [product.as_dict() for product in qs.order_by("-is_featured", "title")],
        "language": language or None,
        "languages": [item["code"] for item in _language_catalog()],
    })


def get_home_courses():
    """Return the bounded, annotated published-course queryset shared by both roads."""
    from django.db.models import Count, Q

    from apps.learning.models import Course

    return (
        Course.objects.filter(is_published=True)
        .select_related("instructor")
        .annotate(
            module_count=Count("modules", distinct=True),
            lesson_count=Count(
                "modules__lessons",
                filter=Q(modules__lessons__is_active=True),
                distinct=True,
            ),
        )
        .order_by("-is_featured", "title")[:6]
    )


def courses_api(request: HttpRequest) -> JsonResponse:
    """GET /apis/courses/ — the public, published learning catalog.

    Adapted from precis-landing for the lms ``Course`` model: difficulty comes
    from ``difficulty_level``, duration from the ``duration`` (hours) field, and
    the module/lesson counts are annotated directly (lms Course has no
    ``module_count``/``lesson_count`` fields).
    """
    from django.conf import settings as django_settings

    courses = list(get_home_courses())
    language = (request.GET.get("language") or "").lower()
    if language:
        courses = [course for course in courses if (course.language or "") == language]
    currency = str(getattr(django_settings, "FUSION_DEFAULT_CURRENCY", "USD") or "USD")
    return JsonResponse({
        "courses": [
            {
                "slug": course.slug,
                "title": course.title,
                "short_description": course.short_description,
                "difficulty": str(course.get_difficulty_level_display()),
                "language": course.language,
                "currency": currency,
                "duration_hours": str(course.duration),
                "price": str(course.price),
                "is_free": course.is_free,
                "is_featured": course.is_featured,
                "has_certificate": course.has_certificate,
                "module_count": course.module_count,
                "lesson_count": course.lesson_count,
                "instructor": course.instructor.get_full_name() or course.instructor.get_username(),
                "href": str(course.url),
            }
            for course in courses
        ],
        "language": language or None,
        "languages": [item["code"] for item in _language_catalog()],
    })


def contact_api(request: HttpRequest) -> JsonResponse:
    return JsonResponse({
        "title": "Get in touch",
        "description": "Questions about courses, content, or the Fusion platform? Send a message.",
        "methods": [{
            "type": "email",
            "label": "Email",
            "value": "support@precis-lms.com",
            "href": "mailto:support@precis-lms.com",
        }],
        "form_title": "Send us a message",
        "form_description": "We will get back to you within one business day.",
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
