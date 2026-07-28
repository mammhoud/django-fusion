"""
Unit tests for BlogPostListView tag filtering.
"""
import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from www.apps.blog.models import BlogPost, BlogTag

User = get_user_model()


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="viewer", password="pass")


@pytest.fixture
def tag_python(db):
    return BlogTag.objects.create(name="Python", slug="python")


@pytest.fixture
def tag_django(db):
    return BlogTag.objects.create(name="Django", slug="django")


@pytest.fixture
def post_python(db, user, tag_python):
    post = BlogPost.objects.create(
        title="Python Post",
        slug="python-post",
        author=user,
        content="About Python",
        status="published",
    )
    post.tags.add(tag_python)
    return post


@pytest.fixture
def post_django(db, user, tag_django):
    post = BlogPost.objects.create(
        title="Django Post",
        slug="django-post",
        author=user,
        content="About Django",
        status="published",
    )
    post.tags.add(tag_django)
    return post


@pytest.fixture
def post_both(db, user, tag_python, tag_django):
    post = BlogPost.objects.create(
        title="Both Post",
        slug="both-post",
        author=user,
        content="About Python and Django",
        status="published",
    )
    post.tags.add(tag_python, tag_django)
    return post


@pytest.fixture
def post_draft(db, user, tag_python):
    post = BlogPost.objects.create(
        title="Draft Post",
        slug="draft-post",
        author=user,
        content="Draft",
        status="draft",
    )
    post.tags.add(tag_python)
    return post


# ---------------------------------------------------------------------------
# BlogPostListView - clean URL tag filtering (/blog/tag/<slug>/)
# ---------------------------------------------------------------------------

class TestBlogPostListViewTagURL:
    def test_clean_url_returns_200(self, client, db, tag_python, post_python):
        url = reverse("blog:tag_filter", kwargs={"tag_slug": "python"})
        response = client.get(url)
        assert response.status_code == 200

    def test_clean_url_filters_to_tagged_posts(self, client, db, post_python, post_django, tag_python):
        url = reverse("blog:tag_filter", kwargs={"tag_slug": "python"})
        response = client.get(url)
        posts = list(response.context["posts"])
        assert post_python in posts
        assert post_django not in posts

    def test_clean_url_excludes_draft_posts(self, client, db, post_python, post_draft, tag_python):
        url = reverse("blog:tag_filter", kwargs={"tag_slug": "python"})
        response = client.get(url)
        posts = list(response.context["posts"])
        assert post_draft not in posts

    def test_clean_url_sets_current_tag_in_context(self, client, db, tag_python, post_python):
        url = reverse("blog:tag_filter", kwargs={"tag_slug": "python"})
        response = client.get(url)
        assert response.context["current_tag"] == "python"

    def test_clean_url_sets_current_tag_obj_in_context(self, client, db, tag_python, post_python):
        url = reverse("blog:tag_filter", kwargs={"tag_slug": "python"})
        response = client.get(url)
        assert response.context["current_tag_obj"] == tag_python

    def test_nonexistent_tag_slug_returns_empty_list(self, client, db, post_python):
        url = reverse("blog:tag_filter", kwargs={"tag_slug": "nonexistent"})
        response = client.get(url)
        assert response.status_code == 200
        assert list(response.context["posts"]) == []

    def test_nonexistent_tag_slug_sets_tag_obj_none(self, client, db, post_python):
        url = reverse("blog:tag_filter", kwargs={"tag_slug": "nonexistent"})
        response = client.get(url)
        assert response.context["current_tag_obj"] is None


# ---------------------------------------------------------------------------
# BlogPostListView - query param tag filtering (/blog/?tag=<slug>)
# ---------------------------------------------------------------------------

class TestBlogPostListViewTagQueryParam:
    def test_query_param_returns_200(self, client, db, tag_python, post_python):
        url = reverse("blog:list") + "?tag=python"
        response = client.get(url)
        assert response.status_code == 200

    def test_query_param_filters_to_tagged_posts(self, client, db, post_python, post_django):
        url = reverse("blog:list") + "?tag=python"
        response = client.get(url)
        posts = list(response.context["posts"])
        assert post_python in posts
        assert post_django not in posts

    def test_query_param_excludes_draft_posts(self, client, db, post_python, post_draft):
        url = reverse("blog:list") + "?tag=python"
        response = client.get(url)
        posts = list(response.context["posts"])
        assert post_draft not in posts

    def test_query_param_sets_current_tag_in_context(self, client, db, tag_python, post_python):
        url = reverse("blog:list") + "?tag=python"
        response = client.get(url)
        assert response.context["current_tag"] == "python"

    def test_no_tag_param_returns_all_published(self, client, db, post_python, post_django, post_draft):
        url = reverse("blog:list")
        response = client.get(url)
        posts = list(response.context["posts"])
        assert post_python in posts
        assert post_django in posts
        assert post_draft not in posts

    def test_multi_tag_post_appears_in_both_filters(self, client, db, post_both):
        for slug in ["python", "django"]:
            url = reverse("blog:list") + f"?tag={slug}"
            response = client.get(url)
            assert post_both in list(response.context["posts"])


# ---------------------------------------------------------------------------
# BlogPostListView - context data
# ---------------------------------------------------------------------------

class TestBlogPostListViewContext:
    def test_context_contains_tags(self, client, db, post_python, tag_python):
        url = reverse("blog:list")
        response = client.get(url)
        assert "tags" in response.context

    def test_context_contains_categories(self, client, db):
        url = reverse("blog:list")
        response = client.get(url)
        assert "categories" in response.context

    def test_search_query_in_context(self, client, db, post_python):
        url = reverse("blog:list") + "?q=Python"
        response = client.get(url)
        assert response.context["search_query"] == "Python"

    def test_search_filters_posts(self, client, db, post_python, post_django):
        url = reverse("blog:list") + "?q=Python"
        response = client.get(url)
        posts = list(response.context["posts"])
        assert post_python in posts
        assert post_django not in posts


# ---------------------------------------------------------------------------
# BlogPostListView - clean URL category filtering (/blog/category/<slug>/)
# ---------------------------------------------------------------------------

from www.apps.blog.models import BlogCategory  # noqa: E402 (appended section)


@pytest.fixture
def category_research(db):
    return BlogCategory.objects.create(name="Research", slug="research")


@pytest.fixture
def category_news(db):
    return BlogCategory.objects.create(name="News", slug="news")


@pytest.fixture
def post_research(db, user, category_research):
    post = BlogPost.objects.create(
        title="Research Post",
        slug="research-post",
        author=user,
        content="About research",
        status="published",
    )
    post.categories.add(category_research)
    return post


@pytest.fixture
def post_news(db, user, category_news):
    post = BlogPost.objects.create(
        title="News Post",
        slug="news-post",
        author=user,
        content="About news",
        status="published",
    )
    post.categories.add(category_news)
    return post


class TestBlogPostListViewCategoryURL:
    def test_clean_url_returns_200(self, client, db, category_research, post_research):
        url = reverse("blog:category_filter", kwargs={"category_slug": "research"})
        response = client.get(url)
        assert response.status_code == 200

    def test_clean_url_filters_to_categorized_posts(self, client, db, post_research, post_news, category_research):
        url = reverse("blog:category_filter", kwargs={"category_slug": "research"})
        response = client.get(url)
        posts = list(response.context["posts"])
        assert post_research in posts
        assert post_news not in posts

    def test_clean_url_sets_current_category_in_context(self, client, db, category_research, post_research):
        url = reverse("blog:category_filter", kwargs={"category_slug": "research"})
        response = client.get(url)
        assert response.context["current_category"] == "research"

    def test_clean_url_sets_current_category_obj_in_context(self, client, db, category_research, post_research):
        url = reverse("blog:category_filter", kwargs={"category_slug": "research"})
        response = client.get(url)
        assert response.context["current_category_obj"] == category_research

    def test_nonexistent_category_slug_returns_empty_list(self, client, db, post_research):
        url = reverse("blog:category_filter", kwargs={"category_slug": "nonexistent"})
        response = client.get(url)
        assert response.status_code == 200
        assert list(response.context["posts"]) == []

    def test_nonexistent_category_slug_sets_category_obj_none(self, client, db, post_research):
        url = reverse("blog:category_filter", kwargs={"category_slug": "nonexistent"})
        response = client.get(url)
        assert response.context["current_category_obj"] is None

    def test_query_param_category_filtering(self, client, db, post_research, post_news):
        url = reverse("blog:list") + "?category=research"
        response = client.get(url)
        posts = list(response.context["posts"])
        assert post_research in posts
        assert post_news not in posts
