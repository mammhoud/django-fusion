"""
Project Model
Reusable project snippet for portfolio
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.images.models import Image
from wagtail.search import index

from .tag import PortfolioTag


class Project(models.Model):
    """
    Reusable Project snippet for portfolio
    Managed via ProjectViewSet in viewsets/project.py
    
    Features:
    - Rich content with HTML support
    - Video embedding (YouTube, Vimeo, etc.)
    - Technology tagging
    - Featured project support
    - Date tracking
    - Multi-field admin panels
    - Search indexing
    """
    title = models.CharField(
        max_length=200,
        verbose_name=_("Title"),
        help_text=_("Project title")
    )
    slug = models.SlugField(
        unique=True,
        verbose_name=_("Slug")
    )
    category = models.CharField(
        max_length=100,
        verbose_name=_("Category"),
        help_text=_("Project category")
    )
    description = models.TextField(
        verbose_name=_("Description"),
        help_text=_("Brief description")
    )
    body = RichTextField(
        verbose_name=_("Body"),
        help_text=_("Detailed project content"),
        blank=True
    )
    image = models.ForeignKey(
        Image,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Featured Image"),
        related_name="portfolio_projects"
    )
    video_url = models.URLField(
        blank=True,
        verbose_name=_("Video URL"),
        help_text=_("YouTube, Vimeo, etc.")
    )
    project_url = models.URLField(
        blank=True,
        verbose_name=_("Project URL"),
        help_text=_("Link to live project")
    )
    tags = models.ManyToManyField(
        PortfolioTag,
        blank=True,
        verbose_name=_("Tags"),
        help_text=_("Select portfolio tags")
    )
    tools = models.TextField(
        blank=True,
        verbose_name=_("Tools & Technologies"),
        help_text=_("Comma-separated list of tools used")
    )
    date_completed = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Date Completed")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active")
    )
    send_newsletter_on_publish = models.BooleanField(
        default=False,
        verbose_name=_("Send Newsletter on Publish"),
        help_text=_("If checked, an email campaign will be generated and sent to all subscribers.")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        MultiFieldPanel([
            FieldPanel("title"),
            FieldPanel("slug"),
            FieldPanel("category"),
        ], heading=_("Basic Information")),
        
        MultiFieldPanel([
            FieldPanel("description"),
            FieldPanel("body"),
            FieldPanel("image"),
        ], heading=_("Content")),
        
        MultiFieldPanel([
            FieldPanel("video_url"),
            FieldPanel("project_url"),
            FieldPanel("tools"),
            FieldPanel("date_completed"),
        ], heading=_("Media & Links")),
        
        MultiFieldPanel([
            FieldPanel("tags", widget=None),
        ], heading=_("Tags & Settings")),
        
        MultiFieldPanel([
            FieldPanel("is_active"),
            FieldPanel("send_newsletter_on_publish"),
        ], heading=_("Visibility & Newsletter")),
    ]

    search_fields = [
        index.SearchField("title", partial_match=True),
        index.SearchField("description"),
        index.SearchField("body"),
    ]

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ["-date_completed", "-created_at"]
        app_label = 'portfolio'

    def __str__(self):
        return self.title

    def get_tools_list(self):
        """Return tools as a list"""
        if self.tools:
            return [t.strip() for t in self.tools.split(",")]
        return []

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        trigger_newsletter = self.send_newsletter_on_publish
        if trigger_newsletter:
            self.send_newsletter_on_publish = False
        super().save(*args, **kwargs)
        if trigger_newsletter:
            from pages.connect.services.newsletter_tasks import trigger_project_newsletter
            trigger_project_newsletter.delay(self.pk)
