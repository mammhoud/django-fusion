"""
Base Template Context & Fragment Handler
========================================
Core mixins for template context management and fragment rendering.
Separated concerns for better reusability.
"""

import logging
from typing import Any

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.paginator import Page as DjangoPage
from django.http.request import HttpRequest
from django.http.response import HttpResponse, JsonResponse
from django.utils.functional import cached_property

from django_fusion.contrib.context import SETTINGS

logger = logging.getLogger(__name__)

class BaseTemplateContextMixin:
    """
    Base mixin for template context management.
    Handles user profile, template data, and context building.
    """

    template_name: str | None = "base_page.html"
    page_title: str = "Panel"
    layout_path: str = "base.html"
    fragment_name: str | None = None
    strategy: str = "document"

    # -----------------------------------------
    # Safe user profile access
    # -----------------------------------------
    def get_user_profile(self, user):
        """Safely retrieve user profile with error handling."""
        try:
            return user.get_user_profile()
        except Exception as e:
            logger.warning(f"[BaseTemplateContext] Profile fetch failed: {e}")
            return None

    # -----------------------------------------
    # TEMPLATE DATA (request-aware)
    # -----------------------------------------
    def get_template_data(self, request: HttpRequest | None = None, **kwargs) -> dict[str, Any]:
        """
        Get template-specific data.
        Override in subclasses to add custom data.
        """
        context = kwargs.get("context", {})

        if request is not None:
            context["strategy"] = self.resolve_strategy(request)
        if self.strategy == "document":
            settings = SETTINGS(request)

            context.update(settings)

        return context

    def resolve_strategy(self, request: HttpRequest) -> str:
        """
        Determine rendering strategy based on request.
        Default: fragment for HTMX, document otherwise.
        """
        try:
            if hasattr(request, "htmx") and request.htmx:
                return "fragment"
            elif hasattr(request, "is_unpoly") and request.is_unpoly:
                return "fragment"
            return "document"
        except Exception as e:
            logger.warning(f"Strategy resolution error: {e}")
            return "document"

    # -----------------------------------------
    # MAIN CONTEXT BUILDER (safe)
    # -----------------------------------------
    def get_context_data(self, request: HttpRequest | None = None, **kwargs) -> dict[str, Any]:
        """
        Build complete context dictionary.
        Combines base context, template data, and view-specific data.
        """
        # Get base context from TemplateView
        if hasattr(super(), "get_context_data"):
            base_context = super().get_context_data(**kwargs)
        else:
            base_context = {}

        # Get template-specific data
        template_data = self.get_template_data(request=request, **kwargs)
        # Build final context
        final_context = {
            **base_context,
            "layout_path": self.layout_path,
            "strategy": self.strategy,
            "fragment_name": self.fragment_name,
            "template_name": self.template_name,
            "page_title": self.page_title,
            **template_data,
            **kwargs,
        }

        return final_context


class FragmentHandlerMixin(BaseTemplateContextMixin):
    """
    Handles fragment-specific rendering logic.
    Separated from template context for clarity.
    """

    base_template_name = "base.html"

    def render_fragment(
        self,
        request: HttpRequest,
        context: dict,
        fragment_name: str = None,
        title: str = "",
    ) -> HttpResponse:
        """
        Handle fragment rendering with component fallback.
        Used for HTMX/UnPoly partial requests.
        """
        # Determine fragment template
        fragment_name = fragment_name or self.fragment_name

        if fragment_name:
            # Convert dotted path to template path
            template_name = f"{fragment_name.replace('.', '/')}.html"  # noqa: F841

            # Set fragment-specific context
            context.update(
                {
                    "fragment_name": fragment_name,
                    "is_fragment": True,
                }
            )

            # Handle UnPoly title updates
            try:
                if hasattr(request, "is_unpoly") and request.is_unpoly:
                    request.up.set_title(title or self.page_title)
            except:  # noqa: E722
                pass

            # Render using parent's render_to_response
            if hasattr(self, "render_to_response"):
                return self.render_to_response(context)

        # Fallback to fragment template
        self.template_name = self.fragment_template
        context["is_fragment"] = True

        if hasattr(self, "render_to_response"):
            return self.render_to_response(context)

        # Last resort fallback
        from django.shortcuts import render

        return render(request, self.fragment_template, context)

    def render_layout(self, context: dict) -> HttpResponse:
        """Handle full document layout rendering."""
        try:
            if not self.template_name:
                self.template_name = self.base_template_name

            if hasattr(self, "render_to_response"):
                return self.render_to_response(context)

            # Fallback
            from django.shortcuts import render

            return render(self.request, self.template_name, context)

        except Exception as e:
            logger.error(f"[FragmentHandler] Layout render failed: {e}")
            return JsonResponse({"error": "Rendering failed", "details": str(e)}, status=500)

    def resolve_template_name(self) -> str:
        """
        Resolve the appropriate template name based on strategy.
        """
        if self.strategy == "fragment" and self.fragment_name:
            return f"{self.fragment_name.replace('.', '/')}.html"
        elif self.strategy == "fragment":
            return self.fragment_template

        return self.template_name or self.base_template_name


class PaginatedBaseMixin:
    """
    Base pagination mixin with configuration and core functionality.
    """

    # Configuration
    paginate_by: int = 10
    page_kwarg: str = "page"
    paginator_class = Paginator
    allow_empty: bool = True
    orphans: int = 0
    paginate_by_param: str = "per_page"
    max_paginate_by: int = 100

    # Data source
    queryset = None
    data_list: list[Any] = []
    object_list: list[Any] = []

    # Pagination style
    pagination_style: str = "numbers"  # 'numbers', 'simple', 'load_more', 'infinite'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._paginator = None
        self._page = None
        self._paginated_context = {}

    def get_paginate_by(self, request: HttpRequest) -> int:
        """
        Get number of items per page.
        Can be overridden for dynamic pagination.
        """
        # Check URL parameter first
        if self.paginate_by_param and self.paginate_by_param in request.GET:
            try:
                per_page = int(request.GET.get(self.paginate_by_param))
                # Enforce maximum
                if per_page > self.max_paginate_by:
                    return self.max_paginate_by
                if per_page > 0:
                    return per_page
            except (ValueError, TypeError):
                pass

        # Check if view has dynamic pagination
        if hasattr(self, "paginate_by") and callable(self.paginate_by):
            return self.paginate_by(request)

        return self.paginate_by

    def get_queryset(self) -> list[Any]:
        """
        Get the list of items to paginate.
        Override in subclasses.
        """
        if self.queryset is not None:
            return self.queryset

        if self.data_list:
            return self.data_list

        if self.object_list:
            return self.object_list

        return []

    def get_context_object_name(self) -> str:
        """Get the name to use for the object list in the template."""
        return "object_list"

    def get_page_number(self, request: HttpRequest) -> int:
        """Get current page number from request."""
        try:
            return int(request.GET.get(self.page_kwarg, 1))
        except (ValueError, TypeError):
            return 1

    @cached_property
    def paginator(self) -> Paginator:
        """Get paginator instance."""
        if self._paginator is None:
            queryset = self.get_queryset()
            paginate_by = self.get_paginate_by(self.request)
            self._paginator = self.paginator_class(
                queryset,
                paginate_by,
                orphans=self.orphans,
                allow_empty_first_page=self.allow_empty,
            )
        return self._paginator

    @cached_property
    def page(self) -> DjangoPage:
        """Get current page object."""
        if self._page is None:
            page_number = self.get_page_number(self.request)
            try:
                self._page = self.paginator.page(page_number)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page
                self._page = self.paginator.page(1)
            except EmptyPage:
                # If page is out of range, deliver last page
                self._page = self.paginator.page(self.paginator.num_pages)
        return self._page

    def get_paginated_context(
        self, page_number: int | None = None, extra_context: dict | None = None
    ) -> dict[str, Any]:
        """
        Get comprehensive pagination context.

        Args:
            page_number: Optional specific page number
            extra_context: Additional context to include

        Returns:
            Dictionary with pagination context
        """
        if page_number:
            try:
                page_obj = self.paginator.page(page_number)
            except (PageNotAnInteger, EmptyPage):
                page_obj = self.page
        else:
            page_obj = self.page

        context = {
            "paginator": self.paginator,
            "page_obj": page_obj,
            "page": page_obj,  # Alias for compatibility
            "listed_data": page_obj.object_list,
            # Metadata
            "is_paginated": self.paginator.num_pages > 1,
            "page_number": page_obj.number,
            "total_pages": self.paginator.num_pages,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
            "next_page_number": page_obj.next_page_number() if page_obj.has_next() else None,
            "previous_page_number": page_obj.previous_page_number()
            if page_obj.has_previous()
            else None,
            # Counts
            "data_count": len(self.get_queryset()),
            "start_index": page_obj.start_index(),
            "end_index": page_obj.end_index(),
            "total_count": self.paginator.count,
            # Pagination style
            "pagination_style": self.pagination_style,
            "page_kwarg": self.page_kwarg,
            "paginate_by_param": self.paginate_by_param,
            "current_per_page": self.get_paginate_by(self.request),
            # HTMX support
            "is_htmx_pagination": hasattr(self.request, "htmx") and self.request.htmx,
        }

        # Add page range for numbered pagination
        if self.pagination_style == "numbers":
            context["page_range"] = self.get_page_range(page_obj.number, self.paginator.num_pages)

        # Merge extra context
        if extra_context:
            context.update(extra_context)

        # Cache for performance
        self._paginated_context = context

        logger.debug(
            f"Paginated context for page {page_obj.number}: "
            f"{len(page_obj.object_list)} items of {self.paginator.count} total"
        )

        return context

    def get_page_range(
        self, current_page: int, total_pages: int, delta: int = 2
    ) -> list[int | str]:
        """
        Get page range for numbered pagination with ellipsis.

        Args:
            current_page: Current page number
            total_pages: Total number of pages
            delta: Number of pages to show on each side of current page

        Returns:
            List of page numbers and ellipsis markers
        """
        if total_pages <= 1:
            return []

        # Show all pages if few
        if total_pages <= (delta * 2) + 5:
            return list(range(1, total_pages + 1))

        # Calculate range
        left = current_page - delta
        right = current_page + delta + 1

        # Create range with ellipsis
        page_range = []
        last = 0

        for page in range(1, total_pages + 1):
            if page == 1 or page == total_pages or (left <= page < right):
                if last and page - last > 1:
                    page_range.append("...")
                page_range.append(page)
                last = page

        return page_range

    def extend_context(self, request: HttpRequest, context: dict[str, Any]) -> dict[str, Any]:
        """
        Extend existing context with pagination data.

        Args:
            request: HTTP request
            context: Existing context dictionary

        Returns:
            Updated context with pagination
        """
        # Store request for paginator access
        self.request = request

        # Get object list from context or instance
        object_list = context.get(self.get_context_object_name())
        if object_list is None:
            object_list = self.get_queryset()

        # Set object list for pagination
        self.object_list = object_list

        # Get pagination context
        pagination_context = self.get_paginated_context()

        # Update context
        context.update(pagination_context)

        # Set object list in context with proper name
        context[self.get_context_object_name()] = pagination_context["listed_data"]

        return context
