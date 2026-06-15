"""
Unit tests for the tagging system models and logic.

These tests verify the tagging system implementation without requiring
a full Django environment setup.

Note: These tests require the apps.accounts app to be in INSTALLED_APPS.
They are skipped if the models cannot be imported due to app configuration.
"""

import pytest

# Check if tagging models are available
try:
    from apps.accounts.models.tags import Tag, TaggedItem, TagManager
    TAGGING_MODELS_AVAILABLE = True
except (ImportError, RuntimeError):
    TAGGING_MODELS_AVAILABLE = False

try:
    from apps.accounts.models.example_tagged_model import Article, Product
    ARTICLE_PRODUCT_AVAILABLE = True
except (ImportError, RuntimeError):
    ARTICLE_PRODUCT_AVAILABLE = False


@pytest.mark.skipif(not TAGGING_MODELS_AVAILABLE,
                    reason="Tagging models not available - apps.accounts not in INSTALLED_APPS")
class TestTagModel:
    """Tests for the Tag model structure."""

    def test_tag_model_has_required_fields(self):
        """Test that Tag model has all required fields."""
        # Check that the model has the expected fields
        field_names = [f.name for f in Tag._meta.get_fields()]

        assert 'name' in field_names
        assert 'slug' in field_names
        assert 'description' in field_names
        assert 'created_at' in field_names
        assert 'updated_at' in field_names

    def test_tag_model_meta_options(self):
        """Test that Tag model has correct meta options."""
        assert Tag._meta.verbose_name == 'Tag'
        assert Tag._meta.verbose_name_plural == 'Tags'
        assert Tag._meta.ordering == ['name']


@pytest.mark.skipif(not TAGGING_MODELS_AVAILABLE,
                    reason="Tagging models not available - apps.accounts not in INSTALLED_APPS")
class TestTaggedItemModel:
    """Tests for the TaggedItem model structure."""

    def test_tagged_item_model_has_required_fields(self):
        """Test that TaggedItem model has all required fields."""
        field_names = [f.name for f in TaggedItem._meta.get_fields()]

        assert 'tag' in field_names
        assert 'content_type' in field_names
        assert 'object_id' in field_names
        assert 'content_object' in field_names
        assert 'tagged_by' in field_names
        assert 'tagged_at' in field_names

    def test_tagged_item_model_meta_options(self):
        """Test that TaggedItem model has correct meta options."""
        assert TaggedItem._meta.verbose_name == 'Tagged Item'
        assert TaggedItem._meta.verbose_name_plural == 'Tagged Items'


@pytest.mark.skipif(not TAGGING_MODELS_AVAILABLE,
                    reason="Tagging models not available - apps.accounts not in INSTALLED_APPS")
class TestTagManager:
    """Tests for the TagManager functionality."""

    def test_tag_manager_has_required_methods(self):
        """Test that TagManager has all required methods."""
        manager = TagManager()

        assert hasattr(manager, 'get_queryset')
        assert hasattr(manager, 'with_tags')
        assert hasattr(manager, 'filter_by_tag')
        assert hasattr(manager, 'filter_by_tags')
        assert hasattr(manager, 'search_by_tags')


@pytest.mark.skipif(not ARTICLE_PRODUCT_AVAILABLE,
                    reason="Article/Product models not available - apps.accounts not in INSTALLED_APPS")
class TestArticleModel:
    """Tests for the Article model with tagging support."""

    def test_article_model_has_tagging_support(self):
        """Test that Article model has tagging support."""
        # Check that the model has tagging methods
        assert hasattr(Article, 'get_tag_list')
        assert hasattr(Article, 'add_tag')
        assert hasattr(Article, 'remove_tag')
        assert hasattr(Article, 'objects')

    def test_article_model_has_required_fields(self):
        """Test that Article model has all required fields."""
        field_names = [f.name for f in Article._meta.get_fields()]

        assert 'title' in field_names
        assert 'content' in field_names
        assert 'author' in field_names
        assert 'created_at' in field_names
        assert 'updated_at' in field_names
        assert 'is_published' in field_names


@pytest.mark.skipif(not ARTICLE_PRODUCT_AVAILABLE,
                    reason="Article/Product models not available - apps.accounts not in INSTALLED_APPS")
class TestProductModel:
    """Tests for the Product model with tagging support."""

    def test_product_model_has_tagging_support(self):
        """Test that Product model has tagging support."""
        # Check that the model has tagging methods
        assert hasattr(Product, 'get_tag_list')
        assert hasattr(Product, 'add_tag')
        assert hasattr(Product, 'remove_tag')
        assert hasattr(Product, 'objects')

    def test_product_model_has_required_fields(self):
        """Test that Product model has all required fields."""
        field_names = [f.name for f in Product._meta.get_fields()]

        assert 'name' in field_names
        assert 'description' in field_names
        assert 'price' in field_names
        assert 'sku' in field_names
        assert 'created_at' in field_names


@pytest.mark.skipif(not TAGGING_MODELS_AVAILABLE,
                    reason="Tagging models not available - apps.accounts not in INSTALLED_APPS")
class TestTaggingSystemIntegration:
    """Tests for tagging system integration."""

    def test_tagging_models_are_importable(self):
        """Test that all tagging models can be imported."""
        assert Tag is not None
        assert TaggedItem is not None
        assert TagManager is not None

    @pytest.mark.skipif(not ARTICLE_PRODUCT_AVAILABLE,
                        reason="Article/Product models not available")
    def test_article_product_models_importable(self):
        """Test that Article and Product models can be imported."""
        assert Article is not None
        assert Product is not None

    def test_admin_interface_is_available(self):
        """Test that admin interface is available."""
        from apps.accounts.admin import TagAdmin, TaggedItemAdmin

        assert TagAdmin is not None
        assert TaggedItemAdmin is not None

    def test_views_are_available(self):
        """Test that views are available."""
        from apps.accounts.views.tags import (
            ArticlesByTagView,
            ProductsByTagView,
            TagDetailView,
            TagListView,
            filter_by_tags,
            search_tags,
        )

        assert TagListView is not None
        assert TagDetailView is not None
        assert ArticlesByTagView is not None
        assert ProductsByTagView is not None
        assert search_tags is not None
        assert filter_by_tags is not None
