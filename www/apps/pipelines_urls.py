"""
Legacy 'pipelines' URL namespace — maps old pipelines:* names to allauth views.
Templates using {% url 'pipelines:login' %} etc. will resolve correctly.
"""
from allauth.account.views import LoginView, LogoutView, SignupView
from django.urls import path

app_name = "pipelines"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", SignupView.as_view(), name="register"),
]
