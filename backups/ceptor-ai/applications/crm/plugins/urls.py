"""Root URL patterns for the CRM plugins."""
from django.urls import include, path
from allauth.account.views import LoginView, LogoutView

app_name = "plugins"

urlpatterns = [
    # allauth auth aliases
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    # Plugin namespaces
    path("crm/accounts/", include("plugins.accounts_app.urls", namespace="crm_accounts")),
]
