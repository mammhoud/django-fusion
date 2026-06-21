"""
Certification SnippetViewSet for Wagtail admin.
Registered via wagtail_hooks.py.
"""
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.snippets.views.snippets import SnippetViewSet

from django_rseal.content.models.certification import CertificationTemplate


class CertificationViewSet(SnippetViewSet):
    """
    Admin interface for managing certificate templates.
    """
    model = CertificationTemplate

    menu_label = _("Certificates")
    menu_icon = "doc-full"
    menu_order = 300
    add_to_admin_menu = False  # Will be in a group
    list_display = ["name", "organization_name", "is_active", "updated_at"]
    list_filter = ["is_active"]
    search_fields = ["name", "organization_name"]

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("name"),
                FieldPanel("is_active"),
            ],
            heading=_("Identity"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("certificate_title"),
                FieldPanel("organization_name"),
                FieldPanel("certifies_text"),
                FieldPanel("body_text"),
                FieldPanel("footer_text"),
            ],
            heading=_("Text Content"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("border_color"),
                FieldPanel("accent_color"),
                FieldPanel("text_color"),
            ],
            heading=_("Colors"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("logo_image"),
                FieldPanel("signature_image"),
            ],
            heading=_("Images"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("custom_template"),
                FieldPanel("custom_css"),
            ],
            heading=_("Custom Template"),
        ),
        FieldPanel("notes"),
    ]
