"""
django_fusion.builder.models
============================

The abstract ``BuilderPage`` — the landing builder's page model.

A concrete product subclasses ``BuilderPage`` (Wagtail page models must be
concrete) and registers it in its own app. The abstract model carries:

- ``theme`` / ``brand`` / ``dark_mode`` — the theme engine activation state.
- ``template_context`` — JSON values backing dynamic template fields
  (``{{ company.name }}``) in section copy.
- ``sections`` — the StreamField section stack (see ``blocks.py``).

Rendering is delegated to ``BuilderRenderer`` for both the server-rendered
HTML road (Wagtail preview + public template) and the JSON data-API road.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.search import index

from django_fusion.builder.blocks import BUILDER_SECTION_BLOCKS
from django_fusion.builder.themes import brand_choices, theme_choices


class BuilderPage(Page):
    """Abstract base for landing-builder pages.

    Subclass in a product app and add ``parent_page_types`` / ``subpage_types``
    plus any product-specific fields. The ``template`` defaults to
    ``builder/page.html`` (override in the subclass for a custom shell).
    """

    theme = models.CharField(
        max_length=32,
        choices=theme_choices(),
        default="default",
        verbose_name=_("Theme"),
        help_text=_("The theme engine variation applied to this page (data-theme)."),
    )
    brand = models.CharField(
        max_length=32,
        choices=brand_choices(),
        default="",
        blank=True,
        verbose_name=_("Brand"),
        help_text=_("Optional multi-brand palette override (data-brand)."),
    )
    dark_mode = models.BooleanField(
        default=False,
        verbose_name=_("Dark mode"),
        help_text=_("Render the page in dark mode (adds the .dark class)."),
    )
    template_context = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Template context"),
        help_text=_(
            "JSON values for dynamic template fields in section copy, e.g. "
            '{"company": {"name": "Structa"}} resolves {{ company.name }}.'
        ),
    )
    sections = StreamField(
        BUILDER_SECTION_BLOCKS,
        use_json_field=True,
        blank=True,
        verbose_name=_("Sections"),
        help_text=_("Compose the page from the shared fu-* section components."),
    )

    template = "builder/page.html"

    content_panels = Page.content_panels + [
        FieldPanel("template_context", classname="collapsible"),
        FieldPanel("sections"),
    ]

    settings_panels = Page.settings_panels + [
        MultiFieldPanel(
            [
                FieldPanel("theme"),
                FieldPanel("brand"),
                FieldPanel("dark_mode"),
            ],
            heading=_("Theme"),
            classname="collapsible",
        ),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("sections"),
    ]

    def get_context(self, request, *args, **kwargs):
        """Expose the builder renderer to the page template (preview road)."""
        context = super().get_context(request, *args, **kwargs)
        renderer = self.get_builder_renderer(request=request, preview=bool(getattr(request, "is_preview", False)))
        context["builder"] = renderer
        context["builder_sections"] = renderer.sections_html()
        context["builder_theme_attrs"] = renderer.theme_attrs()
        context["builder_css_urls"] = renderer.css_urls()
        context["builder_preview_issues"] = renderer.preview_issues()
        return context

    def get_builder_renderer(self, *, request=None, preview: bool = False, context_override=None):
        """Return a BuilderRenderer for this page (override point for products)."""
        from django_fusion.builder.rendering import BuilderRenderer

        return BuilderRenderer(self, request=request, preview=preview, context_override=context_override)

    def builder_payload(self) -> dict:
        """The JSON payload for the data-API road."""
        return self.get_builder_renderer().to_dict()

    class Meta:
        abstract = True


__all__ = ["BuilderPage"]
