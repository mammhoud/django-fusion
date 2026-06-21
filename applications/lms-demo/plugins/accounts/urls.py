# type: ignore NOQA
from django.urls import path

from .views.auth import AllauthLoginView, AllauthSignupView
from .apps import AccountsConfig

app_name = AccountsConfig.label

urlpatterns = [
    path("auth/login/", AllauthLoginView.as_view(), name="allauth-login"),
    path("auth/signup/", AllauthSignupView.as_view(), name="allauth-signup"),
]
