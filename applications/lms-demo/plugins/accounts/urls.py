# type: ignore NOQA
from django.urls import path

from .apps import AccountsConfig
from .views.allauth import AllauthLoginView, AllauthSignupView

app_name = AccountsConfig.label

urlpatterns = [
    path("auth/login/", AllauthLoginView.as_view(), name="allauth-login"),
    path("auth/signup/", AllauthSignupView.as_view(), name="allauth-signup"),
]
