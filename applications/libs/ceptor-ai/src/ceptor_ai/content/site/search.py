
from django.http import HttpRequest
from django.shortcuts import render

from core.commons.views import BaseSearchView
from django_fusion.comp.views.includes import PaginatedBaseView

from ..models import Course  # Ensure you have this model


class CourseSearchView(BaseSearchView):
    """
    Search view specifically for courses.
    result = {
            "data__title": getattr(item, "title", "No Title"),
                "data__rating_count": getattr(item, "rating_count", 0),
                "data__price": getattr(item, "price", 0),
                "data__old_price": getattr(item, "old_price", 0),
            }
    """

    model = Course
    htmx_page = "front/courses/partials/searchbar_results.html"
    input_name = "search_bar__input"

    def format_results(self, queryset) -> list[dict]:
        """
        Enhances the default result format to include course-specific fields.
        """
        return queryset


class CourseFilterView(BaseSearchView):
    model = Course
    htmx_page = "front/courses/partials/index_courses.html"

    def format_results(self, queryset) -> list[dict]:
        """
        Enhances the default result format to include course-specific fields.
        """
        return queryset

    def filter_queryset(self, queryset, search_input: str):
        """
        Filters the given queryset based on the search input.
        """
        return queryset.filter(specialization__slug=search_input)

    def get(self, request: HttpRequest, *args, **kwargs):
        """
        Handles GET requests and performs the search.
        """

        context = self.get_context_data(**kwargs)
        queryset = self.get_queryset()
        if queryset is not None:
            filtered_queryset = self.filter_queryset(queryset, search_input)
            context["data_list"] = self.format_results(filtered_queryset)

        front_view = PaginatedBaseView()
        context = front_view.extend_context(request, context)

        if request.is_htmx:
            return render(request, self.htmx_page, context)
        return render(request, self.template_name, context)
