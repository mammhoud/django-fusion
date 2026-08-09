"""
Landing-fusion API endpoints — all data served from Wagtail/django-fusion.

Endpoints:
    GET /apis/site/settings/   — branding, social links, footer
    GET /apis/navigation/      — nav links from published pages
    GET /apis/contact/         — contact methods
    GET /apis/pages/<slug>/    — page data (JSON)
    GET /apis/pages/<slug>/data/ — page data with fusion encoding

Mirrors lms-fusion's /apis/ pattern but trimmed to landing needs.
"""

import copy
import logging

from django.http import JsonResponse
from django.shortcuts import render
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from wagtail.models import Page

logger = logging.getLogger(__name__)


# ── Fusion Render Mode (django-fusion settings config) ─────────────────────

def get_effective_render_first(request=None) -> bool:
    """Return the effective ``fusion_render_first`` preference.

    Mirrors django-fusion's ``FusionDualModeMixin.get_effective_render_first()``
    for the landing project: the ``X-Fusion-Render-First: true|false`` header
    overrides per request; otherwise the ``FUSION_RENDER_FIRST_DEFAULT``
    setting (read fresh from Django settings, which is what django-fusion's
    ``DjangoComponentsSettings`` resolves at init) decides the mode.

    ``True``  → “fusion render first” — Django renders finished HTML.
    ``False`` → “data APIs” — the client renders from /apis/* JSON.
    """
    if request is not None:
        header = request.headers.get("X-Fusion-Render-First")
        if header in ("true", "false"):
            return header == "true"
    from django.conf import settings as django_settings

    return bool(getattr(django_settings, "FUSION_RENDER_FIRST_DEFAULT", False))


def brand_api(request):
    """GET /apis/brand/ — the brand kit boards, one per live product.

    Single source for the /brand/ page AND the product-tooltip brand modal:
    each board carries the product card (title, href, logo, tagline) plus the
    brandkit story (essence, metaphor, construction, voice, palette swatches
    pre-resolved to CSS).
    """
    from apps.pages.brand_spec import get_brand_boards
    from apps.pages.models import BrandPage

    try:
        boards = get_brand_boards(brand_page=BrandPage.objects.first())
    except Exception:
        logger.exception("brand_api error")
        boards = []
    return JsonResponse({"boards": boards})


def render_mode_api(request):
    """GET /apis/render-mode/ — report the active fusion render mode.

    Lets operators (and the frontend) switch between and verify the two
    content delivery options:

    .. code-block:: json

        {
          "fusion_render_first": true,
          "mode": "fusion-render",
          "content": {"html": "/about/", "data": "/apis/pages/about/"}
        }

    The ``X-Fusion-Render-First: true|false`` request header overrides the
    configured default for a single request.
    """
    render_first = get_effective_render_first(request)
    return JsonResponse(
        {
            "fusion_render_first": render_first,
            "mode": "fusion-render" if render_first else "data-api",
            "content": {
                "html": "/about/",
                "data": "/apis/pages/about/",
            },
        }
    )


# ── Site Settings ───────────────────────────────────────────────────────────

def site_settings_api(request):
    """GET /apis/site/settings/ — branding, social links, footer content.

    Returns all Wagtail-managed site identity data consumed by the
    Astro frontend (Header, Footer, Layout components).
    """
    from apps.content.models.settings import SiteSettings

    try:
        settings = SiteSettings.for_request(request)
    except Exception:
        settings = None

    # Social links
    social_links = []
    try:
        from apps.content.models.settings import SocialLink
        social_links = [
            {
                "platform": s.platform,
                "label": s.label or s.get_platform_display(),
                "url": s.url,
                "icon_class": s.icon_class or f"fab fa-{s.platform}",
            }
            for s in SocialLink.objects.filter(is_active=True).order_by("sort_order")
        ]
    except Exception:
        pass

    # Footer link groups
    footer_groups = []
    if settings:
        try:
            for group in settings.footer_link_groups.all().order_by("sort_order"):
                footer_groups.append({
                    "title": group.title,
                    "links": [
                        {"label": link.label, "url": link.url}
                        for link in group.links.all().order_by("sort_order")
                    ],
                })
        except Exception:
            pass

    # Logo URL
    logo_url = None
    if settings and settings.logo:
        try:
            logo_url = settings.logo.get_rendition("height-60").url
        except Exception:
            pass

    data = {
        # ── Brand ──
        "site_name": settings.site_name if settings else "Structa Cloud",
        "site_tagline": settings.site_tagline if settings else "",
        "logo_url": logo_url,
        "favicon_url": _get_rendition_url(settings, "favicon", "width-32") if settings else None,
        "primary_color": getattr(settings, "primary_color", "#0B57D0") if settings else "#0B57D0",
        "accent_color": getattr(settings, "accent_color", "#FFE14D") if settings else "#FFE14D",
        # ── SEO ──
        "meta_description": getattr(settings, "meta_description", "") if settings else "",
        "meta_keywords": getattr(settings, "meta_keywords", "") if settings else "",
        "meta_author": getattr(settings, "meta_author", "Mahmoud Ezzat Moustafa") if settings else "Mahmoud Ezzat Moustafa",
        "og_image_url": _get_rendition_url(settings, "og_image", "width-1200") if settings else None,
        "twitter_handle": getattr(settings, "twitter_handle", "") if settings else "",
        # ── Analytics ──
        "analytics_provider": getattr(settings, "analytics_provider", "") if settings else "",
        "google_tag_manager_id": getattr(settings, "google_tag_manager_id", "") if settings else "",
        "google_analytics_id": getattr(settings, "google_analytics_id", "") if settings else "",
        # ── Navigation ──
        "nav_show_home": getattr(settings, "nav_show_home", True) if settings else True,
        "nav_show_contact": getattr(settings, "nav_show_contact", True) if settings else True,
        "nav_cta_label": getattr(settings, "nav_cta_label", "Get Started") if settings else "Get Started",
        # The header CTA points at a real page (contact) — a bare /#cta anchor
        # would dead-end on pages without a CTA section (APPEND_SLASH=False).
        "nav_cta_url": getattr(settings, "nav_cta_url", "/contact/") if settings else "/contact/",
        # ── Footer ──
        "footer_description": settings.footer_description if settings else "",
        "footer_address": settings.footer_address if settings else "",
        "footer_phone": settings.footer_phone if settings else "",
        "footer_email": settings.footer_email if settings else "",
        "footer_copyright": settings.footer_copyright if settings else f"\u00a9 2026 structa.cloud",
        "newsletter_prompt": getattr(settings, "newsletter_prompt", "") if settings else "",
        # ── App store ──
        "google_play_url": getattr(settings, "google_play_url", "") if settings else "",
        "apple_store_url": getattr(settings, "apple_store_url", "") if settings else "",
        # ── Legal ──
        "privacy_policy_url": settings.privacy_policy_url if settings else "/privacy",
        "terms_of_use_url": settings.terms_of_use_url if settings else "",
        # ── Chat ──
        "chat_enabled": getattr(settings, "chat_enabled", False) if settings else False,
        "chat_provider": getattr(settings, "chat_provider", "") if settings else "",
        "chat_widget_id": getattr(settings, "chat_widget_id", "") if settings else "",
        # ── Social & footer groups ──
        "social_links": social_links,
        "footer_link_groups": footer_groups,
    }
    return JsonResponse(data)


# ── Navigation ──────────────────────────────────────────────────────────────

def navigation_api(request):
    """GET /apis/navigation/ — nav links from the django-fusion Site.

    Uses ``LandingSite.get_navigation_context()`` as the single source of truth
    for navigation structure. Falls back to walking the Wagtail page tree if
    the Site class is unavailable.
    """
    try:
        from apps.core.site import landing_site
        nav_items = landing_site.get_navigation_context(request)
        # Filter to show_in_nav=True only
        nav_items = [item for item in nav_items if item.get("show_in_nav", True)]
        # Remove the show_in_nav key from the response (children carry their own)
        for item in nav_items:
            item.pop("show_in_nav", None)
            item["children"] = item.get("children") or []
    except Exception:
        nav_items = _navigation_from_wagtail_tree(request)

    language = _requested_content_language(request)
    if language != "en":
        try:
            from apps.content.models.translations import PageTranslation
            from apps.pages.models import HomePage

            landing_root = HomePage.objects.first()
            landing_pages = (
                landing_root.get_descendants(inclusive=True).live()
                if landing_root is not None
                else Page.objects.none()
            )
            for item in nav_items:
                slug = str(item.get("href", "")).strip("/").split("/")[-1] or "home"
                page = landing_pages.filter(slug=slug).first()
                translation = PageTranslation.for_page(page, language) if page else None
                if translation and translation.title:
                    item["label"] = translation.title
                # Translate dropdown children whose pages carry a localized title.
                for child in item.get("children", []):
                    child_slug = str(child.get("href", "")).strip("/").split("/")[-1]
                    child_page = landing_pages.filter(slug=child_slug).first()
                    child_translation = PageTranslation.for_page(child_page, language) if child_page else None
                    if child_translation and child_translation.title:
                        child["label"] = child_translation.title
        except Exception:
            logger.exception("navigation translation lookup failed")
    return JsonResponse({
        "nav_items": nav_items,
        "language": language,
        "available_languages": _supported_language_codes(),
    })


def content_languages_api(request):
    """GET /apis/content/languages/ — editorial languages and coverage.

    The language catalog is a seeded, admin-editable ``SiteLanguage`` snippet
    (mirroring the Astro ``LANG_META`` table). If the snippet is empty or
    unavailable (fresh DB before seeding), a static en/ar fallback is served so
    the switcher never loses the editorial languages.
    """
    from apps.content.models.languages import SiteLanguage
    from apps.content.models.translations import PageTranslation

    try:
        languages = [lang.as_dict() for lang in SiteLanguage.active().order_by("sort_order", "code")]
    except Exception:
        logger.exception("content_languages_api SiteLanguage query failed")
        languages = []

    if not languages:
        # Fallback — mirrors the seeded DEFAULT_SITE_LANGUAGES so a fresh DB
        # (before the seed command runs) still reports the full offered catalog
        # (Django LANGUAGES + the Astro LANG_META table all list these seven).
        languages = [
            {"code": "en", "name": "English", "native": "English", "dir": "ltr", "flag": "🇬🇧"},
            {"code": "ar", "name": "Arabic", "native": "العربية", "dir": "rtl", "flag": "🇸🇦"},
            {"code": "sv", "name": "Swedish", "native": "Svenska", "dir": "ltr", "flag": "🇸🇪"},
            {"code": "fr", "name": "French", "native": "Français", "dir": "ltr", "flag": "🇫🇷"},
            {"code": "de", "name": "German", "native": "Deutsch", "dir": "ltr", "flag": "🇩🇪"},
            {"code": "es", "name": "Spanish", "native": "Español", "dir": "ltr", "flag": "🇪🇸"},
            {"code": "pt", "name": "Portuguese", "native": "Português", "dir": "ltr", "flag": "🇧🇷"},
        ]

    # Coverage is reported for every advertised language. Only seeded Arabic
    # and explicit English overlays have editorial records today; other
    # languages intentionally fall back to canonical Wagtail content until an
    # editor adds translations.
    pages = Page.objects.live().filter(depth__gt=1)
    coverage = {
        language["code"]: PageTranslation.objects.filter(
            page__in=pages,
            language=language["code"],
        ).count()
        for language in languages
    }
    return JsonResponse({
        "languages": languages,
        "coverage": coverage,
        "ui_languages": [lang["code"] for lang in languages],
    })


def _navigation_from_wagtail_tree(request):
    """Fallback: walk the Wagtail page tree for navigation items."""
    nav_items = []
    try:
        from apps.pages.models import HomePage
        home = HomePage.objects.first()
        if home:
            nav_items.append({"label": home.title, "href": "/", "active": request.path == "/", "children": []})
            for child in home.get_children().live().order_by("title"):
                show = getattr(child.specific, "show_in_nav", True)
                if not show:
                    continue
                nav_items.append({
                    "label": child.title,
                    "href": f"/{child.slug}/",
                    "active": request.path.startswith(f"/{child.slug}/"),
                    "children": [],
                })
    except Exception:
        pass

    if not nav_items:
        nav_items = [
            {"label": "Home", "href": "/", "active": request.path == "/", "children": []},
            {"label": "Products", "href": "/products/", "active": False, "children": []},
            {"label": "Features", "href": "/features/", "active": False, "children": []},
            {"label": "About", "href": "/about/", "active": False, "children": []},
            {"label": "FAQ", "href": "/faq/", "active": False, "children": []},
            {"label": "Contact", "href": "/contact/", "active": False, "children": []},
        ]

    return nav_items


# ── Contact ─────────────────────────────────────────────────────────────────

def contact_api(request):
    """GET /apis/contact/ — contact methods + form topics from Wagtail ContactPage."""
    try:
        from apps.pages.models import ContactPage
        page = ContactPage.objects.first()
        if page and page.contact:
            for block in page.contact:
                if block.block_type == "contact":
                    methods = []
                    for method in block.value.get("methods", []):
                        # A chosen page wins over the manual link (mailto:/tel:/
                        # URLs still work when no page is picked).
                        page = method.get("page")
                        href = method.get("href", "")
                        if page is not None:
                            href = href or getattr(page, "url", "") or ""
                        methods.append({
                            "type": method.get("method_type", "email"),
                            "label": method.get("label", ""),
                            "value": method.get("value", ""),
                            "href": href,
                        })
                    return JsonResponse({
                        "title": block.value.get("title", "Get in touch"),
                        "description": block.value.get("description", ""),
                        "methods": methods,
                        "form_title": block.value.get("form_title", "Send us a message"),
                        "form_description": block.value.get("form_description", ""),
                        "topics": [str(t) for t in block.value.get("topics", [])],
                    })
    except Exception:
        pass

    # Fallback
    return JsonResponse({
        "title": "Get in touch",
        "description": "Have a question or want to work with us? Send a message.",
        "methods": [
            {"type": "email", "label": "Email", "value": "structa.cloud@gmail.com", "href": "mailto:structa.cloud@gmail.com"},
            {"type": "address", "label": "GitHub", "value": "github.com/mammhoud", "href": "https://github.com/mammhoud"},
            {"type": "hours", "label": "Portfolio", "value": "mammhoud.github.io", "href": "https://mammhoud.github.io"},
            {"type": "address", "label": "LinkedIn", "value": "linkedin.com/in/mammhoud", "href": "https://linkedin.com/in/mammhoud"},
        ],
        "form_title": "Send us a message",
        "form_description": "Fill out the form and our team will get back to you.",
        "topics": [],
    })


# ── Page Data ────────────────────────────────────────────────────────────────

import wagtail.blocks


def _stream_to_plain(value, keep_pages=False):
    """Recursively convert Wagtail StreamField values to plain JSON-serializable
    Python dicts/lists. Handles StructValue/ListValue from wagtail.blocks and
    resolves PageChooserBlock values to ``{id, title, url}`` dicts.

    With ``keep_pages=True`` PageChooserBlock values reduce to their primary
    key so a merged overlay can be re-hydrated through ``Block.to_python``
    (which resolves pks back to Page instances) instead of the JSON dict
    shape."""
    if isinstance(value, Page):
        # PageChooserBlock value — expose id/title/url so JSON keeps working.
        if keep_pages:
            return value.pk
        try:
            return {"id": value.pk, "title": value.title, "url": value.url}
        except Exception:
            return {"id": value.pk, "title": value.title, "url": ""}
    if hasattr(value, 'items') and hasattr(value, 'get'):
        # StructValue or dict-like
        return {k: _stream_to_plain(v, keep_pages) for k, v in value.items()}
    if hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
        # ListValue or list-like
        return [_stream_to_plain(v, keep_pages) for v in value]
    return value


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


def _normalize_page_links(value):
    """Recursively promote serialized PageChooserBlock values to href keys.

    ``_stream_to_plain`` turns a chosen page into ``{id, title, url}``.
    Editors may pick a page instead of typing a URL, so ``page`` → ``href``
    and ``<name>_page`` → ``<name>_href``; the page title fills an empty
    label. Applies to nested dicts/lists so section item lists (pricing
    tiers, editions, services, blog posts) are covered too.
    """
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                _normalize_page_links(item)
        return value
    if not isinstance(value, dict):
        return value
    for key, item in list(value.items()):
        if isinstance(item, list):
            for sub in item:
                if isinstance(sub, dict):
                    _normalize_page_links(sub)
            continue
        if isinstance(item, dict) and item.get("url"):
            if key == "page":
                value["href"] = value.get("href") or item["url"]
                value["label"] = value.get("label") or item.get("title")
            elif key.endswith("_page"):
                base = key[: -len("_page")]
                value[f"{base}_href"] = value.get(f"{base}_href") or item["url"]
                value[f"{base}_label"] = value.get(f"{base}_label") or item.get("title")
            elif key.endswith("_post"):
                # SnippetBlock.related_post → related_post_href/title so the
                # Astro road can render a deep-dive link card from the API.
                value[f"{key}_href"] = value.get(f"{key}_href") or item["url"]
                value[f"{key}_title"] = value.get(f"{key}_title") or item.get("title")
    return value


def _get_wagtail_page(slug: str, page_type: str | None = None):
    """Retrieve a live Wagtail page by slug, optionally narrowed by model type."""
    normalized = slug.strip("/") or "home"
    try:
        queryset = Page.objects.live().filter(slug=normalized)
        if page_type:
            queryset = queryset.filter(content_type__model=page_type.lower())
        return queryset.first()
    except Exception:
        return None


# Section blocks whose nested *item list* is exposed directly on the page
# payload. The Astro frontend maps items ("Open-source repos", a feature card,
# a testimonial, an FAQ entry), so stats/features/testimonials/faq (and
# services/process/blog) are flattened to their item lists. ``projects`` stays
# block-level because each block is already one project card; ``pricing`` stays
# block-level because each block carries a ``tiers`` list (the frontend
# flattens it when it needs a plan array).
SECTION_ITEM_LIST_KEYS = {
    "stats": "stats",
    "features": "features",
    "testimonials": "testimonials",
    "faq": "items",
    "services": "services",
    "process": "steps",
    "blog": "posts",
    "tech": "items",
    "editions": "editions",
    "snippets": "snippets",
    "team": "members",
}


def _page_to_dict(page) -> dict:
    """Serialize a Wagtail page to a frontend-consumable dict.

    This is the canonical English/base representation. Locale overlays are
    applied by ``page_data_api`` after serialization so every caller retains a
    predictable fallback payload.
    """
    from apps.pages.models import AboutPage, ProductsPage, FeaturesPage
    from apps.content.blocks import SECTION_STACK_FIELDS

    data = {
        "id": page.pk,
        "slug": page.slug if hasattr(page, "slug") and page.slug else "home",
        "title": page.title,
        "type": page.__class__.__name__,
        "show_in_nav": bool(getattr(page, "show_in_nav", True)),
        "seo_title": getattr(page, "seo_title", "") or page.title,
        "search_description": getattr(page, "search_description", ""),
    }

    # ProductPage category — lets the detail hero label the catalog section.
    if hasattr(page, "get_category_display"):
        data["category"] = page.get_category_display().lower()

    # DisplayModeMixin — page / modal / both surfacing option. Any page type
    # carrying the mixin (BrandPage, ProductPage, TeamPage) exposes it, so
    # every render road sees the same field. The default ("both") is always
    # truthy, so the key is present whenever the page has the mixin.
    if hasattr(page, "display_mode") and page.display_mode:
        data["display_mode"] = page.display_mode

    # BrandPage palette overrides — editor-authored hex swatches per product
    # slug, so the Astro /brand/ road applies the same overrides as the
    # backend boards (get_brand_boards). Absent when no overrides are set.
    if page.__class__.__name__ == "BrandPage":
        overrides = page.get_palette_overrides()
        if overrides:
            data["palette_overrides"] = overrides

    # ProductPage catalog fields — logo, tagline, status, hidden flag.
    if hasattr(page, "logo_style"):
        data["logo_style"] = page.logo_style
        data["status"] = page.status
        data["hidden"] = bool(page.hidden)
    if hasattr(page, "version") and page.version:
        data["version"] = page.version
    if hasattr(page, "tagline") and page.tagline:
        data["tagline"] = page.tagline

    # Hero
    if hasattr(page, "hero") and page.hero:
        for block in page.hero:
            if block.block_type == "hero":
                hero_val = block.value
                data["hero"] = {
                    "badge": hero_val.get("badge", ""),
                    "title": hero_val.get("title", page.title),
                    "accent": hero_val.get("accent", ""),
                    "subtitle": hero_val.get("subtitle", ""),
                    "primary_cta": _button_to_dict(hero_val.get("primary_cta")),
                    "secondary_cta": _button_to_dict(hero_val.get("secondary_cta")),
                    "trusted_by": hero_val.get("trusted_by", ""),
                }
                break

    # CTA
    if hasattr(page, "cta") and page.cta:
        for block in page.cta:
            if block.block_type == "cta":
                cta_val = block.value
                data["cta"] = {
                    "title": cta_val.get("title", ""),
                    "subtitle": cta_val.get("subtitle", ""),
                    "primary_cta": _button_to_dict(cta_val.get("primary_cta")),
                    "secondary_cta": _button_to_dict(cta_val.get("secondary_cta")),
                }
                break

    # Body (RichText)
    if hasattr(page, "body") and page.body:
        data["body"] = str(page.body)

    # Delivery phase / prompt metadata and hierarchy.
    if page.__class__.__name__ == "PhasePage":
        data["phase_number"] = page.phase_number
        data["phase_label"] = page.get_phase_label_display()
        data["outcomes"] = [line.strip() for line in page.outcomes.splitlines() if line.strip()]
        data["prompts"] = [
            {
                "slug": child.slug,
                "title": child.title,
                "href": f"/services/phases/{page.slug}/prompts/{child.slug}/",
            }
            for child in page.get_children().live().specific()
        ]
    elif page.__class__.__name__ == "PromptPage":
        data["prompt"] = page.prompt
        data["context"] = str(page.context) if page.context else ""
        data["output"] = str(page.output) if page.output else ""
        data["tool"] = page.tool
        parent = page.get_parent().specific
        data["phase"] = {"title": parent.title, "slug": parent.slug, "href": f"/services/phases/{parent.slug}/"}

    # Blog post meta (BlogPostPage) — category, date, read time, excerpt.
    # The date is serialized as an ISO string so the frontend renders it
    # without a client-side date dependency.
    for field_name in ("category", "read_time", "excerpt"):
        value = getattr(page, field_name, "")
        if value:
            data[field_name] = str(value)
    if getattr(page, "post_date", None):
        data["post_date"] = page.post_date.isoformat()
    # BlogPostPage hero screenshot — the optional image under the post hero.
    if getattr(page, "hero_screenshot_url", ""):
        data["hero_screenshot_url"] = page.hero_screenshot_url

    # Section stack fields (stats, features, testimonials, pricing, faq, projects)
    for field_name in SECTION_STACK_FIELDS:
        if hasattr(page, field_name):
            field_val = getattr(page, field_name)
            if field_val:
                items = []
                for block in field_val:
                    block_data = _stream_to_plain(block.value)
                    if not isinstance(block_data, dict):
                        items.append(block_data)
                        continue
                    # Resolve PageChooserBlock values (page/cta_page) to hrefs
                    # before flattening so both frontends keep the plain href
                    # contract even when an editor picked an internal page.
                    _normalize_page_links(block_data)
                    # Flatten section blocks to their item list (see
                    # SECTION_ITEM_LIST_KEYS); keep projects/pricing block-level.
                    item_key = SECTION_ITEM_LIST_KEYS.get(block.block_type)
                    nested = block_data.get(item_key) if item_key else None
                    if isinstance(nested, list):
                        items.extend(nested)
                    else:
                        block_data["type"] = block.block_type
                        items.append(block_data)
                if items:
                    data[field_name] = items

    # Product detail pages use edition captures as their public visual
    # preview gallery. Keep the legacy editor field stored in Wagtail for
    # migrations/history, but remove it from the public product payload so
    # clients cannot accidentally render code blocks again.
    if page.__class__.__name__ == "ProductPage":
        data.pop("snippets", None)
        data["editions"] = page.get_editions()
        data["preview_gallery"] = page.get_preview_gallery()

    # Services delivery phases — nested Wagtail documents exposed to the
    # Astro services page without a second content source.
    if page.__class__.__name__ == "ServicesPage":
        data["phases"] = [
            {
                "id": child.pk,
                "slug": child.slug,
                "title": child.title,
                "phase_number": child.phase_number,
                "phase_label": child.get_phase_label_display(),
                "href": f"/services/phases/{child.slug}/",
            }
            for child in page.get_children().live().specific()
            if child.__class__.__name__ == "PhasePage"
        ]

    # Product listing (ProductsPage) — one card per live ProductPage child.
    # The home document also exposes the catalog so every Astro road can render
    # the same backend-owned product cards without a second content source.
    if hasattr(page, "get_product_cards"):
        product_cards = page.get_product_cards()
        if product_cards:
            data["products"] = product_cards
    elif page.__class__.__name__ == "HomePage":
        from apps.pages.models import ProductsPage

        products_page = ProductsPage.objects.first()
        if products_page:
            # Home preview grid is curated — subproducts (vResume) stay
            # catalog-only and never appear on the homepage cards.
            product_cards = products_page.get_product_cards(for_home=True)
            if product_cards:
                data["products"] = product_cards

    # Contact section
    if hasattr(page, "contact") and page.contact:
        contact_blocks = []
        for block in page.contact:
            block_data = _stream_to_plain(block.value)
            if isinstance(block_data, dict):
                _normalize_page_links(block_data)
                block_data["type"] = block.block_type
            contact_blocks.append(block_data)
        if contact_blocks:
            data["contact"] = contact_blocks

    return data


def page_fragment_api(request, slug="home"):
    """GET /fragment/pages/<slug>/ — render one backend content fragment.

    The public Astro shell lives behind the frontend proxy, so a fragment
    request must not fetch ``/<slug>/`` directly: that would return the Astro
    document again. This endpoint deliberately renders the shared Django
    content partial and is safe to swap into an Astro shell.
    """
    page = _get_wagtail_page(slug)
    if page is None:
        return JsonResponse({"error": "Page not found"}, status=404)
    specific = page.specific
    language = _requested_content_language(request)
    localized_content = _apply_page_translation(specific, _page_to_dict(specific), language)
    # Reuse the handler's bound-block/body/breadcrumb helpers so HTMX fragments
    # follow the exact same localization road as full-page requests.
    from apps.handlers.views import LandingPageView

    localization_view = LandingPageView()
    localization_view.request = request
    fragment_context = {
        "page": specific,
        "content": specific,
        "localized_content": localized_content,
        "localized_blocks": localization_view._get_localized_blocks(specific, language),
        "localized_body": localization_view._get_localized_body(specific, language),
        "breadcrumb_current": localization_view._get_localized_title(specific, language),
        "breadcrumbs": localization_view._get_breadcrumbs(specific),
        "content_language": language,
        "courses": get_home_courses() if specific.slug == "home" else [],
        "site_name": "Structa Cloud",
        "fusion_render_first": get_effective_render_first(request),
        "fusion_render_mode": "fusion-render",
    }
    if specific.__class__.__name__ == "PhasePage":
        from apps.pages.models import PromptPage

        outcomes = localized_content.get("outcomes")
        fragment_context["phase_outcomes"] = (
            outcomes
            if isinstance(outcomes, list)
            else [line.strip() for line in specific.outcomes.splitlines() if line.strip()]
        )
        fragment_context["phase_prompts"] = [
            {
                "title": _apply_page_translation(
                    prompt, _page_to_dict(prompt), language
                ).get("title", prompt.title),
                "slug": prompt.slug,
                "href": f"/services/phases/{specific.slug}/prompts/{prompt.slug}/",
            }
            for prompt in PromptPage.objects.live().child_of(specific).order_by("title")
        ]
    elif specific.__class__.__name__ == "PromptPage":
        from apps.pages.models import PromptPage

        phase = specific.get_parent().specific
        fragment_context["phase"] = phase
        fragment_context["localized_phase"] = _apply_page_translation(
            phase, _page_to_dict(phase), language
        )
    return render(request, "pages/fragments/page.html", fragment_context)


def _deep_merge(base: dict, overlay: dict) -> dict:
    """Merge nested translation overrides without mutating the base payload."""
    result = copy.deepcopy(base)
    for key, value in overlay.items():
        if isinstance(result.get(key), dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _supported_language_codes() -> list[str]:
    """Return the shared language catalog codes in stable switcher order."""
    try:
        from apps.content.models.languages import SUPPORTED_LANGUAGE_CODES

        return list(SUPPORTED_LANGUAGE_CODES)
    except Exception:
        return ["en", "ar", "sv", "fr", "de", "es", "pt"]


def _requested_content_language(request) -> str:
    """Return a supported request language, with English as the safe fallback.

    Editorial overlays cover every supported language; untranslated fields
    resolve to canonical English content rather than failing or silently
    advertising an unsupported code.
    """
    supported = set(_supported_language_codes())
    requested = (request.GET.get("lang") or "").lower().split("-")[0]
    if requested in supported:
        return requested
    cookie = (request.COOKIES.get("django_language") or "").lower().split("-")[0]
    if cookie in supported:
        return cookie
    header = (request.headers.get("Accept-Language") or "").lower()
    for language in header.replace(";", ",").split(","):
        code = language.strip().split("-")[0]
        if code in supported:
            return code
    return "en"


def _apply_page_translation(page, data: dict, language: str) -> dict:
    """Apply an optional PageTranslation overlay and expose locale metadata."""
    from apps.content.models.translations import PageTranslation

    requested_translation = PageTranslation.for_page(page, language)
    translation = requested_translation
    if translation is None and language != "en":
        # Arabic may be partial; English is the explicit final fallback.
        translation = PageTranslation.for_page(page, "en")
    if translation is not None:
        overrides = translation.as_overrides()
        if overrides.get("body"):
            overrides["body"] = strip_tags(overrides["body"])
        data = _deep_merge(data, overrides)
    # Product detail pages never expose legacy code snippets, including when
    # a translated override was authored before the visual gallery migration.
    if page.__class__.__name__ == "ProductPage":
        data.pop("snippets", None)
        # Preserve translated edition fields while filling the stable routing
        # and media contract from the canonical edition records.
        canonical_editions = {
            str(edition.get("name", "")).casefold(): edition
            for edition in page.get_editions()
        }
        localized_editions = data.get("editions", [])
        if isinstance(localized_editions, list):
            for edition in localized_editions:
                if not isinstance(edition, dict):
                    continue
                canonical = canonical_editions.get(str(edition.get("name", "")).casefold(), {})
                for key in ("preview_href", "preview_images", "tier", "featured"):
                    if key not in edition and key in canonical:
                        edition[key] = copy.deepcopy(canonical[key])
        data["preview_gallery"] = page.get_preview_gallery()
    data["language"] = language
    data["available_languages"] = _supported_language_codes()
    if requested_translation is not None:
        data["translation_source"] = "model"
    elif translation is not None:
        data["translation_source"] = "fallback"
    else:
        data["translation_source"] = "canonical"
    data["translation_language"] = translation.language if translation is not None else "en"
    return data


def page_data_api(request, slug):
    """GET /apis/pages/<slug>/ — full page data as JSON.

    ``?lang=en|ar`` selects the editorial overlay. Missing Arabic fields fall
    back to the canonical Wagtail content, so partial translations never blank
    a page. The same response contract is used by Astro and other clients.
    """
    page = _get_wagtail_page(slug)
    if page is None:
        return JsonResponse({"error": "Page not found"}, status=404)

    try:
        data = _apply_page_translation(
            page.specific,
            _page_to_dict(page.specific),
            _requested_content_language(request),
        )
        return JsonResponse(data)
    except Exception as exc:
        logger.exception("page_data_api error for slug=%s", slug)
        return JsonResponse({"error": str(exc)}, status=500)


def _get_rendition_url(settings_obj, field_name: str, filter_spec: str) -> str | None:
    """Safely get a Wagtail image rendition URL from a settings field."""
    if not settings_obj:
        return None
    image = getattr(settings_obj, field_name, None)
    if image:
        try:
            return image.get_rendition(filter_spec).url
        except Exception:
            pass
    return None


# ── Assets ──────────────────────────────────────────────────────────────────

def assets_api(request):
    """GET /apis/assets/ — unified asset manifest for frontend bundler integration.

    Returns the FUSION_ASSETS config that both the Django template tags
    (fusion_top_assets / fusion_bottom_assets) and the Astro frontend can
    consume to keep CSS/JS bundles in sync across server and client.
    """
    from django.conf import settings as django_settings
    from django_fusion.config.assets import get_asset_pipeline_options

    try:
        opts = get_asset_pipeline_options()
    except Exception:
        opts = None

    # Merge Django STATIC_URL info with any configured assets
    static_url = getattr(django_settings, "STATIC_URL", "/static/")
    fusion_assets = getattr(django_settings, "FUSION_ASSETS", {}) or {}

    # Build a version hash from the asset config for cache busting
    version = hex(hash(str(fusion_assets)) & 0xFFFFFFFF)[2:]

    data = {
        "version": version,
        "static_url": static_url,
        "fusion_render_first": get_effective_render_first(request),
        "enabled": opts.enabled if opts else True,
        "webpack_enabled": opts.webpack_enabled if opts else False,
        "webpack_bundle_dir": opts.webpack_bundle_dir if opts else "",
        "top": fusion_assets.get("top", {}),
        "bottom": fusion_assets.get("bottom", {}),
        "fonts": fusion_assets.get("fonts", []),
        "preconnect": fusion_assets.get("preconnect", []),
    }
    return JsonResponse(data)


def get_home_courses():
    """Return the bounded, annotated course queryset shared by both roads."""
    from django.db.models import Count, Q
    from apps.learning.models import Course

    return (
        Course.objects.filter(is_published=True)
        .select_related("instructor")
        .annotate(
            _module_count=Count("modules", distinct=True),
            _lesson_count=Count(
                "modules__lessons",
                filter=Q(modules__lessons__is_active=True),
                distinct=True,
            ),
        )
        .order_by("-is_featured", "title")[:6]
    )


@require_GET
def courses_api(request):
    """GET /apis/courses/ — the public, published learning catalog.

    The homepage uses this compact contract for its course cards while
    ``/learning/`` remains the full HTMX catalog. Counts are annotated here so
    rendering several cards never creates one count query per course.
    """
    courses = get_home_courses()
    return JsonResponse({
        "courses": [
            {
                "slug": course.slug,
                "title": course.title,
                "short_description": course.short_description,
                "difficulty": str(course.get_difficulty_display()),
                "language": course.language,
                "duration_hours": str(course.duration_hours),
                "price": str(course.price),
                "is_free": course.is_free,
                "is_featured": course.is_featured,
                "has_certificate": course.has_certificate,
                "module_count": course.module_count,
                "lesson_count": course.lesson_count,
                "instructor": course.instructor.get_full_name() or course.instructor.get_username(),
                "href": course.get_absolute_url(),
            }
            for course in courses
        ],
    })


def pricing_api(request):
    """GET /apis/pricing/ — every live, non-hidden product with its editions.

    Drives the tabbed /pricing/ page (Formints · Precis LMS · Loop · Syntara ·
    vResume): each product carries its slug, title, tagline, logo style,
    status and the edition list (name / price / period / tier / featured).
    Hidden products (ceptor-ai) are excluded.
    """
    try:
        from apps.pages.models import PricingPage

        page = PricingPage.objects.first()
        products = page.get_product_pricing() if page else []
        return JsonResponse({"products": products})
    except Exception:
        logger.exception("pricing_api error")
        return JsonResponse({"products": []})


def page_list_api(request):
    """GET /apis/pages/ — list of all published pages."""
    try:
        pages = []
        for p in Page.objects.live().filter(depth__gt=1).order_by("title"):
            specific_class = getattr(p, "specific_class", None)
            if specific_class is None:
                # Orphaned/stale content types (removed models, old seeds) —
                # skip rather than fail the whole list.
                continue
            pages.append({
                "id": p.pk,
                "slug": p.slug,
                "title": p.title,
                "type": specific_class.__name__,
            })
        return JsonResponse({"pages": pages, "total": len(pages)})
    except Exception:
        logger.exception("page_list_api error")
        return JsonResponse({"pages": [], "total": 0})


# ── Newsletter Subscribe ────────────────────────────────────────────────────

def auth_status_api(request):
    """GET /apis/auth/status/ — auth state plus learner entitlements.

    The account remains owned by allauth; learning only contributes a compact
    summary for the shared Astro header/profile dropdown.
    """
    user = request.user if request.user.is_authenticated else None
    learning = {"active": 0, "completed": 0, "next": None}
    if user:
        try:
            from apps.learning.models import Enrollment

            rows = Enrollment.objects.filter(user=user)
            active = rows.filter(status=Enrollment.Status.ACTIVE)
            next_enrollment = active.select_related("course").order_by("-last_accessed_at", "-enrolled_at").first()
            learning = {
                "active": active.count(),
                "completed": rows.filter(status=Enrollment.Status.COMPLETED).count(),
                "next": {
                    "title": next_enrollment.course.title,
                    "href": next_enrollment.course.get_absolute_url(),
                    "progress": next_enrollment.progress,
                } if next_enrollment else None,
            }
        except Exception:
            logger.exception("auth_status learning summary failed")
    return JsonResponse({
        "authenticated": user is not None,
        "user": {
            "email": user.email,
            "display": user.email.split("@")[0] if user else None,
        } if user else None,
        "learning": learning,
    })


def _comment_to_dict(comment) -> dict:
    """Flatten one approved PostComment for the JSON roads."""
    return {
        "id": comment.pk,
        "author": comment.display_name,
        "display": comment.display_name,
        "body": comment.body,
        "created_at": comment.created_at.isoformat() if comment.created_at else "",
    }


@csrf_exempt
def blog_comments_api(request, slug):
    """GET/POST /apis/blog/<slug>/comments/ — the post comment thread.

    GET — the approved comments (public, drives the Astro road and any
    embed). POST — creates a comment; requires an authenticated session.
    Accepts form-encoded (HTMX) or JSON bodies with ``body``. HTMX requests
    get a rendered comment-card fragment back for an instant swap; everyone
    else gets JSON (201 / 400 / 401 / 404).
    """
    from apps.pages.models import BlogPostPage
    from apps.content.models.comments import PostComment

    post = BlogPostPage.objects.filter(slug=slug).first()
    if post is None:
        return JsonResponse({"error": "Post not found"}, status=404)

    if request.method == "POST":
        user = request.user if request.user.is_authenticated else None
        if user is None:
            return JsonResponse(
                {"error": "Authentication required — sign in to comment."},
                status=401,
            )
        import json

        body = ""
        if request.content_type == "application/json":
            try:
                body = json.loads(request.body.decode("utf-8")).get("body", "")
            except (json.JSONDecodeError, UnicodeDecodeError):
                body = ""
        else:
            body = request.POST.get("body", "")
        body = str(body).strip()
        if not body or len(body) > 2000:
            return JsonResponse(
                {"error": "Comments must be between 1 and 2000 characters."},
                status=400,
            )

        comment = PostComment.objects.create(
            post=post, author=user, body=body, is_approved=True
        )
        logger.info("blog_comment: %s on %s (id=%s)", user, post.slug, comment.pk)
        payload = _comment_to_dict(comment)
        if request.headers.get("HX-Request"):
            return render(
                request,
                "content/partials/comment.html",
                {"comment": comment},
            )
        return JsonResponse(payload, status=201)

    comments = [_comment_to_dict(c) for c in post.get_approved_comments()]
    return JsonResponse({"comments": comments, "total": len(comments)})


@csrf_exempt
def htxm_ping_api(request):
    """GET /fragment/ping/ — returns the current server time as an HTML fragment.

    Used by the homepage HTMX demo to show live fragment swapping.
    """
    from datetime import datetime
    from django.http import HttpResponse

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return HttpResponse(
        f'<div class="text-center">'
        f'<p class="font-mono text-2xl font-bold text-fu-link tabular-nums">{now}</p>'
        f'<p class="mt-1 font-mono text-[0.65rem] uppercase tracking-[0.16em] text-fu-muted">'
        f'server time · text/html fragment</p>'
        f'</div>'
    )


@csrf_exempt
def contact_submit_api(request):
    """POST /fragment/contact/ — handle the contact form submission.

    Accepts form-encoded (Django template form) or JSON (Astro ContactForm)
    bodies with ``name``/``email``/``subject``/``message``. Returns an HTML
    fragment for HTMX swaps into ``#contact-form-result`` (the Django form)
    and JSON for plain API consumers. Every valid submission is persisted as
    a ``ContactSubmission`` snippet (the archived ctc-research / Precis
    enhancement) so inquiries are reviewable in the Wagtail admin.
    """
    import json
    import re

    EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    data = {}
    if request.method == "POST":
        if request.content_type == "application/json":
            try:
                data = json.loads(request.body.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                data = {}
        else:
            data = request.POST

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    subject = str(data.get("subject", "")).strip()
    topic = str(data.get("topic", "")).strip()
    message = str(data.get("message", "")).strip()

    errors = []
    if not name:
        errors.append("Please provide your name.")
    if not EMAIL_RE.match(email):
        errors.append("Please provide a valid email address.")
    if len(message) < 10:
        errors.append("Please write a message (at least 10 characters).")

    def fragment(text, ok):
        from django.http import HttpResponse
        klass = "text-fu-live font-medium" if ok else "text-red-500 font-medium"
        return HttpResponse(f'<p class="{klass}">{text}</p>')

    if errors:
        detail = "<br>".join(errors)
        if request.headers.get("HX-Request"):
            return fragment(detail, False)
        return JsonResponse({"success": False, "message": detail}, status=400)

    logger.info(
        "contact_submit: %s <%s> topic=%s %s",
        name, email, topic or "(none)", subject or "(no subject)",
    )

    # Persist the submission — the audit trail every contact form needs. The
    # model mirrors the archived ctc-research / Precis ContactSubmission.
    try:
        from apps.content.models.contact import ContactSubmission

        ContactSubmission.objects.create(
            form_id="landing-contact",
            page_id=0,
            page_title="Contact page",
            page_url=request.build_absolute_uri(),
            submitted_data={
                "name": name,
                "email": email,
                "subject": subject,
                "topic": topic,
                "message": message,
            },
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            referrer=request.META.get("HTTP_REFERER", ""),
        )
    except Exception:
        logger.exception("contact_submit persistence error")

    from django.utils.html import escape

    if request.headers.get("HX-Request"):
        # User input is interpolated into an HTML fragment — escape it so a
        # crafted name/email cannot inject markup into the HTMX swap target.
        return fragment(
            f"✓ Thanks, {escape(name)}! We'll get back to you at {escape(email)} within one business day.",
            True,
        )
    return JsonResponse(
        {"success": True, "message": f"Thanks, {name}! We'll be in touch."}
    )


@csrf_exempt
def newsletter_subscribe_api(request):
    """POST /api/newsletter/subscribe/ — subscribe an email address.

    Accepts form-encoded or JSON body with ``email`` (and optional ``source``).
    Upserts a ``NewsletterSubscriber`` row (re-activates if it was paused),
    then returns an HTML fragment (HTMX swap into ``#newsletter-feedback``)
    or JSON.
    """
    import json
    import re

    EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    # Parse the email + source from the request body
    email = ""
    source = "footer"
    if request.method == "POST":
        if request.content_type == "application/json":
            try:
                body = json.loads(request.body.decode("utf-8"))
                email = body.get("email", "").strip()
                source = body.get("source", "footer").strip() or "footer"
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
        else:
            email = request.POST.get("email", "").strip()
            source = request.POST.get("source", "footer").strip() or "footer"

    if not email:
        return JsonResponse(
            {"success": False, "message": "Please provide an email address."},
            status=400,
        )

    if not EMAIL_RE.match(email):
        return JsonResponse(
            {"success": False, "message": "Please enter a valid email address."},
            status=400,
        )

    # Persist the subscription — upsert by email, re-activate paused rows.
    subscriber = None
    created = False
    try:
        from apps.content.models.newsletter import NewsletterSubscriber

        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email__iexact=email,
            defaults={"email": email, "source": source, "is_active": True},
        )
        if not created:
            # Normalize the stored address casing + re-activate.
            if subscriber.email != email:
                subscriber.email = email
            subscriber.is_active = True
            subscriber.source = source or subscriber.source
            subscriber.save(update_fields=["email", "is_active", "source", "updated_at"])
        logger.info("newsletter_subscribe: %s (new=%s, source=%s)", email, created, source)
    except Exception:
        logger.exception("newsletter_subscribe persistence error for %s", email)

    # Fire the post-subscribe side effects — a branded welcome email on fresh
    # signups and an idempotent push to the configured email provider — without
    # ever blocking the response (the service logs its own failures).
    if subscriber is not None:
        try:
            from apps.content.services.newsletter import notify_newsletter_subscription
            notify_newsletter_subscription(subscriber, is_new=created)
        except Exception:
            logger.exception("newsletter_subscribe side effects error for %s", email)

    # Check if this is an HTMX request — return HTML fragment for swap.
    if request.headers.get("HX-Request"):
        from django.http import HttpResponse
        from django.utils.html import escape
        # User input is interpolated into an HTML fragment — escape it so a
        # crafted email cannot inject markup into the HTMX swap target.
        safe_email = escape(email)
        return HttpResponse(
            '<div class="live-fragment__fallback" style="border-color:hsl(var(--fu-live))">'
            '<p class="text-fu-live font-medium">✓ Subscribed!</p>'
            '<p class="text-sm text-fu-muted mt-1">We\'ll send updates to '
            f'<code class="font-mono text-fu-ink">{safe_email}</code>.</p>'
            '</div>'
        )

    return JsonResponse({
        "success": True,
        "message": f"Subscribed! We'll send updates to {email}.",
    })


def newsletter_status_api(request):
    """GET /api/newsletter/status/ — subscriber count for the footer badge.

    Returns the number of active subscribers so the UI can show social proof
    (e.g. "Join 1,200+ readers").
    """
    try:
        from apps.content.models.newsletter import NewsletterSubscriber

        count = NewsletterSubscriber.objects.filter(is_active=True).count()
    except Exception:
        count = 0
    return JsonResponse({"subscriber_count": count})
