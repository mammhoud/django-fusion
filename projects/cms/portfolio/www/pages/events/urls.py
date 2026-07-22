from django.urls import path

from .views import EventDetailView, event_list_view

app_name = "events"

urlpatterns = [
    path("", event_list_view, name="list"),
    path("<int:pk>/", EventDetailView.as_view(), name="detail"),
]
