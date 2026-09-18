from django.urls import path

from apps.core.api import resource_api

urlpatterns = [
    path("campaigns/", resource_api, {"resource": "campaigns"}, name="campaigns_api"),
    path("channels/", resource_api, {"resource": "channels"}, name="channels_api"),
    path("posts/", resource_api, {"resource": "posts"}, name="posts_api"),
    path("calendar/", resource_api, {"resource": "posts"}, name="calendar_api"),
]
