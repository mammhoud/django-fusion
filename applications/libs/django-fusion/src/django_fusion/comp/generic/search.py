"""Search mixin for list views."""


class SearchableViewMixin:
    """Mixin that adds search capability to list views."""

    search_fields: list = []
    search_param: str = "q"

    def get_search_query(self):
        return self.request.GET.get(self.search_param, "").strip()

    def get_queryset(self):
        qs = super().get_queryset()
        query = self.get_search_query()
        if query and self.search_fields:
            from django.db.models import Q
            filters = Q()
            for field in self.search_fields:
                filters |= Q(**{f"{field}__icontains": query})
            qs = qs.filter(filters)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["search_query"] = self.get_search_query()
        return ctx
