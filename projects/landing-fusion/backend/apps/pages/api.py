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

import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
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
        "nav_cta_url": getattr(settings, "nav_cta_url", "/#cta") if settings else "/#cta",
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
        # Remove the show_in_nav key from the response
        for item in nav_items:
            item.pop("show_in_nav", None)
    except Exception:
        nav_items = _navigation_from_wagtail_tree(request)

    return JsonResponse({"nav_items": nav_items})


def _navigation_from_wagtail_tree(request):
    """Fallback: walk the Wagtail page tree for navigation items."""
    nav_items = []
    try:
        from apps.pages.models import HomePage
        home = HomePage.objects.first()
        if home:
            nav_items.append({"label": home.title, "href": "/", "active": request.path == "/"})
            for child in home.get_children().live().order_by("title"):
                show = getattr(child.specific, "show_in_nav", True)
                if not show:
                    continue
                nav_items.append({
                    "label": child.title,
                    "href": f"/{child.slug}/",
                    "active": request.path.startswith(f"/{child.slug}/"),
                })
    except Exception:
        pass

    if not nav_items:
        nav_items = [
            {"label": "Home", "href": "/", "active": request.path == "/"},
            {"label": "Products", "href": "/products/", "active": False},
            {"label": "Projects", "href": "/projects/", "active": False},
            {"label": "Features", "href": "/features/", "active": False},
            {"label": "About", "href": "/about/", "active": False},
            {"label": "FAQ", "href": "/faq/", "active": False},
            {"label": "Contact", "href": "/contact/", "active": False},
        ]

    return nav_items


# ── Contact ─────────────────────────────────────────────────────────────────

def contact_api(request):
    """GET /apis/contact/ — contact methods from Wagtail ContactPage."""
    try:
        from apps.pages.models import ContactPage
        page = ContactPage.objects.first()
        if page and page.contact:
            for block in page.contact:
                if block.block_type == "contact":
                    methods = []
                    for method in block.value.get("methods", []):
                        methods.append({
                            "type": method.get("method_type", "email"),
                            "label": method.get("label", ""),
                            "value": method.get("value", ""),
                            "href": method.get("href", ""),
                        })
                    return JsonResponse({
                        "title": block.value.get("title", "Get in touch"),
                        "description": block.value.get("description", ""),
                        "methods": methods,
                        "form_title": block.value.get("form_title", "Send us a message"),
                        "form_description": block.value.get("form_description", ""),
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
    })


# ── Page Data ────────────────────────────────────────────────────────────────

import wagtail.blocks


def _stream_to_plain(value):
    """Recursively convert Wagtail StreamField values to plain JSON-serializable
    Python dicts/lists. Handles StructValue and ListValue from wagtail.blocks."""
    if hasattr(value, 'items') and hasattr(value, 'get'):
        # StructValue or dict-like
        return {k: _stream_to_plain(v) for k, v in value.items()}
    if hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
        # ListValue or list-like
        return [_stream_to_plain(v) for v in value]
    return value


def _get_wagtail_page(slug: str):
    """Try to retrieve a live Wagtail page by slug."""
    normalized = slug.strip("/") or "home"
    try:
        return Page.objects.live().filter(slug=normalized).first()
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
}


def _page_to_dict(page) -> dict:
    """Serialize a Wagtail page to a frontend-consumable dict."""
    from apps.pages.models import AboutPage, ProductsPage, FeaturesPage, ProjectsPage
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

    # Hero
    if hasattr(page, "hero") and page.hero:
        for block in page.hero:
            if block.block_type == "hero":
                hero_val = block.value
                data["hero"] = {
                    "badge": hero_val.get("badge", ""),
                    "title": hero_val.get("title", page.title),
                    "subtitle": hero_val.get("subtitle", ""),
                    "primary_cta": hero_val.get("primary_cta", None),
                    "secondary_cta": hero_val.get("secondary_cta", None),
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
                    "primary_cta": cta_val.get("primary_cta", None),
                    "secondary_cta": cta_val.get("secondary_cta", None),
                }
                break

    # Body (RichText)
    if hasattr(page, "body") and page.body:
        data["body"] = str(page.body)

    # Blog post meta (BlogPostPage) — category, date, read time, excerpt.
    # The date is serialized as an ISO string so the frontend renders it
    # without a client-side date dependency.
    for field_name in ("category", "read_time", "excerpt"):
        value = getattr(page, field_name, "")
        if value:
            data[field_name] = str(value)
    if getattr(page, "post_date", None):
        data["post_date"] = page.post_date.isoformat()

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

    # Product listing (ProductsPage) — one card per live ProductPage child.
    if hasattr(page, "get_product_cards") and page.get_product_cards():
        data["products"] = page.get_product_cards()

    # Contact section
    if hasattr(page, "contact") and page.contact:
        contact_blocks = []
        for block in page.contact:
            block_data = _stream_to_plain(block.value)
            if isinstance(block_data, dict):
                block_data["type"] = block.block_type
            contact_blocks.append(block_data)
        if contact_blocks:
            data["contact"] = contact_blocks

    return data


def page_data_api(request, slug):
    """GET /apis/pages/<slug>/ — full page data as JSON.

    Returns all StreamField content for the requested Wagtail page.
    Used by Astro pages to render server-driven content.
    """
    page = _get_wagtail_page(slug)
    if page is None:
        return JsonResponse({"error": "Page not found"}, status=404)

    try:
        data = _page_to_dict(page.specific)
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


def page_list_api(request):
    """GET /apis/pages/ — list of all published pages."""
    try:
        pages = []
        for p in Page.objects.live().filter(depth__gt=1).order_by("title"):
            pages.append({
                "id": p.pk,
                "slug": p.slug,
                "title": p.title,
                "type": p.specific_class.__name__,
            })
        return JsonResponse({"pages": pages, "total": len(pages)})
    except Exception:
        return JsonResponse({"pages": [], "total": 0})


# ── Newsletter Subscribe ────────────────────────────────────────────────────

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
    and JSON for plain API consumers. In production this would queue an
    email/CRM notification.
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

    logger.info("contact_submit: %s <%s> %s", name, email, subject or "(no subject)")

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

    Accepts form-encoded or JSON body with ``email``. Returns an HTML
    fragment (for HTMX swap into ``#newsletter-feedback``) on success
    or failure.

    In production this would connect to Mailchimp/SendGrid. For now it
    validates and echoes a confirmation.
    """
    import json
    import re

    EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    # Parse the email from the request body
    email = ""
    if request.method == "POST":
        if request.content_type == "application/json":
            try:
                body = json.loads(request.body.decode("utf-8"))
                email = body.get("email", "").strip()
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass
        else:
            email = request.POST.get("email", "").strip()

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

    # Success — in production, queue a Mailchimp/SendGrid API call here.
    logger.info("newsletter_subscribe: %s", email)

    # Check if this is an HTMX request — return HTML fragment for swap.
    if request.headers.get("HX-Request"):
        from django.http import HttpResponse
        return HttpResponse(
            '<div class="live-fragment__fallback" style="border-color:hsl(var(--fu-live))">'
            '<p class="text-fu-live font-medium">✓ Subscribed!</p>'
            '<p class="text-sm text-fu-muted mt-1">We\'ll send updates to '
            f'<code class="font-mono text-fu-ink">{email}</code>.</p>'
            '</div>'
        )

    return JsonResponse({
        "success": True,
        "message": f"Subscribed! We'll send updates to {email}.",
    })
