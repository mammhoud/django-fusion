"""
Integration tests for blog comment, like, and search views.
"""
import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from www.apps.blog.models import BlogComment, BlogPost

User = get_user_model()


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="commenter", password="pass")


@pytest.fixture
def other_user(db):
    return User.objects.create_user(username="other", password="pass")


@pytest.fixture
def published_post(db, user):
    return BlogPost.objects.create(
        title="Test Post",
        slug="test-post",
        author=user,
        content="Some content",
        status="published",
    )


@pytest.fixture
def draft_post(db, user):
    return BlogPost.objects.create(
        title="Draft Post",
        slug="draft-post",
        author=user,
        content="Draft content",
        status="draft",
    )


# ---------------------------------------------------------------------------
# AddCommentView
# ---------------------------------------------------------------------------

class TestAddCommentView:
    def test_post_creates_unapproved_comment(self, client, user, published_post):
        client.force_login(user)
        url = reverse("blog:add_comment", kwargs={"slug": published_post.slug})
        response = client.post(url, {"content": "Great post!"})
        assert response.status_code == 200
        comment = BlogComment.objects.get(post=published_post)
        assert comment.content == "Great post!"
        assert comment.is_approved is False
        assert comment.author == user

    def test_post_empty_content_returns_422(self, client, user, published_post):
        client.force_login(user)
        url = reverse("blog:add_comment", kwargs={"slug": published_post.slug})
        response = client.post(url, {"content": ""})
        assert response.status_code == 422
        assert BlogComment.objects.filter(post=published_post).count() == 0

    def test_post_requires_login(self, client, published_post):
        url = reverse("blog:add_comment", kwargs={"slug": published_post.slug})
        response = client.post(url, {"content": "Hello"})
        # Should redirect to login
        assert response.status_code in (302, 403)

    def test_post_to_draft_returns_404(self, client, user, draft_post):
        client.force_login(user)
        url = reverse("blog:add_comment", kwargs={"slug": draft_post.slug})
        response = client.post(url, {"content": "Hello"})
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# BlogPostLikeView
# ---------------------------------------------------------------------------

class TestBlogPostLikeView:
    def test_post_increments_likes_count(self, client, user, published_post):
        initial_likes = published_post.likes_count
        client.force_login(user)
        url = reverse("blog:like_post", kwargs={"slug": published_post.slug})
        response = client.post(url)
        assert response.status_code == 200
        published_post.refresh_from_db()
        assert published_post.likes_count == initial_likes + 1

    def test_post_requires_login(self, client, published_post):
        url = reverse("blog:like_post", kwargs={"slug": published_post.slug})
        response = client.post(url)
        assert response.status_code in (302, 403)

    def test_post_to_draft_returns_404(self, client, user, draft_post):
        client.force_login(user)
        url = reverse("blog:like_post", kwargs={"slug": draft_post.slug})
        response = client.post(url)
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# BlogSearchView
# ---------------------------------------------------------------------------

class TestBlogSearchView:
    def test_get_returns_200(self, client, db):
        url = reverse("blog:search")
        response = client.get(url)
        assert response.status_code == 200

    def test_get_returns_search_results(self, client, published_post):
        url = reverse("blog:search") + "?q=Test"
        response = client.get(url)
        assert response.status_code == 200
        posts = list(response.context["posts"])
        assert published_post in posts

    def test_get_filters_by_q(self, client, user, published_post):
        other = BlogPost.objects.create(
            title="Unrelated", slug="unrelated", author=user,
            content="Nothing here", status="published",
        )
        url = reverse("blog:search") + "?q=Test+Post"
        response = client.get(url)
        posts = list(response.context["posts"])
        assert published_post in posts
        assert other not in posts

    def test_get_filters_by_tag(self, client, user, published_post):
        from www.apps.blog.models import BlogTag
        tag = BlogTag.objects.create(name="Python", slug="python")
        published_post.tags.add(tag)
        other = BlogPost.objects.create(
            title="Other", slug="other", author=user, content="x", status="published"
        )
        url = reverse("blog:search") + "?tag=python"
        response = client.get(url)
        posts = list(response.context["posts"])
        assert published_post in posts
        assert other not in posts

    def test_get_filters_by_category(self, client, user, published_post):
        from www.apps.blog.models import BlogCategory
        cat = BlogCategory.objects.create(name="Tech", slug="tech")
        published_post.categories.add(cat)
        other = BlogPost.objects.create(
            title="Other", slug="other", author=user, content="x", status="published"
        )
        url = reverse("blog:search") + "?category=tech"
        response = client.get(url)
        posts = list(response.context["posts"])
        assert published_post in posts
        assert other not in posts

    def test_search_query_in_context(self, client, published_post):
        url = reverse("blog:search") + "?q=hello"
        response = client.get(url)
        assert response.context["search_query"] == "hello"

    def test_excludes_draft_posts(self, client, draft_post):
        url = reverse("blog:search") + "?q=Draft"
        response = client.get(url)
        posts = list(response.context["posts"])
        assert draft_post not in posts
