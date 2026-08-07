"""
Landing-fusion routing — django-fusion Application for the marketing pages.

The public marketing surface is registered as a single ``Application`` with
one ``menu_path`` entry per page (name / icon / title metadata), reusing the
existing ``PageHandler`` subclasses so the enhanced dual-mode pipeline stays
intact:

* plain browser load   → full document (``strategy == "full"``)
* HTMX request         → content-region fragment (``strategy == "fragment"``)

The Application adds the fusion-routing layer on top: namespaced routes,
``application_context()`` shared site data, and ``menu_items()`` menu
integration (every ``menu_path`` pattern becomes a menu item with its icon +
title). ``apps/handlers/urls.py`` remains the flat fallback reference; this
module is the canonical registry consumed by the root URL conf.
"""
from __future__ import annotations

from django.urls import path
from django.views.generic import RedirectView

from django_fusion.routes.core.base import menu_path
from django_fusion.routes.core.sites import Application

from apps.handlers import views
from apps.pages.api import get_effective_render_first


class LandingPagesApplication(Application):
    """Marketing pages — every public route, declared once with menu metadata.

    Mounted at the site root (``path("", landing_pages_application.url_pattern)``)
    with namespace ``pages``. The ``PageHandler`` subclasses below keep the
    fragment/full dual-mode renderer; the menu metadata feeds django-fusion's
    ``menu_items()`` and any side-nav renderer.
    """

    title = "Pages"
    icon = "web"
    app_name = "pages"

    urlpatterns = [
        menu_path("", views.LandingHomeView.as_view(), name="home", icon="home", title="Home"),
        menu_path("about/", views.AboutPageView.as_view(), name="about", icon="info", title="About"),
        menu_path("about/team/", views.TeamPageView.as_view(), name="about_team", icon="group", title="Team"),
        menu_path("about/startup/", views.StartupPageView.as_view(), name="about_startup", icon="rocket_launch", title="Startup"),
        menu_path("about/founder/", views.FounderPageView.as_view(), name="about_founder", icon="person", title="Founder"),
        # Company merged into About — legacy URL redirects permanently.
        path("company/", RedirectView.as_view(url="/about/", permanent=True), name="company_redirect"),
        # Projects merged into Products — the catalog carries the repo project
        # grid; the legacy URL redirects permanently.
        path("projects/", RedirectView.as_view(url="/products/", permanent=True), name="projects_redirect"),
        menu_path("services/", views.ServicesPageView.as_view(), name="services", icon="construction", title="Services"),
        path("services/phases/<slug:slug>/prompts/<slug:prompt_slug>/", views.PromptPageView.as_view(), name="service_prompt"),
        path("services/phases/<slug:slug>/", views.PhasePageView.as_view(), name="service_phase"),
        menu_path("pricing/", views.PricingPageView.as_view(), name="pricing", icon="payments", title="Pricing"),
        menu_path("blog/", views.BlogPageView.as_view(), name="blog", icon="edit_note", title="Blog"),
        path("blog/<slug:slug>/", views.BlogPostPageView.as_view(), name="blog_post"),
        menu_path("products/", views.ProductsPageView.as_view(), name="products", icon="inventory_2", title="Products"),
        path("products/<slug:slug>/", views.ProductPageView.as_view(), name="product"),
        path("products/<slug:slug>/preview/<slug:edition>/", views.ProductPreviewView.as_view(), name="product_preview"),
        menu_path("brand/", views.BrandPageView.as_view(), name="brand", icon="palette", title="Brand"),
        menu_path("features/", views.FeaturesPageView.as_view(), name="features", icon="tune", title="Features"),
        menu_path("contact/", views.ContactPageView.as_view(), name="contact", icon="mail", title="Contact"),
        menu_path("faq/", views.FaqPageView.as_view(), name="faq", icon="help", title="FAQ"),
        menu_path("privacy/", views.PrivacyPageView.as_view(), name="privacy", icon="policy", title="Privacy"),
    ]

    def application_context(self, request) -> dict:
        """Shared site data for routed views and the fusion menu system.

        Mirrors the context the ``PageHandler`` views attach themselves, so a
        routed child view (or any renderer consuming ``application_context``)
        gets the same site name, navigation, and render-mode contract.
        """
        from apps.core.site import landing_site

        render_first = get_effective_render_first(request)
        return {
            "site_name": "Structa Cloud",
            "nav_items": landing_site.get_navigation_context(request),
            "fusion_render_first": render_first,
            "fusion_render_mode": "fusion-render" if render_first else "data-api",
        }


# Singleton — mounted once from the root URL conf.
landing_pages_application = LandingPagesApplication()
