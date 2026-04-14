"""
Tests for the blog tagging system.

These tests verify that the tagging system works correctly for blog posts,
including tag creation, assignment, filtering, and search functionality.
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.blog.models import BlogCategory, BlogPost, BlogTag

User = get_user_model()


@pytest.mark.django_db
class TestBlogTagModel(TestCase):
    """Tests for the BlogTag model."""

    def setUp(self):
        """Set up test data."""
        self.tag = BlogTag.objects.create(
            name="Python",
            slug="python"
        )

    def test_create_tag(self):
        """Test creating a blog tag."""
        assert self.tag.name == "Python"
        assert self.tag.slug == "python"

    def test_tag_uniqueness(self):
        """Test that tag names are unique."""
        with pytest.raises(Exception):
            BlogTag.objects.create(
                name="Python",
                slug="python-2"
            )

    def test_tag_slug_uniqueness(self):
        """Test that tag slugs are unique."""
        with pytest.raises(Exception):
            BlogTag.objects.create(
                name="Python Programming",
                slug="python"
            )

    def test_tag_ordering(self):
        """Test that tags are ordered by name."""
        tag2 = BlogTag.objects.create(name="Django", slug="django")
        tag3 = BlogTag.objects.create(name="API", slug="api")

        tags = list(BlogTag.objects.all())
        assert tags[0].name == "API"
        assert tags[1].name == "Django"
        assert tags[2].name == "Python"

    def test_tag_string_representation(self):
        """Test the string representation of a tag."""
        assert str(self.tag) == "Python"

    def test_get_post_count(self):
        """Test getting the count of posts with a tag."""
        user = User.objects.create_user(username="testuser", password="testpass")

        # Create posts
        post1 = BlogPost.objects.create(
            title="Post 1",
            slug="post-1",
            author=user,
            content="Content 1",
            status="published"
        )
        post2 = BlogPost.objects.create(
            title="Post 2",
            slug="post-2",
            author=user,
            content="Content 2",
            status="draft"
        )

        # Add tags
        post1.tags.add(self.tag)
        post2.tags.add(self.tag)

        # Only published posts should be counted
        assert self.tag.get_post_count() == 1


@pytest.mark.django_db
class TestBlogPostTagging(TestCase):
    """Tests for tagging blog posts."""

    def setUp(self):
        """Set up test data."""
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
        assert self.tag1 in self.post.tags.all()
        assert self.tag2 in self.post.tags.all()
        assert self.tag3 in self.post.tags.all()

    def test_remove_tag_from_post(self):
        """Test removing a tag from a post."""
        self.post.tags.add(self.tag1, self.tag2)
        self.post.tags.remove(self.tag1)
        assert self.post.tags.count() == 1
        assert self.tag1 not in self.post.tags.all()
        assert self.tag2 in self.post.tags.all()

    def test_clear_all_tags_from_post(self):
        """Test clearing all tags from a post."""
        self.post.tags.add(self.tag1, self.tag2, self.tag3)
        self.post.tags.clear()
        assert self.post.tags.count() == 0

    def test_get_tag_list(self):
        """Test getting a list of tag names for a post."""
        self.post.tags.add(self.tag1, self.tag2)
        tag_names = [tag.name for tag in self.post.tags.all()]
        assert "Python" in tag_names
        assert "Django" in tag_names
        assert len(tag_names) == 2


@pytest.mark.django_db
class TestBlogTagFiltering(TestCase):
    """Tests for filtering blog posts by tags."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.tag1 = BlogTag.objects.create(name="Python", slug="python")
        self.tag2 = BlogTag.objects.create(name="Django", slug="django")
        self.tag3 = BlogTag.objects.create(name="API", slug="api")

        # Create posts
        self.post1 = BlogPost.objects.create(
            title="Python Basics",
            slug="python-basics",
            author=self.user,
            content="Content 1",
            status="published"
        )
        self.post2 = BlogPost.objects.create(
            title="Django Tutorial",
            slug="django-tutorial",
            author=self.user,
            content="Content 2",
            status="published"
        )
        self.post3 = BlogPost.objects.create(
            title="REST API Design",
            slug="rest-api-design",
            author=self.user,
            content="Content 3",
            status="published"
        )
        self.post4 = BlogPost.objects.create(
            title="Draft Post",
            slug="draft-post",
            author=self.user,
            content="Content 4",
            status="draft"
        )

        # Add tags
        self.post1.tags.add(self.tag1)
        self.post2.tags.add(self.tag1, self.tag2)
        self.post3.tags.add(self.tag2, self.tag3)
        self.post4.tags.add(self.tag1)

    def test_filter_posts_by_single_tag(self):
        """Test filtering posts by a single tag."""
        posts = BlogPost.objects.filter(
            status="published",
            tags__slug="python"
        ).distinct()

        assert posts.count() == 2
        assert self.post1 in posts
        assert self.post2 in posts

    def test_filter_posts_by_multiple_tags_any(self):
        """Test filtering posts by multiple tags (any match)."""
        posts = BlogPost.objects.filter(
            status="published",
            tags__slug__in=["python", "api"]
        ).distinct()

        assert posts.count() == 3
        assert self.post1 in posts
        assert self.post2 in posts
        assert self.post3 in posts

    def test_filter_posts_by_multiple_tags_all(self):
        """Test filtering posts by multiple tags (all match)."""
        posts = BlogPost.objects.filter(
            status="published",
            tags__slug="django"
        ).filter(
            tags__slug="python"
        ).distinct()

        assert posts.count() == 1
        assert self.post2 in posts

    def test_filter_excludes_draft_posts(self):
        """Test that filtering only returns published posts."""
        posts = BlogPost.objects.filter(
            status="published",
            tags__slug="python"
        ).distinct()

        assert self.post4 not in posts

    def test_filter_with_nonexistent_tag(self):
        """Test filtering with a tag that doesn't exist."""
        posts = BlogPost.objects.filter(
            status="published",
            tags__slug="nonexistent"
        ).distinct()

        assert posts.count() == 0


@pytest.mark.django_db
class TestBlogTagSearch(TestCase):
    """Tests for searching blog posts by tags."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.tag1 = BlogTag.objects.create(name="Python", slug="python")
        self.tag2 = BlogTag.objects.create(name="Django", slug="django")
        self.tag3 = BlogTag.objects.create(name="API", slug="api")

        self.post1 = BlogPost.objects.create(
            title="Python Basics",
            slug="python-basics",
            author=self.user,
            content="Content 1",
            status="published"
        )
        self.post2 = BlogPost.objects.create(
            title="Django Tutorial",
            slug="django-tutorial",
            author=self.user,
            content="Content 2",
            status="published"
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

    def test_search_tags_partial_match(self):
        """Test searching tags with partial matches."""
        tags = BlogTag.objects.filter(name__icontains="jango")
        assert tags.count() == 1
        assert self.tag2 in tags

    def test_search_posts_by_tag_name(self):
        """Test searching posts by tag name."""
        posts = BlogPost.objects.filter(
            status="published",
            tags__name__icontains="python"
        ).distinct()

        assert posts.count() == 1
        assert self.post1 in posts


@pytest.mark.django_db
class TestBlogTagViews(TestCase):
    """Tests for blog tag views and filtering."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.tag1 = BlogTag.objects.create(name="Python", slug="python")
        self.tag2 = BlogTag.objects.create(name="Django", slug="django")

        self.post1 = BlogPost.objects.create(
            title="Python Basics",
            slug="python-basics",
            author=self.user,
            content="Content 1",
            status="published"
        )
        self.post2 = BlogPost.objects.create(
            title="Django Tutorial",
            slug="django-tutorial",
            author=self.user,
            content="Content 2",
            status="published"
        )

        self.post1.tags.add(self.tag1)
        self.post2.tags.add(self.tag1, self.tag2)

    def test_blog_list_view_with_tag_filter(self):
        """Test blog list view with tag filtering."""
        response = self.client.get(reverse("blog:list"), {"tag": "python"})
        assert response.status_code == 200
        assert "posts" in response.context
        posts = response.context["posts"]
        assert self.post1 in posts or self.post2 in posts

    def test_blog_list_view_shows_all_tags(self):
        """Test that blog list view shows all available tags."""
        response = self.client.get(reverse("blog:list"))
        assert response.status_code == 200
        assert "tags" in response.context
        tags = response.context["tags"]
        assert self.tag1 in tags
        assert self.tag2 in tags

    def test_blog_detail_view_shows_tags(self):
        """Test that blog detail view shows post tags."""
        response = self.client.get(reverse("blog:detail", args=[self.post1.slug]))
        assert response.status_code == 200
        assert "post" in response.context
        post = response.context["post"]
        assert self.tag1 in post.tags.all()


@pytest.mark.django_db
class TestBlogTagIntegration(TestCase):
    """Integration tests for the blog tagging system."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.category = BlogCategory.objects.create(name="Tech", slug="tech")
        self.tag1 = BlogTag.objects.create(name="Python", slug="python")
        self.tag2 = BlogTag.objects.create(name="Django", slug="django")

    def test_post_with_categories_and_tags(self):
        """Test creating a post with both categories and tags."""
        post = BlogPost.objects.create(
            title="Full Featured Post",
            slug="full-featured-post",
            author=self.user,
            content="Content",
            status="published"
        )
        post.categories.add(self.category)
        post.tags.add(self.tag1, self.tag2)

        assert post.categories.count() == 1
        assert post.tags.count() == 2
        assert self.category in post.categories.all()
        assert self.tag1 in post.tags.all()
        assert self.tag2 in post.tags.all()

    def test_tag_count_with_multiple_posts(self):
        """Test tag count with multiple posts."""
        post1 = BlogPost.objects.create(
            title="Post 1",
            slug="post-1",
            author=self.user,
            content="Content 1",
            status="published"
        )
        post2 = BlogPost.objects.create(
            title="Post 2",
            slug="post-2",
            author=self.user,
            content="Content 2",
            status="published"
        )
        post3 = BlogPost.objects.create(
            title="Post 3",
            slug="post-3",
            author=self.user,
            content="Content 3",
            status="draft"
        )

        post1.tags.add(self.tag1)
        post2.tags.add(self.tag1)
        post3.tags.add(self.tag1)

        # Only published posts should be counted
        assert self.tag1.get_post_count() == 2

    def test_related_posts_by_tags(self):
        """Test getting related posts by shared tags."""
        post1 = BlogPost.objects.create(
            title="Post 1",
            slug="post-1",
            author=self.user,
            content="Content 1",
            status="published"
        )
        post2 = BlogPost.objects.create(
            title="Post 2",
            slug="post-2",
            author=self.user,
            content="Content 2",
            status="published"
        )
        post3 = BlogPost.objects.create(
            title="Post 3",
            slug="post-3",
            author=self.user,
            content="Content 3",
            status="published"
        )

        post1.tags.add(self.tag1, self.tag2)
        post2.tags.add(self.tag1)
        post3.tags.add(self.tag2)

        related = post1.get_related_posts(limit=5)
        assert post2 in related
        assert post3 in related
