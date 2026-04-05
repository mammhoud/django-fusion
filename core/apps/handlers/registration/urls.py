"""
Registration URL Configuration
"""

from django.urls import path

from .allauth_views import AllauthLoginView, AllauthSignupView

urlpatterns = [
    path("auth/login/", AllauthLoginView.as_view(), name="allauth-login"),
    path("auth/signup/", AllauthSignupView.as_view(), name="allauth-signup"),
]
