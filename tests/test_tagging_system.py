"""
Tests for the custom tagging system.
"""

import pytest
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from apps.accounts.models.example_tagged_model import Article, Product
from apps.accounts.models.tags import Tag, TaggedItem


@pytest.mark.django_db
class TestTagModel:
    """Tests for the Tag model."""

    def test_create_tag(self):
        """Test creating a tag."""
        tag = Tag.objects.create(
            name='Python',
            slug='python',
            description='Python programming language'
        )
        assert tag.name == 'Python'
        assert tag.slug == 'python'
        assert str(tag) == 'Python'

    def test_tag_uniqueness(self):
        """Test that tag names are unique."""
        Tag.objects.create(name='Django', slug='django')
        with pytest.raises(Exception):
            Tag.objects.create(name='Django', slug='django-2')

    def test_tag_ordering(self):
        """Test that tags are ordered by name."""
        Tag.objects.create(name='Zebra', slug='zebra')
        Tag.objects.create(name='Apple', slug='apple')
        Tag.objects.create(name='Banana', slug='banana')

        tags = list(Tag.objects.all())
        assert tags[0].name == 'Apple'
        assert tags[1].name == 'Banana'
        assert tags[2].name == 'Zebra'


@pytest.mark.django_db
class TestTaggedItem:
    """Tests for the TaggedItem model."""

    def test_create_tagged_item(self):
        """Test creating a tagged item."""
        user = User.objects.create_user(username='testuser')
        article = Article.objects.create(
            title='Test Article',
            content='Test content',
            author=user
        )
        tag = Tag.objects.create(name='Test', slug='test')

        tagged_item = TaggedItem.objects.create(
            tag=tag,
            content_type=ContentType.objects.get_for_model(Article),
            object_id=article.id,
            tagged_by=user
        )

        assert tagged_item.tag == tag
        assert tagged_item.content_object == article
        assert tagged_item.tagged_by == user

    def test_tagged_item_uniqueness(self):
        """Test that duplicate tags on same object are prevented."""
        user = User.objects.create_user(username='testuser')
        article = Article.objects.create(
            title='Test Article',
            content='Test content',
            author=user
        )
        tag = Tag.objects.create(name='Test', slug='test')

        TaggedItem.objects.create(
            tag=tag,
            content_type=ContentType.objects.get_for_model(Article),
            object_id=article.id,
            tagged_by=user
        )

        with pytest.raises(Exception):
            TaggedItem.objects.create(
                tag=tag,
                content_type=ContentType.objects.get_for_model(Article),
                object_id=article.id,
                tagged_by=user
            )


@pytest.mark.django_db
class TestArticleTagging:
    """Tests for tagging articles."""

    def test_add_tag_to_article(self):
        """Test adding a tag to an article."""
        user = User.objects.create_user(username='testuser')
        article = Article.objects.create(
            title='Test Article',
            content='Test content',
            author=user
        )

        article.add_tag('Python', user)

        tags = article.get_tag_list()
        assert 'Python' in tags

    def test_remove_tag_from_article(self):
        """Test removing a tag from an article."""
        user = User.objects.create_user(username='testuser')
        article = Article.objects.create(
            title='Test Article',
            content='Test content',
            author=user
        )

        article.add_tag('Python', user)
        article.remove_tag('Python')

        tags = article.get_tag_list()
        assert 'Python' not in tags

    def test_get_tag_list(self):
        """Test getting all tags for an article."""
        user = User.objects.create_user(username='testuser')
        article = Article.objects.create(
            title='Test Article',
            content='Test content',
            author=user
        )

        article.add_tag('Python', user)
        article.add_tag('Django', user)
        article.add_tag('Web Development', user)

        tags = article.get_tag_list()
        assert len(tags) == 3
        assert 'Python' in tags
        assert 'Django' in tags
        assert 'Web Development' in tags


@pytest.mark.django_db
class TestProductTagging:
    """Tests for tagging products."""

    def test_add_tag_to_product(self):
        """Test adding a tag to a product."""
        product = Product.objects.create(
            name='Test Product',
            description='Test description',
            price=99.99,
            sku='TEST-001'
        )

        product.add_tag('Electronics')

        tags = product.get_tag_list()
        assert 'Electronics' in tags

    def test_multiple_tags_on_product(self):
        """Test adding multiple tags to a product."""
        product = Product.objects.create(
            name='Test Product',
            description='Test description',
            price=99.99,
            sku='TEST-001'
        )

        product.add_tag('Electronics')
        product.add_tag('Gadgets')
        product.add_tag('New')

        tags = product.get_tag_list()
        assert len(tags) == 3


@pytest.mark.django_db
class TestTagFiltering:
    """Tests for tag-based filtering."""

    def test_filter_articles_by_single_tag(self):
        """Test filtering articles by a single tag."""
        user = User.objects.create_user(username='testuser')

        article1 = Article.objects.create(
            title='Article 1',
            content='Content 1',
            author=user
        )
        article2 = Article.objects.create(
            title='Article 2',
            content='Content 2',
            author=user
        )
        article3 = Article.objects.create(
            title='Article 3',
            content='Content 3',
            author=user
        )

        article1.add_tag('Python', user)
        article2.add_tag('Python', user)
        article3.add_tag('JavaScript', user)

        filtered = Article.objects.filter_by_tag('Python')
        assert filtered.count() == 2
        assert article1 in filtered
        assert article2 in filtered
        assert article3 not in filtered

    def test_filter_articles_by_multiple_tags_any(self):
        """Test filtering articles by multiple tags (any match)."""
        user = User.objects.create_user(username='testuser')

        article1 = Article.objects.create(
            title='Article 1',
            content='Content 1',
            author=user
        )
        article2 = Article.objects.create(
            title='Article 2',
            content='Content 2',
            author=user
        )
        article3 = Article.objects.create(
            title='Article 3',
            content='Content 3',
            author=user
        )

        article1.add_tag('Python', user)
        article2.add_tag('JavaScript', user)
        article3.add_tag('Ruby', user)

        filtered = Article.objects.filter_by_tags(['Python', 'JavaScript'], match_all=False)
        assert filtered.count() == 2
        assert article1 in filtered
        assert article2 in filtered

    def test_filter_articles_by_multiple_tags_all(self):
        """Test filtering articles by multiple tags (all must match)."""
        user = User.objects.create_user(username='testuser')

        article1 = Article.objects.create(
            title='Article 1',
            content='Content 1',
            author=user
        )
        article2 = Article.objects.create(
            title='Article 2',
            content='Content 2',
            author=user
        )

        article1.add_tag('Python', user)
        article1.add_tag('Django', user)
        article2.add_tag('Python', user)

        filtered = Article.objects.filter_by_tags(['Python', 'Django'], match_all=True)
        assert filtered.count() == 1
        assert article1 in filtered
        assert article2 not in filtered


@pytest.mark.django_db
class TestTagSearch:
    """Tests for tag-based search."""

    def test_search_articles_by_tag_name(self):
        """Test searching articles by tag name."""
        user = User.objects.create_user(username='testuser')

        article1 = Article.objects.create(
            title='Article 1',
            content='Content 1',
            author=user
        )
        article2 = Article.objects.create(
            title='Article 2',
            content='Content 2',
            author=user
        )

        article1.add_tag('Python Programming', user)
        article2.add_tag('JavaScript', user)

        filtered = Article.objects.search_by_tags('Python')
        assert filtered.count() == 1
        assert article1 in filtered

    def test_search_articles_by_tag_description(self):
        """Test searching articles by tag description."""
        user = User.objects.create_user(username='testuser')

        article = Article.objects.create(
            title='Article 1',
            content='Content 1',
            author=user
        )

        tag = Tag.objects.create(
            name='Web',
            slug='web',
            description='Web development and design'
        )

        content_type = ContentType.objects.get_for_model(Article)
        TaggedItem.objects.create(
            tag=tag,
            content_type=content_type,
            object_id=article.id,
            tagged_by=user
        )

        filtered = Article.objects.search_by_tags('development')
        assert filtered.count() == 1
        assert article in filtered


@pytest.mark.django_db
class TestTagManager:
    """Tests for the TagManager."""

    def test_with_tags_prefetch(self):
        """Test prefetching tags for better performance."""
        user = User.objects.create_user(username='testuser')

        article = Article.objects.create(
            title='Article 1',
            content='Content 1',
            author=user
        )

        article.add_tag('Python', user)

        # This should use prefetch_related
        articles = Article.objects.with_tags()
        assert articles.count() == 1
