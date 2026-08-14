"""
Blog Post Views
"""
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView
from django_fusion.routes.views.mixins import FilterMixin, SearchMixin

from apps.pages.blog.models import BlogCategory, BlogPost, BlogTag
from apps.pages.blog.services import TagService


class BlogPostListView(SearchMixin, FilterMixin, ListView):
    """
    Standalone Django list view for blog posts (fallback when no Wagtail
    BlogIndexPage is published). Uses the same blog_index.html template as
    the Wagtail page so the UI is identical.

    Supports two filtering styles:
      - Query param:  /blog/?tag=python
      - Clean URL:    /blog/tag/python/  (tag slug passed via url_kwargs)
    """

    model = BlogPost
    template_name = "blog/blog_index.html"
    context_object_name = "posts"
    paginate_by = 10

    # SearchMixin config
    search_fields = ["title", "content", "excerpt"]

    # FilterMixin config (handles GET param ?tag= and ?category=)
    filter_by_tag = "tags__slug"
    filter_by_category = "categories__slug"

    def _get_tag_slug(self):
        """Return the active tag slug from URL kwargs or query params."""
        return self.kwargs.get("tag_slug") or self.request.GET.get("tag")

    def _get_category_slug(self):
        """Return the active category slug from URL kwargs or query params."""
        return self.kwargs.get("category_slug") or self.request.GET.get("category")

    def get_queryset(self):
        # Start with published posts as the base queryset
        queryset = BlogPost.objects.filter(status="published").order_by("-published_date")

        # Apply URL-kwargs filtering (clean URLs like /blog/tag/python/)
        tag_slug = self.kwargs.get("tag_slug")
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug).distinct()

        category_slug = self.kwargs.get("category_slug")
        if category_slug:
            queryset = queryset.filter(categories__slug=category_slug).distinct()

        # Apply GET param filtering via FilterMixin
        queryset = self.get_filter_queryset(queryset)

        # Apply search via SearchMixin
        query = self.get_search_query()
        if query:
            queryset = self.get_search_queryset(queryset, query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Blog")
        context["categories"] = BlogCategory.objects.all()
        context["tags"] = TagService.get_popular_tags(limit=20)

        # Active tag slug (from URL or query param)
        tag_slug = self._get_tag_slug()
        context["current_tag"] = tag_slug

        # Resolve the tag object for display purposes
        if tag_slug:
            try:
                context["current_tag_obj"] = BlogTag.objects.get(slug=tag_slug)
            except BlogTag.DoesNotExist:
                context["current_tag_obj"] = None
        else:
            context["current_tag_obj"] = None

        # Active category slug (from URL or query param)
        category_slug = self._get_category_slug()
        context["current_category"] = category_slug

        # Resolve the category object for display purposes
        if category_slug:
            try:
                context["current_category_obj"] = BlogCategory.objects.get(slug=category_slug)
            except BlogCategory.DoesNotExist:
                context["current_category_obj"] = None
        else:
            context["current_category_obj"] = None

        # Total count for the filter banner
        context["total_posts"] = self.get_queryset().count()
        context["has_pagination"] = self.get_queryset().count() > self.paginate_by

        return context


class BlogPostDetailView(DetailView):
    """
    Detail view for a single blog post.
    """

    model = BlogPost
    template_name = "blog/blog_detail.html"
    context_object_name = "post"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        # Only show published posts to non-staff users
        if self.request.user.is_staff:
            return BlogPost.objects.all()
        return BlogPost.objects.filter(status="published")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.object.title
        context["related_posts"] = self.object.get_related_posts(limit=3)
        context["approved_comments"] = self.object.comments.filter(is_approved=True).select_related("author")

        # Previous / next post navigation
        published_qs = BlogPost.objects.filter(status="published").order_by("-published_date")
        post_ids = list(published_qs.values_list("id", flat=True))
        try:
            idx = post_ids.index(self.object.id)
            context["prev_post"] = published_qs.get(id=post_ids[idx + 1]) if idx + 1 < len(post_ids) else None
            context["next_post"] = published_qs.get(id=post_ids[idx - 1]) if idx > 0 else None
        except (ValueError, BlogPost.DoesNotExist):
            context["prev_post"] = None
            context["next_post"] = None

        return context



class BlogSearchView(SearchMixin, FilterMixin, ListView):
    """
    HTMX-powered live search endpoint.
    Returns a partial HTML fragment (no full page) for HTMX requests,
    or redirects to the full list view for plain GET requests.
    """

    model = BlogPost
    template_name = "blog/components/search_results.html"
    context_object_name = "posts"
    paginate_by = 10

    # SearchMixin config
    search_fields = ["title", "content", "excerpt"]
    search_template = "blog/components/search_results.html"

    # FilterMixin config
    filter_by_tag = "tags__slug"
    filter_by_category = "categories__slug"

    def get_queryset(self):
        # Start with published posts as the base queryset
        queryset = BlogPost.objects.filter(status="published").order_by("-published_date")

        # Apply GET param filtering via FilterMixin
        queryset = self.get_filter_queryset(queryset)

        # Apply search via SearchMixin
        query = self.get_search_query()
        if query:
            queryset = self.get_search_queryset(queryset, query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_tag"] = self.request.GET.get("tag")
        context["current_category"] = self.request.GET.get("category")
        context["result_count"] = self.get_queryset().count()
        context["total_posts"] = context["result_count"]
        return context
