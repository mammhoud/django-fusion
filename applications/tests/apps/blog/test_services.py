"""
Unit tests for TagService and PostFilterService.
"""
import pytest
from django.contrib.auth import get_user_model
from www.apps.blog.models import BlogPost, BlogTag
from www.apps.blog.services import PostFilterService, TagService

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="pass")


@pytest.fixture
def tag_python(db):
    return BlogTag.objects.create(name="Python", slug="python")


@pytest.fixture
def tag_django(db):
    return BlogTag.objects.create(name="Django", slug="django")


@pytest.fixture
def tag_unused(db):
    return BlogTag.objects.create(name="Unused", slug="unused")


@pytest.fixture
def published_post(db, user, tag_python):
    post = BlogPost.objects.create(
        title="Python Post",
        slug="python-post",
        author=user,
        content="Content about Python",
        status="published",
    )
    post.tags.add(tag_python)
    return post


@pytest.fixture
def draft_post(db, user, tag_python):
    post = BlogPost.objects.create(
        title="Draft Post",
        slug="draft-post",
        author=user,
        content="Draft content",
        status="draft",
    )
    post.tags.add(tag_python)
    return post


@pytest.fixture
def multi_tag_post(db, user, tag_python, tag_django):
    post = BlogPost.objects.create(
        title="Multi Tag Post",
        slug="multi-tag-post",
        author=user,
        content="Content about Python and Django",
        status="published",
    )
    post.tags.add(tag_python, tag_django)
    return post


# ---------------------------------------------------------------------------
# TagService tests
# ---------------------------------------------------------------------------

class TestTagServiceGetPopularTags:
    def test_returns_tags_with_posts(self, db, published_post, tag_python, tag_unused):
        result = TagService.get_popular_tags(limit=10)
        slugs = [t.slug for t in result]
        assert "python" in slugs
        assert "unused" not in slugs

    def test_respects_limit(self, db, user):
        for i in range(5):
            tag = BlogTag.objects.create(name=f"Tag{i}", slug=f"tag{i}")
            post = BlogPost.objects.create(
                title=f"Post {i}", slug=f"post-{i}", author=user,
                content="x", status="published",
            )
            post.tags.add(tag)
        result = TagService.get_popular_tags(limit=3)
        assert len(result) <= 3

    def test_ordered_by_post_count_descending(self, db, user, tag_python, tag_django):
        # tag_python gets 2 posts, tag_django gets 1
        for i in range(2):
            post = BlogPost.objects.create(
                title=f"Py Post {i}", slug=f"py-post-{i}", author=user,
                content="x", status="published",
            )
            post.tags.add(tag_python)
        post = BlogPost.objects.create(
            title="Dj Post", slug="dj-post", author=user,
            content="x", status="published",
        )
        post.tags.add(tag_django)
        result = list(TagService.get_popular_tags(limit=10))
        assert result[0].slug == "python"


class TestTagServiceSearchTags:
    def test_finds_by_name(self, db, tag_python):
        result = TagService.search_tags("pyth")
        assert tag_python in result

    def test_finds_by_slug(self, db, tag_python):
        result = TagService.search_tags("python")
        assert tag_python in result

    def test_case_insensitive(self, db, tag_python):
        result = TagService.search_tags("PYTHON")
        assert tag_python in result

    def test_no_match_returns_empty(self, db, tag_python):
        result = TagService.search_tags("zzznomatch")
        assert result.count() == 0


class TestTagServiceGetRelatedTags:
    def test_returns_co_occurring_tags(self, db, multi_tag_post, tag_python, tag_django):
        related = list(TagService.get_related_tags(tag_python, limit=10))
        assert tag_django in related

    def test_excludes_self(self, db, multi_tag_post, tag_python):
        related = list(TagService.get_related_tags(tag_python, limit=10))
        assert tag_python not in related

    def test_no_related_returns_empty(self, db, published_post, tag_python, tag_unused):
        # tag_unused has no posts, so no co-occurrence
        related = list(TagService.get_related_tags(tag_unused, limit=10))
        assert related == []


class TestTagServiceGetTagCloud:
    def test_returns_tags_with_size(self, db, published_post, tag_python):
        cloud = TagService.get_tag_cloud(limit=10)
        assert len(cloud) >= 1
        for tag in cloud:
            assert hasattr(tag, "size")
            assert 1 <= tag.size <= 5

    def test_empty_when_no_posts(self, db):
        result = TagService.get_tag_cloud(limit=10)
        assert result == []

    def test_single_tag_gets_size_3(self, db, published_post, tag_python):
        cloud = TagService.get_tag_cloud(limit=10)
        assert cloud[0].size == 3


class TestTagServiceCleanupUnusedTags:
    def test_removes_unused_tags(self, db, tag_unused):
        count = TagService.cleanup_unused_tags()
        assert count == 1
        assert not BlogTag.objects.filter(slug="unused").exists()

    def test_keeps_used_tags(self, db, published_post, tag_python, tag_unused):
        TagService.cleanup_unused_tags()
        assert BlogTag.objects.filter(slug="python").exists()

    def test_returns_count(self, db, tag_unused):
        count = TagService.cleanup_unused_tags()
        assert count == 1


class TestTagServiceMergeTags:
    def test_moves_posts_to_new_tag(self, db, published_post, tag_python, tag_django):
        TagService.merge_tags(tag_python, tag_django)
        assert published_post.tags.filter(slug="django").exists()

    def test_removes_old_tag(self, db, published_post, tag_python, tag_django):
        TagService.merge_tags(tag_python, tag_django)
        assert not BlogTag.objects.filter(slug="python").exists()


# ---------------------------------------------------------------------------
# PostFilterService tests
# ---------------------------------------------------------------------------

class TestPostFilterServiceFilterByTags:
    def test_filters_by_single_tag(self, db, published_post, draft_post, tag_python):
        qs = BlogPost.objects.all()
        result = PostFilterService.filter_by_tags(qs, ["python"])
        assert published_post in result
        assert draft_post in result  # filter doesn't restrict by status

    def test_empty_slugs_returns_all(self, db, published_post):
        qs = BlogPost.objects.all()
        result = PostFilterService.filter_by_tags(qs, [])
        assert result.count() == BlogPost.objects.count()

    def test_match_all_requires_all_tags(self, db, user, tag_python, tag_django, tag_unused):
        post_both = BlogPost.objects.create(
            title="Both", slug="both", author=user, content="x", status="published"
        )
        post_both.tags.add(tag_python, tag_django)
        post_one = BlogPost.objects.create(
            title="One", slug="one", author=user, content="x", status="published"
        )
        post_one.tags.add(tag_python)

        qs = BlogPost.objects.all()
        result = PostFilterService.filter_by_tags(qs, ["python", "django"], match_all=True)
        assert post_both in result
        assert post_one not in result

    def test_no_duplicates_with_multiple_tags(self, db, multi_tag_post, tag_python, tag_django):
        qs = BlogPost.objects.all()
        result = PostFilterService.filter_by_tags(qs, ["python", "django"])
        ids = list(result.values_list("id", flat=True))
        assert len(ids) == len(set(ids))


class TestPostFilterServiceSearchPosts:
    def test_finds_by_title(self, db, published_post):
        qs = BlogPost.objects.all()
        result = PostFilterService.search_posts(qs, "Python Post")
        assert published_post in result

    def test_finds_by_content(self, db, published_post):
        qs = BlogPost.objects.all()
        result = PostFilterService.search_posts(qs, "Content about Python")
        assert published_post in result

    def test_empty_query_returns_all(self, db, published_post):
        qs = BlogPost.objects.all()
        result = PostFilterService.search_posts(qs, "")
        assert result.count() == BlogPost.objects.count()

    def test_no_match_returns_empty(self, db, published_post):
        qs = BlogPost.objects.all()
        result = PostFilterService.search_posts(qs, "zzznomatch")
        assert result.count() == 0


class TestPostFilterServiceFilterByCategories:
    def test_filters_by_single_category(self, db, user):
        from www.apps.blog.models import BlogCategory
        cat = BlogCategory.objects.create(name="Science", slug="science")
        post_in = BlogPost.objects.create(
            title="Science Post", slug="science-post", author=user, content="x", status="published"
        )
        post_in.categories.add(cat)
        post_out = BlogPost.objects.create(
            title="Other Post", slug="other-post", author=user, content="x", status="published"
        )
        qs = BlogPost.objects.all()
        result = PostFilterService.filter_by_categories(qs, ["science"])
        assert post_in in result
        assert post_out not in result

    def test_empty_slugs_returns_all(self, db, published_post):
        qs = BlogPost.objects.all()
        result = PostFilterService.filter_by_categories(qs, [])
        assert result.count() == BlogPost.objects.count()

    def test_no_duplicates_with_multiple_categories(self, db, user):
        from www.apps.blog.models import BlogCategory
        cat_a = BlogCategory.objects.create(name="CatA", slug="cat-a")
        cat_b = BlogCategory.objects.create(name="CatB", slug="cat-b")
        post = BlogPost.objects.create(
            title="Multi Cat", slug="multi-cat", author=user, content="x", status="published"
        )
        post.categories.add(cat_a, cat_b)
        qs = BlogPost.objects.all()
        result = PostFilterService.filter_by_categories(qs, ["cat-a", "cat-b"])
        ids = list(result.values_list("id", flat=True))
        assert len(ids) == len(set(ids))


class TestPostFilterServiceFilterByStatus:
    def test_filters_published(self, db, published_post, draft_post):
        qs = BlogPost.objects.all()
        result = PostFilterService.filter_by_status(qs, "published")
        assert published_post in result
        assert draft_post not in result

    def test_filters_draft(self, db, published_post, draft_post):
        qs = BlogPost.objects.all()
        result = PostFilterService.filter_by_status(qs, "draft")
        assert draft_post in result
        assert published_post not in result

    def test_empty_status_returns_all(self, db, published_post, draft_post):
        qs = BlogPost.objects.all()
        result = PostFilterService.filter_by_status(qs, "")
        assert result.count() == BlogPost.objects.count()


class TestPostFilterServiceApplyFilters:
    def test_combined_tag_and_status(self, db, published_post, draft_post, tag_python):
        qs = BlogPost.objects.all()
        result = PostFilterService.apply_filters(qs, tags=["python"], status="published")
        assert published_post in result
        assert draft_post not in result

    def test_combined_search_and_status(self, db, published_post, draft_post):
        qs = BlogPost.objects.all()
        result = PostFilterService.apply_filters(qs, status="published", query="Python Post")
        assert published_post in result
        assert draft_post not in result

    def test_no_filters_returns_all(self, db, published_post, draft_post):
        qs = BlogPost.objects.all()
        result = PostFilterService.apply_filters(qs)
        assert result.count() == BlogPost.objects.count()

    def test_combined_category_and_tag(self, db, user, tag_python):
        from www.apps.blog.models import BlogCategory
        cat = BlogCategory.objects.create(name="Tech", slug="tech")
        post = BlogPost.objects.create(
            title="Tech Python", slug="tech-python", author=user, content="x", status="published"
        )
        post.tags.add(tag_python)
        post.categories.add(cat)
        other = BlogPost.objects.create(
            title="Other", slug="other-x", author=user, content="x", status="published"
        )
        qs = BlogPost.objects.all()
        result = PostFilterService.apply_filters(qs, tags=["python"], categories=["tech"])
        assert post in result
        assert other not in result
