"""
Connect URL Configuration
"""
from django.urls import path
from .views import (
    SubscribeView, 
    ConfirmSubscriptionView, 
    UnsubscribeView,
    TrackOpenView, 
    TrackClickView
)

app_name = "connect"

urlpatterns = [
    # Newsletter
    path("newsletter/subscribe/", SubscribeView.as_view(), name="subscribe"),
    path("newsletter/confirm/<str:token>/", ConfirmSubscriptionView.as_view(), name="confirm"),
    path("newsletter/unsubscribe/<str:token>/", UnsubscribeView.as_view(), name="unsubscribe"),
    # Tracking
    path("newsletter/track/open/<str:token>/", TrackOpenView.as_view(), name="track_open"),
    path("newsletter/track/click/<str:token>/<str:url_hash>/", TrackClickView.as_view(), name="track_click"),
]
