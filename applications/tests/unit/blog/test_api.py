"""
Unit tests for blog tag API endpoints.
"""
import json

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
def tag_python(db):
    return BlogTag.objects.create(name="Python", slug="python")


@pytest.fixture
def tag_django(db):
    return BlogTag.objects.create(name="Django", slug="django")


@pytest.fixture
def user(db):
    return User.objects.create_user(username="u", password="p")


@pytest.fixture
def post_with_both_tags(db, user, tag_python, tag_django):
    post = BlogPost.objects.create(
        title="Post", slug="post", author=user, content="x", status="published"
    )
    post.tags.add(tag_python, tag_django)
    return post


# ---------------------------------------------------------------------------
# search_tags endpoint
# ---------------------------------------------------------------------------

class TestSearchTagsAPI:
    def test_returns_200(self, client, db, tag_python):
        response = client.get(reverse("blog:api_search_tags") + "?q=py")
        assert response.status_code == 200

    def test_returns_json(self, client, db, tag_python):
        response = client.get(reverse("blog:api_search_tags") + "?q=py")
        data = json.loads(response.content)
        assert "tags" in data

    def test_finds_matching_tag(self, client, db, tag_python):
        response = client.get(reverse("blog:api_search_tags") + "?q=py")
        data = json.loads(response.content)
        slugs = [t["slug"] for t in data["tags"]]
        assert "python" in slugs

    def test_short_query_returns_empty(self, client, db, tag_python):
        response = client.get(reverse("blog:api_search_tags") + "?q=p")
        data = json.loads(response.content)
        assert data["tags"] == []

    def test_no_query_returns_empty(self, client, db, tag_python):
        response = client.get(reverse("blog:api_search_tags"))
        data = json.loads(response.content)
        assert data["tags"] == []

    def test_no_match_returns_empty_list(self, client, db, tag_python):
        response = client.get(reverse("blog:api_search_tags") + "?q=zzznomatch")
        data = json.loads(response.content)
        assert data["tags"] == []

    def test_result_has_required_fields(self, client, db, tag_python):
        response = client.get(reverse("blog:api_search_tags") + "?q=py")
        data = json.loads(response.content)
        if data["tags"]:
            tag = data["tags"][0]
            assert "id" in tag
            assert "name" in tag
            assert "slug" in tag


# ---------------------------------------------------------------------------
# tag_autocomplete endpoint
# ---------------------------------------------------------------------------

class TestTagAutocompleteAPI:
    def test_returns_200(self, client, db, tag_python):
        response = client.get(reverse("blog:api_tag_autocomplete"))
        assert response.status_code == 200

    def test_no_query_returns_all_tags(self, client, db, tag_python, tag_django):
        response = client.get(reverse("blog:api_tag_autocomplete"))
        data = json.loads(response.content)
        slugs = [r["slug"] for r in data["results"]]
        assert "python" in slugs
        assert "django" in slugs

    def test_query_filters_results(self, client, db, tag_python, tag_django):
        response = client.get(reverse("blog:api_tag_autocomplete") + "?q=py")
        data = json.loads(response.content)
        slugs = [r["slug"] for r in data["results"]]
        assert "python" in slugs
        assert "django" not in slugs

    def test_result_has_id_text_slug(self, client, db, tag_python):
        response = client.get(reverse("blog:api_tag_autocomplete") + "?q=py")
        data = json.loads(response.content)
        if data["results"]:
            item = data["results"][0]
            assert "id" in item
            assert "text" in item
            assert "slug" in item

    def test_text_field_is_tag_name(self, client, db, tag_python):
        response = client.get(reverse("blog:api_tag_autocomplete") + "?q=py")
        data = json.loads(response.content)
        if data["results"]:
            assert data["results"][0]["text"] == "Python"


# ---------------------------------------------------------------------------
# tag_cloud endpoint
# ---------------------------------------------------------------------------

class TestTagCloudAPI:
    def test_returns_200(self, client, db):
        response = client.get(reverse("blog:api_tag_cloud"))
        assert response.status_code == 200

    def test_returns_tags_key(self, client, db):
        response = client.get(reverse("blog:api_tag_cloud"))
        data = json.loads(response.content)
        assert "tags" in data

    def test_tag_has_size_field(self, client, db, post_with_both_tags):
        response = client.get(reverse("blog:api_tag_cloud"))
        data = json.loads(response.content)
        if data["tags"]:
            assert "size" in data["tags"][0]

    def test_tag_has_count_field(self, client, db, post_with_both_tags):
        response = client.get(reverse("blog:api_tag_cloud"))
        data = json.loads(response.content)
        if data["tags"]:
            assert "count" in data["tags"][0]

    def test_limit_param_respected(self, client, db, user):
        for i in range(5):
            tag = BlogTag.objects.create(name=f"Tag{i}", slug=f"tag{i}")
            post = BlogPost.objects.create(
                title=f"P{i}", slug=f"p{i}", author=user, content="x", status="published"
            )
            post.tags.add(tag)
        response = client.get(reverse("blog:api_tag_cloud") + "?limit=2")
        data = json.loads(response.content)
        assert len(data["tags"]) <= 2


# ---------------------------------------------------------------------------
# related_tags endpoint
# ---------------------------------------------------------------------------

class TestRelatedTagsAPI:
    def test_returns_200_for_existing_tag(self, client, db, post_with_both_tags):
        response = client.get(
            reverse("blog:api_related_tags", kwargs={"tag_slug": "python"})
        )
        assert response.status_code == 200

    def test_returns_404_for_missing_tag(self, client, db):
        response = client.get(
            reverse("blog:api_related_tags", kwargs={"tag_slug": "nonexistent"})
        )
        assert response.status_code == 404

    def test_returns_related_tags(self, client, db, post_with_both_tags):
        response = client.get(
            reverse("blog:api_related_tags", kwargs={"tag_slug": "python"})
        )
        data = json.loads(response.content)
        related_slugs = [t["slug"] for t in data["related_tags"]]
        assert "django" in related_slugs

    def test_response_has_tag_info(self, client, db, post_with_both_tags):
        response = client.get(
            reverse("blog:api_related_tags", kwargs={"tag_slug": "python"})
        )
        data = json.loads(response.content)
        assert data["tag"]["slug"] == "python"
        assert data["tag"]["name"] == "Python"

    def test_related_tag_has_count(self, client, db, post_with_both_tags):
        response = client.get(
            reverse("blog:api_related_tags", kwargs={"tag_slug": "python"})
        )
        data = json.loads(response.content)
        if data["related_tags"]:
            assert "count" in data["related_tags"][0]
