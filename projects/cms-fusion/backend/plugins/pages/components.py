"""Fusion page component views for CMS Fusion."""

from __future__ import annotations

from typing import Any
from django.http import Http404
from django_fusion.routes import RoutableComponent


class FusionPageView(RoutableComponent):
    """Base view for Wagtail FusionPage models in CMS Fusion."""

    model_class: type | None = None
    layout: str = "default"

    def get_fragment_name(self) -> str:
        page = self._get_page()
        if page and page.fragment_name:
            return page.fragment_name
        if page:
            return f"pages.{page.slug.replace('-', '_')}"
        return super().get_fragment_name() or f"pages.{self.route_name}"

    def get_fusion_render_first(self) -> bool:
        page = self._get_page()
        if page is not None:
            return bool(page.fusion_render_first)
        return super().get_fusion_render_first()

    def _get_page(self):
        slug = self.kwargs.get("slug", "")
        if not slug:
            return self._get_home_page()
        model_cls = self.model_class
        if model_cls is None:
            from plugins.pages.models import FusionContentPage
            model_cls = FusionContentPage
        try:
            return model_cls.objects.live().get(slug=slug)
        except model_cls.DoesNotExist:
            return None

    def _get_home_page(self):
        try:
            from plugins.pages.models import FusionHomePage
            return FusionHomePage.objects.live().first()
        except ImportError:
            return None

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        page = self._get_page()
        page_ctx = page.get_context() if page and hasattr(page, "get_context") else {
            "title": "Page", "layout": "default", "fusion_render_first": False}
        context.update({
            "page": page, "page_obj": page,
            "title": page_ctx.get("title", "Page"),
            "layout": page_ctx.get("layout", self.layout),
            "fusion_render_first": page_ctx.get("fusion_render_first", False),
            "fragment_name": self.get_fragment_name(),
            "component": self,
        })
        context.update(page_ctx)
        return context


class FusionHomePageView(FusionPageView):
    route_name = "home"
    route_path = ""
    title = "Home"
    icon = "home"
    layout = "full_width"
    fusion_render_first = True
    template_name = "pages/fusion_home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self._get_home_page()
        if page and hasattr(page, "get_context"):
            context.update(page.get_context())
            context["layout"] = page.effective_layout
        context.setdefault("hero_heading", "Welcome to Fusion CMS")
        return context


class FusionContentPageView(FusionPageView):
    route_name = "content"
    route_path = "<slug:slug>/"
    template_name = "pages/fusion_content.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self._get_page()
        if page is None:
            raise Http404(f"Page not found: {self.kwargs.get('slug', '')}")
        if hasattr(page, "get_context"):
            context.update(page.get_context())
            context["layout"] = page.effective_layout
        return context
