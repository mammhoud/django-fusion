"""
Blog Wagtail Pages — bakerydemo-inspired BlogIndexPage with RoutablePageMixin
"""
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock as SimpleImageBlock
from wagtail.search import index

from www.apps.content.models.pages.base import BasePage


class BlogIndexPage(RoutablePageMixin, BasePage):
    """
    Wagtail Blog Index Page — bakerydemo-style.

    Uses RoutablePageMixin to provide clean sub-URLs for tag and category
    filtering, matching the bakerydemo pattern:
      /blog/                       → all posts
      /blog/tags/                  → tag archive
      /blog/tags/<slug>/           → posts by tag
      /blog/category/<slug>/       → posts by category
    """

    page_title = _("Blog")
    template = "blog/blog_index.html"

    # ── Content fields ──────────────────────────────────────────────────────
    intro = RichTextField(
        blank=True,
        verbose_name=_("Introduction"),
        help_text=_("Introduction text displayed at the top of the blog index"),
    )

    posts_per_page = models.PositiveIntegerField(
        default=10,
        verbose_name=_("Posts per Page"),
        help_text=_("Number of posts to display per page"),
    )

    # Header StreamField (page title + hero image)
    head = StreamField(
        [
            (
                "page_title",
                blocks.StructBlock(
                    [
                        (
                            "page_title_background",
                            SimpleImageBlock(
                                template="django_grep/comp/blocks/media/simple_image.html"
                            ),
                        ),
                        ("page_title", blocks.CharBlock(required=True, max_length=200)),
                        (
                            "breadcrumb_home_text",
                            blocks.CharBlock(default="Home", max_length=50),
                        ),
                    ],
                    icon="image",
                    label="Page Title Section",
                ),
            ),
        ],
        use_json_field=True,
        null=True,
        blank=True,
        max_num=1,
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("head"),
        FieldPanel("intro"),
        FieldPanel("posts_per_page"),
    ]

    search_fields = BasePage.search_fields + [
        index.SearchField("intro"),
    ]

    subpage_types = []  # No Wagtail child pages; posts are Django model instances

    class Meta:
        verbose_name = _("Blog Index Page")
        verbose_name_plural = _("Blog Index Pages")

    # ── Helpers ─────────────────────────────────────────────────────────────

    def get_posts(self, category: str = None, tag: str = None, query: str = None):
        """Return published BlogPost queryset with optional filters."""
        from www.apps.blog.services import PostFilterService

        from .post import BlogPost

        qs = BlogPost.objects.filter(status="published").order_by("-published_date")

        if category:
            qs = PostFilterService.filter_by_categories(qs, [category])
        if tag:
            qs = PostFilterService.filter_by_tags(qs, [tag])
        if query:
            qs = PostFilterService.search_posts(qs, query)

        return qs

    def _paginate(self, request, queryset):
        """Paginate a queryset and return a Page object."""
        paginator = Paginator(queryset, self.posts_per_page)
        page_number = request.GET.get("page")
        try:
            return paginator.page(page_number)
        except PageNotAnInteger:
            return paginator.page(1)
        except EmptyPage:
            return paginator.page(paginator.num_pages)

    def _sidebar_context(self):
        """Return categories and tags for the sidebar."""
        from www.apps.blog.services import TagService

        from .category import BlogCategory
        from .tag import BlogTag

        return {
            "categories": BlogCategory.objects.all(),
            "tags": TagService.get_popular_tags(limit=30),
        }

    # ── Default route (all posts) ────────────────────────────────────────────

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        category = request.GET.get("category")
        tag = request.GET.get("tag")
        query = request.GET.get("q", "").strip()

        posts_qs = self.get_posts(category=category, tag=tag, query=query)
        paged = self._paginate(request, posts_qs)

        # Resolve tag/category objects for display
        from .category import BlogCategory
        from .tag import BlogTag

        tag_obj = None
        if tag:
            try:
                tag_obj = BlogTag.objects.get(slug=tag)
            except BlogTag.DoesNotExist:
                pass

        category_obj = None
        if category:
            try:
                category_obj = BlogCategory.objects.get(slug=category)
            except BlogCategory.DoesNotExist:
                pass

        context.update({
            "posts": paged,
            "current_category": category,
            "current_category_obj": category_obj,
            "current_tag": tag,
            "current_tag_obj": tag_obj,
            "search_query": query,
            "total_posts": posts_qs.count(),
            "has_pagination": paged.paginator.num_pages > 1,
            **self._sidebar_context(),
        })

        return context

    # ── Routable sub-pages (bakerydemo pattern) ──────────────────────────────

    @route(r"^tags/$", name="tag_archive")
    @route(r"^tags/([\w-]+)/$", name="tag_archive")
    def tag_archive(self, request, tag=None):
        """
        Display posts filtered by a tag slug.
        Mirrors bakerydemo's tag_archive route.
        """
        from .tag import BlogTag

        tag_obj = None
        if tag:
            try:
                tag_obj = BlogTag.objects.get(slug=tag)
            except BlogTag.DoesNotExist:
                messages.info(
                    request,
                    _('There are no blog posts tagged with "%(tag)s".') % {"tag": tag},
                )
                return redirect(self.url)

        posts_qs = self.get_posts(tag=tag)
        paged = self._paginate(request, posts_qs)

        context = self.get_context(request)
        context.update({
            "posts": paged,
            "current_tag": tag,
            "current_tag_obj": tag_obj,
            "total_posts": posts_qs.count(),
            "has_pagination": paged.paginator.num_pages > 1,
        })

        return render(request, self.template, context)

    @route(r"^category/([\w-]+)/$", name="category_archive")
    def category_archive(self, request, category=None):
        """Display posts filtered by a category slug."""
        from .category import BlogCategory

        category_obj = None
        if category:
            try:
                category_obj = BlogCategory.objects.get(slug=category)
            except BlogCategory.DoesNotExist:
                messages.info(
                    request,
                    _('There are no blog posts in category "%(cat)s".') % {"cat": category},
                )
                return redirect(self.url)

        posts_qs = self.get_posts(category=category)
        paged = self._paginate(request, posts_qs)

        context = self.get_context(request)
        context.update({
            "posts": paged,
            "current_category": category,
            "current_category_obj": category_obj,
            "total_posts": posts_qs.count(),
            "has_pagination": paged.paginator.num_pages > 1,
        })

        return render(request, self.template, context)

    @route(r"^search/$", name="search")
    def search_view(self, request):
        """HTMX live-search endpoint — returns the search_results partial."""
        from www.apps.blog.services import PostFilterService

        from .category import BlogCategory
        from .post import BlogPost
        from .tag import BlogTag

        query = request.GET.get("q", "").strip()
        tag = request.GET.get("tag")
        category = request.GET.get("category")

        posts_qs = self.get_posts(category=category, tag=tag, query=query)
        paged = self._paginate(request, posts_qs)

        context = {
            "posts": paged,
            "search_query": query,
            "current_tag": tag,
            "current_category": category,
            "result_count": posts_qs.count(),
            "is_paginated": paged.paginator.num_pages > 1,
            "page_obj": paged,
        }

        return render(request, "blog/components/search_results.html", context)

    def serve_preview(self, request, mode_name):
        return self.serve(request)
