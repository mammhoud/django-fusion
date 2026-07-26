"""
Example model demonstrating how to use the custom tagging system.
"""

from django.contrib.contenttypes.models import ContentType
from django.db import models

from .tags import Tag, TaggedItem, TagManager


class Article(models.Model):
    """
    Example model that can be tagged using our custom tagging system.
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)

    objects = TagManager()

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_tag_list(self):
        """Return a list of tag names for this article."""
        content_type = ContentType.objects.get_for_model(self)
        tagged_items = TaggedItem.objects.filter(
            content_type=content_type,
            object_id=self.id
        )
        return [item.tag.name for item in tagged_items]

    def add_tag(self, tag_name, user=None):
        """Add a tag to this article with user tracking."""
        tag, created = Tag.objects.get_or_create(
            name=tag_name,
            defaults={'slug': tag_name.lower().replace(' ', '-')}
        )
        content_type = ContentType.objects.get_for_model(self)
        tagged_item, created = TaggedItem.objects.get_or_create(
            tag=tag,
            content_type=content_type,
            object_id=self.id,
            defaults={'tagged_by': user}
        )
        return tagged_item

    def remove_tag(self, tag_name):
        """Remove a tag from this article."""
        tag = Tag.objects.get(name=tag_name)
        content_type = ContentType.objects.get_for_model(self)
        TaggedItem.objects.filter(
            tag=tag,
            content_type=content_type,
            object_id=self.id
        ).delete()


class Product(models.Model):
    """
    Another example model that can be tagged.
    """
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sku = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TagManager()

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_tag_list(self):
        """Return a list of tag names for this product."""
        content_type = ContentType.objects.get_for_model(self)
        tagged_items = TaggedItem.objects.filter(
            content_type=content_type,
            object_id=self.id
        )
        return [item.tag.name for item in tagged_items]

    def add_tag(self, tag_name, user=None):
        """Add a tag to this product with user tracking."""
        tag, created = Tag.objects.get_or_create(
            name=tag_name,
            defaults={'slug': tag_name.lower().replace(' ', '-')}
        )
        content_type = ContentType.objects.get_for_model(self)
        tagged_item, created = TaggedItem.objects.get_or_create(
            tag=tag,
            content_type=content_type,
            object_id=self.id,
            defaults={'tagged_by': user}
        )
        return tagged_item

    def remove_tag(self, tag_name):
        """Remove a tag from this product."""
        tag = Tag.objects.get(name=tag_name)
        content_type = ContentType.objects.get_for_model(self)
        TaggedItem.objects.filter(
            tag=tag,
            content_type=content_type,
            object_id=self.id
        ).delete()
