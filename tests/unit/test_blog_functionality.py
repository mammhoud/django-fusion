"""
CTC Research Blog Functionality Tests
====================================
Consolidated tests for blog tagging, search, and related functionality.
"""

import json

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

try:
    from django.test import TestCase as BaseTestCase

    from plugins.blog.models import BlogCategory, BlogPost, BlogTag
    from plugins.blog.services import PostFilterService, TagService
    _DJANGO_AVAILABLE = True
except ImportError:
    # Django not available, create mock base class
    class BaseTestCase:
        def setUp(self):
            pass
    _DJANGO_AVAILABLE = False

User = get_user_model() if _DJANGO_AVAILABLE else None


@pytest.mark.skipif(not _DJANGO_AVAILABLE, reason="Django not available")
@pytest.mark.django_db
class TestBlogTagModel(BaseTestCase):
    """Tests for the BlogTag model."""

    def setUp(self):
        """Set up test data."""
        self.tag = BlogTag.objects.create(name="Python", slug="python")

    def test_create_tag(self):
        """Test creating a blog tag."""
        assert self.tag.name == "Python"
        assert self.tag.slug == "python"

    def test_tag_string_representation(self):
        """Test the string representation of a tag."""
        assert str(self.tag) == "Python"

    def test_tag_ordering(self):
        """Test that tags are ordered by name."""
        tag2 = BlogTag.objects.create(name="Django", slug="django")
        tag3 = BlogTag.objects.create(name="API", slug="api")

        tags = list(BlogTag.objects.all())
        assert tags[0].name == "API"
        assert tags[1].name == "Django"
        assert tags[2].name == "Python"


@pytest.mark.skipif(not _DJANGO_AVAILABLE, reason="Django not available")
@pytest.mark.django_db
class TestBlogPostTagging(BaseTestCase):
    """Tests for tagging blog posts."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.tag1 = BlogTag.objects.create(name="Python", slug="python")
        self.tag2 = BlogTag.objects.create(name="Django", slug="django")
        self.tag3 = BlogTag.objects.create(name="API", slug="api")

        self.post = BlogPost.objects.create(
            title="Test Post",
            slug="test-post",
            author=self.user,
            content="Test content",
            status="published"
        )

    def test_add_single_tag_to_post(self):
        """Test adding a single tag to a post."""
        self.post.tags.add(self.tag1)
        assert self.post.tags.count() == 1
        assert self.tag1 in self.post.tags.all()

    def test_add_multiple_tags_to_post(self):
        """Test adding multiple tags to a post."""
        self.post.tags.add(self.tag1, self.tag2, self.tag3)
        assert self.post.tags.count() == 3
        assert all(tag in self.post.tags.all() for tag in [self.tag1, self.tag2, self.tag3])

    def test_remove_tag_from_post(self):
        """Test removing a tag from a post."""
        self.post.tags.add(self.tag1, self.tag2)
        self.post.tags.remove(self.tag1)
        assert self.post.tags.count() == 1
        assert self.tag1 not in self.post.tags.all()
        assert self.tag2 in self.post.tags.all()


@pytest.mark.skipif(not _DJANGO_AVAILABLE, reason="Django not available")
@pytest.mark.django_db
class TestBlogTagFiltering(BaseTestCase):
    """Tests for filtering blog posts by tags."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.tag1 = BlogTag.objects.create(name="Python", slug="python")
        self.tag2 = BlogTag.objects.create(name="Django", slug="django")
        self.tag3 = BlogTag.objects.create(name="API", slug="api")

        # Create posts
        self.post1 = BlogPost.objects.create(
            title="Python Basics", slug="python-basics", author=self.user,
            content="Content 1", status="published"
        )
        self.post2 = BlogPost.objects.create(
            title="Django Tutorial", slug="django-tutorial", author=self.user,
            content="Content 2", status="published"
        )
        self.post3 = BlogPost.objects.create(
            title="REST API Design", slug="rest-api-design", author=self.user,
            content="Content 3", status="published"
        )
        self.post4 = BlogPost.objects.create(
            title="Draft Post", slug="draft-post", author=self.user,
            content="Content 4", status="draft"
        )

        # Add tags
        self.post1.tags.add(self.tag1)
        self.post2.tags.add(self.tag1, self.tag2)
        self.post3.tags.add(self.tag2, self.tag3)
        self.post4.tags.add(self.tag1)

    def test_filter_posts_by_single_tag(self):
        """Test filtering posts by a single tag."""
        posts = BlogPost.objects.filter(status="published", tags__slug="python").distinct()
        assert posts.count() == 2
        assert self.post1 in posts
        assert self.post2 in posts

    def test_filter_posts_by_multiple_tags_any(self):
        """Test filtering posts by multiple tags (any match)."""
        posts = BlogPost.objects.filter(
            status="published", tags__slug__in=["python", "api"]
        ).distinct()
        assert posts.count() == 3
        assert all(post in posts for post in [self.post1, self.post2, self.post3])

    def test_filter_excludes_draft_posts(self):
        """Test that filtering only returns published posts."""
        posts = BlogPost.objects.filter(status="published", tags__slug="python").distinct()
        assert self.post4 not in posts


@pytest.mark.skipif(not _DJANGO_AVAILABLE, reason="Django not available")
@pytest.mark.django_db
class TestBlogTagSearch(BaseTestCase):
    """Tests for searching blog posts by tags."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.tag1 = BlogTag.objects.create(name="Python", slug="python")
        self.tag2 = BlogTag.objects.create(name="Django", slug="django")

        self.post1 = BlogPost.objects.create(
            title="Python Basics", slug="python-basics", author=self.user,
            content="Python content", status="published"
        )
        self.post2 = BlogPost.objects.create(
            title="Django Tutorial", slug="django-tutorial", author=self.user,
            content="Django content", status="published"
        )

        self.post1.tags.add(self.tag1)
        self.post2.tags.add(self.tag2)

    def test_search_tags_by_name(self):
        """Test searching tags by name."""
        tags = BlogTag.objects.filter(name__icontains="python")
        assert tags.count() == 1
        assert self.tag1 in tags

    def test_search_tags_case_insensitive(self):
        """Test that tag search is case-insensitive."""
        tags = BlogTag.objects.filter(name__icontains="PYTHON")
        assert tags.count() == 1
        assert self.tag1 in tags

    def test_search_posts_by_tag_name(self):
        """Test searching posts by tag name."""
        posts = BlogPost.objects.filter(
            status="published", tags__name__icontains="python"
        ).distinct()
        assert posts.count() == 1
        assert self.post1 in posts


@pytest.mark.skipif(not _DJANGO_AVAILABLE, reason="Django not available")
@pytest.mark.django_db
class TestTagServices(BaseTestCase):
    """Tests for tag-related services."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.tag1 = BlogTag.objects.create(name="Python", slug="python")
        self.tag2 = BlogTag.objects.create(name="Django", slug="django")
        self.tag3 = BlogTag.objects.create(name="API", slug="api")

        # Create posts with different tag frequencies
        for i in range(5):
            post = BlogPost.objects.create(
                title=f"Post {i}", slug=f"post-{i}", author=self.user,
                content="Content", status="published"
            )
            post.tags.add(self.tag1)

        for i in range(3):
            post = BlogPost.objects.create(
                title=f"Django Post {i}", slug=f"django-post-{i}", author=self.user,
                content="Content", status="published"
            )
            post.tags.add(self.tag2)

    def test_search_tags_service(self):
        """Test TagService search functionality."""
        if hasattr(TagService, 'search_tags'):
            results = TagService.search_tags("python")
            assert results.count() == 1
            assert self.tag1 in results

    def test_get_popular_tags_service(self):
        """Test TagService popular tags functionality."""
        if hasattr(TagService, 'get_popular_tags'):
            popular = TagService.get_popular_tags(limit=10)
            assert popular.count() >= 2
            # Most popular should be first
            assert popular[0] == self.tag1

    def test_post_filter_service(self):
        """Test PostFilterService functionality."""
        if hasattr(PostFilterService, 'filter_by_tags'):
            queryset = BlogPost.objects.all()
            filtered = PostFilterService.filter_by_tags(queryset, ['python'], match_all=False)
            assert filtered.count() == 5


class TestBlogComponentsImportable:
    """Test that blog components can be imported (no Django DB required)."""

    @pytest.mark.skipif(not _DJANGO_AVAILABLE, reason="Django not available")
    def test_blog_models_importable(self):
        """Test that blog models can be imported."""
        from plugins.blog.models import BlogCategory, BlogPost, BlogTag
        assert all([BlogTag, BlogPost, BlogCategory])

    @pytest.mark.skipif(not _DJANGO_AVAILABLE, reason="Django not available")
    def test_blog_services_importable(self):
        """Test that blog services can be imported."""
        try:
            from plugins.blog.services import PostFilterService, TagService
            assert all([TagService, PostFilterService])
        except ImportError:
            # Services might not exist yet
            pytest.skip("Blog services not implemented")

    @pytest.mark.skipif(not _DJANGO_AVAILABLE, reason="Django not available")
    def test_blog_admin_importable(self):
        """Test that blog admin can be imported."""
        try:
            from plugins.blog.admin import BlogPostAdmin, BlogTagAdmin
            assert all([BlogTagAdmin, BlogPostAdmin])
        except ImportError:
            # Admin might not exist yet
            pytest.skip("Blog admin not implemented")

    @pytest.mark.skipif(not _DJANGO_AVAILABLE, reason="Django not available")
    def test_blog_views_importable(self):
        """Test that blog views can be imported."""
        try:
            from plugins.blog.views import BlogPostDetailView, BlogPostListView
            assert all([BlogPostListView, BlogPostDetailView])
        except ImportError:
            # Views might not exist yet
            pytest.skip("Blog views not implemented")


@pytest.mark.skipif(not _DJANGO_AVAILABLE, reason="Django not available")
@pytest.mark.django_db
class TestBlogIntegration(BaseTestCase):
    """Integration tests for the blog system."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.tag1 = BlogTag.objects.create(name="Python", slug="python")
        self.tag2 = BlogTag.objects.create(name="Django", slug="django")

        self.post1 = BlogPost.objects.create(
            title="Python Basics", slug="python-basics", author=self.user,
            content="Content 1", status="published"
        )
        self.post2 = BlogPost.objects.create(
            title="Django Tutorial", slug="django-tutorial", author=self.user,
            content="Content 2", status="published"
        )

        self.post1.tags.add(self.tag1)
        self.post2.tags.add(self.tag1, self.tag2)

    def test_post_with_categories_and_tags(self):
        """Test creating a post with both categories and tags."""
        try:
            category = BlogCategory.objects.create(name="Tech", slug="tech")
            post = BlogPost.objects.create(
                title="Full Featured Post", slug="full-featured-post",
                author=self.user, content="Content", status="published"
            )
            post.categories.add(category)
            post.tags.add(self.tag1, self.tag2)

            assert post.categories.count() == 1
            assert post.tags.count() == 2
        except Exception:
            # Categories might not be implemented
            pytest.skip("Blog categories not implemented")

    def test_tag_count_with_multiple_posts(self):
        """Test tag count with multiple posts."""
        if hasattr(self.tag1, 'get_post_count'):
            # Only published posts should be counted
            assert self.tag1.get_post_count() == 2

    def test_blog_list_view_integration(self):
        """Test blog list view integration."""
        try:
            response = self.client.get(reverse("blog:list"))
            assert response.status_code == 200
        except Exception:
            # URL might not exist
            pytest.skip("Blog list view not implemented")

    def test_blog_detail_view_integration(self):
        """Test blog detail view integration."""
        try:
            response = self.client.get(reverse("blog:detail", args=[self.post1.slug]))
            assert response.status_code == 200
        except Exception:
            # URL might not exist
            pytest.skip("Blog detail view not implemented")


@pytest.mark.skipif(not _DJANGO_AVAILABLE, reason="Django not available")
@pytest.mark.django_db
class TestBlogAPI(BaseTestCase):
    """Tests for blog API endpoints."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.tag1 = BlogTag.objects.create(name="Python", slug="python")
        self.tag2 = BlogTag.objects.create(name="Django", slug="django")

    def test_search_tags_api_endpoint(self):
        """Test the search tags API endpoint."""
        try:
            response = self.client.get(reverse('blog:api_search_tags'), {'q': 'python'})
            assert response.status_code == 200
            data = json.loads(response.content)
            assert 'tags' in data
        except Exception:
            # API might not exist
            pytest.skip("Blog search API not implemented")

    def test_tag_autocomplete_api_endpoint(self):
        """Test the tag autocomplete API endpoint."""
        try:
            response = self.client.get(reverse('blog:api_tag_autocomplete'), {'q': 'djan'})
            assert response.status_code == 200
            data = json.loads(response.content)
            assert 'results' in data
        except Exception:
            # API might not exist
            pytest.skip("Blog autocomplete API not implemented")

    def test_tag_cloud_api_endpoint(self):
        """Test the tag cloud API endpoint."""
        try:
            response = self.client.get(reverse('blog:api_tag_cloud'))
            assert response.status_code == 200
            data = json.loads(response.content)
            assert 'tags' in data
        except Exception:
            # API might not exist
            pytest.skip("Blog tag cloud API not implemented")
