"""
Property-based tests for tag-based search and filtering.

**Validates: Requirements 6 (Data Tags System)**
  - Tag-based filtering
  - Tag-based search functionality
"""
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from hypothesis import given, settings
from hypothesis import strategies as st
from hypothesis.extra.django import TestCase
from www.apps.blog.models import BlogPost, BlogTag
from www.apps.blog.services import PostFilterService, TagService

User = get_user_model()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_user():
    import uuid
    username = f"user_{uuid.uuid4().hex[:8]}"
    return User.objects.create_user(username=username, password="pass")


def make_tag(name):
    slug = slugify(name)
    if not slug:
        slug = f"tag-{name[:10]}"
    # Ensure uniqueness
    base_slug = slug[:40]
    slug = base_slug
    counter = 1
    while BlogTag.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return BlogTag.objects.create(name=name[:50], slug=slug[:50])


def make_post(user, title, tags, status="published"):
    slug = slugify(title)
    if not slug:
        slug = f"post-{title[:10]}"
    base_slug = slug[:200]
    slug = base_slug
    counter = 1
    while BlogPost.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    post = BlogPost.objects.create(
        title=title[:255],
        slug=slug,
        author=user,
        content="content",
        status=status,
    )
    for tag in tags:
        post.tags.add(tag)
    return post


# ---------------------------------------------------------------------------
# Property: filtering by a tag slug always returns only posts with that tag
# ---------------------------------------------------------------------------

class TestFilterByTagProperty(TestCase):
    """
    **Validates: Requirements 6 (Data Tags System) - Tag-based filtering**

    Property: For any tag T, filtering posts by T's slug returns only posts
    that have T assigned.
    """

    @given(
        tag_names=st.lists(
            st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll")), min_size=3, max_size=15),
            min_size=1,
            max_size=4,
            unique=True,
        ),
        num_posts=st.integers(min_value=1, max_value=6),
    )
    @settings(max_examples=20, deadline=5000)
    def test_filter_returns_only_posts_with_tag(self, tag_names, num_posts):
        """
        **Validates: Requirements 6 - Tag-based filtering**

        Filtering by a tag slug must return only posts that have that tag.
        """
        user = make_user()
        tags = [make_tag(name) for name in tag_names]
        target_tag = tags[0]

        # Create posts: some with target_tag, some without
        posts_with_tag = []
        posts_without_tag = []
        for i in range(num_posts):
            if i % 2 == 0:
                post = make_post(user, f"Post With {i}", [target_tag])
                posts_with_tag.append(post)
            else:
                other_tags = tags[1:] if len(tags) > 1 else []
                post = make_post(user, f"Post Without {i}", other_tags)
                posts_without_tag.append(post)

        qs = BlogPost.objects.all()
        result = PostFilterService.filter_by_tags(qs, [target_tag.slug])
        result_ids = set(result.values_list("id", flat=True))

        # All posts in result must have the target tag
        for post in result:
            assert post.tags.filter(slug=target_tag.slug).exists(), (
                f"Post '{post.title}' in filtered result does not have tag '{target_tag.slug}'"
            )

        # All posts_with_tag must be in result
        for post in posts_with_tag:
            assert post.id in result_ids, (
                f"Post '{post.title}' with tag '{target_tag.slug}' missing from result"
            )


# ---------------------------------------------------------------------------
# Property: search_tags always returns tags whose name/slug contains the query
# ---------------------------------------------------------------------------

class TestSearchTagsProperty(TestCase):
    """
    **Validates: Requirements 6 (Data Tags System) - Tag-based search**

    Property: search_tags(query) returns only tags whose name or slug
    contains the query (case-insensitive).
    """

    @given(
        tag_names=st.lists(
            st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll")), min_size=3, max_size=15),
            min_size=2,
            max_size=5,
            unique=True,
        ),
    )
    @settings(max_examples=20, deadline=5000)
    def test_search_results_contain_query(self, tag_names):
        """
        **Validates: Requirements 6 - Tag-based search**

        Every tag returned by search_tags must contain the query string
        in its name or slug.
        """
        tags = [make_tag(name) for name in tag_names]
        query = tag_names[0][:3].lower()

        results = TagService.search_tags(query)
        for tag in results:
            assert (
                query.lower() in tag.name.lower() or query.lower() in tag.slug.lower()
            ), (
                f"Tag '{tag.name}' (slug='{tag.slug}') returned for query '{query}' "
                f"but does not contain it"
            )


# ---------------------------------------------------------------------------
# Property: filter_by_tags with match_all=True returns only posts with ALL tags
# ---------------------------------------------------------------------------

class TestFilterMatchAllProperty(TestCase):
    """
    **Validates: Requirements 6 (Data Tags System) - Tag-based filtering**

    Property: filter_by_tags with match_all=True returns only posts that
    have every specified tag.
    """

    @given(
        num_posts=st.integers(min_value=2, max_value=6),
    )
    @settings(max_examples=15, deadline=5000)
    def test_match_all_requires_all_tags(self, num_posts):
        """
        **Validates: Requirements 6 - Tag-based filtering (match_all)**

        With match_all=True, every post in the result must have all
        specified tags.
        """
        user = make_user()
        tag_a = make_tag("Alpha")
        tag_b = make_tag("Beta")

        posts_both = []
        posts_one = []
        for i in range(num_posts):
            if i % 2 == 0:
                post = make_post(user, f"Both {i}", [tag_a, tag_b])
                posts_both.append(post)
            else:
                post = make_post(user, f"One {i}", [tag_a])
                posts_one.append(post)

        qs = BlogPost.objects.all()
        result = PostFilterService.filter_by_tags(qs, [tag_a.slug, tag_b.slug], match_all=True)

        for post in result:
            assert post.tags.filter(slug=tag_a.slug).exists()
            assert post.tags.filter(slug=tag_b.slug).exists()

        result_ids = set(result.values_list("id", flat=True))
        for post in posts_one:
            assert post.id not in result_ids, (
                "Post with only one tag should not appear in match_all result"
            )


# ---------------------------------------------------------------------------
# Property: get_popular_tags never returns tags with zero posts
# ---------------------------------------------------------------------------

class TestGetPopularTagsProperty(TestCase):
    """
    **Validates: Requirements 6 (Data Tags System) - Tag-based search**

    Property: get_popular_tags never returns tags that have no posts.
    """

    @given(
        num_used=st.integers(min_value=0, max_value=4),
        num_unused=st.integers(min_value=0, max_value=3),
    )
    @settings(max_examples=15, deadline=5000)
    def test_popular_tags_have_posts(self, num_used, num_unused):
        """
        **Validates: Requirements 6 - Tag-based search (popular tags)**

        get_popular_tags must only return tags that have at least one post.
        """
        user = make_user()

        for i in range(num_used):
            tag = make_tag(f"Used{i}")
            post = make_post(user, f"Post {i}", [tag])

        for i in range(num_unused):
            make_tag(f"Unused{i}")

        result = TagService.get_popular_tags(limit=100)
        for tag in result:
            assert tag.post_count > 0, (
                f"Tag '{tag.name}' has post_count=0 but appeared in get_popular_tags"
            )


# ---------------------------------------------------------------------------
# Property: filter_by_tags returns no duplicates
# ---------------------------------------------------------------------------

class TestFilterNoDuplicatesProperty(TestCase):
    """
    **Validates: Requirements 6 (Data Tags System) - Tag-based filtering**

    Property: filter_by_tags never returns duplicate posts.
    """

    @given(
        num_tags=st.integers(min_value=1, max_value=3),
        num_posts=st.integers(min_value=1, max_value=5),
    )
    @settings(max_examples=15, deadline=5000)
    def test_no_duplicate_posts_in_result(self, num_tags, num_posts):
        """
        **Validates: Requirements 6 - Tag-based filtering (no duplicates)**

        Filtering by multiple tags must not return duplicate posts.
        """
        user = make_user()
        tags = [make_tag(f"T{i}") for i in range(num_tags)]

        for i in range(num_posts):
            make_post(user, f"Post {i}", tags)

        qs = BlogPost.objects.all()
        slugs = [t.slug for t in tags]
        result = PostFilterService.filter_by_tags(qs, slugs)
        ids = list(result.values_list("id", flat=True))
        assert len(ids) == len(set(ids)), "filter_by_tags returned duplicate posts"


# ---------------------------------------------------------------------------
# Property: search_posts(q) always returns posts where title/content/excerpt
# contains q
# ---------------------------------------------------------------------------

class TestSearchPostsContainsQueryProperty(TestCase):
    """
    **Validates: Requirements 6 (Data Tags System) - Search functionality**

    Property: search_posts(q) returns only posts where title, content, or
    excerpt contains q (case-insensitive).
    """

    @given(
        queries=st.lists(
            st.text(
                alphabet=st.characters(whitelist_categories=("Lu", "Ll")),
                min_size=3,
                max_size=10,
            ),
            min_size=1,
            max_size=4,
            unique=True,
        ),
        num_posts=st.integers(min_value=1, max_value=5),
    )
    @settings(max_examples=20, deadline=5000)
    def test_search_returns_posts_containing_query(self, queries, num_posts):
        """
        **Validates: Requirements 6 - Search functionality**

        Every post returned by search_posts(q) must have q in its title,
        content, or excerpt.
        """
        user = make_user()
        query = queries[0].lower()

        # Create posts: some containing the query, some not
        for i in range(num_posts):
            if i % 2 == 0:
                # Post that contains the query in title
                title = f"Post {query} {i}"
            else:
                # Post that does not contain the query
                title = f"Unrelated {i}"
            slug = f"search-prop-{i}-{query[:5]}"
            base_slug = slug[:200]
            slug = base_slug
            counter = 1
            while BlogPost.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            BlogPost.objects.create(
                title=title[:255],
                slug=slug,
                author=user,
                content="content",
                status="published",
            )

        qs = BlogPost.objects.all()
        results = PostFilterService.search_posts(qs, query)

        for post in results:
            contains = (
                query.lower() in post.title.lower()
                or query.lower() in post.content.lower()
                or query.lower() in post.excerpt.lower()
            )
            assert contains, (
                f"Post '{post.title}' returned for query '{query}' "
                f"but does not contain it in title/content/excerpt"
            )
