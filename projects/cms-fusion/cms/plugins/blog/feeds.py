"""
Blog RSS/Atom Feeds
"""
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.utils.feedgenerator import Atom1Feed

from .models import BlogCategory, BlogPost, BlogTag


class LatestBlogPostsFeed(Feed):
    """RSS 2.0 feed for the latest 20 published blog posts."""

    title = "Blog"
    link = "/blog/"
    description = "Latest blog posts"

    def items(self):
        return BlogPost.objects.filter(status="published").order_by("-published_date")[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt or item.meta_description

    def item_pubdate(self, item):
        return item.published_date

    def item_author_name(self, item):
        return item.author.get_full_name() or item.author.username


class LatestBlogPostsAtomFeed(LatestBlogPostsFeed):
    """Atom feed for the latest 20 published blog posts."""

    feed_type = Atom1Feed
    subtitle = LatestBlogPostsFeed.description


class BlogTagFeed(Feed):
    """RSS feed filtered by tag slug."""

    def get_object(self, request, slug):
        return get_object_or_404(BlogTag, slug=slug)

    def title(self, obj):
        return f"Blog — Tag: {obj.name}"

    def link(self, obj):
        return f"/blog/tag/{obj.slug}/"

    def description(self, obj):
        return f'Blog posts tagged "{obj.name}"'

    def items(self, obj):
        return BlogPost.objects.filter(
            status="published", tags=obj
        ).order_by("-published_date")[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt or item.meta_description

    def item_pubdate(self, item):
        return item.published_date

    def item_author_name(self, item):
        return item.author.get_full_name() or item.author.username


class BlogCategoryFeed(Feed):
    """RSS feed filtered by category slug."""

    def get_object(self, request, slug):
        return get_object_or_404(BlogCategory, slug=slug)

    def title(self, obj):
        return f"Blog — Category: {obj.name}"

    def link(self, obj):
        return f"/blog/category/{obj.slug}/"

    def description(self, obj):
        return f'Blog posts in category "{obj.name}"'

    def items(self, obj):
        return BlogPost.objects.filter(
            status="published", categories=obj
        ).order_by("-published_date")[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.excerpt or item.meta_description

    def item_pubdate(self, item):
        return item.published_date

    def item_author_name(self, item):
        return item.author.get_full_name() or item.author.username
