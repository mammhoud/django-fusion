"""
Pytest configuration for structa top-level tests.

Configures a minimal Django environment with SQLite in-memory database
so that tests can use @pytest.mark.django_db without the full project
settings stack (Dynaconf, Wagtail, etc.).
"""
from django.conf import settings


def pytest_configure(config):
    """Configure minimal Django settings for the test suite."""
    if not settings.configured:
        settings.configure(
            INSTALLED_APPS=[
                "django.contrib.contenttypes",
                "django.contrib.auth",
                "django.contrib.admin",
                "django.contrib.sites",
                "django.contrib.sessions",
                "allauth",
                "allauth.account",
                "allauth.socialaccount",
                "wagtail",
                "wagtail.images",
                "wagtail.documents",
                "wagtail.snippets",
                "wagtail.search",
                "wagtail.admin",
                "wagtail.contrib.settings",
                "taggit",
                "modelcluster",
                "apps.handlers",
                "apps.handlers.registration",
            ],
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": ":memory:",
                }
            },
            SECRET_KEY="test-secret-key-for-structa-tests-at-least-50-chars-long!!",
            USE_TZ=True,
            DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
            STATIC_URL="/static/",
            MEDIA_URL="/media/",
            WAGTAIL_SITE_NAME="Test",
            SITE_ID=1,
            AUTHENTICATION_BACKENDS=[
                "django.contrib.auth.backends.ModelBackend",
                "allauth.account.auth_backends.AuthenticationBackend",
            ],
            ACCOUNT_EMAIL_VERIFICATION="none",
            ACCOUNT_AUTHENTICATION_METHOD="username",
            ACCOUNT_EMAIL_REQUIRED=False,
            TEMPLATES=[
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "DIRS": [],
                    "APP_DIRS": False,
                    "OPTIONS": {
                        "context_processors": [
                            "django.template.context_processors.request",
                            "django.contrib.auth.context_processors.auth",
                            "django.contrib.messages.context_processors.messages",
                        ],
                        "loaders": [
                            (
                                "django.template.loaders.locmem.Loader",
                                {
                                    "registration/fragments/login_form.html": "<form></form>",
                                    "registration/fragments/register_form.html": "<form></form>",
                                    "registration/login.html": "<html></html>",
                                    "registration/register.html": "<html></html>",
                                },
                            )
                        ],
                    },
                }
            ],
            SESSION_ENGINE="django.contrib.sessions.backends.db",
            MIDDLEWARE=[
                "django.contrib.sessions.middleware.SessionMiddleware",
                "django.contrib.auth.middleware.AuthenticationMiddleware",
                "allauth.account.middleware.AccountMiddleware",
            ],
        )
