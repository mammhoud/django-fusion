"""
Example model demonstrating how to use the custom tagging system.
"""

from django.db import models
from taggit.managers import TaggableManager

from .tags import TaggedItem


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

    # Custom tagging manager using our TaggedItem model
    tags = TaggableManager(through=TaggedItem, blank=True)

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_tag_list(self):
        """Return a list of tag names for this article."""
        return [tag.name for tag in self.tags.all()]

    def add_tag_with_user(self, tag_name, user):
        """Add a tag to this article with user tracking."""
        tag, created = self.tags.get_or_create(name=tag_name)
        tagged_item, created = TaggedItem.objects.get_or_create(
            tag=tag,
            content_object=self,
            defaults={'tagged_by': user}
        )
        return tagged_item


class Product(models.Model):
    """
    Another example model that can be tagged.
    """
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sku = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Custom tagging manager
    tags = TaggableManager(through=TaggedItem, blank=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['name']

    def __str__(self):
        return self.name
