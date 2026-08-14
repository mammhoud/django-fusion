"""Example tagged models used by legacy tag demo views."""

from __future__ import annotations

from django.db import models


class TaggedExampleQuerySet(models.QuerySet):
    def filter_by_tag(self, tag_slug: str):
        return self.none() if not tag_slug else self.none()

    def filter_by_tags(self, tag_names: list[str], *, match_all: bool = False):
        return self.none()


class Article(models.Model):
    title = models.CharField(max_length=255)

    objects = TaggedExampleQuerySet.as_manager()

    class Meta:
        app_label = "accounts"
        managed = False


class Product(models.Model):
    title = models.CharField(max_length=255)

    objects = TaggedExampleQuerySet.as_manager()

    class Meta:
        app_label = "accounts"
        managed = False
