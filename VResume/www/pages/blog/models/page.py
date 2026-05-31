"""
BlogPage — single routable page that handles both the blog listing
and individual post detail (like PortfolioPage).

Structure:
  BlogPage (root, routable)
    ├── listing view  → /blog/
    ├── tag filter    → /blog/tags/<slug>/
    ├── author filter → /blog/author/<slug>/
    └── post detail   → /blog/<post-slug>/   (child BlogPage instances)

Each blog post IS a BlogPage child — no separate BlogIndexPage needed.
The root BlogPage acts as the index; child BlogPages are the posts.
"""
from django.core.paginator import Paginator
from django.db import models
from django.shortcuts import render
from django.template.defaultfilters import truncatewords
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel, InlinePanel, MultiFieldPanel,
    TabbedInterface, ObjectList,
)
from wagtail.api import APIField
from wagtail.blocks import RichTextBlock
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable
from wagtail.search import index

from core.pages_base import BasePage
from .snippets.tag import BlogTag
from .tag import BlogPageTag


class BlogPage(BasePage):
    """
    Routable blog page.

    When used as the ROOT blog page (no parent BlogPage):
      - Acts as the index: lists child BlogPage posts.
      - Has introduction, header image, featured tags, display settings.

    When used as a CHILD blog page (parent is BlogPage):
      - Acts as an individual post.
      - Has body, authors, tags, SEO fields.

    TabbedInterface: Content | Authors | Tags | SEO | Settings
    """
    template = "base.html"
    template_name = "blog"

    # ── Shared fields (both index and post) ──────────────────────────────────
    subtitle = models.CharField(max_length=255, blank=True, verbose_name=_("Subtitle"))
    introduction = models.TextField(blank=True, verbose_name=_("Introduction"))
    featured_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Featured Image"),
    )



    # SEO
    meta_title = models.CharField(max_length=255, blank=True, verbose_name=_("Meta Title"))
    meta_description = models.TextField(blank=True, verbose_name=_("Meta Description"))
    canonical_url = models.URLField(blank=True, verbose_name=_("Canonical URL"))
    og_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("OG Image"),
    )
    # ── Newsletter Integration ──
    send_newsletter_on_publish = models.BooleanField(
        default=False,
        verbose_name=_("Send Newsletter on Publish"),
        help_text=_("If checked, an email campaign will be generated and sent to all subscribers when this page is published."),
    )

    # ── TabbedInterface ──────────────────────────────────────────────────────

    _content_panels = BasePage.content_panels + [
        MultiFieldPanel([
            FieldPanel("subtitle"),
            FieldPanel("introduction"),
            FieldPanel("featured_image"),
        ], heading=_("Basic Info")),
        InlinePanel("tagged_items", label=_("Tags")),
    ]

    _seo_panels = [
        MultiFieldPanel([
            FieldPanel("meta_title"),
            FieldPanel("meta_description"),
            FieldPanel("canonical_url"),
            FieldPanel("og_image"),
        ], heading=_("SEO & OpenGraph")),
    ]

    _settings_panels = BasePage.settings_panels + [
        FieldPanel("send_newsletter_on_publish"),
    ]

    edit_handler = TabbedInterface([
        ObjectList(_content_panels, heading=_("Content")),
        ObjectList(_seo_panels, heading=_("SEO")),
        ObjectList(BasePage.promote_panels, heading=_("Promote")),
        ObjectList(_settings_panels, heading=_("Settings")),
    ])

    search_fields = BasePage.search_fields + [
        index.SearchField("subtitle"),
        index.SearchField("introduction"),
    ]


    class Meta:
        verbose_name = _("Blog Page")
        verbose_name_plural = _("Blog Pages")
        app_label = "blog"

    def __str__(self):
        return self.title

    # ── helpers ──────────────────────────────────────────────────────────────

    @property
    def is_index(self):
        """Always True as this is only the index page."""
        return True

    def get_posts(self, tag_slug=None, author_slug=None):
        from .snippets.post import BlogPost
        posts = BlogPost.objects.filter(is_published=True).order_by("-created_at")
        if tag_slug:
            posts = posts.filter(tags__slug=tag_slug)
        if author_slug:
            posts = posts.filter(author_relationships__author__slug=author_slug)
        return posts


    def get_all_tags(self):
        return BlogTag.objects.filter(is_active=True).order_by("display_order", "name")



    # ── context ──────────────────────────────────────────────────────────────

    def get_context(self, request, *args, **kwargs):
        import json
        context = super().get_context(request, *args, **kwargs)
        context["page"] = self
        if self.is_index:
            posts = self.get_posts()
            tags = self.get_all_tags()
            tags_json = json.dumps([
                {'slug': tag.slug, 'name': tag.name}
                for tag in tags
            ])
            context.update({
                "posts": list(posts),
                "tags": tags,
                "tags_json": tags_json,
                "is_index": True,
                "current_tags": "",
                "current_q": "",
                # "featured_posts": posts.filter(is_featured=True)[:5],
            })
        return context

    def serve_preview(self, request, mode_name):
        return self.serve(request)

    # ── save ─────────────────────────────────────────────────────────────────

    def save(self, *args, **kwargs):
        if not self.meta_title:
            self.meta_title = self.title
        if not self.meta_description:
            self.meta_description = truncatewords(self.introduction or "", 25)
            
        trigger_newsletter = self.send_newsletter_on_publish
        if trigger_newsletter:
            self.send_newsletter_on_publish = False
            
        super().save(*args, **kwargs)
        
        if trigger_newsletter:
            from pages.connect.services.newsletter_tasks import trigger_blog_newsletter
            trigger_blog_newsletter.delay(self.pk)
