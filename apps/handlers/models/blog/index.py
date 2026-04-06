# apps/blog/models/index.py
from django.contrib import messages
from django.db import models
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.fields import RichTextField
from wagtail.models import Page

from .post import BlogPage
from .tags import BlogTag


class BlogIndexPage(RoutablePageMixin, Page):
    """
    Displays a list of all BlogPage entries and supports tag and author filtering.
    """

    introduction = RichTextField(
        blank=True,
        help_text=_("Optional introduction text for the blog index.")
    )

    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Header Image"),
    )

    posts_per_page = models.PositiveIntegerField(
        default=10,
        verbose_name=_("Posts Per Page"),
        help_text=_("Number of blog posts to show per page")
    )

    show_featured_section = models.BooleanField(
        default=True,
        verbose_name=_("Show Featured Section"),
        help_text=_("Display a featured posts section at the top")
    )

    featured_posts_count = models.PositiveIntegerField(
        default=3,
        verbose_name=_("Featured Posts Count"),
        help_text=_("Number of featured posts to display")
    )

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("image"),
        MultiFieldPanel([
            FieldPanel("posts_per_page"),
            FieldPanel("show_featured_section"),
            FieldPanel("featured_posts_count"),
        ], heading=_("Display Settings")),
    ]

    api_fields = [
        APIField("introduction"),
        APIField("image"),
        APIField("posts_per_page"),
    ]

    subpage_types = ["blog.BlogPage"]
    parent_page_types = ["home.HomePage"]
    template = "blog/blog_index_page.html"

    # ======================
    # UTILITY METHODS
    # ======================

    def get_posts(self, tag=None, author=None, featured_only=False):
        """Return filtered blog posts."""
        posts = BlogPage.objects.live().descendant_of(self).order_by("-published_date")

        if tag:
            posts = posts.filter(tags__slug=tag)

        if author:
            posts = posts.filter(author_relationships__author__slug=author)

        if featured_only:
            # Simple heuristic for featured posts
            posts = posts.filter(page_views__gt=1000)

        return posts

    def get_featured_posts(self):
        """Get featured posts for the index page."""
        return self.get_posts(featured_only=True)[:self.featured_posts_count]

    def get_recent_posts(self, limit=None):
        """Get recent posts."""
        posts = self.get_posts()
        if limit:
            posts = posts[:limit]
        return posts

    def get_child_tags(self):
        """Collect unique tags from child posts."""
        from django.db.models import Count
        return BlogTag.objects.filter(
            tagged_blogs__content_object__live=True,
            tagged_blogs__content_object__path__startswith=self.path
        ).annotate(
            post_count=Count('tagged_blogs')
        ).order_by('-post_count', 'name')

    def get_authors(self):
        """Get all authors who have written posts in this blog."""
        from apps.profiles.models.contact import Person
        return Person.objects.filter(
            blog_posts__page__live=True,
            blog_posts__page__path__startswith=self.path
        ).distinct().order_by('last_name', 'first_name')

    def get_context(self, request, *args, **kwargs):
        """Extend context with posts and tag list."""
        context = super().get_context(request)

        # Get page number from request
        page_number = request.GET.get('page', 1)

        # Get paginated posts
        from django.core.paginator import Paginator
        posts = self.get_posts()
        paginator = Paginator(posts, self.posts_per_page)
        page_obj = paginator.get_page(page_number)

        context.update({
            "posts": page_obj,
            "tags": self.get_child_tags(),
            "authors": self.get_authors(),
            "featured_posts": self.get_featured_posts() if self.show_featured_section else [],
            "paginator": paginator,
            "page_obj": page_obj,
        })

        return context

    # ======================
    # ROUTES
    # ======================

    @route(r"^tags/$", name="all_tags")
    def all_tags(self, request):
        """View showing all tags."""
        context = self.get_context(request)
        context['current_view'] = 'all_tags'
        return render(request, "blog/tag_archive.html", context)

    @route(r"^tags/(?P<tag>[-\w]+)/$", name="tag_archive")
    def tag_archive(self, request, tag=None):
        """View for filtering by tag."""
        if not tag:
            messages.info(request, _("No tag provided."))
            return redirect(self.url)

        posts = self.get_posts(tag=tag)
        context = self.get_context(request)
        context.update({
            "posts": posts,
            "current_tag": tag,
            "current_view": 'tag_archive',
        })
        return render(request, "blog/blog_index_page.html", context)

    @route(r"^author/(?P<author>[-\w]+)/$", name="author_archive")
    def author_archive(self, request, author=None):
        """View for filtering by author."""
        if not author:
            messages.info(request, _("No author specified."))
            return redirect(self.url)

        posts = self.get_posts(author=author)
        context = self.get_context(request)
        context.update({
            "posts": posts,
            "current_author": author,
            "current_view": 'author_archive',
        })
        return render(request, "blog/blog_index_page.html", context)

    @route(r"^featured/$", name="featured_posts")
    def featured_posts(self, request):
        """View showing only featured posts."""
        posts = self.get_featured_posts()
        context = self.get_context(request)
        context.update({
            "posts": posts,
            "current_view": 'featured_posts',
        })
        return render(request, "blog/blog_index_page.html", context)

    def serve_preview(self, request, mode_name):
        """Fix preview issues."""
        return self.serve(request)

    class Meta:
        verbose_name = _("Blog Index")
        verbose_name_plural = _("Blog Index Pages")

    def __str__(self):
        return f"Blog Index: {self.title}"
