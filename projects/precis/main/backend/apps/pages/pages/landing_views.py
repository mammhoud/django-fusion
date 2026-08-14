"""
Fusion Landing Views — server-side rendered pages with django-fusion + HTMX.

Provides:
    - FusionLandingView: base view for all landing pages with
      fusion_render_first=True (Django renders full HTML, Next.js hydrates).
    - HTMX fragment endpoints for dynamic interactions (forms, search, pagination).

Wire in Application.viewsets or standalone urls.py:

    from apps.pages.pages.landing_views import HomePageView
    # Or: path('', HomePageView.as_view(), name='home'),
"""

from __future__ import annotations

import logging
from typing import Any

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views import View
from django_fusion.plugins.htmx.core import is_htmx_request, trigger_client_event
from django_fusion.routes.rendering.renderers import fusion_json_response

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# Fusion Landing View — server-rendered first
# ═══════════════════════════════════════════════════════════════════

class FusionLandingView(View):
    """Base view for fusion landing pages.

    Renders the full page server-side (django-fusion templates) so that
    the Next.js FusionProxy receives pre-built HTML on first load.
    HTMX requests get fragment-only responses.

    Subclasses set:
        - template_name: Django template path
        - page_slug: Wagtail page slug to fetch
        - fragment_name: dotted fragment identifier
        - layout: 'full_width' | 'sidebar' | 'default' | 'blank'
    """

    template_name: str = "pages/fusion_landing.html"
    fragment_template_name: str | None = None
    page_slug: str = "home"
    fragment_name: str = "pages.home"
    layout: str = "full_width"
    title: str = "LMS Fusion"
    fusion_render_first: bool = True

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        context = self.get_context_data(request)

        # HTMX fragment request → return only the content block. The page
        # template (e.g. ``pages/home/main.html``) extends the site skeleton,
        # so rendering it for an HX request would embed the full document
        # (header/footer) inside a LiveFragment region — the same page
        # rendering twice, nested. Fragment requests render the matching
        # ``fragment.html`` (content-only) when one is configured, otherwise
        # the content template with the layout stripped.
        if is_htmx_request(request):
            fragment = self.fragment_template_name
            if fragment:
                return render(request, fragment, context)
            return render(request, self.template_name, context)

        # Full page render → server-side HTML for the FusionProxy
        return render(request, self.template_name, context)

    def get_context_data(self, request: HttpRequest) -> dict[str, Any]:
        """Build context with page data, site settings, and navigation."""
        page = self._get_wagtail_page()
        blocks = self._get_page_blocks(page)
        site_context = self._get_site_context(request)

        return {
            "request": request,
            "page": page,
            "page_obj": page,
            "title": self.title,
            "page_slug": self.page_slug,
            "layout": getattr(page, "layout", self.layout) if page else self.layout,
            "fusion_render_first": self.fusion_render_first,
            "fragment_name": self.fragment_name,
            "blocks": blocks,
            "site_settings": site_context.get("site_settings", {}),
            "social_links": site_context.get("social_links", []),
            "nav_items": site_context.get("nav_items", []),
            "footer": site_context.get("footer", {}),
        }

    def _get_wagtail_page(self):
        """Retrieve the Wagtail page for this view."""
        try:
            from wagtail.models import Page
            return Page.objects.live().filter(slug=self.page_slug).first()
        except Exception:
            return None

    def _get_page_blocks(self, page) -> list[dict]:
        """Extract StreamField blocks from a Wagtail page."""
        if page is None or not hasattr(page, "body"):
            return []
        try:
            from apps.content.models.pages.dynamic import page_to_dict
            return page_to_dict(page).get("blocks", [])
        except Exception:
            return []

    def _get_site_context(self, request) -> dict:
        """Get site settings + nav from Wagtail."""
        try:
            from apps.content.models.settings import SiteSettings, SocialLink

            settings = SiteSettings.for_request(request)
            socials = list(SocialLink.objects.filter(is_active=True))
            return {
                "site_settings": settings,
                "social_links": socials,
                "nav_items": self._get_nav_items(),
                "footer": {
                    "description": settings.footer_description,
                    "copyright": settings.footer_copyright,
                },
            }
        except Exception:
            return {}

    def _get_nav_items(self) -> list[dict]:
        """Get navigation tree for header."""
        try:
            from wagtail.models import Page
            return [
                {"title": p.title, "slug": p.slug, "url": f"/{p.slug}/"}
                for p in Page.objects.live().filter(depth__gt=1, show_in_nav=True)
            ]
        except Exception:
            return []


# ═══════════════════════════════════════════════════════════════════
# Concrete Landing Views
# ═══════════════════════════════════════════════════════════════════

class HomePageView(FusionLandingView):
    """Home page — hero, stats, featured sections, CTA."""
    template_name = "home/main.html"
    fragment_template_name = "home/fragment.html"
    page_slug = "home"
    fragment_name = "pages.home"
    title = "LMS Fusion — Modern Content Platform"


class AboutPageView(FusionLandingView):
    """About us page."""
    template_name = "about/main.html"
    fragment_template_name = "about/fragment.html"
    page_slug = "about-us"
    fragment_name = "pages.about"
    title = "About Us"


class ServicesPageView(FusionLandingView):
    """Services page."""
    template_name = "services/main.html"
    fragment_template_name = "services/fragment.html"
    page_slug = "services"
    fragment_name = "pages.services"
    title = "Our Services"


class ContactPageView(FusionLandingView):
    """Contact page."""
    template_name = "contact/main.html"
    fragment_template_name = "contact/fragment.html"
    page_slug = "contact"
    fragment_name = "pages.contact"
    title = "Contact Us"


class TeamPageView(FusionLandingView):
    """Team page."""
    template_name = "team/main.html"
    fragment_template_name = "team/fragment.html"
    page_slug = "team"
    fragment_name = "pages.team"
    title = "Our Team"


class PricingPageView(FusionLandingView):
    """Pricing page."""
    template_name = "pages/fusion_content.html"
    page_slug = "pricing"
    fragment_name = "pages.pricing"
    title = "Pricing Plans"


class FaqPageView(FusionLandingView):
    """FAQ page."""
    template_name = "pages/fusion_content.html"
    page_slug = "faq"
    fragment_name = "pages.faq"
    title = "Frequently Asked Questions"


class TestimonialsPageView(FusionLandingView):
    """Testimonials page."""
    template_name = "pages/fusion_content.html"
    page_slug = "testimonials"
    fragment_name = "pages.testimonials"
    title = "What Our Clients Say"


# ═══════════════════════════════════════════════════════════════════
# HTMX Fragment Endpoints
# ═══════════════════════════════════════════════════════════════════

class HtmxNewsletterView(View):
    """POST /htmx/newsletter/ — subscribe to newsletter."""

    def post(self, request: HttpRequest) -> HttpResponse:
        email = request.POST.get("email", "").strip()
        if not email:
            return HttpResponse(
                '<p class="text-red-500">Please enter a valid email.</p>',
                status=400,
            )

        # Future: save to EmailSubscriber model or Mailchimp
        logger.info("Newsletter signup: %s", email)
        response = HttpResponse(
            '<p class="text-green-600 font-medium">Thanks for subscribing!</p>'
        )
        trigger_client_event(response, "newsletter-subscribed", {"email": email})
        return response


class HtmxContactView(View):
    """POST /htmx/contact/ — submit contact form."""

    def post(self, request: HttpRequest) -> HttpResponse:
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()

        if not all([name, email, message]):
            return HttpResponse(
                '<p class="text-red-500">All fields are required.</p>',
                status=400,
            )

        # Future: save to ContactSubmission model
        logger.info("Contact form: %s <%s> — %s", name, email, message[:80])
        response = HttpResponse(
            '<div class="p-4 bg-green-50 rounded-lg text-green-700">'
            '<h3 class="font-bold">Message Sent!</h3>'
            '<p>We\'ll get back to you within 24 hours.</p>'
            '</div>'
        )
        trigger_client_event(response, "contact-submitted", {"name": name})
        return response


def htmx_search(request: HttpRequest) -> JsonResponse:
    """GET /htmx/search/?q=... — live search results fragment."""
    import json
    q = request.GET.get("q", "").strip()
    if len(q) < 2:
        return JsonResponse({"results": []})

    try:
        from wagtail.models import Page
        results = [
            {"title": p.title, "url": f"/{p.slug}/", "type": "page"}
            for p in Page.objects.live().filter(title__icontains=q)[:5]
        ]
    except Exception:
        results = []

    html = '<ul class="fusion-search-results">' + "".join(
        f'<li><a href="{r["url"]}">{r["title"]}</a></li>' for r in results
    ) + '</ul>' if results else '<p class="text-gray-500 p-2">No results found.</p>'

    return HttpResponse(html)
