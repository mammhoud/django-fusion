from wagtail.images.blocks import ImageChooserBlock as SimpleImageBlock

"""
Blog Wagtail Pages
"""
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField, StreamField
from apps.pages.models.pages.base import BasePage

class BlogIndexPage(BasePage):
    """
    Wagtail page for blog listing with filtering and pagination.
    """
    page_title = _("Blog")

    template = "blog/blog_index.html"

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

    # Header section
    head = StreamField(
        [
            (
                "page_title",
                blocks.StructBlock(
                    [
                        ("page_title_background", SimpleImageBlock(template="django_grep/comp/blocks/media/simple_image.html")),
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

    content_panels = Page.content_panels + [
        FieldPanel("head"),
        FieldPanel("intro"),
        FieldPanel("posts_per_page"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("intro"),
    ]

    class Meta:
        verbose_name = _("Blog Index Page")
        verbose_name_plural = _("Blog Index Pages")

    def get_posts(self, category: str = None, tag: str = None):
        """
        Get published posts with optional filtering.

        Args:
            category: Category slug to filter by
            tag: Tag slug to filter by

        Returns:
            QuerySet of published BlogPost instances
        """
        posts = BlogPost.objects.filter(status="published").order_by("-published_date")

        if category:
            posts = posts.filter(categories__slug=category)

        if tag:
            posts = posts.filter(tags__slug=tag)

        return posts

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Get filter parameters
        category = request.GET.get("category")
        tag = request.GET.get("tag")

        # Get filtered posts
        posts = self.get_posts(category=category, tag=tag)

        # Paginate
        paginator = Paginator(posts, self.posts_per_page)
        page_number = request.GET.get("page")

        try:
            paged_posts = paginator.page(page_number)
        except PageNotAnInteger:
            paged_posts = paginator.page(1)
        except EmptyPage:
            paged_posts = paginator.page(paginator.num_pages)

        # Get all categories and tags for filter UI
        from .category import BlogCategory
        from .tag import BlogTag

        context.update({
            "posts": paged_posts,
            "categories": BlogCategory.objects.all(),
            "tags": BlogTag.objects.all(),
            "current_category": category,
            "current_tag": tag,
            "total_posts": paginator.count,
            "has_pagination": paginator.num_pages > 1,
        })

        return context
