"""Search views for domain."""
import logging

from django.views.generic import View

logger = logging.getLogger(__name__)


class BaseSearchView(View):
    """Base search view."""
    model = None
    htmx_page = ""
    template_name = ""
    input_name = "q"

    def get_queryset(self):
        return self.model.objects.all() if self.model else []

    def format_results(self, queryset):
        return queryset

    def filter_queryset(self, queryset, search_input):
        return queryset


class SearchView(BaseSearchView):
    """Generic search view."""
    pass


class CourseSearchView(BaseSearchView):
    """Course search view."""
    pass


class CourseFilterView(BaseSearchView):
    """Course filter view."""
    pass
