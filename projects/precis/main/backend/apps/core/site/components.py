"""FragmentComponent subclasses for cross-cutting HTMX fragment endpoints.

App-specific fragments (course grid, blog list, dashboard KPIs) now live
in their related apps:

  - CourseGridFragment, CourseFiltersFragment, DashboardKPIsFragment
    → apps.learning.components
  - BlogPostListFragment
    → apps.pages.blog.components

Only truly cross-cutting fragments stay here:
  - CMSHeadContentFragment (Wagtail page metadata)
  - CheckoutFragment (stub for future payment integration)
"""

from __future__ import annotations

import logging

from django.http import HttpRequest
from django.shortcuts import render

from django_fusion.routes.components.fragments import FragmentComponent
from django_fusion.routes.components.dual_mode import FusionDualModeMixin

logger = logging.getLogger(__name__)


# ─── CMS head content (FusionAssets replacement) ───────────────────


class CMSHeadContentFragment(FusionDualModeMixin, FragmentComponent):
    """GET /core/cms/head-content/ — CMS-injected <head> content.

    Returns custom CSS, JS, or meta tags from Wagtail pages.
    Registered in ``CoreApp`` under the ``/core/`` prefix.
    """

    route_name = "cms-head-content"
    route_path = "cms/head-content/"
    htmx_only = True
    # Head content is always HTML — force render-first regardless of session.
    force_render_first = True

    def get_fragment_context(self, **kwargs):
        context = super().get_fragment_context(**kwargs)
        context["head_html"] = self.get_fragment_data().get("head_html", "")
        return context

    def get_fragment_data(self) -> dict:
        head_html = ""

        try:
            from wagtail.models import Page, Site as WagtailSite

            site = WagtailSite.find_for_request(self.request)
            if site and site.root_page:
                custom_css = getattr(site.root_page, "custom_css", "")
                if custom_css:
                    head_html += f"<style>{custom_css}</style>"

                ga_code = getattr(site.root_page, "ga_tracking_code", "")
                if ga_code:
                    head_html += ga_code
        except Exception:
            pass

        return {"head_html": head_html}

    def render_fragment_response(self, context):
        """Return raw HTML content (no template wrapper)."""
        from django.http import HttpResponse
        return HttpResponse(
            context.get("head_html", ""),
            content_type="text/html",
            headers={"HX-Partial": "true"},
        )


# ─── Checkout fragment (stub) ──────────────────────────────────────


class CheckoutFragment(FusionDualModeMixin, FragmentComponent):
    """POST /core/checkout/ — Process checkout and return result fragment.

    This is a stub for future Stripe integration.
    Registered in ``CoreApp`` under the ``/core/`` prefix.
    """

    route_name = "checkout"
    route_path = "checkout/"
    fragment_name = "htmx.checkout_result"
    htmx_only = True

    def post(self, request: HttpRequest, *args, **kwargs):
        try:
            email = request.POST.get("email", "").strip()
            if not email:
                return self.render_error("htmx/checkout_result.html", {
                    "status": "error",
                    "message": "Email is required.",
                })

            # TODO: Actual Stripe payment intent creation
            # from apps.learning.views import StripeInitView

            response = render(request, "htmx/checkout_result.html", {
                "status": "success",
                "message": "Order placed successfully! Check your email for confirmation.",
                "email": email,
            })
            response["HX-Trigger"] = "checkout-complete"
            response["HX-Partial"] = "true"
            return response

        except Exception:
            logger.exception("HTMX checkout error")
            return self.render_error("htmx/checkout_result.html", {
                "status": "error",
                "message": "An unexpected error occurred. Please try again.",
            })