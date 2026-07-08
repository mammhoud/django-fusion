"""
Page Components & Smart Views
=============================
Production-ready component views with integrated:
- Template context management
- Unified fragment / layout rendering pipeline
- HTMX/UnPoly support
- Notification system
- Error handling
"""

from __future__ import annotations

import json
import logging
from typing import Any, List

from django.http import JsonResponse
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView

from ._context_mixins import FragmentHandlerMixin, is_htmx_request
from .notifications import NotificationMixin
from .paginators import HTMXPaginationMixin
from .plugins import HtmxDetails
from .response import HttpResponseClientRedirect

logger = logging.getLogger(__name__)


class ComponentViews(FragmentHandlerMixin, TemplateView):
    """
    Base component view — the foundation for all django-fusion views.

    Combines ``FragmentHandlerMixin`` (unified render pipeline) with
    Django's ``TemplateView``.  Subclass this for standalone views wired
    in ``urls.py``; use ``RoutableComponent`` for views in the root `/` routing tree.

    Rendering pipeline
    ------------------
    ``setup()`` calls ``resolve_strategy()`` (from ``BaseTemplateContextMixin``)
    which sets ``self.strategy`` to ``"fragment"`` or ``"document"``.

    ``get()`` then calls ``render_response(request, context)`` which
    dispatches to ``_render_fragment_response`` or ``_render_layout_response``
    based on ``self.strategy``.  There is **one** pipeline, not two.

    Template resolution
    -------------------
    ``resolve_template_name()`` (from ``FragmentHandlerMixin``) is the
    single method:

    * ``strategy == "fragment"`` and ``fragment_name`` set →
      ``fragment_name.replace('.', '/') + '.html'``
    * otherwise → ``template_name``

    Attributes:
        component_name:  Optional identifier for this component.
        require_auth:    Redirect unauthenticated users when ``True``.
        login_url:       Login redirect target (defaults to ``"/login/"``).
        show_breadcrumbs, show_sidebar, full_width:
            Page-level layout flags (previously on ``PageHandler``).
    """

    component_name: str | None = None
    require_auth: bool = False
    login_url: str | None = None

    # Layout flags (absorbed from PageHandler — no separate subclass needed)
    show_breadcrumbs: bool = False
    show_sidebar: bool = False
    full_width: bool = False

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def setup(self, request: HttpRequest, *args: Any, **kwargs: Any) -> None:
        """Initialise view: detect strategy, resolve template, check auth."""
        super().setup(request, *args, **kwargs)
        self.request = request
        self.strategy = self.resolve_strategy(request)
        self.template_name = self.resolve_template_name()

        if self.require_auth and not request.user.is_authenticated:
            self._handle_unauthenticated()

    def _handle_unauthenticated(self) -> None:
        """Store a redirect flag; actual redirect happens in ``get()``."""
        self._unauthenticated = True

    # ------------------------------------------------------------------
    # GET / POST
    # ------------------------------------------------------------------

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Handle GET — build context then dispatch through unified pipeline."""
        if getattr(self, "_unauthenticated", False):
            if is_htmx_request(request):
                resp = HttpResponse(status=401)
                resp["HX-Redirect"] = self.login_url or "/login/"
                return resp
            return redirect(self.login_url or "/login/")

        try:
            context = self.get_context_data(request=request, *args, **kwargs)
            if hasattr(self, "get_notifications"):
                context["notifications"] = self.get_notifications(request)
            return self.render_response(request, context, title=self.page_title)
        except Exception as exc:
            logger.error("[ComponentViews] GET failed: %s", exc)
            return self._handle_error(request, exc)

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Handle POST — delegates to ``process_post()``."""
        try:
            result = self.process_post(request, *args, **kwargs)
            if isinstance(result, HttpResponse):
                return result
            return self._handle_success(request, result)
        except Exception as exc:
            logger.error("[ComponentViews] POST failed: %s", exc)
            return self._handle_error(request, exc)

    def process_post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        """Override in subclasses to handle POST data."""
        raise NotImplementedError("Subclasses must implement process_post()")

    # ------------------------------------------------------------------
    # Success / error helpers
    # ------------------------------------------------------------------

    def _handle_success(self, request: HttpRequest, result: Any) -> HttpResponse:
        redirect_url = getattr(result, "get_absolute_url", None)
        if callable(redirect_url):
            redirect_url = redirect_url()

        if is_htmx_request(request):
            if redirect_url:
                return HttpResponseClientRedirect(redirect_url)
            resp = self.get(request)
            resp["HX-Trigger"] = json.dumps({"refresh": True})
            return resp

        if redirect_url:
            return redirect(redirect_url)
        return self.get(request)

    def _handle_error(self, request: HttpRequest, error: Exception) -> HttpResponse:
        error_message = str(error)
        if hasattr(self, "add_error"):
            notification_response = self.add_error(
                f"Error: {error_message}", request=request
            )
            if notification_response:
                return notification_response

        if is_htmx_request(request):
            return JsonResponse({"error": error_message, "status": "error"}, status=400)

        context = self.get_context_data(request=request)
        context["error"] = error_message
        return self._render_layout_response(context)

    # ------------------------------------------------------------------
    # render_to_response — add HTMX headers
    # ------------------------------------------------------------------

    def render_to_response(
        self, context: dict[str, Any], **response_kwargs: Any
    ) -> HttpResponse:
        response = super().render_to_response(context, **response_kwargs)
        if self.strategy == "fragment" and is_htmx_request(self.request):
            response["HX-Reswap"] = "innerHTML"
            if getattr(self, "fragment_target", None):
                response["HX-Retarget"] = self.fragment_target
        return response

    # ------------------------------------------------------------------
    # Context — layout flags
    # ------------------------------------------------------------------

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "show_breadcrumbs": self.show_breadcrumbs,
                "show_sidebar": self.show_sidebar,
                "full_width": self.full_width,
                "current_page": getattr(self.__class__, "page_title", ""),
            }
        )
        if self.show_breadcrumbs:
            context["breadcrumbs"] = self.get_breadcrumbs()
        return context

    def get_breadcrumbs(self) -> List[dict[str, str]]:
        """Return a static breadcrumb trail.  Override for dynamic trails."""
        return [
            {"title": "Home", "url": "/"},
            {"title": self.page_title, "url": self.request.path, "active": True},
        ]

    def get_sidebar_context(self) -> dict[str, Any]:
        """Return sidebar data.  Override in subclasses."""
        return {}


# ---------------------------------------------------------------------------
# PageHandler — kept as a thin alias for backward compatibility.
# New code should use ComponentViews (or RoutableComponent) directly.
# ---------------------------------------------------------------------------

class PageHandler(NotificationMixin, ComponentViews):
    """
    Backward-compatible alias for ``ComponentViews`` with notifications.

    All layout flags (``show_breadcrumbs``, ``show_sidebar``, ``full_width``)
    are now on ``ComponentViews`` itself.  ``PageHandler`` adds only
    ``NotificationMixin`` on top.

    .. deprecated::
        Prefer ``RoutableComponent`` for views in the root `/` routing tree,
        or ``ComponentViews`` for standalone ``urls.py`` views.
    """


# ---------------------------------------------------------------------------
# ModalComponent
# ---------------------------------------------------------------------------

class ModalComponent(ComponentViews):
    """Component for modal dialogs rendered as HTMX fragments."""

    fragment_name: str = "base_modal"
    modal_size: str = "md"
    modal_title: str = ""
    close_button: bool = True
    backdrop: bool = True

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "modal_size": self.modal_size,
                "modal_title": self.modal_title or self.page_title,
                "close_button": self.close_button,
                "backdrop": self.backdrop,
                "is_modal": True,
            }
        )
        return context


# ---------------------------------------------------------------------------
# PaginatedComponentView / PaginatedListView
# ---------------------------------------------------------------------------

class PaginatedComponentView(HTMXPaginationMixin, ComponentViews):
    """Component view with built-in HTMX pagination."""

    pagination_template: str = "components/pagination/default.html"
    items_template: str = "components/items/list.html"
    items_fragment_selector: str = "#items-container"
    pagination_fragment_selector: str = "#pagination-container"

    def setup(self, request: HttpRequest, *args: Any, **kwargs: Any) -> None:
        super().setup(request, *args, **kwargs)
        self._setup_pagination(request)

    def _setup_pagination(self, request: HttpRequest) -> None:
        if request.GET.get("pagination_style"):
            self.pagination_style = request.GET["pagination_style"]
        if is_htmx_request(request):
            trigger = request.headers.get("HX-Trigger", "")
            if trigger == "load-more":
                self.pagination_style = "load_more"
                self.load_more_enabled = True  # type: ignore[attr-defined]
            elif trigger == "infinite-scroll":
                self.pagination_style = "infinite"
                self.infinite_scroll_enabled = True  # type: ignore[attr-defined]

    def get_queryset(self) -> list:
        return super().get_queryset()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        return self.get_paginated_context_with_htmx(self.request, context)  # type: ignore[attr-defined]

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        htmx_response = self.get_htmx_response(request, {})  # type: ignore[attr-defined]
        if htmx_response:
            return htmx_response
        context = self.get_context_data(**kwargs)
        return self.render_response(request, context)

    def get_pagination_urls(self) -> dict[str, str]:
        if not hasattr(self, "request"):
            return {}
        base_url = self.request.path
        page = self.get_page_number(self.request)  # type: ignore[attr-defined]
        urls: dict[str, str] = {
            "first": f"{base_url}?{self.page_kwarg}=1",  # type: ignore[attr-defined]
            "last": f"{base_url}?{self.page_kwarg}={self.paginator.num_pages}",  # type: ignore[attr-defined]
        }
        if page > 1:
            urls["prev"] = f"{base_url}?{self.page_kwarg}={page - 1}"  # type: ignore[attr-defined]
        if page < self.paginator.num_pages:  # type: ignore[attr-defined]
            urls["next"] = f"{base_url}?{self.page_kwarg}={page + 1}"  # type: ignore[attr-defined]
        return urls


class PaginatedListView(PaginatedComponentView):
    """List view with pagination for displaying model querysets."""

    template_name: str = "components/paginated_list.html"
    fragment_name: str = "components.paginated_list"
    model: Any = None
    ordering: str | None = None

    def get_queryset(self) -> list:
        if self.model:
            qs = self.model.objects.all()
            if self.ordering:
                qs = qs.order_by(self.ordering)
            return qs
        return super().get_queryset()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if self.model:
            context["model_name"] = self.model._meta.verbose_name_plural
        return context
