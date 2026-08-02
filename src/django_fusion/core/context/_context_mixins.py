"""
Base Template Context & Fragment Handler
========================================
Core mixins for template context management and fragment rendering.

``fragment_name`` is the single convention for identifying a fragment.
It is a dotted string (e.g. ``"profile.blog"``) that maps to a template
path by replacing dots with slashes and appending ``.html``:

    "profile.blog"  →  "profile/blog.html"

``BaseTemplateContextMixin``  — context building, strategy detection
``FragmentHandlerMixin``      — unified render pipeline (fragment / layout)
``PaginatedBaseMixin``        — pagination helpers
"""

from __future__ import annotations

import logging
from typing import Any

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.paginator import Page as DjangoPage
from django.http import HttpResponseServerError
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.utils.functional import cached_property

from django_fusion.config.context import SETTINGS

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Single HTMX detection helper — used by every layer
# ---------------------------------------------------------------------------


from django_fusion.plugins.htmx import is_htmx_request

# ``is_htmx_request`` is the single canonical HTMX check used throughout
# django-fusion. The implementation lives in ``django_fusion.plugins.htmx``.




# ---------------------------------------------------------------------------
# Base context mixin
# ---------------------------------------------------------------------------


class BaseTemplateContextMixin:
    """
    Base mixin for template context management.

    Attributes:
        template_name:  Full-page template (e.g. ``"base_page.html"``).
        page_title:     Human-readable page title.
        layout_path:    Outer layout template (e.g. ``"base.html"``).
        fragment_name:  Dotted fragment identifier (e.g. ``"profile.blog"``).
                        Converted to a template path via
                        ``fragment_name.replace('.', '/') + '.html'``.
        strategy:       Current rendering strategy —                        ``"fragment"`` or
                        ``"full"``.  Set by ``resolve_strategy()`` in

                        ``setup()``.
    """

    template_name: str | None = "base_page.html"
    page_title: str = "Panel"
    layout_path: str = "base.html"
    fragment_name: str | None = None
    strategy: str = "full"

    # ------------------------------------------------------------------
    # Fragment name resolution — single convention with default derivation
    # ------------------------------------------------------------------

    def get_fragment_name(self) -> str | None:
        """Return the dotted fragment identifier for this view.

        The default implementation returns ``self.fragment_name`` as-is.
        Subclasses (notably ``RoutableComponent``) override this to derive
        a default from the component's identity when ``fragment_name`` is
        not explicitly set.

        The returned dotted string maps to a template path by replacing
        dots with slashes and appending ``.html``::

            "profile.blog"  →  "profile/blog.html"

        Returns ``None`` when no fragment name is available.
        """
        return self.fragment_name

    # ------------------------------------------------------------------
    # Safe user profile access
    # ------------------------------------------------------------------

    def get_user_profile(self, user: Any) -> Any | None:
        """Safely retrieve user profile with error handling."""
        try:
            return user.get_user_profile()
        except Exception as exc:
            logger.warning("[BaseTemplateContext] Profile fetch failed: %s", exc)
            return None

    # ------------------------------------------------------------------
    # Strategy detection — single source of truth
    # ------------------------------------------------------------------

    def resolve_strategy(self, request: HttpRequest) -> str:
        """Determine rendering strategy from the request.

        Returns ``"fragment"`` for HTMX or UnPoly requests, ``"full"``
        otherwise.  Delegates HTMX detection to the module-level
        :func:`is_htmx_request` so there is exactly one check site.
        """
        try:
            if is_htmx_request(request):
                return "fragment"
            if getattr(request, "is_unpoly", False):
                return "fragment"
            return "full"
        except Exception as exc:
            logger.warning("Strategy resolution error: %s", exc)
            return "full"

    # ------------------------------------------------------------------
    # Template data
    # ------------------------------------------------------------------

    def get_template_data(
        self, request: HttpRequest | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        """Return template-specific data.  Override in subclasses."""
        context: dict[str, Any] = kwargs.get("context", {})
        if request is not None:
            context["strategy"] = self.resolve_strategy(request)
        if self.strategy == "full":
            context["SETTINGS"] = SETTINGS(request)
        return context

    # ------------------------------------------------------------------
    # Context builder
    # ------------------------------------------------------------------

    def get_context_data(self, request: HttpRequest | None = None, **kwargs: Any) -> dict[str, Any]:
        """Build the complete template context."""
        base_context: dict[str, Any] = {}
        if hasattr(super(), "get_context_data"):
            base_context = super().get_context_data(**kwargs)  # type: ignore[misc]

        template_data = self.get_template_data(request=request, **kwargs)

        return {
            **base_context,
            "layout_path": self.layout_path,
            "strategy": self.strategy,
            "fragment_name": self.get_fragment_name(),
            "template_name": self.template_name,
            "page_title": self.page_title,
            **template_data,
            **kwargs,
        }


# ---------------------------------------------------------------------------
# Fragment handler mixin — unified render pipeline
# ---------------------------------------------------------------------------


class FragmentHandlerMixin(BaseTemplateContextMixin):
    """
    Unified rendering pipeline for fragment and full-page responses.

    Both ``ComponentViews`` (standalone views) and ``RoutableComponent``
    (routed views) use this single pipeline.  The decision point is
    ``self.strategy``:

    * ``"fragment"`` → :meth:`_render_fragment_response`        * ``"full"`` → :meth:`_render_layout_response`


    Template resolution follows one rule: if ``fragment_name`` is set and
    the strategy is ``"fragment"``, the template is
    ``fragment_name.replace('.', '/') + '.html'``.  Otherwise
    ``template_name`` is used.  This is the **only** template resolution
    path — ``resolve_template_name()`` is the single method that
    implements it.
    """

    base_template_name: str = "base.html"

    # ------------------------------------------------------------------
    # Template resolution — single method, one convention
    # ------------------------------------------------------------------

    def resolve_template_name(self) -> str:
        """Return the template path for the current strategy.

        Fragment strategy with a fragment name available (via
        ``get_fragment_name()``):
            ``"profile.blog"``  →  ``"profile/blog.html"``

        Otherwise: ``template_name`` or ``base_template_name``.
        """
        if self.strategy == "fragment":
            fragment_name = self.get_fragment_name()
            if fragment_name:
                return fragment_name.replace(".", "/") + ".html"
        return self.template_name or self.base_template_name

    # ------------------------------------------------------------------
    # Unified render entry point
    # ------------------------------------------------------------------

    def render_response(
        self,
        request: HttpRequest,
        context: dict[str, Any],
        title: str = "",
    ) -> HttpResponse:
        """Render the response using the current strategy.

        This is the **single entry point** for all rendering.  Callers
        should not call ``render_fragment`` / ``render_layout`` directly.

        * ``strategy == "fragment"`` → :meth:`_render_fragment_response`
        * ``strategy == "full"`` → :meth:`_render_layout_response`
        """
        if self.strategy == "fragment":
            return self._render_fragment_response(request, context, title=title)
        return self._render_layout_response(context)

    # ------------------------------------------------------------------
    # Fragment rendering
    # ------------------------------------------------------------------

    def _render_fragment_response(
        self,
        request: HttpRequest,
        context: dict[str, Any],
        title: str = "",
    ) -> HttpResponse:
        """Render the fragment template and set HTMX headers."""
        context.update({"fragment_name": self.get_fragment_name(), "is_fragment": True})

        # UnPoly title update
        try:
            if getattr(request, "is_unpoly", False):
                request.up.set_title(title or self.page_title)  # type: ignore[attr-defined]
        except Exception:
            pass

        if hasattr(self, "render_to_response"):
            return self.render_to_response(context)  # type: ignore[attr-defined]

        from django.shortcuts import render

        return render(request, self.resolve_template_name(), context)

    # ------------------------------------------------------------------
    # Layout rendering
    # ------------------------------------------------------------------

    def _render_layout_response(self, context: dict[str, Any]) -> HttpResponse:
        """Render the full-page layout template."""
        try:
            if hasattr(self, "render_to_response"):
                return self.render_to_response(context)  # type: ignore[attr-defined]
            from django.shortcuts import render

            return render(self.request, self.resolve_template_name(), context)  # type: ignore[attr-defined]
        except Exception as exc:
            logger.error("[FragmentHandler] Layout render failed: %s", exc)
            try:
                from django.shortcuts import render
                return render(
                    self.request,  # type: ignore[attr-defined]
                    "errors/nxx.html",
                    {
                        "status_code": 500,
                        "error_title": "Rendering Error",
                        "error_message": str(exc),
                        "exception": str(exc),
                    },
                    status=500,
                )
            except Exception:
                return HttpResponseServerError(
                    "An internal error occurred while rendering the page."
                )

    # ------------------------------------------------------------------
    # Backward-compat aliases (deprecated — use render_response())
    # ------------------------------------------------------------------

    def render_fragment(
        self,
        request: HttpRequest,
        context: dict[str, Any],
        fragment_name: str | None = None,
        title: str = "",
    ) -> HttpResponse:
        """Deprecated: use ``render_response()`` instead."""
        if fragment_name:
            self.fragment_name = fragment_name
        return self._render_fragment_response(request, context, title=title)

    def render_layout(self, context: dict[str, Any]) -> HttpResponse:
        """Deprecated: use ``render_response()`` instead."""
        return self._render_layout_response(context)


# ---------------------------------------------------------------------------
# Pagination mixin
# ---------------------------------------------------------------------------


class PaginatedBaseMixin:
    """Base pagination mixin with configuration and core functionality."""

    paginate_by: int = 10
    page_kwarg: str = "page"
    paginator_class = Paginator
    allow_empty: bool = True
    orphans: int = 0
    paginate_by_param: str = "per_page"
    max_paginate_by: int = 100

    queryset: Any = None
    data_list: list[Any] = []
    object_list: list[Any] = []

    pagination_style: str = "numbers"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._paginator: Paginator | None = None
        self._page: DjangoPage | None = None
        self._paginated_context: dict[str, Any] = {}

    def get_paginate_by(self, request: HttpRequest) -> int:
        if self.paginate_by_param and self.paginate_by_param in request.GET:
            try:
                per_page = int(request.GET[self.paginate_by_param])
                if 0 < per_page <= self.max_paginate_by:
                    return per_page
            except (ValueError, TypeError):
                pass
        if callable(self.paginate_by):
            return self.paginate_by(request)  # type: ignore[operator]
        return self.paginate_by

    def get_queryset(self) -> list[Any]:
        if self.queryset is not None:
            return self.queryset
        if self.data_list:
            return self.data_list
        if self.object_list:
            return self.object_list
        return []

    def get_context_object_name(self) -> str:
        return "object_list"

    def get_page_number(self, request: HttpRequest) -> int:
        try:
            return int(request.GET.get(self.page_kwarg, 1))
        except (ValueError, TypeError):
            return 1

    @cached_property
    def paginator(self) -> Paginator:
        if self._paginator is None:
            self._paginator = self.paginator_class(
                self.get_queryset(),
                self.get_paginate_by(self.request),  # type: ignore[attr-defined]
                orphans=self.orphans,
                allow_empty_first_page=self.allow_empty,
            )
        return self._paginator

    @cached_property
    def page(self) -> DjangoPage:
        if self._page is None:
            page_number = self.get_page_number(self.request)  # type: ignore[attr-defined]
            try:
                self._page = self.paginator.page(page_number)
            except PageNotAnInteger:
                self._page = self.paginator.page(1)
            except EmptyPage:
                self._page = self.paginator.page(self.paginator.num_pages)
        return self._page

    def get_paginated_context(
        self,
        page_number: int | None = None,
        extra_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        page_obj = self.paginator.page(page_number) if page_number else self.page
        context: dict[str, Any] = {
            "paginator": self.paginator,
            "page_obj": page_obj,
            "page": page_obj,
            "listed_data": page_obj.object_list,
            "is_paginated": self.paginator.num_pages > 1,
            "page_number": page_obj.number,
            "total_pages": self.paginator.num_pages,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
            "next_page_number": page_obj.next_page_number() if page_obj.has_next() else None,
            "previous_page_number": page_obj.previous_page_number()
            if page_obj.has_previous()
            else None,
            "data_count": len(self.get_queryset()),
            "start_index": page_obj.start_index(),
            "end_index": page_obj.end_index(),
            "total_count": self.paginator.count,
            "pagination_style": self.pagination_style,
            "page_kwarg": self.page_kwarg,
            "paginate_by_param": self.paginate_by_param,
            "current_per_page": self.get_paginate_by(self.request),  # type: ignore[attr-defined]
            "is_htmx_pagination": is_htmx_request(self.request),  # type: ignore[attr-defined]
        }
        if self.pagination_style == "numbers":
            context["page_range"] = self.get_page_range(page_obj.number, self.paginator.num_pages)
        if extra_context:
            context.update(extra_context)
        self._paginated_context = context
        return context

    def get_page_range(
        self, current_page: int, total_pages: int, delta: int = 2
    ) -> list[int | str]:
        if total_pages <= 1:
            return []
        if total_pages <= (delta * 2) + 5:
            return list(range(1, total_pages + 1))
        left = current_page - delta
        right = current_page + delta + 1
        page_range: list[int | str] = []
        last = 0
        for p in range(1, total_pages + 1):
            if p == 1 or p == total_pages or (left <= p < right):
                if last and p - last > 1:
                    page_range.append("...")
                page_range.append(p)
                last = p
        return page_range

    def extend_context(self, request: HttpRequest, context: dict[str, Any]) -> dict[str, Any]:
        self.request = request  # type: ignore[attr-defined]
        object_list = context.get(self.get_context_object_name()) or self.get_queryset()
        self.object_list = object_list
        pagination_context = self.get_paginated_context()
        context.update(pagination_context)
        context[self.get_context_object_name()] = pagination_context["listed_data"]
        return context
