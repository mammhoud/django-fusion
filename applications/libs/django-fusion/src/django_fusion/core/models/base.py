"""
Base model classes for django-fusion.

Provides abstract base models with common fields and functionality
that every Django application needs.
"""

import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    """Abstract base model with UUID primary key and automatic timestamps.

    All concrete models in the project should inherit from this class
    (or one of its subclasses) to get a consistent primary key type and
    audit trail.

    Attributes:
        id (UUIDField): Auto-generated UUID primary key.
        created_at (DateTimeField): Set automatically on first save.
        updated_at (DateTimeField): Updated automatically on every save.

    Example::

        class Article(BaseModel):
            title = models.CharField(max_length=255)

        article = Article.objects.create(title="Hello")
        print(article.id)          # UUID
        print(article.created_at)  # datetime
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_("Unique identifier"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text=_("Creation timestamp"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("Last update timestamp"),
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Return a human-readable representation including the class name and id."""
        return f"{self.__class__.__name__}({self.id})"


class TimeStampedModel(BaseModel):
    """Alias for BaseModel that makes the timestamp intent explicit.

    Prefer this class when you want to signal that timestamp tracking
    is the primary reason for inheriting from the base.

    Attributes:
        id (UUIDField): Inherited from BaseModel.
        created_at (DateTimeField): Inherited from BaseModel.
        updated_at (DateTimeField): Inherited from BaseModel.

    Example::

        class Post(TimeStampedModel):
            body = models.TextField()
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs) -> None:
        """Save the model instance, ensuring timestamps are updated.

        Args:
            *args: Positional arguments forwarded to ``Model.save()``.
            **kwargs: Keyword arguments forwarded to ``Model.save()``.
        """
        super().save(*args, **kwargs)


class UUIDModel(BaseModel):
    """Abstract model that explicitly documents UUID primary key usage.

    Functionally identical to BaseModel; use this alias when you want
    to make it clear that the UUID primary key is the key design choice
    (e.g. for distributed systems or when PKs must not be guessable).

    Attributes:
        id (UUIDField): Inherited from BaseModel.

    Example::

        class Subscription(UUIDModel):
            plan = models.CharField(max_length=50)
    """

    class Meta:
        abstract = True
