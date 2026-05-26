"""Root URL patterns for www.apps — served from plugins/."""
from allauth.account.views import LoginView, LogoutView, PasswordResetView, SignupView
from django.urls import include, path
from django.views.generic import TemplateView

app_name = "plugins"

urlpatterns = [
    path("accounts/", include("allauth.urls")),
    # Plugin namespaces
    path("accounts/", include("plugins.accounts.urls", namespace="accounts")),
    path("profile/", include("plugins.profile.urls", namespace="profile")),
    path("", include("plugins.products.urls", namespace="products")),
    # Auth URL aliases — merged from legacy 'pipelines' namespace
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/register/", SignupView.as_view(), name="register"),
    path("auth/password/forgot/", PasswordResetView.as_view(), name="password_forgot"),
    # Privacy modal — rendered inline, stub view returns empty
    path("auth/privacy-modal/", TemplateView.as_view(template_name="auth/privacy_modal_content.html"), name="privacy_modal"),
]
