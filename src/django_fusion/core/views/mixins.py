"""
django_fusion.views.mixins
=========================

Generic, reusable view mixins for Django projects.

These mixins have **no dependency** on django-ceptor, Wagtail, Celery, or any
application-layer package.  They are safe to use in any Django project that
installs django-fusion.

Classes
-------
AjaxResponseMixin
    Detect AJAX requests and return JSON responses.
JSONResponseMixin
    Standardised success / error JSON response helpers for class-based views.
MessageMixin
    Attach Django messages to form-valid / form-invalid / delete cycles.
SearchMixin
    Q-based full-text search with HTMX live-search support.
"""

from typing import Any, Dict, List, Optional

from django.contrib import messages
from django.db.models import Q, QuerySet
from django.http import JsonResponse


class AjaxResponseMixin:
    """
    Mixin that adds AJAX detection and JSON response helpers to any view.

    Usage::

        class MyView(AjaxResponseMixin, View):
            def get(self, request, *args, **kwargs):
                if self.is_ajax():
                    return self.render_to_json_response({"ok": True})
                return super().get(request, *args, **kwargs)
    """

    def render_to_json_response(self, context: Dict[str, Any], **response_kwargs) -> JsonResponse:
        """
        Serialise *context* as a JSON response.

        Args:
            context: Mapping to serialise.
            **response_kwargs: Extra keyword arguments forwarded to
                :class:`django.http.JsonResponse`.

        Returns:
            :class:`~django.http.JsonResponse`
        """
        return JsonResponse(context, **response_kwargs)

    def is_ajax(self) -> bool:
        """
        Return ``True`` when the current request carries the
        ``X-Requested-With: XMLHttpRequest`` header.

        Returns:
            bool
        """
        return getattr(self, "request", None) and \
            self.request.headers.get("X-Requested-With") == "XMLHttpRequest"

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        return super().dispatch(request, *args, **kwargs)


class JSONResponseMixin:
    """
    Mixin that provides standardised ``success`` / ``error`` JSON helpers.

    Intended for class-based views that need a consistent JSON envelope::

        {"status": "success"|"error", "message": "...", "data": {...}}

    Usage::

        class ItemCreateView(JSONResponseMixin, View):
            def post(self, request):
                ...
                return self.success_response({"id": item.pk}, "Created")
    """

    def success_response(
        self,
        data: Dict[str, Any] = None,
        message: str = "Success",
        status: int = 200,
    ) -> JsonResponse:
        """
        Return a ``200 OK`` (or custom *status*) JSON envelope.

        Args:
            data: Payload to include under the ``"data"`` key.
            message: Human-readable success message.
            status: HTTP status code (default ``200``).

        Returns:
            :class:`~django.http.JsonResponse`
        """
        return JsonResponse(
            {"status": "success", "message": message, "data": data or {}},
            status=status,
        )

    def error_response(
        self,
        message: str,
        errors: Dict[str, Any] = None,
        status: int = 400,
    ) -> JsonResponse:
        """
        Return an error JSON envelope.

        Args:
            message: Human-readable error description.
            errors: Optional field-level error mapping.
            status: HTTP status code (default ``400``).

        Returns:
            :class:`~django.http.JsonResponse`
        """
        return JsonResponse(
            {"status": "error", "message": message, "errors": errors or {}},
            status=status,
        )


class MessageMixin:
    """
    Mixin that attaches Django flash messages to form lifecycle hooks.

    Set :attr:`success_message` and/or :attr:`error_message` on the view
    subclass::

        class ArticleUpdateView(MessageMixin, UpdateView):
            success_message = "Article saved."
            error_message   = "Please correct the errors below."
    """

    success_message: str = ""
    error_message: str = ""

    def form_valid(self, form):
        """Add :attr:`success_message` when the form is valid."""
        if self.success_message:
            messages.success(self.request, self.success_message)
        return super().form_valid(form)

    def form_invalid(self, form):
        """Add :attr:`error_message` when the form is invalid."""
        if self.error_message:
            messages.error(self.request, self.error_message)
        return super().form_invalid(form)

    def delete(self, request, *args, **kwargs):
        """Add :attr:`success_message` after a successful delete."""
        response = super().delete(request, *args, **kwargs)
        if self.success_message:
            messages.success(self.request, self.success_message)
        return response


class BaseDashboardMixin:
    """
    Abstract base for site-specific dashboard view implementations.

    Subclass and implement :meth:`get_dashboard_context` and
    :meth:`get_recent_activity` for your project::

        class MyDashboard(BaseDashboardMixin, TemplateView):
            template_name = "dashboard/index.html"

            def get_dashboard_context(self, request):
                return {"stats": compute_stats(request.user)}

            def get_recent_activity(self, user):
                return Activity.objects.filter(user=user)[:10]
    """

    def get_dashboard_context(self, request) -> Dict[str, Any]:
        """Return context dict for the dashboard view."""
        raise NotImplementedError("Subclasses must implement get_dashboard_context()")

    def get_recent_activity(self, user) -> Any:
        """Return recent activity queryset or list for *user*."""
        raise NotImplementedError("Subclasses must implement get_recent_activity()")

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if hasattr(self, "request"):
            context.update(self.get_dashboard_context(self.request))
        return context


class BaseCartMixin:
    """
    Abstract base for site-specific cart view implementations.

    Subclass and implement all abstract methods for your site::

        class CourseCartMixin(BaseCartMixin, View):
            def get_cart_items(self, request):
                return CourseCartItem.objects.filter(session=request.session)

            def calculate_total(self, items):
                return sum(i.price for i in items)

            def add_item(self, request, item_id):
                ...

            def remove_item(self, request, item_id):
                ...
    """

    def get_cart_items(self, request) -> Any:
        """Return cart items for the current request/session."""
        raise NotImplementedError("Subclasses must implement get_cart_items()")

    def calculate_total(self, items) -> Any:
        """Calculate and return the cart total from *items*."""
        raise NotImplementedError("Subclasses must implement calculate_total()")

    def add_item(self, request, item_id) -> None:
        """Add item with *item_id* to the cart."""
        raise NotImplementedError("Subclasses must implement add_item()")

    def remove_item(self, request, item_id) -> None:
        """Remove item with *item_id* from the cart."""
        raise NotImplementedError("Subclasses must implement remove_item()")


class SearchMixin:
    """
    Mixin that adds Q-based full-text search with HTMX live-search support.

    Configure on the view subclass::

        class ArticleListView(SearchMixin, ListView):
            model = Article
            search_fields = ["title", "body"]
            search_template = "articles/_search_results.html"

    The mixin hooks into :meth:`get_queryset` automatically.  When an HTMX
    request is detected the view renders :attr:`search_template` instead of
    the default template.

    Attributes:
        search_fields: List of model field lookups to search (e.g.
            ``["title__icontains", "body"]``).  Plain field names are
            automatically suffixed with ``__icontains``.
        search_param: Query-string parameter name (default ``"q"``).
        search_template: Partial template rendered for HTMX requests.
    """

    search_fields: List[str] = []
    search_param: str = "q"
    search_template: Optional[str] = None

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def get_search_query(self) -> str:
        """
        Return the raw search string from the GET parameters.

        Returns:
            str: Stripped query string, or empty string when absent.
        """
        return self.request.GET.get(self.search_param, "").strip()

    def is_htmx_request(self) -> bool:
        """
        Return ``True`` when the request carries the ``HX-Request`` header.

        Returns:
            bool
        """
        return self.request.headers.get("HX-Request") == "true"

    def get_search_queryset(self, queryset: QuerySet, query: str) -> QuerySet:
        """
        Filter *queryset* by *query* across :attr:`search_fields`.

        Each entry in :attr:`search_fields` is treated as an ``icontains``
        lookup unless it already contains a ``__`` lookup separator.  All
        field conditions are OR-combined via :class:`~django.db.models.Q`.

        Args:
            queryset: Base queryset to filter.
            query: Search string.

        Returns:
            Filtered :class:`~django.db.models.QuerySet`.
        """
        if not query or not self.search_fields:
            return queryset

        q_filter = Q()
        for field in self.search_fields:
            lookup = field if "__" in field else f"{field}__icontains"
            q_filter |= Q(**{lookup: query})

        return queryset.filter(q_filter)

    def get_search_context(self) -> Dict[str, Any]:
        """
        Return a context dict with search metadata.

        Returns:
            dict with keys:

            * ``search_query`` – the current search string
            * ``is_htmx`` – whether this is an HTMX request
        """
        return {
            "search_query": self.get_search_query(),
            "is_htmx": self.is_htmx_request(),
        }

    # ------------------------------------------------------------------
    # ListView integration
    # ------------------------------------------------------------------

    def get_queryset(self) -> QuerySet:
        """Apply search filtering on top of the parent queryset."""
        queryset = super().get_queryset()
        query = self.get_search_query()
        if query:
            queryset = self.get_search_queryset(queryset, query)
        return queryset

    def get_template_names(self) -> List[str]:
        """
        Return the partial template for HTMX requests when configured.

        Falls back to the standard template resolution when
        :attr:`search_template` is not set or the request is not HTMX.
        """
        if self.is_htmx_request() and self.search_template:
            return [self.search_template]
        return super().get_template_names()

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Inject search context into the template context."""
        context = super().get_context_data(**kwargs)
        context.update(self.get_search_context())
        return context


class FilterMixin:
    """
    Mixin that adds declarative queryset filtering with tag and category support.

    Configure on the view subclass::

        class ArticleListView(SearchMixin, FilterMixin, ListView):
            model = Article
            filter_fields = [("status", "status"), ("author", "author__username")]
            filter_by_tag = "tags__slug"
            filter_by_category = "categories__slug"

    Attributes:
        filter_fields: List of ``(param_name, field_lookup)`` tuples.
            Each ``param_name`` is read from ``request.GET``; the value is
            applied as an exact-match filter on ``field_lookup``.
        filter_by_tag: Field lookup for tag filtering (e.g. ``"tags__slug"``).
            Reads the ``"tag"`` or ``"tags"`` GET parameter (comma-separated).
        filter_by_category: Field lookup for category filtering
            (e.g. ``"categories__slug"``).  Reads ``"category"`` or
            ``"categories"`` GET parameter (comma-separated).
    """

    filter_fields: List[tuple] = []
    filter_by_tag: Optional[str] = None
    filter_by_category: Optional[str] = None

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def get_active_filters(self) -> Dict[str, Any]:
        """
        Return a dict of currently active filter values from GET parameters.

        Returns:
            dict with keys for each active filter (non-empty values only).
        """
        active: Dict[str, Any] = {}

        for param_name, _ in self.filter_fields:
            value = self.request.GET.get(param_name, "").strip()
            if value:
                active[param_name] = value

        if self.filter_by_tag:
            tags = self._get_multi_param("tag", "tags")
            if tags:
                active["tags"] = tags

        if self.filter_by_category:
            categories = self._get_multi_param("category", "categories")
            if categories:
                active["categories"] = categories

        return active

    def get_filter_queryset(self, queryset: QuerySet) -> QuerySet:
        """
        Apply all active filters to *queryset* and return the result.

        Args:
            queryset: Base queryset to filter.

        Returns:
            Filtered :class:`~django.db.models.QuerySet`.
        """
        for param_name, field_lookup in self.filter_fields:
            value = self.request.GET.get(param_name, "").strip()
            if value:
                queryset = queryset.filter(**{field_lookup: value})

        if self.filter_by_tag:
            tags = self._get_multi_param("tag", "tags")
            for tag in tags:
                queryset = queryset.filter(**{self.filter_by_tag: tag})

        if self.filter_by_category:
            categories = self._get_multi_param("category", "categories")
            for category in categories:
                queryset = queryset.filter(**{self.filter_by_category: category})

        return queryset

    def get_filter_context(self) -> Dict[str, Any]:
        """
        Return a context dict with active filter metadata.

        Returns:
            dict with key ``"active_filters"``.
        """
        return {"active_filters": self.get_active_filters()}

    # ------------------------------------------------------------------
    # ListView integration
    # ------------------------------------------------------------------

    def get_queryset(self) -> QuerySet:
        """Apply filter on top of the parent queryset."""
        queryset = super().get_queryset()
        return self.get_filter_queryset(queryset)

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Inject filter context into the template context."""
        context = super().get_context_data(**kwargs)
        context.update(self.get_filter_context())
        return context

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_multi_param(self, singular: str, plural: str) -> List[str]:
        """
        Read a comma-separated GET parameter, trying *singular* then *plural*.

        Args:
            singular: Primary parameter name (e.g. ``"tag"``).
            plural: Fallback parameter name (e.g. ``"tags"``).

        Returns:
            List of non-empty stripped values.
        """
        raw = self.request.GET.get(singular) or self.request.GET.get(plural, "")
        return [v.strip() for v in raw.split(",") if v.strip()]
