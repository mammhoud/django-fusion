"""
Pytest configuration for blog app tests.

Sets up a minimal Django environment with only the apps needed for blog tests,
avoiding the complex dependency chain of apps.pages and ceptor_ai.
"""
import sys
from unittest.mock import MagicMock

from django.conf import settings


def pytest_configure(config):
    """Configure minimal Django settings for blog tests."""
    if settings.configured:
        return

    # Mock the apps.pages dependency chain before Django setup.
    # apps.blog.models.pages imports BasePage from www.apps.pages which pulls in
    # ceptor_ai and other heavy dependencies not needed for blog unit tests.
    _mock_pages_deps()

    settings.configure(
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "django.contrib.admin",
            "django.contrib.sites",
            "django.contrib.staticfiles",
            "django.contrib.sessions",
            "wagtail",
            "wagtail.images",
            "wagtail.documents",
            "wagtail.snippets",
            "wagtail.search",
            "wagtail.admin",
            "wagtail.contrib.settings",
            "taggit",
            "modelcluster",
            "apps.blog",
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        SECRET_KEY="test-secret-key-for-blog-tests-at-least-50-chars-long!!",
        USE_TZ=True,
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        STATIC_URL="/static/",
        MEDIA_URL="/media/",
        STORAGES={
            "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
            "staticfiles": {
                "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"
            },
        },
        WAGTAIL_SITE_NAME="Test",
        SITE_ID=1,
        ROOT_URLCONF="apps.blog.tests.urls",
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
                                "blog/blog_list.html": (
                                    "{% for post in posts %}{{ post.title }}{% endfor %}"
                                ),
                                "blog/blog_index.html": (
                                    "{% for post in posts %}{{ post.title }}{% endfor %}"
                                ),
                                "blog/blog_detail.html": "{{ post.title }}",
                                "blog/tags/tag_list.html": (
                                    "{% for tag in tags %}{{ tag.name }}{% endfor %}"
                                ),
                                "blog/tags/tag_form.html": "<form></form>",
                                "blog/tags/tag_confirm_delete.html": "<form></form>",
                                "blog/tags/tag_cleanup.html": (
                                    "{% for tag in unused_tags %}{{ tag.name }}{% endfor %}"
                                ),
                                "blog/components/comments.html": (
                                    "{% for c in comments %}{{ c.content }}{% endfor %}"
                                ),
                                "blog/components/search_results.html": (
                                    "{% for post in posts %}{{ post.title }}{% endfor %}"
                                ),
                                "blog/profile/post_form.html": "<form></form>",
                                "blog/profile/post_list_fragment.html": (
                                    "{% for post in blog_posts %}{{ post.title }}{% endfor %}"
                                ),
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
            "django.contrib.messages.middleware.MessageMiddleware",
        ],
        MESSAGE_STORAGE="django.contrib.messages.storage.cookie.CookieStorage",
    )


def _mock_pages_deps():
    """
    Mock apps.pages and its deep dependency chain.

    We provide a minimal BasePage stand-in with content_panels and
    search_fields so that BlogIndexPage can be defined without requiring
    the full apps.pages / ceptor_ai stack.
    """
    class _MockBasePage:
        """Minimal stand-in for BasePage used only during test imports."""
        content_panels = []
        search_fields = []

        class Meta:
            abstract = True

    pages_mock = MagicMock()
    pages_mock.BasePage = _MockBasePage

    sys.modules.setdefault("apps.pages", MagicMock())
    sys.modules.setdefault("apps.pages.models", MagicMock())
    sys.modules.setdefault("apps.pages.models.pages", MagicMock())
    sys.modules["apps.pages.models.pages.base"] = pages_mock

    # Mock core.CI and apps.accounts.site to prevent import of heavy
    # dependencies (cart, courses, etc.) that require settings.PROFILE_MODEL
    # and other production-only settings.
    for mod in [
        "core.CI",
        "core.CI.models",
        "core.CI.models.cart",
        "core.CI.services",
        "core.CI.services.cart_service",
        "apps.accounts.site.cart",
        "apps.accounts.site.certifications",
        "apps.accounts.site.courses",
        "apps.accounts.site.dashboard",
        "apps.accounts.site.messages",
        "apps.accounts.site.notes",
        "apps.accounts.site.profile",
        "apps.accounts.site.settings",
    ]:
        sys.modules.setdefault(mod, MagicMock())

    # Stub apps.accounts.site itself so its __init__ star-imports are skipped
    if "apps.accounts.site" not in sys.modules:
        import types
        site_pkg = types.ModuleType("apps.accounts.site")
        site_pkg.__path__ = []  # make it look like a package
        site_pkg.__package__ = "apps.accounts.site"
        sys.modules["apps.accounts.site"] = site_pkg
