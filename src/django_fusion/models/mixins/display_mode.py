"""
Display Mode Mixin for Wagtail Pages
=====================================

Provides a ``display_mode`` field on Wagtail page models that lets editors
choose whether the page content should open as a **detail page** (full-page
navigation) or in a **modal** overlay (Unpoly layer / HTMX modal).

Usage in a Wagtail Page model::

    from django_fusion.models.mixins.display_mode import DisplayModeMixin

    class BlogPage(DisplayModeMixin, BasePage):
        ...

The setting appears in the ``Settings`` tab of the Wagtail page editor.
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import FieldPanel


class DisplayModeMixin(models.Model):
    """
    Mixin that adds a ``display_mode`` field to choose between detail page
    and modal overlay rendering.

    The field is used by ``WagtailPageMixin`` (in
    ``django_fusion.site.interface._context_mixins``) to decide whether to serve
    the page as a full document or as a fragment target for an overlay.
    """

    class DisplayModeChoices(models.TextChoices):
        DETAIL = "detail", _("Detail page")
        MODAL  = "modal",  _("Modal / Overlay")

    display_mode = models.CharField(
        max_length=20,
        choices=DisplayModeChoices.choices,
        default=DisplayModeChoices.DETAIL,
        verbose_name=_("Display mode"),
        help_text=_(
            "How this page is displayed when navigated to.\n"
            "\n"
            "• **Detail page** — full-page navigation (default).\n"
            "• **Modal / Overlay** — opens in a modal dialog or overlay.\n"
            "\n"
            "Modal mode works with Unpoly (up-layer=\"modal\") and HTMX "
            "(swapped into a modal container)."
        ),
    )

    modal_size = models.CharField(
        max_length=10,
        choices=[
            ("sm", _("Small")),
            ("md", _("Medium")),
            ("lg", _("Large")),
            ("xl", _("Extra large")),
            ("fullscreen", _("Full screen")),
        ],
        default="lg",
        verbose_name=_("Modal size"),
        help_text=_("Width of the modal dialog (only applies when display mode is 'Modal')."),
    )

    display_mode_panels = [
        FieldPanel("display_mode"),
        FieldPanel("modal_size"),
    ]

    class Meta:
        abstract = True
        verbose_name = _("Display Mode Mixin")
        verbose_name_plural = _("Display Mode Mixins")

    @property
    def is_modal(self) -> bool:
        """Convenience: return True when the page should open in a modal."""
        return self.display_mode == self.DisplayModeChoices.MODAL

    @property
    def is_detail(self) -> bool:
        """Convenience: return True when the page should open as a full detail page."""
        return self.display_mode == self.DisplayModeChoices.DETAIL
