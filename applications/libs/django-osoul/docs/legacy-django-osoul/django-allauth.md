# django-allauth

[django-allauth](https://docs.allauth.org/) provides account management, email verification, password reset, and social login.

## Installation

```python
INSTALLED_APPS = [
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.facebook",
]

MIDDLEWARE = [
    ...
    "allauth.account.middleware.AccountMiddleware",
]
```

## Custom Adapter

Both sites use `AuthHTMXAdapter` to integrate allauth with the HTMX fragment system.

## Key Settings

```python
ACCOUNT_ADAPTER = "plugins.accounts.adapters.AuthHTMXAdapter"
SOCIALACCOUNT_ADAPTER = "plugins.accounts.adapters.AuthHTMXSocialAccountAdapter"
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_LOGIN_METHODS = ["email"]
```

## URL Configuration

```python
# plugins/urls.py
urlpatterns = [
    path("accounts/", include("allauth.urls")),  # allauth built-in views
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    ...
]
```

## Template Override

allauth templates are overridden via `AuthHTMXAdapter.TEMPLATE_MAP`.
