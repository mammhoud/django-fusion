"""
Example model demonstrating how to use the custom tagging system.
"""

from django.contrib.contenttypes.models import ContentType
from django.db import models

from .tags import Tag, TaggedItem, TagManager


class TaggableMixin(models.Model):
    """Mixin that adds tagging support to a model."""

    class Meta:
        abstract = True

    def add_tag(self, tag_name, user=None):
        """Add a tag to this object by name."""
        tag, _ = Tag.objects.get_or_create(
            name=tag_name,
            defaults={"slug": tag_name.lower().replace(" ", "-")},
        )
        content_type = ContentType.objects.get_for_model(self.__class__)
        TaggedItem.objects.get_or_create(
            tag=tag,
            content_type=content_type,
            object_id=self.pk,
            defaults={"tagged_by": user},
        )

    def remove_tag(self, tag_name):
        """Remove a tag from this object by name."""
        content_type = ContentType.objects.get_for_model(self.__class__)
        TaggedItem.objects.filter(
            tag__name=tag_name,
            content_type=content_type,
            object_id=self.pk,
        ).delete()

    def get_tag_list(self):
        """Return a list of tag names for this object."""
        content_type = ContentType.objects.get_for_model(self.__class__)
        return list(
            TaggedItem.objects.filter(
                content_type=content_type,
                object_id=self.pk,
            ).values_list("tag__name", flat=True)
        )


class ArticleManager(TagManager):
    pass


class Article(TaggableMixin, models.Model):
    """
    Example model that can be tagged using our custom tagging system.
    """

    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)

    objects = ArticleManager()

    class Meta:
        app_label = 'accounts'
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def add_tag_with_user(self, tag_name, user):
        """Add a tag to this article with user tracking (alias for add_tag)."""
        return self.add_tag(tag_name, user)


class ProductManager(TagManager):
    pass


class Product(TaggableMixin, models.Model):
    """
    Another example model that can be tagged.
    """

    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sku = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ProductManager()

    class Meta:
        app_label = 'accounts'
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ["name"]

    def __str__(self):
        return self.name
