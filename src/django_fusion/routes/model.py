from django.urls import path

from django_fusion.contrib import DEFAULT, has_object_perm
from django_fusion.contrib import ViewProp as viewprop
from .base import Viewset
from django_fusion.fragments.generic.list import ListModelView


class BaseModelViewset(Viewset):
    model = DEFAULT
    queryset = DEFAULT

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        assert self.model is not DEFAULT, f"No model specified for {self}"
        # Defer model._meta access by using a sentinel value
        # The actual model will be set before any view is created

    def __getattribute__(self, name):
        attr = super(BaseModelViewset, self).__getattribute__(name)
        if name == "title" and attr is None:
            # Defer model._meta access until model is actually set
            model = super(BaseModelViewset, self).__getattribute__("model")
            if model is None or model is DEFAULT:
                return None  # Return None instead of crashing
            return model._meta.verbose_name_plural.capitalize()
        elif name == "app_name" and attr is None:
            model = super(BaseModelViewset, self).__getattribute__("model")
            if model is None or model is DEFAULT:
                return None
            return model._meta.object_name.lower()
        return attr

    def filter_kwargs(self, view_class, **kwargs):
        model = super(BaseModelViewset, self).__getattribute__("model")
        # Defer to subclass for model resolution if needed
        if model is None:
            model = getattr(self, "_resolve_model", lambda: None)()
        return super().filter_kwargs(
            view_class,
            **{"model": model, "viewset": self, "queryset": self.queryset, **kwargs},
        )

    @property
    def index_path(self):
        return path("", self.list_view, name="index")

    """
    List
    """
    list_view_class = ListModelView
    list_columns = DEFAULT
    list_paginate_by = DEFAULT
    list_object_link_columns = DEFAULT
    list_page_actions = DEFAULT
    list_filterset_class = DEFAULT
    list_filterset_initial = DEFAULT
    list_filter_fields = DEFAULT
    list_search_fields = DEFAULT
    list_ordering_fields = DEFAULT

    def has_view_permission(self, user, obj=None):
        if has_object_perm(user, "view", self.model, obj=obj):
            return True
        if hasattr(self, "has_change_permission"):
            return self.has_change_permission(user, obj=obj)
        return False

    def get_list_page_actions(self, request, *actions):
        return (*self.list_page_actions, *actions)

    def get_list_view_kwargs(self, **kwargs):
        view_kwargs = {
            "columns": self.list_columns,
            "paginate_by": self.list_paginate_by,
            "object_link_columns": self.list_object_link_columns,
            "filterset_class": self.list_filterset_class,
            "filterset_initial": self.list_filterset_initial,
            "filter_fields": self.list_filter_fields,
            "search_fields": self.list_search_fields,
            "ordering": self.list_ordering_fields,
            **self.list_view_kwargs,
            **kwargs,
        }
        return self.filter_kwargs(self.list_view_class, **view_kwargs)

    @viewprop
    def list_view_kwargs(self):
        return {}

    @viewprop
    def list_view(self):
        return self.list_view_class.as_view(**self.get_list_view_kwargs())

    @property
    def list_path(self):
        return path("", self.list_view, name="list")
