from django.contrib.contenttypes.fields import GenericRelation
from django.utils.translation import gettext_lazy as _
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.api import APIField
from wagtail.fields import StreamField
from wagtail.models import (
    DraftStateMixin,
    PreviewableMixin,
    RevisionMixin,
    TranslatableMixin,
)
from wagtail.search import index

from django_fusion.models.newsletter import AbstractNewsletter

from apps.domain.blocks.content.overview import OverviewBlock


class Newsletter(
    DraftStateMixin,
    RevisionMixin,
    PreviewableMixin,
    TranslatableMixin,
    ClusterableModel,
    AbstractNewsletter,
    index.Indexed,
):
    """Advanced LMS newsletter with site-specific Wagtail content blocks."""

    body = StreamField(
        OverviewBlock(template="shared/comp/blocks/content/heading_block.html"),
        blank=True,
        use_json_field=True,
        verbose_name=_("Newsletter Content"),
    )

    revisions = GenericRelation(
        "wagtailcore.Revision",
        content_type_field="base_content_type",
        object_id_field="object_id",
        related_query_name="newsletter",
        for_concrete_model=False,
    )

    content_panels = [
        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldPanel("subject"),
                FieldPanel("preview_text"),
                FieldPanel("header_image"),
                FieldPanel("body"),
            ],
            heading=_("Content"),
        ),
    ]
    template_panels = [
        MultiFieldPanel([FieldPanel("template")], heading=_("Template Configuration")),
    ]
    audience_panels = [
        MultiFieldPanel(
            [FieldPanel("audience_type"), FieldPanel("target_user_levels")],
            heading=_("Audience Targeting"),
        ),
    ]
    settings_panels = [
        MultiFieldPanel(
            [
                FieldPanel("schedule_type"),
                FieldRowPanel([FieldPanel("scheduled_date")]),
                FieldRowPanel([FieldPanel("track_opens"), FieldPanel("track_clicks")]),
                FieldPanel("include_unsubscribe"),
                FieldPanel("important_announcement"),
                FieldPanel("show_in_portal"),
                FieldPanel("test_email_addresses"),
            ],
            heading=_("Settings"),
        ),
    ]
    analytics_panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("sent_date", read_only=True),
                        FieldPanel("total_recipients", read_only=True),
                    ]
                ),
                FieldRowPanel(
                    [
                        FieldPanel("open_count", read_only=True),
                        FieldPanel("click_count", read_only=True),
                    ]
                ),
            ],
            heading=_("Delivery Analytics"),
        ),
    ]
    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading=_("Content")),
            ObjectList(template_panels, heading=_("Template")),
            ObjectList(audience_panels, heading=_("Audience")),
            ObjectList(settings_panels, heading=_("Settings")),
            ObjectList(analytics_panels, heading=_("Analytics")),
        ]
    )

    search_fields = [
        index.SearchField("title"),
        index.AutocompleteField("title"),
        index.SearchField("subject"),
        index.FilterField("audience_type"),
        index.FilterField("schedule_type"),
        index.FilterField("sent_date"),
    ]
    api_fields = [
        APIField("title"),
        APIField("subject"),
        APIField("body"),
        APIField("audience_type"),
        APIField("sent_date"),
    ]

    def save(self, *args, **kwargs):
        if not self.template:
            from apps.domain.services.email.models import EmailTemplate

            self.template = EmailTemplate.objects.filter(
                is_default=True,
                is_active=True,
            ).first()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta(TranslatableMixin.Meta):
        verbose_name = _("Newsletter")
        verbose_name_plural = _("Newsletters")
        ordering = ["-created_at"]
