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

from django.http import Http404, HttpRequest

from django_fusion.routes.pages.handler import PageHandler

from apps.pages.api import (
    _apply_page_translation,
    _page_to_dict,
    _requested_content_language,
    get_effective_render_first,
)

from apps.pages.models import (
    AboutPage,
    BlogPage,
    BlogPostPage,
    BrandPage,
    ContactPage,
    FaqPage,
    FeaturesPage,
    FounderPage,
    HomePage,
    PricingPage,
    PrivacyPage,
    PhasePage,
    ProductPage,
    PromptPage,
    ProductsPage,
    ServicesPage,
    StartupPage,
    TeamPage,
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
        """Attach the Wagtail page instance + fusion render mode to the context."""
        context = super().get_context_data(request=request, **kwargs)
        page = self._get_page()
        language = _requested_content_language(self.request)
        serialized = _apply_page_translation(page, _page_to_dict(page), language)
        context.update(
            {
                "page": page,
                "content": page,
                "localized_content": serialized,
                "content_language": language,
                "site_name": "Structa Cloud",
                # Main nav (show_in_nav items only) — single source of truth is
                # LandingSite.NAV_ITEMS; the header partial renders from this.
                "nav_items": self._get_nav_items(),
                # Breadcrumb trail for subpages (team/founder/startup, phases +
                # prompts, product detail/preview, blog posts). Rendered by
                # pages/partials/breadcrumbs.html at the top of the shared
                # content region — empty for top-level pages.
                "breadcrumbs": self._get_breadcrumbs(page),
                # django-fusion settings config — which content-delivery option
                # this request is served under (see settings.FUSION_RENDER_FIRST_DEFAULT
                # and the X-Fusion-Render-First per-request override).
                "fusion_render_first": get_effective_render_first(self.request),
                "fusion_render_mode": "fusion-render"
                if get_effective_render_first(self.request)
                else "data-api",
            }
        )
        return context

    def _get_breadcrumbs(self, page) -> list[dict]:
        """The in-page trail for subpages — a list of ancestor links, newest last.

        Top-level pages (home, about, services, products, …) return an empty
        list so the breadcrumb partial renders nothing there. The final crumb
        (the current page title) is added by the partial itself.
        """
        page_name = page.__class__.__name__
        if page_name in ("TeamPage", "FounderPage", "StartupPage"):
            return [{"label": "Home", "href": "/"}, {"label": "About", "href": "/about/"}]
        if page_name == "PhasePage":
            return [{"label": "Home", "href": "/"}, {"label": "Services", "href": "/services/"}]
        if page_name == "PromptPage":
            phase = getattr(page, "get_parent", lambda: None)()
            phase_href = f"/services/phases/{phase.slug}/" if phase is not None else "/services/"
            return [
                {"label": "Home", "href": "/"},
                {"label": "Services", "href": "/services/"},
                {"label": phase.title, "href": phase_href},
            ]
        if page_name == "ProductPage":
            return [{"label": "Home", "href": "/"}, {"label": "Products", "href": "/products/"}]
        if page_name == "BlogPostPage":
            return [{"label": "Home", "href": "/"}, {"label": "Blog", "href": "/blog/"}]
        return []

    def _get_nav_items(self) -> list[dict]:
        """Return the main navigation items (show_in_nav only), for the header partial."""
        from apps.core.site import landing_site

        items = []
        for item in landing_site.get_navigation_context(self.request):
            if not item.get("show_in_nav", True):
                continue
            clean = {k: v for k, v in item.items() if k != "show_in_nav"}
            clean["children"] = clean.get("children") or []
            items.append(clean)
        return items

    def _get_page(self) -> HomePage:
        """Resolve the page instance from the request path via the Wagtail tree."""
        path = self.request.path.strip("/") or "home"
        from wagtail.models import Page

        page = Page.objects.filter(url_path=f"/{path}/").first()
        if page is None:
            return self.model.objects.first()  # fallback: home
        return page.specific


# ── Per-page handlers (one class per Wagtail model) ─────────────────
# Each mirrors the Astro frontend route: `/` home, `/about`, `/services`,
# `/products` (+ `/products/<slug>/` product pages), `/contact`, `/faq`,
# `/privacy`.

class LandingHomeView(LandingPageView):
    """Home page — full document or ``#main`` fragment for HTMX."""

    template_name = "pages/home.html"

    def _get_page(self) -> HomePage:
        return HomePage.objects.first()


class AboutPageView(LandingPageView):
    template_name = "pages/about.html"

    def _get_page(self) -> AboutPage:
        return AboutPage.objects.first()


class ServicesPageView(LandingPageView):
    template_name = "pages/services.html"

    def _get_page(self) -> ServicesPage:
        return ServicesPage.objects.first()


class PricingPageView(LandingPageView):
    template_name = "pages/pricing.html"

    def _get_page(self) -> PricingPage:
        return PricingPage.objects.first()


class BlogPageView(LandingPageView):
    template_name = "pages/blog.html"

    def _get_page(self) -> BlogPage:
        return BlogPage.objects.first()


class BlogPostPageView(LandingPageView):
    """A single blog post — resolved by slug from the Blog index children.

    Post pages are children of the Blog page, so they are looked up from the
    ``<slug>`` URL kwarg (their full url_path is ``/blog/<slug>/``). Unknown
    slugs are a 404 — never a silent fallback to another post.
    """

    model = BlogPostPage
    template_name = "pages/blog_post.html"

    def _get_page(self) -> BlogPostPage:
        """Resolve the post page by slug — unknown slugs are 404, never a fallback."""
        slug = self.kwargs.get("slug")
        page = BlogPostPage.objects.filter(slug=slug).first() if slug else None
        if page is None:
            raise Http404(f"No blog post with slug {slug!r}")
        return page


class ProductsPageView(LandingPageView):
    template_name = "pages/products.html"

    def _get_page(self) -> ProductsPage:
        return ProductsPage.objects.first()


class ProductPageView(LandingPageView):
    """A single product page — resolved by slug from the Products page children.

    Product pages are children of the Products page, so they are looked up
    from the ``<slug>`` URL kwarg rather than the generic url_path resolver
    (their full url_path is ``/home/products/<slug>/``).
    """

    model = ProductPage
    template_name = "pages/product.html"

    def _get_page(self) -> ProductPage:
        """Resolve the product page by slug — unknown slugs are 404, never a fallback."""
        slug = self.kwargs.get("slug")
        page = ProductPage.objects.filter(slug=slug).first() if slug else None
        if page is None:
            raise Http404(f"No product page with slug {slug!r}")
        return page


class ProductPreviewView(LandingPageView):
    """Per-edition preview page — /products/<slug>/preview/<edition>/.

    A flexible subpage that previews ONE edition of a product (e.g. the
    Formints Community terminal, the vResume resume mock, the Loop site
    builder). Renders the product lockup, the edition's price/tagline/
    features, and a stylized product mock keyed by product slug. Unknown
    slugs or edition names are 404s.
    """

    model = ProductPage
    template_name = "pages/product_preview.html"

    def _get_page(self) -> ProductPage:
        """Resolve the product page by slug — unknown slugs are 404."""
        slug = self.kwargs.get("slug")
        page = ProductPage.objects.filter(slug=slug).first() if slug else None
        if page is None:
            raise Http404(f"No product page with slug {slug!r}")
        return page

    def get_context_data(self, request: HttpRequest | None = None, **kwargs) -> dict:
        context = super().get_context_data(request=request, **kwargs)
        page = context.get("page") or self._get_page()
        edition_name = self.kwargs.get("edition", "")
        edition = page.get_edition(edition_name)
        if edition is None:
            raise Http404(f"No edition named {edition_name!r} on {page.slug}")
        # Other editions of the same product — links for switching previews.
        context["preview_edition"] = edition
        from django.utils.text import slugify

        context["preview_slug"] = slugify(edition_name)
        context["preview_others"] = [
            {"name": e.get("name", ""), "slug": slugify(str(e.get("name", "")))}
            for e in page.get_editions()
            if slugify(str(e.get("name", ""))) != slugify(edition_name)
        ]
        # Preview trail: Home → Products → <product> → <edition> (the edition
        # name is rendered as the current crumb via breadcrumb_current).
        context["breadcrumbs"] = [
            {"label": "Home", "href": "/"},
            {"label": "Products", "href": "/products/"},
            {"label": page.title, "href": f"/products/{page.slug}/"},
        ]
        context["breadcrumb_current"] = edition.get("name", edition_name)
        return context


class BrandPageView(LandingPageView):
    """Brand kit page — the product family's identity system.

    Renders ``pages/brand.html``: one identity board per live product
    (lockup, construction, essence, colour system, voice), driven by
    ``get_brand_boards()`` (BRAND_SPEC + the seeded product cards). The page
    is a real Wagtail model (``BrandPage``) whose ``display_mode`` field
    decides page / modal / both surfacing.
    """

    model = BrandPage
    template_name = "pages/brand.html"
    fragment_name = "pages.fragments.brand"

    def _get_page(self) -> BrandPage:
        """Resolve the brand page — fall back to the products page tree root."""
        page = BrandPage.objects.first()
        return page or ProductsPage.objects.first()

    def get_context_data(self, request: HttpRequest | None = None, **kwargs) -> dict:
        context = super().get_context_data(request=request, **kwargs)
        from apps.pages.brand_spec import get_brand_boards

        context["brand_boards"] = get_brand_boards()
        page = context.get("page") or self._get_page()
        context["display_mode"] = getattr(page, "display_mode", "both")
        return context


class TeamPageView(LandingPageView):
    """About → Team subpage (/about/team/) — the people behind the products."""

    template_name = "pages/team.html"

    def _get_page(self) -> TeamPage:
        return TeamPage.objects.first()


class StartupPageView(LandingPageView):
    """About → Startup subpage (/about/startup/) — the structa.cloud origin story.

    A real Wagtail page (``StartupPage``, child of About) carrying hero, story
    body, a numbered timeline (process) and stats — mirroring the Astro
    startup page. Falls back to the About page only if the page is missing.
    """

    template_name = "pages/startup.html"

    def _get_page(self) -> StartupPage:
        return StartupPage.objects.first() or AboutPage.objects.first() or HomePage.objects.first()


class FounderPageView(LandingPageView):
    """About → Founder subpage (/about/founder/) — the engineer behind the code.

    A real Wagtail page (``FounderPage``, child of About) carrying hero, story
    body, tech stack and skills grid — mirroring the Astro founder page.
    Falls back to the About page only if the page is missing.
    """

    template_name = "pages/founder.html"

    def _get_page(self) -> FounderPage:
        return FounderPage.objects.first() or AboutPage.objects.first() or HomePage.objects.first()


class PhasePageView(LandingPageView):
    """A service delivery phase, resolved beneath Services by slug."""

    model = PhasePage
    template_name = "pages/phase.html"

    def _get_page(self) -> PhasePage:
        slug = self.kwargs.get("slug")
        page = PhasePage.objects.filter(slug=slug).first() if slug else None
        if page is None or page.get_parent().specific.__class__.__name__ != "ServicesPage":
            raise Http404(f"No phase named {slug!r}")
        return page

    def get_context_data(self, request: HttpRequest | None = None, **kwargs) -> dict:
        context = super().get_context_data(request=request, **kwargs)
        phase = context["page"]
        context["phase_outcomes"] = [line.strip() for line in phase.outcomes.splitlines() if line.strip()]
        context["phase_prompts"] = [
            {"title": prompt.title, "slug": prompt.slug, "href": f"/services/phases/{phase.slug}/prompts/{prompt.slug}/"}
            for prompt in PromptPage.objects.live().child_of(phase).order_by("title")
        ]
        return context


class PromptPageView(LandingPageView):
    """A reusable implementation prompt beneath a delivery phase."""

    model = PromptPage
    template_name = "pages/prompt.html"

    def _get_page(self) -> PromptPage:
        slug = self.kwargs.get("prompt_slug")
        page = PromptPage.objects.filter(slug=slug).first() if slug else None
        if page is None:
            raise Http404(f"No prompt named {slug!r}")
        phase_slug = self.kwargs.get("slug")
        parent = page.get_parent().specific
        if parent.__class__.__name__ != "PhasePage" or parent.slug != phase_slug:
            raise Http404(f"No prompt named {slug!r} under phase {phase_slug!r}")
        return page

    def get_context_data(self, request: HttpRequest | None = None, **kwargs) -> dict:
        context = super().get_context_data(request=request, **kwargs)
        prompt = context["page"]
        context["phase"] = prompt.get_parent().specific
        return context


class FeaturesPageView(LandingPageView):
    template_name = "pages/features.html"

    def _get_page(self) -> FeaturesPage:
        return FeaturesPage.objects.first()


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
