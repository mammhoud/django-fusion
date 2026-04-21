"""
Registration URL Configuration
"""

from django.urls import path

from .allauth_views import AllauthLoginView, AllauthSignupView
from .views import CreatePasswordView, RegisterView, RegistrationSuccessView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register-account"),
    path(
        "create-password/<str:token>/",
        CreatePasswordView.as_view(),
        name="create-password",
    ),
    path(
        "registration-success/",
        RegistrationSuccessView.as_view(),
        name="registration-success",
    ),
    path("allauth/login/", AllauthLoginView.as_view(), name="allauth-login"),
    path("allauth/signup/", AllauthSignupView.as_view(), name="allauth-signup"),
]
