"""
Pytest configuration for blog app tests.

Sets up a minimal Django environment with only the apps needed for blog tests,
avoiding the complex dependency chain of apps.pages and ceptor_ai.
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from django.conf import settings

_FIXTURES_DIR = Path(__file__).parent.parent.parent / "assets" / "fixtures"

# ---------------------------------------------------------------------------
# Django settings bootstrap
# ---------------------------------------------------------------------------

_TEMPLATES = [
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
                # In-memory templates take priority — override real app templates
                (
                    "django.template.loaders.locmem.Loader",
                    {
                        # Base layouts
                        "base_page.html": "{% block content %}{% endblock %}",
                        "base.html": "{% block content %}{% endblock %}",
                        # Blog list / index — override real template that extends base_page.html
                        "blog/blog_list.html": (
                            "{% for post in posts %}<article>{{ post.title }}</article>{% endfor %}"
                        ),
                        "blog/blog_index.html": (
                            "{% for post in posts %}<article>{{ post.title }}</article>{% endfor %}"
                        ),
                        # Blog detail
                        "blog/blog_detail.html": "<h1>{{ post.title }}</h1>",
                        # Tag management
                        "blog/tags/tag_list.html": (
                            "{% for tag in tags %}<li>{{ tag.name }}</li>{% endfor %}"
                        ),
                        "blog/tags/tag_form.html": (
                            "<form method='post'>{% csrf_token %}{{ form.as_p }}"
                            "<button>Save</button></form>"
                        ),
                        "blog/tags/tag_confirm_delete.html": (
                            "<form method='post'>{% csrf_token %}<button>Delete</button></form>"
                        ),
                        "blog/tags/tag_cleanup.html": (
                            "{% for tag in unused_tags %}<li>{{ tag.name }}</li>{% endfor %}"
                        ),
                        # Components
                        "blog/components/comments.html": (
                            "{% for c in comments %}<div>{{ c.content }}</div>{% endfor %}"
                        ),
                        "blog/components/search_results.html": (
                            "{% for post in posts %}<article>{{ post.title }}</article>{% endfor %}"
                        ),
                        # Profile / legacy fragments
                        "blog/profile/post_form.html": "<form></form>",
                        "blog/profile/post_list_fragment.html": (
                            "{% for post in blog_posts %}{{ post.title }}{% endfor %}"
                        ),
                        # HTMX fragment component templates
                        # Keys use the path form: fragment_name.replace('.', '/') + '.html'
                        "blog/fragments/post_list.html": (
                            "{% for post in object_list %}"
                            "<article>{{ post.title }}</article>"
                            "{% endfor %}"
                        ),
                        "blog/fragments/post_create_form.html": (
                            "<form method='post' hx-post='.' class='htmx-post'>"
                            "{% csrf_token %}"
                            "{{ form.as_p }}"
                            "<button type='submit'>Save</button>"
                            "</form>"
                        ),
                        "blog/fragments/post_create_success.html": (
                            "<div id='post-create-success'>Created: {{ post.title }}</div>"
                        ),
                        "blog/fragments/post_count.html": "<span>{{ post_count }}</span>",
                    },
                ),
                # Fall back to real app templates for anything not overridden above
                "django.template.loaders.app_directories.Loader",
            ],
        },
    }
]


def pytest_configure(config):
    """Configure minimal Django settings for blog tests."""
    if settings.configured:
        return

    # Mock the apps.pages dependency chain before Django setup.
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
        ROOT_URLCONF="tests.unit.blog.urls",
        TEMPLATES=_TEMPLATES,
        SESSION_ENGINE="django.contrib.sessions.backends.db",
        MIDDLEWARE=[
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
        ],
        MESSAGE_STORAGE="django.contrib.messages.storage.cookie.CookieStorage",
    )


# ---------------------------------------------------------------------------
# Dependency mocking
# ---------------------------------------------------------------------------

def _mock_pages_deps():
    """Mock apps.pages and its deep dependency chain."""

    class _MockBasePage:
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

    if "apps.accounts.site" not in sys.modules:
        import types
        site_pkg = types.ModuleType("apps.accounts.site")
        site_pkg.__path__ = []
        site_pkg.__package__ = "apps.accounts.site"
        sys.modules["apps.accounts.site"] = site_pkg


# ---------------------------------------------------------------------------
# Fixture helpers — load JSON fixtures from tests/assets/fixtures/
# ---------------------------------------------------------------------------

@pytest.fixture
def load_blog_fixtures(db):
    """Load the full blog fixture set (users → categories → tags → posts → comments)."""
    from django.core.management import call_command
    for name in ("blog_users", "blog_categories", "blog_tags", "blog_posts", "blog_comments"):
        call_command("loaddata", str(_FIXTURES_DIR / f"{name}.json"), verbosity=0)


@pytest.fixture
def load_blog_full(db):
    """Load the self-contained blog_full fixture (pk=10+, no external deps)."""
    from django.core.management import call_command
    call_command("loaddata", str(_FIXTURES_DIR / "blog_full.json"), verbosity=0)


@pytest.fixture
def fixture_staff_user(load_blog_full):
    """Staff user from blog_full fixture (pk=10)."""
    from django.contrib.auth import get_user_model
    return get_user_model().objects.get(pk=10)


@pytest.fixture
def fixture_published_post(load_blog_full):
    """First published post from blog_full fixture (pk=10)."""
    from apps.blog.models import BlogPost
    return BlogPost.objects.get(pk=10)


@pytest.fixture
def fixture_draft_post(load_blog_full):
    """Draft post from blog_full fixture (pk=12)."""
    from apps.blog.models import BlogPost
    return BlogPost.objects.get(pk=12)


@pytest.fixture
def fixture_tech_category(load_blog_full):
    """Tech category from blog_full fixture (pk=10)."""
    from apps.blog.models import BlogCategory
    return BlogCategory.objects.get(pk=10)


@pytest.fixture
def fixture_python_tag(load_blog_full):
    """Python tag from blog_full fixture (pk=10)."""
    from apps.blog.models import BlogTag
    return BlogTag.objects.get(pk=10)


@pytest.fixture
def fixture_unused_tag(load_blog_full):
    """Unused tag from blog_full fixture (pk=12)."""
    from apps.blog.models import BlogTag
    return BlogTag.objects.get(pk=12)
