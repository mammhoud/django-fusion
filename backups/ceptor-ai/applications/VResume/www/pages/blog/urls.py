"""
Blog URL Configuration
"""
from django.urls import path
from .views import (
    BlogPostDetailView, 
    BlogPostListView, 
    blog_search,
    post_preview, 
    send_newsletter,
    TrackReadView, 
    track_read_simple
)

app_name = "blog"

urlpatterns = [
    path("", BlogPostListView.as_view(), name="list"),
    path("search/", blog_search, name="search"),
    path("preview/<int:pk>/", post_preview, name="post_preview"),
    path("send-newsletter/<int:pk>/", send_newsletter, name="send_newsletter"),
    path("<slug:slug>/", BlogPostDetailView.as_view(), name="detail"),
    # Tracking endpoints
    path("track-read/<int:post_id>/", TrackReadView.as_view(), name="track_read"),
    path("track-read-simple/<int:post_id>/", track_read_simple, name="track_read_simple"),
]
