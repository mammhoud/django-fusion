"""
Legacy 'pipelines' URL namespace — maps old pipelines:* names to allauth views.
Templates using {% url 'pipelines:login' %} etc. will resolve correctly.
"""
from allauth.account.views import LoginView, LogoutView, PasswordResetView, SignupView
from django.urls import path
from django.views.generic import TemplateView

app_name = "pipelines"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", SignupView.as_view(), name="register"),
    path("password/forgot/", PasswordResetView.as_view(), name="password_forgot"),
    # Privacy modal — rendered inline, stub view returns empty
    path("privacy-modal/", TemplateView.as_view(template_name="auth/privacy_modal_content.html"), name="privacy_modal"),
]
