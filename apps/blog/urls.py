"""
Blog URL Configuration
"""
from django.urls import path

from .api import related_tags, search_tags, tag_autocomplete, tag_cloud
from .feeds import BlogCategoryFeed, BlogTagFeed, LatestBlogPostsAtomFeed, LatestBlogPostsFeed
from .views import (
    AddCommentView,
    BlogPostDetailView,
    BlogPostLikeView,
    BlogPostListView,
    BlogSearchView,
    TagCleanupView,
    TagCreateView,
    TagDeleteView,
    TagListView,
    TagUpdateView,
)

app_name = "blog"

urlpatterns = [
    path("", BlogPostListView.as_view(), name="list"),

    # HTMX live search endpoint
    path("search/", BlogSearchView.as_view(), name="search"),

    # Tag-based filtering (clean URL style: /blog/tag/python/)
    path("tag/<slug:tag_slug>/", BlogPostListView.as_view(), name="tag_filter"),

    # Category-based filtering (clean URL style: /blog/category/research/)
    path("category/<slug:category_slug>/", BlogPostListView.as_view(), name="category_filter"),

    # Tag management
    path("tags/", TagListView.as_view(), name="tag_list"),
    path("tags/create/", TagCreateView.as_view(), name="tag_create"),
    path("tags/cleanup/", TagCleanupView.as_view(), name="tag_cleanup"),
    path("tags/<slug:slug>/edit/", TagUpdateView.as_view(), name="tag_edit"),
    path("tags/<slug:slug>/delete/", TagDeleteView.as_view(), name="tag_delete"),

    # API endpoints
    path("api/tags/search/", search_tags, name="api_search_tags"),
    path("api/tags/autocomplete/", tag_autocomplete, name="api_tag_autocomplete"),
    path("api/tags/cloud/", tag_cloud, name="api_tag_cloud"),
    path("api/tags/<slug:tag_slug>/related/", related_tags, name="api_related_tags"),

    # RSS/Atom feeds
    path("feed/", LatestBlogPostsAtomFeed(), name="feed_atom"),
    path("feed/rss/", LatestBlogPostsFeed(), name="feed_rss"),
    path("feed/tag/<slug:slug>/", BlogTagFeed(), name="feed_tag"),
    path("feed/category/<slug:slug>/", BlogCategoryFeed(), name="feed_category"),

    # Post detail (must be last to avoid slug conflicts)
    path("<slug:slug>/", BlogPostDetailView.as_view(), name="detail"),

    # Comments & interactions (after detail to keep slug-based routes grouped)
    path("<slug:slug>/comment/", AddCommentView.as_view(), name="add_comment"),
    path("<slug:slug>/like/", BlogPostLikeView.as_view(), name="like_post"),
]
