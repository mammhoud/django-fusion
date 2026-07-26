"""CMS Fusion page content API — Wagtail model-backed with STATIC_PAGES fallback."""

import logging
from pathlib import Path

from django.http import HttpResponse
from django.template import engines

from plugins.pages.content import STATIC_PAGES, normalize_slug
from www.api.data_adapter import bolt_view, fusion_response
from django_fusion.routes import fusion_json_response, FusionCodec

logger = logging.getLogger(__name__)


def _get_fusion_render_first_from_request(request) -> bool | None:
    h = request.headers.get("X-Fusion-Render-First")
    if h is not None: return h.strip().lower() == "true"
    q = request.GET.get("fusion_render_first")
    if q is not None: return q.strip().lower() == "true"
    return None


def _get_wagtail_page(slug: str):
    normalized = normalize_slug(slug)
    try:
        from plugins.pages.models import FusionHomePage, FusionContentPage
        if normalized == "home":
            return FusionHomePage.objects.live().first()
        return FusionContentPage.objects.live().filter(slug=normalized).first()
    except Exception:
        return None


def _wagtail_page_to_dict(page) -> dict:
    data = {
        "id": page.pk,
        "slug": page.slug if hasattr(page, "slug") and page.slug else "home",
        "title": page.title,
        "type": page.__class__.__name__,
        "layout": getattr(page, "effective_layout", "default"),
        "fusion_render_first": bool(getattr(page, "fusion_render_first", False)),
        "fragment_name": getattr(page, "effective_fragment_name", f"pages.{page.slug}"),
        "show_in_nav": bool(getattr(page, "show_in_nav", True)),
        "seo_title": getattr(page, "seo_title", "") or page.title,
        "search_description": getattr(page, "search_description", ""),
    }
    if hasattr(page, "hero_heading"):
        data["hero_heading"] = page.hero_heading
        data["hero_subheading"] = getattr(page, "hero_subheading", "")
    if hasattr(page, "body"):
        data["body"] = page.body
    if hasattr(page, "featured_image") and page.featured_image:
        try:
            data["featured_image_url"] = page.featured_image.get_rendition("fill-1200x400").url
        except Exception:
            pass
    if hasattr(page, "custom_css") and page.custom_css:
        data["custom_css"] = page.custom_css
    try:
        children = page.get_children().live().filter(show_in_nav=True)
        data["children"] = [{"id": c.pk, "slug": c.slug, "title": c.title} for c in children]
    except Exception:
        data["children"] = []
    return data


@bolt_view
def page_list(request):
    try:
        from plugins.pages.models import FusionHomePage, FusionContentPage
        pages = []
        home = FusionHomePage.objects.live().first()
        if home: pages.append(_wagtail_page_to_dict(home))
        for p in FusionContentPage.objects.live().filter(show_in_nav=True).order_by("title"):
            pages.append(_wagtail_page_to_dict(p))
        return {"pages": pages, "total": len(pages)}
    except Exception:
        return {"pages": [], "total": 0}


@bolt_view
def page_detail(request, slug):
    normalized = normalize_slug(slug)
    wagtail_page = _get_wagtail_page(slug)
    if wagtail_page is not None:
        return _wagtail_page_to_dict(wagtail_page)
    page = STATIC_PAGES.get(normalized)
    if page is None:
        return {"status": "error", "message": "Page not found"}, 404
    return page


def page_fragment(request, slug):
    try:
        normalized = normalize_slug(slug)
        wagtail_page = _get_wagtail_page(slug)
        if wagtail_page is not None:
            pointer = fusion_response(
                wagtail_page.effective_fragment_name, request,
                extra={"page_slug": normalized, "title": wagtail_page.title,
                       "layout": wagtail_page.effective_layout,
                       "fusion_render_first": wagtail_page.fusion_render_first})
            return fusion_json_response(data=pointer, status=200)
        if normalized not in STATIC_PAGES:
            return fusion_json_response({"error": "Page not found"}, status=404)
        pointer = fusion_response(
            f"pages.{normalized.replace('-','_')}", request,
            extra={"page_slug": normalized, "title": STATIC_PAGES[normalized]["title"]})
        return fusion_json_response(data=pointer, status=200)
    except Exception:
        logger.exception("page_fragment error slug=%s", slug)
        return fusion_json_response({"error": "Internal server error"}, status=500)


def page_data(request, slug):
    try:
        normalized = normalize_slug(slug)
        render_first = _get_fusion_render_first_from_request(request)
        wagtail_page = _get_wagtail_page(slug)
        if wagtail_page is not None:
            if render_first:
                from plugins.pages.components import FusionContentPageView, FusionHomePageView
                vc = FusionHomePageView if wagtail_page.__class__.__name__ == "FusionHomePage" else FusionContentPageView
                vi = vc()
                vi.request = request
                vi.kwargs = {"slug": getattr(wagtail_page, "slug", "home")}
                return vi.render_to_response(vi.get_context_data())
            d = _wagtail_page_to_dict(wagtail_page)
            return fusion_json_response(data={"slug": normalized, "title": wagtail_page.title, "encoded": FusionCodec.encode(d)})
        page = STATIC_PAGES.get(normalized)
        if page is None:
            return fusion_json_response({"error": "Page not found"}, status=404)
        if render_first:
            tp = Path(__file__).resolve().parent.parent.parent / "templates" / "pages" / "page.html"
            with open(tp) as f: ts = f.read()
            return HttpResponse(engines["django"].from_string(ts).render({"page": page}, request))
        return fusion_json_response(data={"slug": normalized, "title": page["title"], "encoded": FusionCodec.encode(page)})
    except Exception:
        logger.exception("page_data error slug=%s", slug)
        return fusion_json_response({"error": "Internal server error"}, status=500)
