"""URL patterns for event views (ctc-research)."""

from django.urls import path

from .views.events import EventDetailView, EventListView

app_name = "plugins"

urlpatterns = [
    path("", EventListView.as_view(), name="event-list"),
    path("<int:pk>/", EventDetailView.as_view(), name="event-detail"),
]
