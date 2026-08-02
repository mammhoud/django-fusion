"""
Fragment Components for django-fusion
=====================================

``FragmentComponent`` extends ``RoutableComponent`` for HTMX / Unpoly partial
responses.  Key design decisions:

* ``fragment_name`` (dotted string) is the **single** template convention —
  ``"blog.fragments.post_list"`` → ``"blog/fragments/post_list.html"``.
  ``fragment_template`` is removed; use ``fragment_name`` everywhere.

* ``dispatch()`` is a proper method override — no module-level monkey-patching.

* HTMX detection delegates to ``django_fusion.plugins.htmx``.
  Unpoly detection checks for ``X-Up-Version`` header.

* The rendering pipeline is unified: ``get()`` calls
  ``render_response(request, context)`` from ``FragmentHandlerMixin``,
  which routes to ``_render_fragment_response`` or ``_render_layout_response``
  based on ``self.strategy``.  ``render_fragment_response()`` is kept as a
  named method for subclasses that need to append OOB HTML after the main
  fragment body.
"""

from __future__ import annotations

from typing import Any

from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse

from django_fusion.plugins.htmx.core import is_fragment_request, is_htmx_request
from django_fusion.fragments.renderer import FragmentRequestRenderer
from django_fusion.fragments.registry import register_fragment_component

from .routable import RoutableComponent


class FragmentComponent(RoutableComponent):
    """
    HTMX / Unpoly fragment component registered in the root `/` routing tree.

    Extends ``RoutableComponent`` with:

    * ``fragment_name`` — dotted template identifier, e.g.
      ``"blog.fragments.post_list"`` → ``"blog/fragments/post_list.html"``.
      Set this instead of ``template_name`` for fragment-only components.
      If not set, inherits the default derivation from
      ``RoutableComponent.get_fragment_name()``::

          route_name = "post-list-fragment"
          # → "components.post-list-fragment"
          # → "components/post-list-fragment.html"
    * ``htmx_only`` — return HTTP 400 for non-fragment requests when ``True``.
    * ``oob_fragments`` — ``{element_id: fragment_name}`` dict; each entry
      is rendered and appended as an ``hx-swap-oob`` div.
    * ``paginate_by`` — auto-paginates ``get_queryset()`` and adds
      ``page_obj`` / ``object_list`` to the fragment context.
    * ``dispatch()`` — proper method override (no monkey-patching).

    Template convention
    -------------------
    Use ``fragment_name`` (dotted) for the fragment template::

        fragment_name = "blog.fragments.post_list"
        # → "blog/fragments/post_list.html"

    For the full-page fallback (when ``htmx_only=False`` and a non-HTMX
    request arrives) set ``template_name`` as usual.

    Example::

        class PostListFragment(FragmentComponent):
            route_name = "post-list-fragment"
            route_path = "posts/list-fragment/"
            fragment_name = "blog.fragments.post_list"
            htmx_only = True
            paginate_by = 10

            def get_queryset(self):
                return BlogPost.objects.filter(status="published")

            def get_fragment_context(self, **kwargs):
                context = super().get_fragment_context(**kwargs)
                context["categories"] = BlogCategory.objects.all()
                return context

    OOB fragments::

        class PostCreateFragment(FragmentComponent):
            fragment_name = "blog.fragments.post_create_form"
            oob_fragments = {
                "post-count": "blog.fragments.post_count",
            }
    """

    # fragment_name is inherited from BaseTemplateContextMixin.
    # Set it to a dotted string, e.g. "blog.fragments.post_list".
    htmx_only: bool = False
    oob_fragments: dict[str, str] = {}   # {element_id: dotted_fragment_name}
    paginate_by: int | None = None       # type: ignore[assignment]
    page_kwarg: str = "page"

    # Fragments are never shown in the navigation menu
    show_in_menu: bool = False

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        # Auto-register FragmentComponent subclasses so they can be requested
        # via /fragments/<fragment_name>/.
        # Use __dict__ lookups to avoid inheriting a parent class name.
        fragment_name = cls.__dict__.get("fragment_name")
        route_name = cls.__dict__.get("route_name")
        if not fragment_name and route_name:
            fragment_name = f"components.{route_name}"
        if fragment_name:
            register_fragment_component(fragment_name, cls)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        # Ensure oob_fragments is instance-level, not shared across subclasses
        if not self.oob_fragments:
            self.oob_fragments = {}

    # ------------------------------------------------------------------
    # dispatch() — proper override, no monkey-patching
    # ------------------------------------------------------------------

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Gate non-fragment requests when ``htmx_only=True``.

        Returns HTTP 400 immediately — before ``setup()`` runs permission
        checks — so the error is clearly a client protocol error, not an
        authorisation failure.
        """
        if self.htmx_only and not is_fragment_request(request):
            return HttpResponse(
                "This endpoint only accepts HTMX or Unpoly requests.", status=400
            )
        return super().dispatch(request, *args, **kwargs)

    # ------------------------------------------------------------------
    # setup() — update strategy so resolve_template_name() picks fragment
    # ------------------------------------------------------------------

    def setup(self, request: HttpRequest, *args: Any, **kwargs: Any) -> None:
        """Force strategy to ``"fragment"`` for HTMX / Unpoly requests."""
        super().setup(request, *args, **kwargs)
        # Override strategy so the unified pipeline renders the fragment template
        if is_fragment_request(request):
            self.strategy = "fragment"

    # ------------------------------------------------------------------
    # GET — unified pipeline entry point
    # ------------------------------------------------------------------

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Route to fragment or full-page rendering via the unified pipeline.

        * HTMX / Unpoly request → ``render_fragment_response()`` (fragment + OOB)
        * Non-fragment request → ``render_response()`` → ``_render_layout_response()``
        """
        if is_fragment_request(request):
            context = self.get_fragment_context()
            return self.render_fragment_response(context)
        return super().get(request, *args, **kwargs)

    # ------------------------------------------------------------------
    # Fragment context & pagination
    # ------------------------------------------------------------------

    def get_queryset(self) -> Any:
        """Return the data source for this fragment.  Override in subclasses."""
        return []

    def get_fragment_context(self, **kwargs: Any) -> dict[str, Any]:
        """Build context for fragment rendering.

        If ``paginate_by`` is set, ``get_queryset()`` is paginated and
        ``page_obj``, ``object_list``, and related keys are added.

        Override to add extra context::

            def get_fragment_context(self, **kwargs):
                context = super().get_fragment_context(**kwargs)
                context["categories"] = Category.objects.all()
                return context
        """
        context = self.get_context_data(**kwargs)

        if self.paginate_by is not None:
            queryset = self.get_queryset()
            page_number = self.request.GET.get(self.page_kwarg, 1)
            paginator = Paginator(queryset, self.paginate_by)
            page_obj = paginator.get_page(page_number)
            context.update(
                {
                    "paginator": paginator,
                    "page_obj": page_obj,
                    "object_list": page_obj.object_list,
                    "is_paginated": paginator.num_pages > 1,
                    "has_next": page_obj.has_next(),
                    "has_previous": page_obj.has_previous(),
                    "next_page_number": page_obj.next_page_number()
                    if page_obj.has_next()
                    else None,
                    "previous_page_number": page_obj.previous_page_number()
                    if page_obj.has_previous()
                    else None,
                }
            )

        return context

    # ------------------------------------------------------------------
    # OOB fragments
    # ------------------------------------------------------------------

    def get_oob_fragments(self, request: HttpRequest) -> dict[str, str]:
        """Return ``{element_id: rendered_html}`` for all OOB fragments.

        Override to add conditional OOB entries::

            def get_oob_fragments(self, request):
                fragments = super().get_oob_fragments(request)
                if request.user.is_staff:
                    fragments["admin-stats"] = self.render_oob_fragment(
                        "admin-stats", "admin.fragments.stats", {"count": 42}
                    )
                return fragments
        """
        fragments: dict[str, str] = {}
        context = self.get_fragment_context()
        for element_id, frag_name in self.oob_fragments.items():
            fragments[element_id] = self.render_oob_fragment(
                element_id, frag_name, context
            )
        return fragments

    def render_oob_fragment(
        self,
        element_id: str,
        fragment_name: str,
        context: dict[str, Any],
    ) -> str:
        """Render one OOB fragment and wrap it with ``hx-swap-oob="true"``.

        ``fragment_name`` follows the dotted convention:
        ``"blog.fragments.post_count"`` → ``"blog/fragments/post_count.html"``.
        """
        renderer = FragmentRequestRenderer(self.request, context=context)
        return renderer.render_oob(fragment_name, element_id, context=context)

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def get_template_names(self) -> list[str]:
        """Return the fragment template for HTMX/Unpoly, full-page template otherwise.

        Uses ``get_fragment_name()`` (dotted) → path conversion.  Falls back to
        ``template_name`` for non-fragment requests.
        """
        if is_fragment_request(self.request):
            fragment_name = self.get_fragment_name()
            if fragment_name:
                return [fragment_name.replace(".", "/") + ".html"]
        return super().get_template_names()

    def render_fragment_response(self, context: dict[str, Any]) -> HttpResponse:
        """Render the fragment template, append OOB HTML, set HTMX headers."""
        fragment_name = self.get_fragment_name()
        if fragment_name:
            renderer = FragmentRequestRenderer(self.request, context=context)
            response = renderer.render(fragment_name)
        else:
            response = self.render_to_response(context)

        oob = self.get_oob_fragments(self.request)
        if oob:
            body = response.content.decode("utf-8")
            for oob_html in oob.values():
                body += oob_html
            response.content = body.encode("utf-8")

        if is_htmx_request(self.request):
            response["HX-Partial"] = "true"
        return response

    def render_error(
        self, template: str, context: dict[str, Any] | None = None
    ) -> HttpResponse:
        """Render an empty-state/error response into a fragment template.

        Useful for POST handlers (e.g. checkout) that need to return an
        error fragment. Adds the ``HX-Partial`` header for HTMX requests
        so fragment-aware clients treat the response consistently.
        """
        from django.shortcuts import render

        response = render(self.request, template, context or {})
        if is_htmx_request(self.request):
            response["HX-Partial"] = "true"
        return response

    def render_to_response(
        self, context: dict[str, Any], **response_kwargs: Any
    ) -> HttpResponse:
        """Add ``HX-Reswap`` / ``HX-Retarget`` headers for HTMX requests."""
        response = super().render_to_response(context, **response_kwargs)
        if is_htmx_request(self.request):
            response["HX-Reswap"] = "innerHTML"
            fragment_target = getattr(self, "fragment_target", None)
            if fragment_target:
                response["HX-Retarget"] = fragment_target
        return response
