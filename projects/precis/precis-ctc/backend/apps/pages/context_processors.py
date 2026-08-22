"""Template context processor for SEO metadata.

The Wagtail ``before_serve_page`` hook (apps/pages/pages/wagtail_hooks.py)
resolves the site's ``SiteSettings.get_seo_context()`` once per request and
stores it on ``request.seo_context``. This processor exposes that dict to
every template so ``base.html`` renders meta description/keywords/OG/Twitter/
robots/canonical tags from Wagtail-managed settings instead of hardcoded
strings.

The processor is self-sufficient: when the hook did not run (for example when
a page is rendered through ``Page.serve()`` in tests or from non-Wagtail
views), it resolves ``SiteSettings`` directly and merges defaults, so every
template always receives a dict with all SEO keys present — never an empty
dict that would make ``seo_context.meta_description`` raise
``VariableDoesNotExist`` during rendering.
"""


def _seo_defaults():
    return {
        "meta_description": "",
        "meta_keywords": "",
        "meta_author": "",
        "robots": "index, follow",
        "og_type": "website",
        "og_image_url": None,
        "twitter_handle": "",
        "canonical_url": "",
    }


def seo_context_processor(request):
    seo = getattr(request, "seo_context", None)
    if seo:
        return {"seo_context": seo}

    defaults = _seo_defaults()
    try:
        from apps.content.models.settings import SiteSettings

        settings_obj = SiteSettings.for_request(request)
        if settings_obj is None:
            settings_obj = SiteSettings.load()
        if settings_obj:
            ctx = settings_obj.get_seo_context()
            defaults.update({k: v for k, v in ctx.items() if v})
    except Exception:
        # Never break page rendering over SEO metadata.
        pass
    return {"seo_context": defaults}
