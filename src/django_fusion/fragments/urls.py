"""URL configuration for django_fusion.fragments.

Wire this module into ``ROOT_URLCONF`` under the desired prefix, e.g.::

    # myproject/urls.py
    from django.urls import path, include

    urlpatterns = [
        path("fragments/", include("django_fusion.fragments.urls")),
        # ...
    ]

The resulting routes are::

    /fragments/<str:fragment_name>/   # path-style request
    /fragments/?q=<fragment_name>      # query-style request

Both accept ``Accept: text/event-stream`` for SSE delivery.
"""
from __future__ import annotations

from django.urls import path

from .views import FragmentRequestView

app_name = "fragments"

urlpatterns = [
    # /fragments/components.home.hero/
    path("<str:fragment_name>/", FragmentRequestView.as_view(), name="render"),
    # /fragments/?q=components.home.sections.hero
    path("", FragmentRequestView.as_view(), name="render_query"),
]
