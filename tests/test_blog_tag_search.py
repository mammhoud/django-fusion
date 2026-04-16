"""
Tests for blog tag search functionality.

These tests verify that the tag search system works correctly,
including API endpoints and search services.
"""

import json

import pytest
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.blog.models import BlogPost, BlogTag
from apps.blog.services import PostFilterService, TagService

User = get_user_model()


@pytest.mark.django_db
class TestTagSearchService(TestCase):
    """Tests for the TagService search functionality."""

    def setUp(self):
        """Set up test data."""
        self.tag1 = BlogTag.objects.create(name="Python", slug="python")
        self.tag2 = BlogTag.objects.create(name="Django", slug="django")
        self.tag3 = BlogTag.objects.create(name="API", slug="api")
        self.tag4 = BlogTag.objects.create(name="REST", slug="rest")

    def test_search_tags_by_name(self):
        """Test searching tags by name."""
        results = TagService.search_tags("python")
        assert results.count() == 1
        assert self.tag1 in results

    def test_search_tags_case_insensitive(self):
        """Test that tag search is case-insensitive."""
        results = TagService.search_tags("PYTHON")
        assert results.count() == 1
        assert self.tag1 in results

    def test_search_tags_partial_match(self):
        """Test searching tags with partial matches."""
        results = TagService.search_tags("jango")
        assert results.count() == 1
        assert self.tag2 in results

    def test_search_tags_multiple_results(self):
        """Test searching tags that return multiple results."""
        # "api" matches "API" (name) and "api" (slug)
        results = TagService.search_tags("api")
        assert results.count() == 1
        assert self.tag3 in results

    def test_search_tags_no_results(self):
        """Test searching tags with no results."""
        results = TagService.search_tags("nonexistent")
        assert results.count() == 0

    def test_search_tags_empty_query(self):
        """Test searching with empty query."""
        results = TagService.search_tags("")
        assert results.count() == 4


@pytest.mark.django_db
class TestPopularTags(TestCase):
    """Tests for getting popular tags."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.tag1 = BlogTag.objects.create(name="Python", slug="python")
        self.tag2 = BlogTag.objects.create(name="Django", slug="django")
        self.tag3 = BlogTag.objects.create(name="API", slug="api")
        self.tag4 = BlogTag.objects.create(name="Unused", slug="unused")

        # Create posts
        for i in range(5):
            post = BlogPost.objects.create(
                title=f"Post {i}",
                slug=f"post-{i}",
                author=self.user,
                content="Content",
                status="published"
            )
            post.tags.add(self.tag1)

        for i in range(3):
            post = BlogPost.objects.create(
                title=f"Django Post {i}",
                slug=f"django-post-{i}",
                author=self.user,
                content="Content",
                status="published"
            )
            post.tags.add(self.tag2)

        post = BlogPost.objects.create(
            title="API Post",
            slug="api-post",
            author=self.user,
            content="Content",
            status="published"
        )
        post.tags.add(self.tag3)

    def test_get_popular_tags(self):
        """Test getting popular tags."""
        popular = TagService.get_popular_tags(limit=10)
        assert popular.count() == 3
        assert popular[0] == self.tag1
        assert popular[1] == self.tag2
        assert popular[2] == self.tag3

    def test_get_popular_tags_excludes_unused(self):
        """Test that unused tags are excluded from popular tags."""
        popular = TagService.get_popular_tags(limit=10)
        assert self.tag4 not in popular

    def test_get_popular_tags_limit(self):
        """Test limiting popular tags."""
        popular = TagService.get_popular_tags(limit=2)
        assert popular.count() == 2


@pytest.mark.django_db
class TestTagCloud(TestCase):
    """Tests for tag cloud generation."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.tag1 = BlogTag.objects.create(name="Python", slug="python")
        self.tag2 = BlogTag.objects.create(name="Django", slug="django")
        self.tag3 = BlogTag.objects.create(name="API", slug="api")

        # Create posts with different tag frequencies
        for i in range(5):
            post = BlogPost.objects.create(
                title=f"Post {i}",
                slug=f"post-{i}",
                author=self.user,
                content="Content",
                status="published"
            )
            post.tags.add(self.tag1)

        for i in range(3):
            post = BlogPost.objects.create(
                title=f"Django Post {i}",
                slug=f"django-post-{i}",
                author=self.user,
                content="Content",
                status="published"
            )
            post.tags.add(self.tag2)

        post = BlogPost.objects.create(
            title="API Post",
            slug="api-post",
            author=self.user,
            content="Content",
            status="published"
        )
        post.tags.add(self.tag3)

    def test_get_tag_cloud(self):
        """Test getting tag cloud."""
        cloud = TagService.get_tag_cloud(limit=10)
        assert len(cloud) == 3

    def test_tag_cloud_has_sizes(self):
        """Test that tag cloud includes size weights."""
        cloud = TagService.get_tag_cloud(limit=10)
        for tag in cloud:
            assert hasattr(tag, 'size')
            assert 1 <= tag.size <= 5

    def test_tag_cloud_ordering(self):
        """Test that tag cloud is ordered alphabetically."""
        cloud = TagService.get_tag_cloud(limit=10)
        names = [tag.name for tag in cloud]
        assert names == sorted(names)


@pytest.mark.django_db
class TestRelatedTags(TestCase):
    """Tests for getting related tags."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.tag1 = BlogTag.objects.create(name="Python", slug="python")
        self.tag2 = BlogTag.objects.create(name="Django", slug="django")
        self.tag3 = BlogTag.objects.create(name="API", slug="api")
        self.tag4 = BlogTag.objects.create(name="REST", slug="rest")

        # Create posts with tag combinations
        post1 = BlogPost.objects.create(
            title="Post 1",
            slug="post-1",
            author=self.user,
            content="Content",
            status="published"
        )
        post1.tags.add(self.tag1, self.tag2, self.tag3)

        post2 = BlogPost.objects.create(
            title="Post 2",
            slug="post-2",
            author=self.user,
            content="Content",
            status="published"
        )
        post2.tags.add(self.tag1, self.tag4)

    def test_get_related_tags(self):
        """Test getting related tags."""
        related = TagService.get_related_tags(self.tag1, limit=10)
        assert self.tag2 in related
        assert self.tag3 in related
        assert self.tag4 in related

    def test_get_related_tags_excludes_self(self):
        """Test that related tags don't include the tag itself."""
        related = TagService.get_related_tags(self.tag1, limit=10)
        assert self.tag1 not in related


@pytest.mark.django_db
class TestPostFilterService(TestCase):
    """Tests for the PostFilterService."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.tag1 = BlogTag.objects.create(name="Python", slug="python")
        self.tag2 = BlogTag.objects.create(name="Django", slug="django")

        self.post1 = BlogPost.objects.create(
            title="Python Post",
            slug="python-post",
            author=self.user,
            content="Python content",
            status="published"
        )
        self.post1.tags.add(self.tag1)

        self.post2 = BlogPost.objects.create(
            title="Django Post",
            slug="django-post",
            author=self.user,
            content="Django content",
            status="published"
        )
        self.post2.tags.add(self.tag1, self.tag2)

    def test_filter_by_tags_any(self):
        """Test filtering posts by tags (any match)."""
        queryset = BlogPost.objects.all()
        filtered = PostFilterService.filter_by_tags(queryset, ['python', 'django'], match_all=False)
        assert filtered.count() == 2

    def test_filter_by_tags_all(self):
        """Test filtering posts by tags (all match)."""
        queryset = BlogPost.objects.all()
        filtered = PostFilterService.filter_by_tags(queryset, ['python', 'django'], match_all=True)
        assert filtered.count() == 1
        assert self.post2 in filtered

    def test_search_posts(self):
        """Test searching posts."""
        queryset = BlogPost.objects.all()
        filtered = PostFilterService.search_posts(queryset, 'Python')
        assert filtered.count() == 1
        assert self.post1 in filtered

    def test_apply_multiple_filters(self):
        """Test applying multiple filters."""
        queryset = BlogPost.objects.all()
        filtered = PostFilterService.apply_filters(
            queryset,
            tags=['python'],
            query='Python'
        )
        assert filtered.count() == 1
        assert self.post1 in filtered


@pytest.mark.django_db
class TestTagSearchAPI(TestCase):
    """Tests for tag search API endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.tag1 = BlogTag.objects.create(name="Python", slug="python")
        self.tag2 = BlogTag.objects.create(name="Django", slug="django")
        self.tag3 = BlogTag.objects.create(name="API", slug="api")

        # Create posts tagged with all 3 tags so they appear in the tag cloud
        for i in range(3):
            post = BlogPost.objects.create(
                title=f"Post {i}",
                slug=f"post-{i}",
                author=self.user,
                content="Content",
                status="published"
            )
            post.tags.add(self.tag1)

        # Add posts for tag2 and tag3 so they appear in the tag cloud
        post_django = BlogPost.objects.create(
            title="Django Post",
            slug="django-post",
            author=self.user,
            content="Content",
            status="published"
        )
        post_django.tags.add(self.tag2)

        post_api = BlogPost.objects.create(
            title="API Post",
            slug="api-post",
            author=self.user,
            content="Content",
            status="published"
        )
        post_api.tags.add(self.tag3)

    def test_search_tags_api(self):
        """Test the search tags API endpoint."""
        response = self.client.get(reverse('blog:api_search_tags'), {'q': 'python'})
        assert response.status_code == 200
        data = json.loads(response.content)
        assert 'tags' in data
        assert len(data['tags']) == 1
        assert data['tags'][0]['name'] == 'Python'

    def test_search_tags_api_empty_query(self):
        """Test search tags API with empty query."""
        response = self.client.get(reverse('blog:api_search_tags'), {'q': ''})
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['tags'] == []

    def test_tag_autocomplete_api(self):
        """Test the tag autocomplete API endpoint."""
        response = self.client.get(reverse('blog:api_tag_autocomplete'), {'q': 'djan'})
        assert response.status_code == 200
        data = json.loads(response.content)
        assert 'results' in data
        assert len(data['results']) == 1
        assert data['results'][0]['text'] == 'Django'

    def test_tag_cloud_api(self):
        """Test the tag cloud API endpoint."""
        response = self.client.get(reverse('blog:api_tag_cloud'))
        assert response.status_code == 200
        data = json.loads(response.content)
        assert 'tags' in data
        assert len(data['tags']) == 3

    def test_related_tags_api(self):
        """Test the related tags API endpoint."""
        response = self.client.get(reverse('blog:api_related_tags', args=['python']))
        assert response.status_code == 200
        data = json.loads(response.content)
        assert 'tag' in data
        assert 'related_tags' in data
        assert data['tag']['name'] == 'Python'

    def test_related_tags_api_not_found(self):
        """Test related tags API with nonexistent tag."""
        response = self.client.get(reverse('blog:api_related_tags', args=['nonexistent']))
        assert response.status_code == 404
