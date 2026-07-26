"""
Fusion page component views — RoutableComponent wrappers for Wagtail FusionPage models.

Each component view reads a Wagtail ``FusionPage`` from the database and
renders it through the fusion layout system (``{% fusion_layout %}``).

Usage::

    from plugins.pages.components import FusionHomePageView, FusionContentPageView

    # Register in Site → Application routing tree
    site.add_view(FusionHomePageView)
"""

from __future__ import annotations

from typing import Any

from django.http import Http404, HttpRequest, HttpResponse
from django_fusion.routes import RoutableComponent


class FusionPageView(RoutableComponent):
    """
    Base view for Wagtail FusionPage models.

    Reads a ``FusionPage`` by slug from the database and renders it with
    the fusion layout template system.

    To create a view for a specific page type, subclass and set
    ``model_class`` and ``template_name``.

    Example::

        class AboutPageView(FusionPageView):
            route_name = "about"
            route_path = "about/"
            model_class = FusionContentPage
            template_name = "pages/fusion_content.html"
            layout = "sidebar"  # default layout if page has none set
            fusion_render_first = True
    """

    model_class: type | None = None
    layout: str = "default"

    # ── Override RoutableComponent defaults ─────────────────────────

    def get_fragment_name(self) -> str:
        """Derive fragment name from the page's slug."""
        page = self._get_page()
        if page and page.fragment_name:
            return page.fragment_name
        if page:
            return f"pages.{page.slug.replace('-', '_')}"
        return super().get_fragment_name() or f"pages.{self.route_name}"

    def get_fusion_render_first(self) -> bool:
        """Read render-first preference from the Wagtail page or fall back."""
        page = self._get_page()
        if page is not None:
            return bool(page.fusion_render_first)
        return super().get_fusion_render_first()

    # ── Page retrieval ──────────────────────────────────────────────

    def _get_page(self):
        """Retrieve the Wagtail page for the current request."""
        slug = self.kwargs.get("slug", "")
        if not slug and self.route_path:
            return self._get_home_page()

        model_cls = self.model_class
        if model_cls is None:
            # Try to import the model lazily
            from plugins.pages.models import FusionContentPage

            model_cls = FusionContentPage

        try:
            return model_cls.objects.live().get(slug=slug)
        except model_cls.DoesNotExist:
            return None

    def _get_home_page(self):
        """Get the home page (root FusionHomePage)."""
        try:
            from plugins.pages.models import FusionHomePage
            return FusionHomePage.objects.live().first()
        except ImportError:
            return None

    # ── Context ─────────────────────────────────────────────────────

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        page = self._get_page()

        if page is not None and hasattr(page, "get_context"):
            page_ctx = page.get_context()
        else:
            page_ctx = {
                "title": getattr(page, "title", "Page"),
                "layout": "default",
                "fusion_render_first": False,
            }

        context.update(
            {
                "page": page,
                "page_obj": page,
                "title": page_ctx.get("title", "Page"),
                "page_title": page_ctx.get("title", "Page"),
                "layout": page_ctx.get("layout", self.layout),
                "fusion_render_first": page_ctx.get(
                    "fusion_render_first", False
                ),
                "fragment_name": self.get_fragment_name(),
                "component": self,
            }
        )

        # Merge all page context keys
        context.update(page_ctx)
        return context


class FusionHomePageView(FusionPageView):
    """
    Home page component — renders at the root URL ``/``.

    Always uses ``fusion_render_first=True`` so the Next.js frontend
    gets pre-rendered HTML on first visit.
    """

    route_name = "home"
    route_path = ""
    title = "Home"
    icon = "home"
    layout = "full_width"
    fusion_render_first = True
    template_name = "pages/fusion_home.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        page = self._get_home_page()

        if page is not None and hasattr(page, "get_context"):
            context.update(page.get_context())
            context["layout"] = page.effective_layout

        context.setdefault("hero_heading", "Welcome to Fusion LMS")
        context.setdefault(
            "hero_subheading",
            "Modern learning management powered by django-fusion + django-bolt",
        )
        return context


class FusionContentPageView(FusionPageView):
    """
    Generic content page — renders any ``FusionContentPage`` by slug.

    URL pattern: ``<slug>/``
    """

    route_name = "content"
    route_path = "<slug:slug>/"
    template_name = "pages/fusion_content.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        page = self._get_page()

        if page is None:
            raise Http404(f"Page not found: {self.kwargs.get('slug', '')}")

        if hasattr(page, "get_context"):
            context.update(page.get_context())
            context["layout"] = page.effective_layout

        return context
