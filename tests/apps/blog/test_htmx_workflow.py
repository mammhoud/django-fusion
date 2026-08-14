"""
Integration tests for Blog HTMX workflow.

Tests the full flow of creating posts via HTMX fragments,
including OOB fragment updates and permission handling.
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory
from django.urls import reverse
from www.apps.blog.models import BlogCategory, BlogPost

User = get_user_model()


@pytest.fixture
def staff_user(db):
    """Create a staff user for testing."""
    user = User.objects.create_user(
        username="staff",
        email="staff@example.com",
        password="testpass123",
        is_staff=True,
    )
    return user


@pytest.fixture
def regular_user(db):
    """Create a regular (non-staff) user for testing."""
    user = User.objects.create_user(
        username="user",
        email="user@example.com",
        password="testpass123",
        is_staff=False,
    )
    return user


@pytest.fixture
def category(db):
    """Create a blog category for testing."""
    return BlogCategory.objects.create(name="Tech", slug="tech")


@pytest.fixture
def client():
    """Create a test client."""
    return Client()


class TestBlogPostCreateFragment:
    """Tests for BlogPostCreateFragment HTMX component."""

    def test_get_returns_form(self, client, staff_user):
        """GET request returns the form HTML."""
        client.force_login(staff_user)

        # Use the routable component URL
        url = "/components/blog/posts/create-fragment/"
        response = client.get(url, HTTP_HX_REQUEST="true")

        assert response.status_code == 200
        assert b"<form" in response.content
        assert b'htmx-post' in response.content

    def test_get_without_htmx_returns_400(self, client, staff_user):
        """Non-HTMX GET request returns 400."""
        client.force_login(staff_user)

        url = "/components/blog/posts/create-fragment/"
        response = client.get(url)  # No HX-Request header

        assert response.status_code == 400

    def test_post_creates_post(self, client, staff_user, category):
        """POST with valid data creates a new post."""
        client.force_login(staff_user)

        url = "/components/blog/posts/create-fragment/"
        response = client.post(
            url,
            {
                "title": "Test Post",
                "slug": "test-post",
                "excerpt": "Test excerpt",
                "body": "Test body content",
                "category": category.pk,
                "status": "draft",
            },
            HTTP_HX_REQUEST="true",
        )

        assert response.status_code == 200
        assert BlogPost.objects.filter(slug="test-post").exists()

        post = BlogPost.objects.get(slug="test-post")
        assert post.title == "Test Post"
        assert post.author == staff_user

    def test_post_with_invalid_data_returns_form_errors(self, client, staff_user):
        """POST with invalid data returns form with error messages."""
        client.force_login(staff_user)

        url = "/components/blog/posts/create-fragment/"
        response = client.post(
            url,
            {
                "title": "",  # Required field
                "slug": "",
            },
            HTTP_HX_REQUEST="true",
        )

        assert response.status_code == 200
        assert b"This field is required" in response.content

    def test_post_without_permission_returns_403(self, client, regular_user):
        """Non-staff user cannot access the create form."""
        client.force_login(regular_user)

        url = "/components/blog/posts/create-fragment/"
        response = client.get(url, HTTP_HX_REQUEST="true")

        assert response.status_code == 403

    def test_post_without_login_redirects(self, client):
        """Anonymous user is redirected to login."""
        url = "/components/blog/posts/create-fragment/"
        response = client.get(url, HTTP_HX_REQUEST="true")

        assert response.status_code in [302, 403]


class TestBlogPostListFragment:
    """Tests for BlogPostListFragment HTMX component."""

    def test_list_returns_posts(self, client, staff_user, db):
        """GET request returns list of published posts."""
        # Create a published post
        post = BlogPost.objects.create(
            title="Published Post",
            slug="published-post",
            author=staff_user,
            body="Content",
            status="published",
        )

        url = "/components/blog/posts/list-fragment/"
        response = client.get(url, HTTP_HX_REQUEST="true")

        assert response.status_code == 200
        assert b"Published Post" in response.content

    def test_list_with_search_filters_results(self, client, staff_user, db):
        """Search query filters the post list."""
        # Create posts
        BlogPost.objects.create(
            title="Python Tutorial",
            slug="python-tutorial",
            author=staff_user,
            body="Learn Python",
            status="published",
        )
        BlogPost.objects.create(
            title="Django Guide",
            slug="django-guide",
            author=staff_user,
            body="Learn Django",
            status="published",
        )

        url = "/components/blog/posts/list-fragment/"
        response = client.get(
            url,
            {"q": "Python"},
            HTTP_HX_REQUEST="true",
        )

        assert response.status_code == 200
        assert b"Python Tutorial" in response.content
        assert b"Django Guide" not in response.content

    def test_list_with_category_filters_results(self, client, staff_user, category, db):
        """Category filter works correctly."""
        # Create posts in different categories
        post1 = BlogPost.objects.create(
            title="Tech Post",
            slug="tech-post",
            author=staff_user,
            body="Tech content",
            status="published",
        )
        post1.categories.add(category)

        post2 = BlogPost.objects.create(
            title="Other Post",
            slug="other-post",
            author=staff_user,
            body="Other content",
            status="published",
        )

        url = "/components/blog/posts/list-fragment/"
        response = client.get(
            url,
            {"category": category.slug},
            HTTP_HX_REQUEST="true",
        )

        assert response.status_code == 200
        assert b"Tech Post" in response.content
        assert b"Other Post" not in response.content


class TestNamespaceConflicts:
    """Tests to verify no namespace conflicts between routing systems."""

    def test_traditional_blog_urls_still_work(self, client, staff_user, db):
        """Traditional blog URLs are not affected by routable components."""
        # Create a post
        post = BlogPost.objects.create(
            title="Test Post",
            slug="test-post",
            author=staff_user,
            body="Content",
            status="published",
        )

        # Traditional URL should work
        url = reverse("blog:detail", kwargs={"slug": "test-post"})
        response = client.get(url)

        assert response.status_code == 200

    def test_routable_component_urls_are_unique(self, client, staff_user):
        """Routable component URLs don't conflict with traditional routes."""
        # Routable component URL
        routable_url = "/components/blog/posts/list-fragment/"

        # Traditional blog list URL
        traditional_url = reverse("blog:list")

        # They should be different
        assert routable_url != traditional_url

        # Both should work
        response = client.get(routable_url, HTTP_HX_REQUEST="true")
        assert response.status_code == 200

        response = client.get(traditional_url)
        assert response.status_code == 200

    def test_no_wagtail_conflicts(self, client):
        """Routable components don't conflict with Wagtail pages."""
        # The /components/ prefix should isolate routable components
        # Wagtail handles everything at root level

        # Try accessing a routable component
        url = "/components/blog/posts/list-fragment/"
        response = client.get(url, HTTP_HX_REQUEST="true")

        # Should get a valid response (or 400 for non-HTMX, but not 404)
        assert response.status_code != 404


class TestOOBFragments:
    """Tests for OOB fragment functionality."""

    def test_oob_fragment_in_response(self, client, staff_user, category, db):
        """Successful post creation returns OOB fragments."""
        client.force_login(staff_user)

        url = "/components/blog/posts/create-fragment/"
        response = client.post(
            url,
            {
                "title": "New Post",
                "slug": "new-post",
                "excerpt": "Excerpt",
                "body": "Body",
                "status": "draft",
            },
            HTTP_HX_REQUEST="true",
        )

        assert response.status_code == 200
        # OOB fragments should be in the response
        assert b"hx-swap-oob" in response.content or b"post-create-success" in response.content
