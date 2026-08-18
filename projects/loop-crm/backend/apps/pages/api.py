"""Loop-CRM public page JSON road — GET /apis/pages/<slug>/.

Ports the precis-landing page API contract: Wagtail page models + StreamField
sections flattened into JSON for the Astro frontend. Astro owns every public
URL; this road is the single source of truth for the landing copy.
"""
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_GET
from wagtail.models import Page

from apps.content.blocks import SECTION_ITEM_LIST_KEYS, SECTION_STACK_FIELDS

logger = logging.getLogger(__name__)


def _stream_to_plain(value, keep_pages=False):
    """Recursively convert Wagtail StreamField values to JSON-safe Python.

    Handles StructValue/ListValue from wagtail.blocks and resolves
    PageChooserBlock values to ``{id, title, url}`` dicts (or pks when
    ``keep_pages=True``).
    """
    if isinstance(value, Page):
        if keep_pages:
            return value.pk
        try:
            return {"id": value.pk, "title": value.title, "url": value.url}
        except Exception:
            return {"id": value.pk, "title": value.title, "url": ""}
    if hasattr(value, "items") and hasattr(value, "get"):
        return {k: _stream_to_plain(v, keep_pages) for k, v in value.items()}
    if hasattr(value, "__iter__") and not isinstance(value, (str, bytes)):
        return [_stream_to_plain(v, keep_pages) for v in value]
    return value


def _button_to_dict(btn) -> dict | None:
    """Serialize a ButtonBlock StructValue (label/href/style) to a dict.

    A chosen page resolves to its live URL; the label falls back to the page
    title when the editor left it empty.
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
    tiers, features) are covered too.
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
    return value


def _get_wagtail_page(slug: str):
    """Retrieve a live Wagtail page by slug (defaults to the home page)."""
    normalized = slug.strip("/") or "home"
    try:
        return Page.objects.live().filter(slug=normalized).first()
    except Exception:
        return None


def _page_to_dict(page) -> dict:
    """Serialize a Wagtail page to the frontend-consumable dict."""
    data = {
        "id": page.pk,
        "slug": page.slug if page.slug else "home",
        "title": page.title,
        "type": page.__class__.__name__,
        "show_in_nav": True,
        "seo_title": getattr(page, "seo_title", "") or page.title,
        "search_description": getattr(page, "search_description", ""),
    }

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
                    "note": hero_val.get("note", ""),
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

    # Legal body (RichText)
    if hasattr(page, "body") and page.body:
        data["body"] = str(page.body)

    # Section stack fields — each section's nested item list is flattened
    # onto the page payload (see SECTION_ITEM_LIST_KEYS). The section header
    # (eyebrow/title/description) is exposed as ``<field>_head`` so the
    # frontend renders editor-managed headings — never hard-coded copy.
    for field_name in SECTION_STACK_FIELDS:
        if not hasattr(page, field_name):
            continue
        field_val = getattr(page, field_name)
        if not field_val:
            continue
        items = []
        head = None
        for block in field_val:
            block_data = _stream_to_plain(block.value)
            if not isinstance(block_data, dict):
                items.append(block_data)
                continue
            _normalize_page_links(block_data)
            item_key = SECTION_ITEM_LIST_KEYS.get(block.block_type)
            nested = block_data.get(item_key) if item_key else None
            if isinstance(nested, list):
                # First block's section-level fields become the section head.
                if head is None:
                    head = {
                        key: block_data.get(key, "")
                        for key in ("eyebrow", "title", "description")
                    }
                items.extend(nested)
            else:
                block_data["type"] = block.block_type
                items.append(block_data)
        if items:
            data[field_name] = items
            if head and any(v for v in head.values()):
                data[f"{field_name}_head"] = head

    return data


@require_GET
def page_data_api(request, slug):
    """GET /apis/pages/<slug>/ — full page data as JSON for the landing."""
    page = _get_wagtail_page(slug)
    if page is None:
        return JsonResponse({"error": "Page not found"}, status=404)
    try:
        return JsonResponse(_page_to_dict(page.specific))
    except Exception as exc:
        logger.exception("page_data_api error for slug=%s", slug)
        return JsonResponse({"error": str(exc)}, status=500)


@require_GET
def page_list_api(request):
    """GET /apis/pages/ — live landing pages (slug/title/type) for nav/discovery."""
    try:
        pages = [
            {
                "slug": p.slug,
                "title": p.title,
                "type": p.specific.__class__.__name__,
            }
            for p in Page.objects.live().exclude(depth=1).order_by("path")
        ]
    except Exception as exc:
        logger.exception("page_list_api error")
        return JsonResponse({"error": str(exc)}, status=500)
    return JsonResponse({"pages": pages})
