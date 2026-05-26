"""
Unit tests for blog models: BlogTag, BlogCategory, BlogPost, BlogComment.
"""
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from www.apps.blog.models import BlogCategory, BlogComment, BlogPost, BlogTag

User = get_user_model()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def user(db):
    return User.objects.create_user(username="author", password="pass")


@pytest.fixture
def tag(db):
    return BlogTag.objects.create(name="Python", slug="python")


@pytest.fixture
def category(db):
    return BlogCategory.objects.create(name="Research", slug="research")


@pytest.fixture
def published_post(db, user):
    return BlogPost.objects.create(
        title="Hello World",
        slug="hello-world",
        author=user,
        content="Some content here",
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
# BlogTag
# ---------------------------------------------------------------------------

class TestBlogTag:
    def test_str(self, tag):
        assert str(tag) == "Python"

    def test_save_auto_slug(self, db):
        t = BlogTag.objects.create(name="Machine Learning")
        assert t.slug == "machine-learning"

    def test_save_preserves_existing_slug(self, db):
        t = BlogTag.objects.create(name="Django", slug="custom-slug")
        assert t.slug == "custom-slug"

    def test_get_post_count_published_only(self, db, user, tag):
        # published post counts
        post = BlogPost.objects.create(
            title="Pub", slug="pub", author=user, content="x", status="published"
        )
        post.tags.add(tag)
        # draft post does not count
        draft = BlogPost.objects.create(
            title="Drft", slug="drft", author=user, content="x", status="draft"
        )
        draft.tags.add(tag)
        assert tag.get_post_count() == 1

    def test_get_post_count_zero_when_no_posts(self, tag):
        assert tag.get_post_count() == 0


# ---------------------------------------------------------------------------
# BlogCategory
# ---------------------------------------------------------------------------

class TestBlogCategory:
    def test_str(self, category):
        assert str(category) == "Research"

    def test_save_auto_slug(self, db):
        c = BlogCategory.objects.create(name="Artificial Intelligence")
        assert c.slug == "artificial-intelligence"

    def test_save_preserves_existing_slug(self, db):
        c = BlogCategory.objects.create(name="News", slug="my-news")
        assert c.slug == "my-news"

    def test_description_default_empty(self, db):
        c = BlogCategory.objects.create(name="Empty", slug="empty")
        assert c.description == ""

    def test_get_post_count_published_only(self, db, user, category):
        post = BlogPost.objects.create(
            title="Cat Post", slug="cat-post", author=user, content="x", status="published"
        )
        post.categories.add(category)
        draft = BlogPost.objects.create(
            title="Cat Draft", slug="cat-draft", author=user, content="x", status="draft"
        )
        draft.categories.add(category)
        assert category.get_post_count() == 1

    def test_get_post_count_zero_when_no_posts(self, category):
        assert category.get_post_count() == 0


# ---------------------------------------------------------------------------
# BlogPost
# ---------------------------------------------------------------------------

class TestBlogPost:
    def test_str(self, published_post):
        assert str(published_post) == "Hello World"

    def test_save_auto_slug(self, db, user):
        post = BlogPost.objects.create(
            title="Auto Slug Post", author=user, content="x", status="draft"
        )
        assert post.slug == "auto-slug-post"

    def test_save_preserves_existing_slug(self, db, user):
        post = BlogPost.objects.create(
            title="Some Title", slug="custom-slug", author=user, content="x", status="draft"
        )
        assert post.slug == "custom-slug"

    def test_save_auto_published_date_on_publish(self, db, user):
        post = BlogPost.objects.create(
            title="New Post", slug="new-post", author=user, content="x", status="published"
        )
        assert post.published_date is not None

    def test_save_no_published_date_for_draft(self, db, user):
        post = BlogPost.objects.create(
            title="Draft", slug="draft-x", author=user, content="x", status="draft"
        )
        assert post.published_date is None

    def test_save_does_not_overwrite_existing_published_date(self, db, user):
        fixed_date = timezone.now().replace(microsecond=0)
        post = BlogPost.objects.create(
            title="Dated", slug="dated", author=user, content="x",
            status="published", published_date=fixed_date,
        )
        assert post.published_date == fixed_date

    def test_get_reading_time_minimum_one(self, db, user):
        post = BlogPost.objects.create(
            title="Short", slug="short", author=user, content="hi", status="draft"
        )
        assert post.get_reading_time() == 1

    def test_get_reading_time_scales_with_word_count(self, db, user):
        # 400 words → 2 minutes at 200 wpm
        content = " ".join(["word"] * 400)
        post = BlogPost.objects.create(
            title="Long", slug="long", author=user, content=content, status="draft"
        )
        assert post.get_reading_time() == 2

    def test_is_published_true_for_published(self, published_post):
        assert published_post.is_published is True

    def test_is_published_false_for_draft(self, draft_post):
        assert draft_post.is_published is False

    def test_publish_sets_status_and_date(self, draft_post):
        draft_post.publish()
        draft_post.refresh_from_db()
        assert draft_post.status == "published"
        assert draft_post.published_date is not None

    def test_archive_sets_status(self, published_post):
        published_post.archive()
        published_post.refresh_from_db()
        assert published_post.status == "archived"

    def test_get_related_posts_by_tag(self, db, user, tag):
        post_a = BlogPost.objects.create(
            title="A", slug="a", author=user, content="x", status="published"
        )
        post_a.tags.add(tag)
        post_b = BlogPost.objects.create(
            title="B", slug="b", author=user, content="x", status="published"
        )
        post_b.tags.add(tag)
        related = list(post_a.get_related_posts(limit=5))
        assert post_b in related
        assert post_a not in related

    def test_get_related_posts_excludes_non_published(self, db, user, tag):
        post_a = BlogPost.objects.create(
            title="A", slug="a", author=user, content="x", status="published"
        )
        post_a.tags.add(tag)
        draft = BlogPost.objects.create(
            title="D", slug="d", author=user, content="x", status="draft"
        )
        draft.tags.add(tag)
        related = list(post_a.get_related_posts(limit=5))
        assert draft not in related

    def test_get_related_posts_by_category(self, db, user, category):
        post_a = BlogPost.objects.create(
            title="CA", slug="ca", author=user, content="x", status="published"
        )
        post_a.categories.add(category)
        post_b = BlogPost.objects.create(
            title="CB", slug="cb", author=user, content="x", status="published"
        )
        post_b.categories.add(category)
        related = list(post_a.get_related_posts(limit=5))
        assert post_b in related

    def test_get_related_posts_respects_limit(self, db, user, tag):
        base = BlogPost.objects.create(
            title="Base", slug="base", author=user, content="x", status="published"
        )
        base.tags.add(tag)
        for i in range(5):
            p = BlogPost.objects.create(
                title=f"R{i}", slug=f"r{i}", author=user, content="x", status="published"
            )
            p.tags.add(tag)
        related = list(base.get_related_posts(limit=2))
        assert len(related) <= 2


# ---------------------------------------------------------------------------
# BlogComment
# ---------------------------------------------------------------------------

class TestBlogComment:
    def test_str(self, db, user, published_post):
        comment = BlogComment.objects.create(
            post=published_post, author=user, content="Nice post!"
        )
        assert str(comment) == f"Comment by {user} on '{published_post}'"

    def test_is_approved_default_false(self, db, user, published_post):
        comment = BlogComment.objects.create(
            post=published_post, author=user, content="Test"
        )
        assert comment.is_approved is False

    def test_ordering_by_created_at(self, db, user, published_post):
        c1 = BlogComment.objects.create(post=published_post, author=user, content="First")
        c2 = BlogComment.objects.create(post=published_post, author=user, content="Second")
        comments = list(BlogComment.objects.filter(post=published_post))
        assert comments[0] == c1
        assert comments[1] == c2
