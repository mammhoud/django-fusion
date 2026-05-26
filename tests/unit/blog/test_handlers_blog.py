"""
Unit tests for profile blog management views (BlogPostsView, BlogPostCreateView,
BlogPostEditView, BlogPostDeleteView) from www.apps.accounts.site.blog.

These views use PageHandler (django_osoul) which has complex rendering.
We test the core logic by calling view methods directly with mock requests.
"""
import importlib
import sys
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth import get_user_model
from django.http import HttpRequest, JsonResponse
from django.test import RequestFactory
from www.apps.blog.models import BlogPost

User = get_user_model()


def _import_blog_handlers():
    """
    Import apps.accounts.site.blog directly, bypassing the __init__.py
    which pulls in heavy dependencies (cart, courses, etc.).
    """
    # Stub out the problematic modules before importing
    stubs = [
        "apps.accounts.site.cart",
        "apps.accounts.site.certifications",
        "apps.accounts.site.courses",
        "apps.accounts.site.dashboard",
        "apps.accounts.site.messages",
        "apps.accounts.site.notes",
        "apps.accounts.site.profile",
        "apps.accounts.site.settings",
        "core.CI.services.cart_service",
        "core.CI.services",
        "core.CI.models.cart",
        "core.CI.models",
        "core.CI",
    ]
    for mod in stubs:
        if mod not in sys.modules:
            sys.modules[mod] = MagicMock()

    # Also stub apps.accounts.site.__init__ to avoid star imports
    if "apps.accounts.site" not in sys.modules:
        site_mock = MagicMock()
        sys.modules["apps.accounts.site"] = site_mock

    # Import the blog module directly from the plugins directory
    import importlib.util
    from pathlib import Path
    # Resolve: tests/unit/blog/ → websites/ → ctc-research.com/plugins/profile/views/blog.py
    # (blog views moved from accounts/site/blog.py to profile/views/blog.py per allauth-htmx spec task 2.3)
    _tests_dir = Path(__file__).parent.parent.parent.parent  # websites/
    blog_path = str(_tests_dir / "ctc-research.com" / "plugins" / "profile" / "views" / "blog.py")
    spec = importlib.util.spec_from_file_location("apps.accounts.site.blog", blog_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["apps.accounts.site.blog"] = module
    spec.loader.exec_module(module)

    # Also register as www.apps.accounts.site.blog for tests that import from there
    sys.modules["www.apps.accounts.site.blog"] = module

    return module


# Call at module level to ensure the blog handlers module is importable
# before any test class tries to import from it.
try:
    _blog_handlers = _import_blog_handlers()
    BLOG_HANDLERS_AVAILABLE = True
except (ImportError, RuntimeError, Exception) as _e:
    _blog_handlers = None
    BLOG_HANDLERS_AVAILABLE = False
    import warnings
    warnings.warn(f"test_handlers_blog: could not import blog handlers: {_e}")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

pytestmark = pytest.mark.skipif(
    not BLOG_HANDLERS_AVAILABLE,
    reason="Blog handler views not importable (model conflict or missing module)",
)


@pytest.fixture
def factory():
    return RequestFactory()


@pytest.fixture
def author(db):
    return User.objects.create_user(username="author", password="pass")


@pytest.fixture
def other_user(db):
    return User.objects.create_user(username="other", password="pass")


@pytest.fixture
def post(db, author):
    return BlogPost.objects.create(
        title="My Post",
        slug="my-post",
        author=author,
        content="Content here",
        status="draft",
    )


def _make_request(factory, method, path, user=None, data=None):
    """Helper to build a request with an authenticated user."""
    make = getattr(factory, method)
    req = make(path, data=data or {})
    if user:
        req.user = user
    else:
        from django.contrib.auth.models import AnonymousUser
        req.user = AnonymousUser()
    # Add session support
    from django.contrib.sessions.backends.db import SessionStore
    req.session = SessionStore()
    return req


# ---------------------------------------------------------------------------
# BlogPostsView
# ---------------------------------------------------------------------------

class TestBlogPostsView:
    def _get_view(self):
        from www.apps.accounts.site.blog import BlogPostsView
        view = BlogPostsView()
        return view

    def test_get_context_authenticated_returns_blog_posts(self, db, factory, author, post):
        view = self._get_view()
        req = _make_request(factory, "get", "/profile/blog/", user=author)
        context = view.get_context_data(req)
        assert "blog_posts" in context
        assert post in list(context["blog_posts"])

    def test_get_context_anonymous_returns_empty_context(self, db, factory):
        view = self._get_view()
        req = _make_request(factory, "get", "/profile/blog/")
        context = view.get_context_data(req)
        # Anonymous user: blog_posts not populated
        assert "blog_posts" not in context

    def test_get_context_only_shows_own_posts(self, db, factory, author, other_user, post):
        other_post = BlogPost.objects.create(
            title="Other Post", slug="other-post", author=other_user,
            content="x", status="draft",
        )
        view = self._get_view()
        req = _make_request(factory, "get", "/profile/blog/", user=author)
        context = view.get_context_data(req)
        posts = list(context["blog_posts"])
        assert post in posts
        assert other_post not in posts


# ---------------------------------------------------------------------------
# BlogPostCreateView
# ---------------------------------------------------------------------------

class TestBlogPostCreateView:
    def _get_view(self):
        from www.apps.accounts.site.blog import BlogPostCreateView
        view = BlogPostCreateView()
        return view

    def test_get_anonymous_returns_401(self, factory):
        view = self._get_view()
        req = _make_request(factory, "get", "/profile/blog/create/")
        response = view.get(req)
        assert response.status_code == 401

    def test_get_authenticated_returns_form(self, factory, author):
        view = self._get_view()
        req = _make_request(factory, "get", "/profile/blog/create/", user=author)
        with patch("apps.accounts.site.blog.render") as mock_render:
            mock_render.return_value = MagicMock(status_code=200)
            response = view.get(req)
            assert mock_render.called
            call_args = mock_render.call_args
            assert "form" in call_args[0][2]

    def test_post_anonymous_returns_401(self, factory):
        view = self._get_view()
        req = _make_request(factory, "post", "/profile/blog/create/")
        response = view.post(req)
        assert response.status_code == 401

    def test_post_creates_post_with_author(self, db, factory, author):
        view = self._get_view()
        data = {
            "title": "New Post",
            "content": "Some content",
            "status": "draft",
            "slug": "new-post",
        }
        req = _make_request(factory, "post", "/profile/blog/create/", user=author, data=data)
        with patch("apps.accounts.site.blog.render") as mock_render:
            mock_render.return_value = MagicMock(status_code=200)
            with patch.object(view, "show_notification"):
                view.post(req)
        created = BlogPost.objects.filter(slug="new-post").first()
        assert created is not None
        assert created.author == author


# ---------------------------------------------------------------------------
# BlogPostEditView
# ---------------------------------------------------------------------------

class TestBlogPostEditView:
    def _get_view(self):
        from www.apps.accounts.site.blog import BlogPostEditView
        view = BlogPostEditView()
        return view

    def test_get_anonymous_returns_401(self, factory, post):
        view = self._get_view()
        req = _make_request(factory, "get", f"/profile/blog/{post.id}/edit/")
        response = view.get(req, post_id=post.id)
        assert response.status_code == 401

    def test_get_own_post_returns_form(self, factory, author, post):
        view = self._get_view()
        req = _make_request(factory, "get", f"/profile/blog/{post.id}/edit/", user=author)
        with patch("apps.accounts.site.blog.render") as mock_render:
            mock_render.return_value = MagicMock(status_code=200)
            response = view.get(req, post_id=post.id)
            assert mock_render.called
            call_args = mock_render.call_args
            assert "form" in call_args[0][2]
            assert call_args[0][2]["post"] == post

    def test_get_other_users_post_returns_404(self, factory, other_user, post):
        view = self._get_view()
        req = _make_request(factory, "get", f"/profile/blog/{post.id}/edit/", user=other_user)
        from django.http import Http404
        with pytest.raises(Http404):
            view.get(req, post_id=post.id)

    def test_post_other_users_post_returns_404(self, factory, other_user, post):
        view = self._get_view()
        req = _make_request(factory, "post", f"/profile/blog/{post.id}/edit/", user=other_user)
        from django.http import Http404
        with pytest.raises(Http404):
            view.post(req, post_id=post.id)


# ---------------------------------------------------------------------------
# BlogPostDeleteView
# ---------------------------------------------------------------------------

class TestBlogPostDeleteView:
    def _get_view(self):
        from www.apps.accounts.site.blog import BlogPostDeleteView
        view = BlogPostDeleteView()
        return view

    def test_post_anonymous_returns_401(self, factory, post):
        view = self._get_view()
        req = _make_request(factory, "post", f"/profile/blog/{post.id}/delete/")
        response = view.post(req, post_id=post.id)
        assert response.status_code == 401

    def test_post_deletes_own_post(self, db, factory, author, post):
        view = self._get_view()
        req = _make_request(factory, "post", f"/profile/blog/{post.id}/delete/", user=author)
        with patch("apps.accounts.site.blog.render") as mock_render:
            mock_render.return_value = MagicMock(status_code=200)
            with patch.object(view, "show_notification"):
                view.post(req, post_id=post.id)
        assert not BlogPost.objects.filter(id=post.id).exists()

    def test_post_other_users_post_returns_404(self, factory, other_user, post):
        view = self._get_view()
        req = _make_request(factory, "post", f"/profile/blog/{post.id}/delete/", user=other_user)
        from django.http import Http404
        with pytest.raises(Http404):
            view.post(req, post_id=post.id)
