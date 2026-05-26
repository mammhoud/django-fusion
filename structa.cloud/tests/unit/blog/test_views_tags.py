"""
Unit tests for tag management views (TagListView, TagCreateView, etc.).
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
def staff_user(db):
    return User.objects.create_user(
        username="staff", password="pass", is_staff=True
    )


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(username="regular", password="pass")


@pytest.fixture
def tag_python(db):
    return BlogTag.objects.create(name="Python", slug="python")


@pytest.fixture
def tag_unused(db):
    return BlogTag.objects.create(name="Unused", slug="unused")


@pytest.fixture
def published_post(db, staff_user, tag_python):
    post = BlogPost.objects.create(
        title="Post", slug="post", author=staff_user,
        content="x", status="published",
    )
    post.tags.add(tag_python)
    return post


# ---------------------------------------------------------------------------
# TagListView
# ---------------------------------------------------------------------------

class TestTagListView:
    def test_requires_staff(self, client, db, regular_user):
        client.force_login(regular_user)
        response = client.get(reverse("blog:tag_list"))
        assert response.status_code != 200

    def test_staff_can_access(self, client, db, staff_user, tag_python):
        client.force_login(staff_user)
        response = client.get(reverse("blog:tag_list"))
        assert response.status_code == 200

    def test_lists_all_tags(self, client, db, staff_user, tag_python, tag_unused):
        client.force_login(staff_user)
        response = client.get(reverse("blog:tag_list"))
        tags = list(response.context["tags"])
        names = [t.name for t in tags]
        assert "Python" in names
        assert "Unused" in names

    def test_search_filters_tags(self, client, db, staff_user, tag_python, tag_unused):
        client.force_login(staff_user)
        response = client.get(reverse("blog:tag_list") + "?q=Python")
        tags = list(response.context["tags"])
        names = [t.name for t in tags]
        assert "Python" in names
        assert "Unused" not in names

    def test_context_has_total_tags(self, client, db, staff_user, tag_python, tag_unused):
        client.force_login(staff_user)
        response = client.get(reverse("blog:tag_list"))
        assert response.context["total_tags"] == 2

    def test_context_has_unused_count(self, client, db, staff_user, tag_python, tag_unused, published_post):
        client.force_login(staff_user)
        response = client.get(reverse("blog:tag_list"))
        # tag_unused has no posts
        assert response.context["unused_count"] == 1


# ---------------------------------------------------------------------------
# TagCreateView
# ---------------------------------------------------------------------------

class TestTagCreateView:
    def test_requires_staff(self, client, db, regular_user):
        client.force_login(regular_user)
        response = client.get(reverse("blog:tag_create"))
        assert response.status_code != 200

    def test_staff_can_access_form(self, client, db, staff_user):
        client.force_login(staff_user)
        response = client.get(reverse("blog:tag_create"))
        assert response.status_code == 200

    def test_creates_tag_on_post(self, client, db, staff_user):
        client.force_login(staff_user)
        response = client.post(
            reverse("blog:tag_create"),
            {"name": "NewTag", "slug": "newtag"},
        )
        assert response.status_code == 302
        assert BlogTag.objects.filter(slug="newtag").exists()

    def test_redirects_to_tag_list_on_success(self, client, db, staff_user):
        client.force_login(staff_user)
        response = client.post(
            reverse("blog:tag_create"),
            {"name": "NewTag2", "slug": "newtag2"},
        )
        assert response["Location"] == reverse("blog:tag_list")

    def test_invalid_form_does_not_create(self, client, db, staff_user):
        client.force_login(staff_user)
        client.post(reverse("blog:tag_create"), {"name": "", "slug": ""})
        assert not BlogTag.objects.filter(name="").exists()


# ---------------------------------------------------------------------------
# TagUpdateView
# ---------------------------------------------------------------------------

class TestTagUpdateView:
    def test_requires_staff(self, client, db, regular_user, tag_python):
        client.force_login(regular_user)
        response = client.get(reverse("blog:tag_edit", kwargs={"slug": "python"}))
        assert response.status_code != 200

    def test_staff_can_access_form(self, client, db, staff_user, tag_python):
        client.force_login(staff_user)
        response = client.get(reverse("blog:tag_edit", kwargs={"slug": "python"}))
        assert response.status_code == 200

    def test_updates_tag_name(self, client, db, staff_user, tag_python):
        client.force_login(staff_user)
        client.post(
            reverse("blog:tag_edit", kwargs={"slug": "python"}),
            {"name": "Python3", "slug": "python"},
        )
        tag_python.refresh_from_db()
        assert tag_python.name == "Python3"

    def test_context_has_post_count(self, client, db, staff_user, tag_python, published_post):
        client.force_login(staff_user)
        response = client.get(reverse("blog:tag_edit", kwargs={"slug": "python"}))
        assert response.context["post_count"] == 1


# ---------------------------------------------------------------------------
# TagDeleteView
# ---------------------------------------------------------------------------

class TestTagDeleteView:
    def test_requires_staff(self, client, db, regular_user, tag_python):
        client.force_login(regular_user)
        response = client.get(reverse("blog:tag_delete", kwargs={"slug": "python"}))
        assert response.status_code != 200

    def test_staff_can_access_confirm_page(self, client, db, staff_user, tag_python):
        client.force_login(staff_user)
        response = client.get(reverse("blog:tag_delete", kwargs={"slug": "python"}))
        assert response.status_code == 200

    def test_deletes_tag_on_post(self, client, db, staff_user, tag_python):
        client.force_login(staff_user)
        client.post(reverse("blog:tag_delete", kwargs={"slug": "python"}))
        assert not BlogTag.objects.filter(slug="python").exists()

    def test_redirects_to_tag_list_on_success(self, client, db, staff_user, tag_python):
        client.force_login(staff_user)
        response = client.post(reverse("blog:tag_delete", kwargs={"slug": "python"}))
        assert response.status_code == 302
        assert response["Location"] == reverse("blog:tag_list")


# ---------------------------------------------------------------------------
# TagCleanupView
# ---------------------------------------------------------------------------

class TestTagCleanupView:
    def test_requires_staff(self, client, db, regular_user):
        client.force_login(regular_user)
        response = client.get(reverse("blog:tag_cleanup"))
        assert response.status_code != 200

    def test_staff_can_access(self, client, db, staff_user, tag_unused):
        client.force_login(staff_user)
        response = client.get(reverse("blog:tag_cleanup"))
        assert response.status_code == 200

    def test_lists_only_unused_tags(self, client, db, staff_user, tag_python, tag_unused, published_post):
        client.force_login(staff_user)
        response = client.get(reverse("blog:tag_cleanup"))
        unused = list(response.context["unused_tags"])
        names = [t.name for t in unused]
        assert "Unused" in names
        assert "Python" not in names

    def test_post_deletes_unused_tags(self, client, db, staff_user, tag_unused):
        client.force_login(staff_user)
        client.post(reverse("blog:tag_cleanup"))
        assert not BlogTag.objects.filter(slug="unused").exists()

    def test_post_keeps_used_tags(self, client, db, staff_user, tag_python, tag_unused, published_post):
        client.force_login(staff_user)
        client.post(reverse("blog:tag_cleanup"))
        assert BlogTag.objects.filter(slug="python").exists()

    def test_post_redirects_to_tag_list(self, client, db, staff_user, tag_unused):
        client.force_login(staff_user)
        response = client.post(reverse("blog:tag_cleanup"))
        assert response.status_code == 302
        assert response["Location"] == reverse("blog:tag_list")
