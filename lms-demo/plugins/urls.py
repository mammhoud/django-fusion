"""Root URL patterns for lms-demo plugins."""
from allauth.account.views import LoginView, LogoutView, PasswordResetView, SignupView
from importlib.util import find_spec
from django.urls import include, path
from django.views.generic import TemplateView

app_name = "plugins"

urlpatterns = [
    path("accounts/", include("allauth.urls")),
    path("accounts/", include("plugins.accounts.urls", namespace="accounts")),
    path("profile/", include("plugins.profile.urls", namespace="profile")),
    path("courses/", include("plugins.lms.urls", namespace="lms")),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/register/", SignupView.as_view(), name="register"),
    path("auth/password/forgot/", PasswordResetView.as_view(), name="password_forgot"),
    path(
        "auth/privacy-modal/",
        TemplateView.as_view(template_name="auth/privacy_modal_content.html"),
        name="privacy_modal",
    ),
]

if find_spec("plugins.products") is not None and find_spec("plugins.products.urls") is not None:
    urlpatterns.append(path("", include("plugins.products.urls", namespace="products")))
