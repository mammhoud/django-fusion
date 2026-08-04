"""
Landing page handlers — django-fusion views wired into Wagtail.

Why these exist
---------------
Wagtail normally serves each page through its own ``serve()``. By routing the
public landing URLs through ``PageHandler`` subclasses instead (see
``apps/handlers/urls.py`` — these sit *before* Wagtail's catch-all), every
request goes through django-fusion's unified render pipeline
(``FragmentHandlerMixin``):

    1. ``setup()`` — ``resolve_strategy()`` detects the request strategy:
       ``"fragment"`` (HTMX ``HX-Request`` header, or UnPoly) or ``"full"``
       (plain browser load).
    2. ``get_context_data()`` — loads the Wagtail page instance (via the
       tree, not the DB directly) + its StreamField content blocks.
    3. ``render_response()`` — the single render entry point:

       * ``strategy == "fragment"``  →  ``pages/fragments/page.html``
         (just the content region, swapped in by HTMX)
       * ``strategy == "full"``      →  the page's own template
         (``pages/home.html``, ``pages/about.html``, …) — a full document.

       The *same* Django templates the Astro frontend mirrors render as
       server-side HTML in both cases.

Mechanism (backend → HTML → HTMX/Alpine)
----------------------------------------
- Plain request  → full document (server-rendered HTML, header + footer).
- HTMX request   → fragment — just the content region, so the Astro/Alpine
  shell swaps it into the page without a full navigation.
- Alpine.js hydrates micro-interactions (accordion, toggle, count-up)
  declared as ``x-*`` attributes in those templates.

Skeleton loading
----------------
Both paths ship a default skeleton: the full-page templates include
``partials/skeleton.html`` (shown while the browser waits for first paint)
and HTMX requests show the ``htmx-indicator`` overlay while the fragment is
in flight. See ``partials/skeleton.html`` for the mechanism.

Why each view has a hard-coded ``template_name``
------------------------------------------------
``resolve_template_name()`` uses ``fragment_name`` (fragment strategy) or
``template_name`` (full strategy) — there is no Wagtail-derived fallback, so
each subclass pins the page template explicitly. This also keeps the
handlers independent of Wagtail's model→template mapping, mirroring the
Astro frontend's route→page map.
"""
from __future__ import annotations

from django.http import HttpRequest

from django_fusion.routes.pages.handler import PageHandler

from apps.pages.models import (
    AboutPage,
    CompanyPage,
    ContactPage,
    FaqPage,
    FeaturesPage,
    HomePage,
    PrivacyPage,
    ProductsPage,
    ProjectsPage,
    ServicesPage,
)

# The dotted fragment identifier → template ``pages/fragments/page.html``.
# Rendered for HTMX requests; the same content the Astro shell swaps in.
FRAGMENT_NAME = "pages.fragments.page"


class LandingPageView(PageHandler):
    """
    Base handler — renders a Wagtail landing page through the django-fusion
    fragment/layout pipeline.

    Subclass per page type with a ``template_name`` and ``_get_page()``.

    NOTE: do NOT override ``render_to_response`` here. django-fusion's
    ``_render_fragment_response`` / ``_render_layout_response`` already call
    ``render_to_response``; overriding it to call ``render_response`` again
    would recurse infinitely. ``ComponentViews.render_to_response`` (the
    base) adds the HTMX headers (``HX-Reswap`` / ``HX-Retarget``) instead.
    """

    model = HomePage  # concrete fallback for the tree lookup below
    template_name = "pages/base.html"  # overridden per subclass
    fragment_name = FRAGMENT_NAME

    def get_context_data(self, request: HttpRequest | None = None, **kwargs) -> dict:
        """Attach the Wagtail page instance to the template context."""
        context = super().get_context_data(request=request, **kwargs)
        page = self._get_page()
        context.update(
            {
                "page": page,
                "content": page,
                "site_name": "Fusion CMS",
            }
        )
        return context

    def _get_page(self) -> HomePage:
        """Resolve the page instance from the request path via the Wagtail tree."""
        path = self.request.path.strip("/") or "home"
        from wagtail.models import Page

        page = Page.objects.filter(url_path=f"/{path}/").first()
        if page is None:
            return self.model.objects.first()  # fallback: home
        return page.specific


# ── Per-page handlers (one class per Wagtail model) ─────────────────
# Each mirrors the Astro frontend route: `/` home, `/about`, `/company`,
# `/services`, `/products`, `/contact`, `/faq`, `/privacy`.

class LandingHomeView(LandingPageView):
    """Home page — full document or ``#main`` fragment for HTMX."""

    template_name = "pages/home.html"

    def _get_page(self) -> HomePage:
        return HomePage.objects.first()


class AboutPageView(LandingPageView):
    template_name = "pages/about.html"

    def _get_page(self) -> AboutPage:
        return AboutPage.objects.first()


class CompanyPageView(LandingPageView):
    template_name = "pages/company.html"

    def _get_page(self) -> CompanyPage:
        return CompanyPage.objects.first()


class ServicesPageView(LandingPageView):
    template_name = "pages/services.html"

    def _get_page(self) -> ServicesPage:
        return ServicesPage.objects.first()


class ProductsPageView(LandingPageView):
    template_name = "pages/products.html"

    def _get_page(self) -> ProductsPage:
        return ProductsPage.objects.first()


class FeaturesPageView(LandingPageView):
    template_name = "pages/features.html"

    def _get_page(self) -> FeaturesPage:
        return FeaturesPage.objects.first()


class ProjectsPageView(LandingPageView):
    template_name = "pages/projects.html"

    def _get_page(self) -> ProjectsPage:
        return ProjectsPage.objects.first()


class ContactPageView(LandingPageView):
    template_name = "pages/contact.html"

    def _get_page(self) -> ContactPage:
        return ContactPage.objects.first()


class FaqPageView(LandingPageView):
    template_name = "pages/faq.html"

    def _get_page(self) -> FaqPage:
        return FaqPage.objects.first()


class PrivacyPageView(LandingPageView):
    template_name = "pages/privacy.html"

    def _get_page(self) -> PrivacyPage:
        return PrivacyPage.objects.first()
