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
from pathlib import Path
from urllib.parse import quote

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.html import strip_tags
from django.utils.text import slugify
from django.utils.translation import activate, check_for_language, gettext as _
from django.views.decorators.csrf import csrf_exempt, csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_POST
from wagtail.blocks.list_block import ListValue
from wagtail.blocks.stream_block import StreamValue
from wagtail.blocks.struct_block import StructValue
from wagtail.models import Page
from wagtail.rich_text import RichText

logger = logging.getLogger(__name__)

def _supported_language_codes() -> list[str]:
    """Return the active Wagtail catalog, with shared settings as validation."""
    try:
        from apps.content.models.languages import SiteLanguage

        rows = list(SiteLanguage.active().values_list("code", flat=True))
        if rows:
            return rows
    except Exception:
        logger.debug("Wagtail language snippets are not available during bootstrap", exc_info=True)
    from django_fusion.core.middlewares.language import configured_language_codes

    return list(configured_language_codes())


def _normalize_language(value: object) -> str | None:
    from django_fusion.core.middlewares.language import normalize_language

    return normalize_language(value, _supported_language_codes())


def _language_session_key() -> str:
    from django_fusion.core.middlewares.language import language_session_key

    return language_session_key()


def _requested_language(request: HttpRequest) -> str:
    """Resolve query → session → cookie → middleware/header → default."""
    from django_fusion.core.middlewares.language import resolve_language

    return resolve_language(request)


@require_POST
@csrf_protect
def set_language_api(request: HttpRequest) -> JsonResponse:
    """Persist a language in the Django session and configured cookie.

    Django's stock ``set_language`` view only writes the cookie in current
    releases. The Astro header needs the preference in both stores so API,
    HTMX, Wagtail, and later authenticated requests resolve one language.
    """
    language = _normalize_language(request.POST.get("language"))
    if not language or not check_for_language(language):
        return JsonResponse({"error": "Unsupported language", "language": _requested_language(request)}, status=400)

    from django_fusion.core.middlewares.language import persist_language

    activate(language)
    response = JsonResponse({
        "language": language,
        "default_language": getattr(settings, "LANGUAGE_CODE", "en"),
        "session_key": _language_session_key(),
        "cookie_name": getattr(settings, "LANGUAGE_COOKIE_NAME", "django_language"),
        "available_languages": _supported_language_codes(),
    })
    return persist_language(request, response, language)


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
            # Localized editions may carry localized slugs (e.g. the Arabic
            # "about" page uses a translated slug), so prefer the direct slug
            # match and fall back to the translation chain (translation_key)
            # when the requested locale renames the page.
            localized = pages.filter(locale__language_code=language).first()
            if localized is not None:
                return localized
            base = pages.filter(locale__language_code="en").first() or pages.first()
            if base is not None:
                try:
                    from wagtail.models import Locale as WagtailLocale

                    locale_obj = WagtailLocale.objects.filter(language_code=language).first()
                    translation = base.get_translation_or_none(locale=locale_obj) if locale_obj else None
                except Exception:
                    translation = None
                if translation is not None:
                    return translation
                return base
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


def _page_data(page, request=None, language: str | None = None) -> dict:
    """Return a frontend-shaped page payload from any live LMS page."""
    specific = page.specific
    data = {
        "id": page.pk,
        "slug": page.slug or "home",
        "title": _PAGE_TITLE_OVERRIDES.get(page.slug, page.title),
        "type": specific.__class__.__name__,
        "show_in_nav": bool(getattr(specific, "show_in_nav", True)),
        "seo_title": getattr(page, "seo_title", "") or page.title,
        "search_description": getattr(page, "search_description", "") or "",
    }

    # ── Per-page SEO block ────────────────────────────────────────────
    # Page-level seo_title/search_description win; the site-level defaults
    # (SiteSettings.get_seo_context) fill the gaps so the frontend never
    # hardcodes meta copy. Canonical resolves to the configured origin or
    # the request host, and is localized through the same _live_page chain.
    seo = {
        "title": (getattr(specific, "seo_title", "") or page.title),
        "description": (getattr(specific, "search_description", "") or ""),
        "keywords": "",
        "author": "",
        "og_type": "website",
        "og_image_url": None,
        "twitter_handle": "",
        "robots": "index, follow",
        "canonical_url": "",
    }
    try:
        from apps.content.models.settings import SiteSettings as SeoSettings

        settings_obj = SeoSettings.for_request(request) if request is not None else None
        if settings_obj is None:
            try:
                settings_obj = SeoSettings.load()
            except Exception:
                settings_obj = None
        if settings_obj:
            ctx = settings_obj.get_seo_context()
            seo["description"] = seo["description"] or ctx.get("meta_description", "")
            seo["keywords"] = ctx.get("meta_keywords", "")
            seo["author"] = ctx.get("meta_author", "")
            seo["og_type"] = ctx.get("og_type", "website")
            seo["og_image_url"] = ctx.get("og_image_url")
            seo["twitter_handle"] = ctx.get("twitter_handle", "")
            seo["robots"] = ctx.get("robots", "index, follow") or "index, follow"
            seo["canonical_url"] = ctx.get("canonical_url", "") or seo["canonical_url"]
    except Exception:
        logger.exception("Unable to resolve site SEO defaults")
    if request is not None and not seo["canonical_url"]:
        seo["canonical_url"] = request.build_absolute_uri(request.path)
    data["seo"] = seo

    hero_heading = getattr(specific, "hero_heading", "")
    hero_subheading = getattr(specific, "hero_subheading", "")
    hero_accent = getattr(specific, "hero_accent", "")
    data["hero"] = {
        "badge": _("ctc research · medical research learning"),
        "title": hero_heading or page.title,
        "subtitle": hero_subheading or getattr(specific, "intro_text", "") or "",
        "accent": hero_accent or "",
        "primary_cta": {"label": _("Explore courses"), "href": "/courses/", "style": "primary"},
        "secondary_cta": {"label": _("Learn about CTC Research"), "href": "/about/", "style": "secondary"},
    }

    body = getattr(specific, "body", None) or getattr(specific, "intro_text", None)
    if body:
        data["body"] = str(body)

    # HomePage head.slider — the Wagtail-edited hero carousel. The Astro road
    # renders these slides (image, subtitle, title, description, CTA, alignment)
    # with the Swiper-style slider component; falls back to the seeded agenda
    # strip when the block is empty.
    # NOTE: _stream_items drops list-shaped blocks (a slider's StreamValue of
    # slides), so read the StreamField directly here.
    head_stream = getattr(specific, "head", None)
    if head_stream is not None:
        slides: list[dict] = []
        for block in head_stream:
            if block.block_type != "slider":
                continue
            for slide in block.value:
                value = _plain(slide.value)
                if not isinstance(value, dict):
                    continue
                image = value.get("background_image") or value.get("image")
                slides.append({
                    "image": image.get("url") if isinstance(image, dict) else "",
                    "alt": value.get("alt_text") or value.get("title") or "",
                    "subtitle": value.get("subtitle") or "",
                    "title": value.get("title") or "",
                    "description": value.get("description") or "",
                    "alignment": value.get("text_alignment") or "left",
                    "button_text": value.get("button_text") or "",
                    "button_link": value.get("button_link") or "",
                    "video_url": value.get("video_url") or "",
                })
        if slides:
            data["hero"]["slides"] = slides

    for field_name in ("stats", "features", "testimonials", "pricing", "faq", "projects", "products", "services", "process", "blog"):
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
    _extract_seeded_blocks(specific, data, language)

    # Home section chrome — the CMS-owned headings/intros for the research
    # slider, course slider, hero evidence panel, learning teaser, and the
    # methods/programs section heads (HomePage.home_chrome). Serialized as a
    # flat dict keyed by block type so the Astro shell can render every one
    # of them per locale without a frontend dictionary.
    chrome = getattr(specific, "home_chrome", None)
    if chrome is not None:
        data["home_chrome"] = _home_chrome_data(chrome)

    data.setdefault("cta", {
        "title": _("Start learning with CTC Research"),
        "subtitle": _("A medical research center for clinical evidence, biostatistics, and responsible medical AI."),
        "primary_cta": {"label": _("Browse courses"), "href": "/courses/", "style": "primary"},
    })
    return data


def _home_chrome_data(stream) -> dict:
    """Serialize HomePage.home_chrome into a flat {block_type: fields} dict.

    Only the first block of each type wins (the editor is not expected to
    repeat sections); list-valued blocks (evidence ``stats``) serialize as
    plain JSON via ``_plain`` so the frontend renders them directly.
    """
    sections: dict[str, dict] = {}
    for block in stream:
        block_type = block.block_type
        if block_type in sections:
            continue
        value = _plain(block.value)
        if not isinstance(value, dict):
            continue
        sections[block_type] = {str(key): _plain(item) for key, item in value.items()}
    return sections


def _extract_seeded_blocks(specific, data: dict, language: str | None = None) -> None:
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

    # About page: gallery, counters, experience + video (facts → about),
    # plus the mission/skills/faq blocks. Each block type is processed
    # independently (no early break) so every seeded block is exposed.
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
            elif block.block_type == "mission":
                mission = block.value
                values = mission.get("values") or []
                if values:
                    data["mission_values"] = _plain(values)
                    data.setdefault("mission_title", _plain(mission.get("title") or ""))
                    data.setdefault("mission_subtitle", _plain(mission.get("subtitle") or ""))
                    data.setdefault("mission_intro", _plain(mission.get("intro") or ""))
            elif block.block_type == "skills":
                skills = block.value
                items = skills.get("items") or []
                if items:
                    data["skills"] = _plain(items)
                    data.setdefault("skills_title", _plain(skills.get("title") or ""))
                    data.setdefault("skills_subtitle", _plain(skills.get("subtitle") or ""))
                    data.setdefault("skills_intro", _plain(skills.get("intro") or ""))
            elif block.block_type == "faq":
                faq = block.value
                items = faq.get("items") or []
                if items:
                    data["faq"] = _plain(items)
                    data.setdefault("faq_title", _plain(faq.get("title") or ""))
                    data.setdefault("faq_subtitle", _plain(faq.get("subtitle") or ""))

    # Home page: why-choose "methods" list (CTA → why_choose_section).
    cta = getattr(specific, "CTA", None)
    if cta is not None:
        for block in cta:
            if block.block_type == "why_choose_section":
                methods = block.value.get("methods") or []
                if methods:
                    data["methods"] = _plain(methods)
                break

    # Services page: reusable Wagtail service snippets are the source of
    # truth for the Astro /services/ cards. Do not duplicate this editorial
    # content in the frontend.
    if specific.__class__.__name__ == "ServicesPage":
        try:
            from apps.handlers.models.manage.service import Service

            data["services"] = [
                {
                    "title": service.name,
                    "description": service.description or service.overview,
                    "category": service.category,
                    "icon": service.icon,
                    "deliverables": [],
                    "cta_label": "Discuss this service",
                    "cta_href": "/contact/",
                }
                for service in Service.objects.filter(is_active=True, is_visible=True).order_by("name")
            ]
        except Exception:
            logger.exception("Service listing unavailable")

    # Events page: active/visible Event rows so the Astro /events/ route
    # renders the seeded calendar instead of a 404/fallback. When ``lang`` is
    # requested, an EventTranslation overlay (if present) overrides the
    # canonical English title/description/location — empty overlay fields fall
    # back to the canonical row.
    if specific.__class__.__name__ == "EventPage":
        try:
            from apps.pages.accounts.models import Event

            data["events"] = []
            for event in Event.objects.filter(is_active=True, is_visible=True).order_by("start_date", "title"):
                translation = None
                if language:
                    translation = event.translations.filter(language=language).first()
                data["events"].append(
                    {
                        "title": (translation.title if translation and translation.title else event.title),
                        "description": (
                            translation.description if translation and translation.description else event.description
                        ),
                        "event_type": event.event_type,
                        "event_type_label": event.get_event_type_display(),
                        "location": (
                            translation.location if translation and translation.location else event.location
                        ),
                        "start_date": event.start_date.isoformat() if event.start_date else None,
                        "end_date": event.end_date.isoformat() if event.end_date else None,
                    }
                )
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
        "primary_color": getattr(settings_obj, "primary_color", "") or "#E61919",
        "accent_color": getattr(settings_obj, "accent_color", "") or "#008080",
        "meta_description": seo.get("meta_description", "") or getattr(settings_obj, "footer_description", ""),
        "meta_keywords": seo.get("meta_keywords", ""),
        "meta_author": seo.get("meta_author", ""),
        "og_type": seo.get("og_type", "website"),
        "og_image_url": seo.get("og_image_url"),
        "twitter_handle": seo.get("twitter_handle", ""),
        "robots": seo.get("robots", "index, follow"),
        "canonical_url": seo.get("canonical_url", ""),
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
    """Return the Wagtail language catalog, with Django settings as bootstrap."""
    try:
        from apps.content.models.languages import SiteLanguage

        rows = [language.as_dict() for language in SiteLanguage.active()]
        if rows:
            return rows
    except Exception:
        logger.debug("Precis language snippets are unavailable during bootstrap", exc_info=True)

    from django_fusion.core.middlewares.language import language_context

    return [
        {
            "code": item["code"],
            "name": item["name"],
            "native": item["name_local"],
            "dir": item["dir"],
            "flag": "",
        }
        for item in language_context().get("languages", [])
    ]


@ensure_csrf_cookie
def content_languages_api(request: HttpRequest) -> JsonResponse:
    """GET /apis/content/languages/ — seeded language choices for the frontend.

    This endpoint also establishes the CSRF cookie used by the language
    selector before it POSTs the durable session/cookie preference.
    """
    languages = _language_catalog()
    return JsonResponse({
        "languages": languages,
        "coverage": {language["code"]: 0 for language in languages},
        "ui_languages": [language["code"] for language in languages],
        "language": _requested_language(request),
        "default_language": getattr(settings, "LANGUAGE_CODE", "en"),
        "session_key": _language_session_key(),
        "cookie_name": getattr(settings, "LANGUAGE_COOKIE_NAME", "django_language"),
    })


_DOCUMENT_GUIDANCE = {
    "en": {"title": "How to use the research library", "body": "Start with the document that matches your stage of work. Read the abstract first, then open the source record and record the method decisions that apply to your study.", "steps": ["Frame the question", "Check the method and limits", "Apply the guidance to your protocol"]},
    "sv": {"title": "Så använder du forskningsbiblioteket", "body": "Börja med dokumentet som passar ditt arbete. Läs sammanfattningen och dokumentera sedan de metodbeslut som gäller för din studie.", "steps": ["Formulera frågan", "Kontrollera metod och begränsningar", "Tillämpa vägledningen i protokollet"]},
    "fr": {"title": "Comment utiliser la bibliothèque de recherche", "body": "Choisissez le document correspondant à votre étape de travail. Lisez le résumé, puis notez les décisions méthodologiques utiles à votre étude.", "steps": ["Formuler la question", "Vérifier la méthode et les limites", "Appliquer le guide au protocole"]},
    "de": {"title": "So nutzen Sie die Forschungsbibliothek", "body": "Wählen Sie das Dokument passend zu Ihrer Arbeitsphase. Lesen Sie die Zusammenfassung und halten Sie die relevanten methodischen Entscheidungen fest.", "steps": ["Die Frage präzisieren", "Methode und Grenzen prüfen", "Die Anleitung im Protokoll anwenden"]},
    "es": {"title": "Cómo usar la biblioteca de investigación", "body": "Empieza con el documento que corresponde a tu etapa de trabajo. Lee el resumen y registra las decisiones metodológicas útiles para tu estudio.", "steps": ["Definir la pregunta", "Revisar método y límites", "Aplicar la guía al protocolo"]},
    "ar": {"title": "كيفية استخدام مكتبة الأبحاث", "body": "ابدأ بالوثيقة المناسبة لمرحلة عملك. اقرأ الملخص ثم سجّل القرارات المنهجية التي تنطبق على دراستك.", "steps": ["تحديد السؤال", "مراجعة المنهج والحدود", "تطبيق الإرشاد على البروتوكول"]},
    "pt-br": {"title": "Como usar a biblioteca de pesquisa", "body": "Comece pelo documento adequado à sua etapa de trabalho. Leia o resumo e registre as decisões metodológicas úteis para o seu estudo.", "steps": ["Formular a pergunta", "Verificar método e limites", "Aplicar o guia ao protocolo"]},
}


def _publication_document(publication) -> dict:
    """Serialize one Publication row into the frontend document shape."""
    return {
        "id": publication.pk,
        "title": publication.title,
        "slug": publication.slug,
        "abstract": str(publication.abstract),
        "authors": publication.authors,
        "category": publication.category.name if publication.category else "",
        "language": publication.language,
        "published_at": publication.published_at.isoformat() if publication.published_at else None,
        "external_url": publication.external_url,
    }


def research_publications_api(request: HttpRequest) -> JsonResponse:
    """GET /apis/research/publications/ — localized Wagtail documents.

    Supports the django-fusion query surface (see DF-019):
    ``?category=`` (category slug/name), ``?q=`` (search), ``?ordering=``,
    ``?limit=`` / ``?page=`` / ``?offset=``.
    """
    language = _requested_language(request)
    from apps.content.models.publication import Publication

    queryset = Publication.objects.filter(is_published=True, language=language).select_related("category")

    category = (request.GET.get("category") or "").strip()
    if category:
        queryset = queryset.filter(
            category__slug=category
        ) | queryset.filter(category__name=category)
        queryset = queryset.distinct()

    query = (request.GET.get("q") or request.GET.get("search") or "").strip()
    if query:
        from django.db.models import Q

        queryset = queryset.filter(
            Q(title__icontains=query)
            | Q(authors__icontains=query)
            | Q(abstract__icontains=query)
        )

    ordering = (request.GET.get("ordering") or "").strip()
    if ordering in {"published_at", "-published_at", "title", "-title"}:
        queryset = queryset.order_by(ordering)

    # Pagination (defaults: 100 per page, page 1).
    try:
        limit = int(request.GET.get("limit", 100))
    except (TypeError, ValueError):
        limit = 100
    limit = max(1, min(limit, 500))
    try:
        offset = int(request.GET.get("offset", 0))
    except (TypeError, ValueError):
        offset = 0
    try:
        page = int(request.GET.get("page", 1))
    except (TypeError, ValueError):
        page = 1
    if "offset" in request.GET:
        page = (offset // limit) + 1
    elif "page" in request.GET:
        page = max(1, page)
        offset = (page - 1) * limit

    total = queryset.count()
    documents = [_publication_document(publication) for publication in queryset[offset:offset + limit]]
    return JsonResponse({
        "documents": documents,
        "total": total,
        "count": len(documents),
        "page": page,
        "page_size": limit,
        "language": language,
        "guidance": _DOCUMENT_GUIDANCE[language],
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

# Navigation labels are intentionally shorter than editorial SEO/page titles.
# Stable slugs and the full page content remain unchanged; this map keeps the
# header, API navigation, and Astro shell aligned even before a fresh fixture
# load updates existing Wagtail rows.
_SHORT_PAGE_LABELS = {
    "home": "Home",
    "all-courses": "Courses",
    "about": "About",
    "contact": "Contact",
    "services": "Services",
    "team": "Team",
    "events": "Events",
}
_PAGE_TITLE_OVERRIDES = {"contact": "Contact", "all-courses": "Courses"}

# Content-only fragment template per landing slug. The Astro shell owns the
# document, so /fragment/pages/<slug>/ renders only the matching
# ``<page>/fragment.html`` (no outer layout) — the same contract as the
# FusionLandingView subclasses in landing_views.py. Pages without a dedicated
# fragment (courses, events, blog) fall back to a minimal body snippet.
_FRAGMENT_TEMPLATES = {
    "home": "home/fragment.html",
    "about": "about/fragment.html",
    "about-us": "about/fragment.html",
    "contact": "contact/fragment.html",
    "team": "team/fragment.html",
    "services": "services/fragment.html",
}

# Dropdown children for nav items whose subpages are Astro-owned routes (not
# Wagtail children) — mirrors the Precis Landing ``NAV_CHILDREN_CURATED``
# contract so the About item carries its founder/research/education/services
# organization without needing every subpage to exist in the Wagtail tree.
# ``Team`` is deliberately NOT listed: it is already a first-class top-level
# nav item (``team`` → ``/team/``), so listing it in the About dropdown would
# render the label twice in the header.
_NAV_CHILDREN_CURATED = {
    "about": [
        {"label": "Founder", "href": "/about/founder/"},
        {"label": "Research", "href": "/about/research/"},
        {"label": "Education", "href": "/about/education/"},
        {"label": "Services", "href": "/services/"},
    ],
}


def _nav_children_for(href: str, path: str) -> list[dict]:
    """Return the curated dropdown children for a nav item (empty for leaves)."""
    children = _NAV_CHILDREN_CURATED.get(href.strip("/")) or []
    return [
        {
            "label": child["label"],
            "href": child["href"],
            "active": path.rstrip("/") == child["href"].rstrip("/")
            or path.startswith(child["href"]),
        }
        for child in children
    ]


def navigation_api(request: HttpRequest) -> JsonResponse:
    language = _requested_language(request)
    items = [{
        "label": "Home",
        "href": "/",
        "active": request.path == "/",
        "children": [],
    }]
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
        for child in children.order_by("title"):
            route = _FRONTEND_ROUTES.get(child.slug)
            if route is None:
                continue
            specific = child.specific
            if not (getattr(specific, "show_in_nav", True) or getattr(specific, "show_in_menus", True)):
                continue
            label = _SHORT_PAGE_LABELS.get(child.slug, child.title)
            if language != "en":
                try:
                    from apps.content.models.translations import PageTranslation
                    translation = PageTranslation.for_page(child, language)
                    if translation and translation.title:
                        label = translation.title
                except Exception:
                    pass
            items.append({
                "label": label,
                "href": route,
                "active": request.path == route.rstrip("/") or request.path.startswith(route),
                "children": _nav_children_for(route, request.path),
            })
    except Exception:
        # The API remains useful before the optional Wagtail seed command runs.
        items.extend([
            {"label": "Courses", "href": "/courses/", "active": False, "children": []},
            {"label": "About", "href": "/about/", "active": False,
             "children": _nav_children_for("/about/", request.path)},
            {"label": "Contact", "href": "/contact/", "active": False, "children": []},
        ])
    return JsonResponse({
        "nav_items": items,
        "language": language,
        "available_languages": [item["code"] for item in _language_catalog()],
    })


def page_data_api(request: HttpRequest, slug: str) -> JsonResponse:
    language = _requested_language(request)
    # Activate the requested locale so gettext'd API constants (hero badge,
    # CTA labels, CTA fallback copy) resolve in the same language as the
    # localized Wagtail page payload the client asked for.
    from django.utils import translation

    previous = translation.get_language()
    activate(language)
    try:
        page = _live_page(slug, language)
        if page is None:
            return JsonResponse({"error": "Page not found"}, status=404)
        data = _page_data(page, request, language=language)
        data["language"] = language
        data["available_languages"] = [item["code"] for item in _language_catalog()]
        return JsonResponse(data)
    finally:
        activate(previous)


def page_fragment_api(request: HttpRequest, slug: str = "home") -> HttpResponse:
    """GET /fragment/pages/<slug>/ — render the page's content-only HTML fragment.

    The Astro frontend owns the document shell, so this endpoint must never
    return the full layout (a fragment request for ``/<slug>/`` would return
    the Astro document again). It renders the matching ``<page>/fragment.html``
    content region — the same contract the ``FusionLandingView`` subclasses
    expose for HTMX swaps — which the frontend's RenderModeSwitch/LiveFragment
    HTML road swaps into the page.
    """
    normalized = (slug or "home").strip("/") or "home"
    page = _live_page(normalized, _requested_language(request))
    if page is None:
        return HttpResponse("Page not found", status=404)

    specific = page.specific
    template = _FRAGMENT_TEMPLATES.get(normalized)
    if template is not None:
        return render(
            request,
            template,
            {
                "page": specific,
                "request": request,
                "title": _PAGE_TITLE_OVERRIDES.get(page.slug, page.title),
                "fragment_name": getattr(specific, "fragment_name", None)
                or f"pages.{normalized.replace('-', '_')}",
            },
        )

    # Pages without a dedicated content fragment (courses, events, blog) fall
    # back to a minimal body snippet instead of the full ``base.html`` layout.
    body = getattr(specific, "body", None)
    title = _PAGE_TITLE_OVERRIDES.get(page.slug, page.title)
    fragment = f'<article class="fusion-page" data-slug="{html.escape(page.slug)}"><h1>{html.escape(title)}</h1>'
    if body:
        fragment += str(body)
    fragment += "</article>"
    return HttpResponse(fragment)


def page_list_api(request: HttpRequest) -> JsonResponse:
    """GET /apis/pages/ — published Wagtail pages for the active locale."""
    language = _requested_language(request)
    pages = []
    queryset = Page.objects.live().filter(depth__gt=1, locale__language_code=language).order_by("title")
    for page in queryset:
        pages.append({"id": page.pk, "slug": page.slug, "title": page.title, "type": page.specific_class.__name__})
    return JsonResponse({
        "pages": pages,
        "total": len(pages),
        "language": language,
        "available_languages": [item["code"] for item in _language_catalog()],
    })


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
    button_text = "Send Message"
    success_message = "Message sent successfully! We'll get back to you soon."
    error_message = "Failed to send message. Please try again."
    fields: list[dict] = []
    methods: list[dict] = []

    if page is not None:
        specific = page.specific
        title = _PAGE_TITLE_OVERRIDES.get(page.slug, page.title or title)

        # Seeded form fields (contact_form → contact_form → fields).
        for block in getattr(specific, "contact_form", []) or []:
            if block.block_type == "contact_form":
                fields = _plain(block.value.get("fields") or [])
                break

        if getattr(specific, "form_title", ""):
            form_title = strip_tags(_plain(getattr(specific, "form_title")))
        if getattr(specific, "form_intro", ""):
            form_description = strip_tags(_plain(getattr(specific, "form_intro")))
        if getattr(specific, "button_text", ""):
            button_text = _plain(getattr(specific, "button_text"))
        if getattr(specific, "success_message", ""):
            success_message = strip_tags(_plain(getattr(specific, "success_message")))
        if getattr(specific, "error_message", ""):
            error_message = strip_tags(_plain(getattr(specific, "error_message")))

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
        "button_text": button_text,
        "success_message": success_message,
        "error_message": error_message,
        "fields": fields,
        "language": language,
        "available_languages": [item["code"] for item in _language_catalog()],
    })


def media_manifest_api(request: HttpRequest) -> JsonResponse:
    """GET /apis/content/media/ — CTC archive media for website content.

    The manifest is source-controlled beside the compatible Wagtail dump. The
    endpoint only returns files that exist in the mounted shared media tree,
    so a clean checkout remains valid and a restored archive becomes visible
    without a database reload. It prefers the prepared ``ctc-content/`` copy
    and falls back to the attached archive directory until preparation runs.
    """
    manifest_path = Path(getattr(settings, "CTC_MEDIA_MANIFEST_PATH", ""))
    if not manifest_path.is_file():
        return JsonResponse({"version": 1, "site": "precis-ctc", "logos": [], "items": []})

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        logger.exception("Unable to read CTC media manifest: %s", manifest_path)
        return JsonResponse({"version": 1, "site": "precis-ctc", "logos": [], "items": []})

    source_dir = Path(getattr(settings, "CTC_MEDIA_SOURCE_DIR", Path(settings.MEDIA_ROOT) / "media"))
    content_dir = Path(getattr(settings, "CTC_MEDIA_CONTENT_DIR", Path(settings.MEDIA_ROOT) / "ctc-content"))
    media_url = str(getattr(settings, "MEDIA_URL", "/media/")).rstrip("/")
    content_url = str(getattr(settings, "CTC_MEDIA_CONTENT_URL", f"{media_url}/ctc-content/")).rstrip("/")
    items = []

    for item in manifest.get("items", []):
        source_name = str(item.get("source", ""))
        if not source_name or Path(source_name).name != source_name:
            continue
        source_path = source_dir / source_name
        prepared_name = f"{slugify(Path(source_name).stem) or 'asset'}{Path(source_name).suffix.lower()}"
        prepared_path = content_dir / prepared_name
        if prepared_path.is_file():
            url = f"{content_url}/{quote(prepared_name)}"
        elif source_path.is_file():
            url = f"{media_url}/media/{quote(source_name)}"
        else:
            continue
        items.append({
            "src": url,
            "alt": item.get("alt", "CTC Research archive media"),
            "caption": item.get("caption", ""),
            "category": item.get("category", "research"),
            "media_type": item.get("media_type", "video" if source_name.lower().endswith(".mp4") else "image"),
            "source_name": source_name,
        })

    return JsonResponse({
        "version": manifest.get("version", 1),
        "site": manifest.get("site", "precis-ctc"),
        "archive_root": manifest.get("archive_root", ""),
        "logos": manifest.get("logos", []),
        "items": items,
        "available": len(items),
        "total": len(manifest.get("items", [])),
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
