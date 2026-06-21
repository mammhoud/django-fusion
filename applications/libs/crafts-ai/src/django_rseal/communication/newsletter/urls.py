from django.urls import path
from .subscription import ConfirmSubscriptionView, SubscribeView, UnsubscribeView

app_name = "newsletter"

urlpatterns = [
    path("subscribe/", SubscribeView.as_view(), name="subscribe"),
    path("confirm/<str:token>/", ConfirmSubscriptionView.as_view(), name="confirm"),
    path("unsubscribe/<str:token>/", UnsubscribeView.as_view(), name="unsubscribe"),
]
